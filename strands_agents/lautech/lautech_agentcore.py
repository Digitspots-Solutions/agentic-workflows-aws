"""
LAUTECH University Assistant - AgentCore Version

This version uses Amazon Bedrock AgentCore for production deployment.
Following the same pattern as prod_agent/cdk_agent_core.py

Features:
- Deploys to AWS Lambda via AgentCore
- Database-backed with SQLite (upgradeable to RDS)
- Multi-agent system with intelligent routing
- Production-ready with proper error handling
"""

import logging
import json
import os
import shutil
from pathlib import Path
from typing import Optional

from bedrock_agentcore.runtime import BedrockAgentCoreApp
from bedrock_agentcore.memory.integrations.strands.config import AgentCoreMemoryConfig
from bedrock_agentcore.memory.integrations.strands.session_manager import AgentCoreMemorySessionManager
from strands import Agent, tool
from strands.models import BedrockModel

# Import database utilities (supports both SQLite and PostgreSQL)
from db_utils import (
    init_database,
    get_courses,
    get_fees,
    get_calendar,
    get_hostels,
    USE_POSTGRES
)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize the AgentCore App
app = BedrockAgentCoreApp()

# Memory ID (from agentcore memory list)
MEMORY_ID = os.getenv('AGENTCORE_MEMORY_ID', 'lautech_agentcore_mem-yeGCqwG7EM')

# Database configuration
# For SQLite (local/dev): Set USE_POSTGRES=false and SQLITE_PATH
# For PostgreSQL (production): Set USE_POSTGRES=true and DB_SECRET_NAME
logger.info(f"Database mode: {'PostgreSQL (RDS)' if USE_POSTGRES else 'SQLite (local)'}")


# ============================================================================
# BEDROCK MODEL WITH GUARDRAILS
# ============================================================================

# Guardrail configuration for responsible AI (AWS AI Competency: QCHK-005)
GUARDRAIL_ID = os.getenv('BEDROCK_GUARDRAIL_ID', '')
GUARDRAIL_VERSION = os.getenv('BEDROCK_GUARDRAIL_VERSION', 'DRAFT')

# Build model configuration
model_config = {
    "model_id": "us.anthropic.claude-3-5-haiku-20241022-v1:0",
    "temperature": 0.7,
}

# Add guardrails if configured
if GUARDRAIL_ID:
    model_config["guardrail_config"] = {
        "guardrailIdentifier": GUARDRAIL_ID,
        "guardrailVersion": GUARDRAIL_VERSION
    }
    logger.info(f"🛡️  Guardrails enabled: {GUARDRAIL_ID} (v{GUARDRAIL_VERSION})")
else:
    logger.warning("⚠️  No guardrails configured. Set BEDROCK_GUARDRAIL_ID for production.")

bedrock_model = BedrockModel(**model_config)

# ============================================================================
# SPECIALIST AGENTS
# ============================================================================

@tool
def get_course_info(search: str = None) -> str:
    """Search for courses. Pass a course code or name to search, or leave empty for top results."""
    courses = get_courses(limit=10, search=search)
    if not courses:
        return "No courses found."
    return json.dumps(courses, separators=(',', ':'))  # Compact JSON


@tool
def get_financial_info(level: str = None) -> str:
    """Get tuition fees. Pass level (e.g. '100', '200') to filter, or leave empty for all."""
    fees = get_fees(limit=10, level=level)
    if not fees:
        return "No fees found."
    return json.dumps(fees, separators=(',', ':'))  # Compact JSON


@tool
def get_schedule_info() -> str:
    """Get upcoming academic calendar events and deadlines."""
    events = get_calendar(limit=10)
    if not events:
        return "No calendar events found."
    return json.dumps(events, separators=(',', ':'))  # Compact JSON


@tool
def get_hostel_info(gender: str = None) -> str:
    """Get hostel information. Pass 'male', 'female', or 'mixed' to filter by gender."""
    hostels = get_hostels(limit=50, gender=gender)
    if not hostels:
        return "No hostels found."
    return json.dumps(hostels, separators=(',', ':'))  # Compact JSON


# ============================================================================
# ORCHESTRATOR
# ============================================================================

SYSTEM_PROMPT = """
You are the LAUTECH University Assistant. You are a helpful, friendly AI that assists students.

MEMORY INSTRUCTIONS:
1. You have MEMORY of the current conversation session.
2. You MUST remember details the user tells you (name, level, faculty, etc.).
3. If the user asks "What is my name?", you MUST answer based on the conversation history.
4. DO NOT claim you cannot remember. You CAN remember within the current session.

Your specialist agents for university data:
1. get_course_info - Course details, prerequisites, recommendations
2. get_schedule_info - Registration dates, deadlines, calendar
3. get_financial_info - Tuition fees, payment methods
4. get_hostel_info - Accommodation and facilities

CRITICAL: Always interpret tool results literally. For example, if get_hostel_info returns
a hostel with gender 'Mixed', don't claim there are no mixed hostels. Provide helpful, 
accurate information based on the LIVE database results.
"""

