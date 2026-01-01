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
import sqlite3
from pathlib import Path
from typing import Optional

from bedrock_agentcore.runtime import BedrockAgentCoreApp
from strands import Agent, tool
from strands.models import BedrockModel

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize the AgentCore App
app = BedrockAgentCoreApp()

# Database path
DB_PATH = Path("lautech_data.db")

# ============================================================================
# DATABASE SETUP
# ============================================================================

def init_database():
    """Initialize SQLite database with LAUTECH data"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Create courses table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS courses (
            code TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            credits INTEGER,
            prerequisites TEXT,
            description TEXT,
            semester TEXT,
            lecturer TEXT,
            department TEXT
        )
    """)

    # Create fees table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS fees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            level TEXT NOT NULL,
            amount INTEGER NOT NULL,
            fee_type TEXT,
            session TEXT
        )
    """)

    # Create calendar table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS academic_calendar (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_type TEXT NOT NULL,
            event_date TEXT NOT NULL,
            semester TEXT,
            session TEXT,
            description TEXT
        )
    """)

    # Create hostels table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS hostels (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            gender TEXT,
            capacity INTEGER,
            status TEXT,
            facilities TEXT
        )
    """)

    # Insert sample data (if tables are empty)
    cursor.execute("SELECT COUNT(*) FROM courses")
    if cursor.fetchone()[0] == 0:
        courses = [
            ("CSC201", "Computer Programming II", 3, "CSC101",
             "Advanced programming concepts, data structures, and algorithms",
             "Second Semester", "Dr. Adeyemi O.", "Computer Science"),
            ("CSC301", "Database Management Systems", 3, "CSC201",
             "Database design, SQL, normalization, and transaction management",
             "First Semester", "Prof. Ibrahim S.", "Computer Science"),
            ("CSC302", "Operating Systems", 3, "CSC201",
             "Process management, memory management, file systems, and concurrency",
             "Second Semester", "Dr. Ogunleye T.", "Computer Science"),
            ("CSC303", "Web Programming", 3, "CSC201",
             "HTML, CSS, JavaScript, backend development, and web frameworks",
             "First Semester", "Mr. Adeleke M.", "Computer Science"),
        ]
        cursor.executemany("INSERT INTO courses VALUES (?, ?, ?, ?, ?, ?, ?, ?)", courses)

        fees = [
            ("100 Level", 100000, "Tuition + Acceptance", "2024/2025"),
            ("200-400 Level", 75000, "Tuition", "2024/2025"),
            ("500 Level", 85000, "Tuition", "2024/2025"),
        ]
        cursor.executemany("INSERT INTO fees (level, amount, fee_type, session) VALUES (?, ?, ?, ?)", fees)

        events = [
            ("Registration Start", "2024-09-01", "First Semester", "2024/2025", "Registration opens"),
            ("Registration End", "2024-09-15", "First Semester", "2024/2025", "Registration closes"),
            ("Semester Start", "2024-09-16", "First Semester", "2024/2025", "Classes begin"),
        ]
        cursor.executemany("INSERT INTO academic_calendar (event_type, event_date, semester, session, description) VALUES (?, ?, ?, ?, ?)", events)

        hostels = [
            ("Ajose Hall", "Male", 400, "Available", "24/7 electricity, Water, Security"),
            ("Adeoye Hall", "Female", 380, "Available", "24/7 electricity, Water, Security"),
        ]
        cursor.executemany("INSERT INTO hostels (name, gender, capacity, status, facilities) VALUES (?, ?, ?, ?, ?)", hostels)

    conn.commit()
    conn.close()
    logger.info(f"✅ Database initialized: {DB_PATH.absolute()}")


def get_courses_from_db() -> list:
    """Get courses from database"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM courses")
    courses = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return courses


def get_fees_from_db() -> list:
    """Get fees from database"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM fees")
    fees = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return fees


def get_calendar_from_db() -> list:
    """Get calendar events from database"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM academic_calendar ORDER BY event_date")
    events = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return events


def get_hostels_from_db() -> list:
    """Get hostels from database"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM hostels")
    hostels = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return hostels


# ============================================================================
# BEDROCK MODEL
# ============================================================================

bedrock_model = BedrockModel(
    model_id="us.anthropic.claude-3-5-haiku-20241022-v1:0",
    temperature=0.7,
)

# ============================================================================
# SPECIALIST AGENTS
# ============================================================================

@tool
def get_course_info(query: str) -> str:
    """Academic Agent - handles course information"""
    courses = get_courses_from_db()
    courses_context = json.dumps(courses, indent=2)

    ACADEMIC_AGENT_PROMPT = f"""
You are an Academic Advisor for LAUTECH. Help students with course information.

AVAILABLE COURSES (from database):
{courses_context}

Be helpful, informative, and provide accurate course information.
"""

    academic_agent = Agent(
        system_prompt=ACADEMIC_AGENT_PROMPT,
        model=bedrock_model,
    )

    response = academic_agent(query)
    return str(response)


@tool
def get_financial_info(query: str) -> str:
    """Financial Agent - handles fees and payment information"""
    fees = get_fees_from_db()
    fees_context = json.dumps(fees, indent=2)

    FINANCIAL_AGENT_PROMPT = f"""
You are a Financial Advisor for LAUTECH. Help students with fees and payments.

FINANCIAL INFORMATION (from database):
{fees_context}

Provide clear information about fees (use ₦ for Naira) and payment methods.
"""

    financial_agent = Agent(
        system_prompt=FINANCIAL_AGENT_PROMPT,
        model=bedrock_model,
    )

    response = financial_agent(query)
    return str(response)


@tool
def get_schedule_info(query: str) -> str:
    """Calendar Agent - handles dates and deadlines"""
    events = get_calendar_from_db()
    calendar_context = json.dumps(events, indent=2)

    CALENDAR_AGENT_PROMPT = f"""
You are a Schedule Coordinator for LAUTECH. Help students with dates and deadlines.

ACADEMIC CALENDAR (from database):
{calendar_context}

Provide specific dates clearly and remind about important deadlines.
"""

    calendar_agent = Agent(
        system_prompt=CALENDAR_AGENT_PROMPT,
        model=bedrock_model,
    )

    response = calendar_agent(query)
    return str(response)


@tool
def get_hostel_info(query: str) -> str:
    """Hostel Agent - handles accommodation information"""
    hostels = get_hostels_from_db()
    hostel_context = json.dumps(hostels, indent=2)

    HOSTEL_AGENT_PROMPT = f"""
You are a Hostel Administrator for LAUTECH. Help students with accommodation.

HOSTEL INFORMATION (from database):
{hostel_context}

Provide information about hostels, application process, and facilities.
"""

    hostel_agent = Agent(
        system_prompt=HOSTEL_AGENT_PROMPT,
        model=bedrock_model,
    )

    response = hostel_agent(query)
    return str(response)


# ============================================================================
# ORCHESTRATOR
# ============================================================================

SYSTEM_PROMPT = """
You are the LAUTECH University Assistant. You help students with university queries
by coordinating specialist agents.

Your specialist agents:
1. get_course_info - Course details, prerequisites, recommendations
2. get_schedule_info - Registration dates, deadlines, calendar
3. get_financial_info - Tuition fees, payment methods
4. get_hostel_info - Accommodation and facilities

Analyze queries and call the appropriate agent(s). Provide helpful, accurate information.
"""


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
        # Initialize database if needed
        if not DB_PATH.exists():
            init_database()

        user_input = payload.get("prompt")
        logger.info(f"User input: {user_input}")

        # Create orchestrator agent with tools
        # Note: Memory is automatically managed by AgentCore framework
        # when session IDs are provided via the invoke command
        all_tools = [
            get_course_info,
            get_schedule_info,
            get_financial_info,
            get_hostel_info,
        ]

        agent = Agent(
            tools=all_tools,
            model=bedrock_model,
            system_prompt=SYSTEM_PROMPT
        )

        # Get response from agent
        response = agent(user_input)

        # Extract and return the text content
        return response.message["content"][0]["text"]

    except Exception as e:
        logger.error(f"Error processing request: {e}", exc_info=True)
        raise


# Run the app when executed directly
if __name__ == "__main__":
    app.run()