# ============================================================================
# GLOBAL INITIALIZATION (Run once at module load)
# ============================================================================

# Initialize database once at startup
logger.info("🚀 Initializing database at module load...")
if not USE_POSTGRES:
    # SQLite mode: handle database file setup
    from pathlib import Path
    DB_PATH = Path(os.getenv('SQLITE_PATH', '/tmp/lautech_data.db'))
    PACKAGED_DB_PATH = Path("lautech_data.db")

    if not DB_PATH.exists():
        if PACKAGED_DB_PATH.exists():
            logger.info(f"📦 Copying packaged database to {DB_PATH}")
            shutil.copy(PACKAGED_DB_PATH, DB_PATH)
        else:
            logger.info("🆕 Creating fresh SQLite database")

# Initialize schema once (works for both SQLite and PostgreSQL)
init_database()
logger.info("✅ Database initialized")

# Create tools list once
ALL_TOOLS = [
    get_course_info,
    get_schedule_info,
    get_financial_info,
    get_hostel_info,
]


# ============================================================================
# RESPONSE CACHE (reduces latency for common queries)
# ============================================================================

import hashlib
from functools import lru_cache

# Simple TTL cache for agent responses
_response_cache = {}
_cache_ttl = 300  # 5 minutes

def get_cached_response(query_hash):
    """Get cached response if available and not expired"""
    import time
    if query_hash in _response_cache:
        cached_at, response = _response_cache[query_hash]
        if time.time() - cached_at < _cache_ttl:
            return response
    return None

def cache_response(query_hash, response):
    """Cache a response"""
    import time
    _response_cache[query_hash] = (time.time(), response)


# ============================================================================
# AGENTCORE ENTRYPOINT
# ============================================================================

@app.entrypoint
def lautech_assistant(payload):
    """
    AgentCore entrypoint for LAUTECH Assistant
    
    Args:
        payload (dict): Contains the prompt from the user
        
    Returns:
        str: The agent's response text
    """
    try:
        import time
        start_time = time.time()
        
        user_input = payload.get("prompt")
        logger.info(f"User input: {user_input}")
        
        # Check cache first for common queries
        query_hash = hashlib.md5(user_input.lower().strip().encode()).hexdigest()
        cached = get_cached_response(query_hash)
        if cached:
            logger.info(f"⚡ CACHE HIT - returning in {time.time() - start_time:.2f}s")
            return cached

        # Get session info from payload context - CRITICAL: each user needs unique session for privacy
        # Generate unique ID if not provided to prevent shared conversation history
        session_id = payload.get("session_id") or f"anon_{hashlib.md5(str(time.time()).encode()).hexdigest()[:12]}"
        actor_id = payload.get("actor_id", "anonymous")
        logger.info(f"Session ID: {session_id}, Actor ID: {actor_id}")

        # Configure AgentCore Memory
        t1 = time.time()
        memory_config = AgentCoreMemoryConfig(
            memory_id=MEMORY_ID,
            session_id=session_id,
            actor_id=actor_id
        )
        logger.info(f"⏱️  Memory config creation: {time.time() - t1:.2f}s")

        # Create session manager with memory
        t2 = time.time()
        session_manager = AgentCoreMemorySessionManager(
            agentcore_memory_config=memory_config,
            region_name="us-east-1"
        )
        logger.info(f"⏱️  Session manager init: {time.time() - t2:.2f}s")

        # Create orchestrator agent with tools and memory
        t3 = time.time()
        agent = Agent(
            tools=ALL_TOOLS,
            model=bedrock_model,
            system_prompt=SYSTEM_PROMPT,
            session_manager=session_manager
        )
        logger.info(f"⏱️  Agent creation: {time.time() - t3:.2f}s")

        # Get response from agent
        t4 = time.time()
        response = agent(user_input)
        logger.info(f"⏱️  Agent execution: {time.time() - t4:.2f}s")
        
        logger.info(f"⏱️  TOTAL REQUEST TIME: {time.time() - start_time:.2f}s")

        # Extract and return the text content
        result = response.message["content"][0]["text"]
        
        # Cache the response for similar future queries
        cache_response(query_hash, result)
        
        return result

    except Exception as e:
        logger.error(f"Error processing request: {e}", exc_info=True)
        raise


# Make WSGI app available for AgentCore
application = app
if __name__ == "__main__":
    app.run()
