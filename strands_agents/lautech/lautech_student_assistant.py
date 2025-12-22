"""
LAUTECH Student Query Router - Multi-Agent System

This demonstrates a multi-agent system using the Strands framework where:
1. Specialist agents (Academic, Calendar) are implemented as @tool functions
2. An Orchestrator agent routes student queries to the appropriate specialists
3. Agents can work together to answer complex queries

Pattern: Agents as Tools
- Each specialist agent is a @tool that creates an Agent internally
- The orchestrator Agent has tools=[academic_agent, calendar_agent]
- The orchestrator decides which tools to call based on the query
"""

import json
from datetime import datetime
from strands import Agent, tool
from strands.models import BedrockModel

# ============================================================================
# MOCK DATA - LAUTECH Course Catalog & Academic Calendar
# ============================================================================

COURSE_CATALOG = {
    "CSC201": {
        "name": "Computer Programming II",
        "credits": 3,
        "prerequisites": ["CSC101"],
        "description": "Advanced programming concepts, data structures, and algorithms",
        "semester": "Second Semester"
    },
    "CSC301": {
        "name": "Database Management Systems",
        "credits": 3,
        "prerequisites": ["CSC201"],
        "description": "Database design, SQL, normalization, and transaction management",
        "semester": "First Semester"
    },
    "CSC302": {
        "name": "Operating Systems",
        "credits": 3,
        "prerequisites": ["CSC201"],
        "description": "Process management, memory management, file systems, and concurrency",
        "semester": "Second Semester"
    },
    "CSC303": {
        "name": "Web Programming",
        "credits": 3,
        "prerequisites": ["CSC201"],
        "description": "HTML, CSS, JavaScript, backend development, and web frameworks",
        "semester": "First Semester"
    },
    "MTH301": {
        "name": "Discrete Mathematics",
        "credits": 3,
        "prerequisites": ["MTH201"],
        "description": "Logic, set theory, graph theory, and combinatorics",
        "semester": "First Semester"
    },
    "MTH302": {
        "name": "Numerical Analysis",
        "credits": 3,
        "prerequisites": ["MTH201", "CSC201"],
        "description": "Numerical methods for solving mathematical problems using computers",
        "semester": "Second Semester"
    }
}

ACADEMIC_CALENDAR = {
    "2024/2025_first_semester": {
        "registration_start": "2024-09-01",
        "registration_end": "2024-09-15",
        "semester_start": "2024-09-16",
        "add_drop_deadline": "2024-09-30",
        "mid_semester_break": "2024-11-04",
        "semester_end": "2024-12-20",
        "exam_period": "2025-01-06 to 2025-01-20"
    },
    "2024/2025_second_semester": {
        "registration_start": "2025-02-01",
        "registration_end": "2025-02-15",
        "semester_start": "2025-02-16",
        "add_drop_deadline": "2025-03-02",
        "mid_semester_break": "2025-04-14",
        "semester_end": "2025-06-15",
        "exam_period": "2025-06-20 to 2025-07-10"
    },
    "important_deadlines": {
        "tuition_payment": "Before registration closes",
        "hostel_application": "2024-08-15",
        "course_withdrawal": "Before mid-semester break",
        "examination_clearance": "One week before exams"
    }
}

# ============================================================================
# BEDROCK MODEL CONFIGURATION
# ============================================================================

bedrock_model = BedrockModel(
    model_id="us.anthropic.claude-3-5-haiku-20241022-v1:0",
    temperature=0.7,
)

# ============================================================================
# SPECIALIST AGENTS (implemented as @tool functions)
# ============================================================================

@tool
def get_course_info(query: str) -> str:
    """
    Academic Agent - Handles course information, prerequisites, and schedules.

    This agent has access to the LAUTECH course catalog and can answer:
    - Course details (name, credits, description)
    - Prerequisites for courses
    - Course availability by semester
    - Course recommendations based on completed courses

    Args:
        query: Student's question about courses

    Returns:
        Detailed response about course information
    """
    # Prepare course catalog as context for the agent
    courses_context = json.dumps(COURSE_CATALOG, indent=2)

    ACADEMIC_AGENT_PROMPT = f"""
You are an Academic Advisor for Ladoke Akintola University of Technology (LAUTECH).
You help students with course information, prerequisites, and academic planning.

AVAILABLE COURSES:
{courses_context}

Guidelines:
- Be helpful and informative
- When listing prerequisites, explain what they are
- Suggest courses students can take after completing prerequisites
- Mention the semester when courses are offered
- Be encouraging and supportive

Answer the student's question using the course catalog provided.
"""

    # Create the Academic Agent
    academic_agent = Agent(
        system_prompt=ACADEMIC_AGENT_PROMPT,
        model=bedrock_model,
    )

    # Get response from the academic agent
    response = academic_agent(query)
    return str(response)


@tool
def get_schedule_info(query: str) -> str:
    """
    Calendar Agent - Handles registration dates, deadlines, and academic calendar.

    This agent has access to the LAUTECH academic calendar and can answer:
    - Registration dates (start/end)
    - Semester start/end dates
    - Important deadlines (add/drop, withdrawal, etc.)
    - Exam periods
    - Payment deadlines

    Args:
        query: Student's question about dates and deadlines

    Returns:
        Detailed response about calendar information
    """
    # Prepare calendar as context for the agent
    calendar_context = json.dumps(ACADEMIC_CALENDAR, indent=2)

    CALENDAR_AGENT_PROMPT = f"""
You are a Schedule Coordinator for Ladoke Akintola University of Technology (LAUTECH).
You help students with registration dates, deadlines, and the academic calendar.

ACADEMIC CALENDAR:
{calendar_context}

Guidelines:
- Provide specific dates clearly
- Remind students about important deadlines
- Be helpful with planning and time management tips
- Format dates in a readable way (e.g., "September 1, 2024")
- If multiple semesters are relevant, mention both

Answer the student's question using the academic calendar provided.
"""

    # Create the Calendar Agent
    calendar_agent = Agent(
        system_prompt=CALENDAR_AGENT_PROMPT,
        model=bedrock_model,
    )

    # Get response from the calendar agent
    response = calendar_agent(query)
    return str(response)


# ============================================================================
# ORCHESTRATOR AGENT
# ============================================================================

def create_student_assistant():
    """
    Create the Orchestrator Agent that coordinates specialist agents.

    The orchestrator:
    - Analyzes student queries
    - Decides which specialist agent(s) to call
    - Combines responses from multiple agents when needed
    - Returns comprehensive answers to students

    Tools available to orchestrator:
    - get_course_info: For academic/course questions
    - get_schedule_info: For calendar/deadline questions

    Returns:
        Agent: The orchestrator agent
    """

    ORCHESTRATOR_PROMPT = """
You are the LAUTECH Student Assistant Coordinator. You help route student queries
to the appropriate specialist agents and combine their responses.

Your specialist agents:
1. get_course_info - Use for questions about:
   - Course details, prerequisites, descriptions
   - What courses to take
   - Course availability by semester

2. get_schedule_info - Use for questions about:
   - Registration dates
   - Important deadlines
   - Semester dates
   - Exam periods

How to handle queries:
- If a query is ONLY about courses → call get_course_info
- If a query is ONLY about dates/deadlines → call get_schedule_info
- If a query needs BOTH (e.g., "When is registration and what courses can I take?")
  → call BOTH tools and combine the information

Always be helpful, friendly, and provide complete answers. When combining responses
from multiple agents, present the information in a clear, organized way.
"""

    orchestrator = Agent(
        system_prompt=ORCHESTRATOR_PROMPT,
        tools=[get_course_info, get_schedule_info],  # Specialist agents as tools
        model=bedrock_model,
    )

    return orchestrator


# ============================================================================
# DEMO FUNCTION
# ============================================================================

def demo():
    """
    Demonstrate the multi-agent system with 3 test queries:
    1. Calendar-only query (uses Calendar Agent)
    2. Course-only query (uses Academic Agent)
    3. Combined query (uses BOTH agents - demonstrates multi-agent coordination)
    """
    print("=" * 80)
    print("LAUTECH Student Query Router - Multi-Agent System Demo")
    print("=" * 80)
    print("\nThis demo shows how the Orchestrator routes queries to specialist agents:")
    print("  📚 Academic Agent - Course info, prerequisites, schedules")
    print("  📅 Calendar Agent - Registration dates, deadlines, calendar")
    print("  🎯 Orchestrator - Routes queries and combines responses\n")

    # Create the orchestrator
    assistant = create_student_assistant()

    # Test queries
    test_queries = [
        {
            "query": "When is registration for the upcoming semester?",
            "expected_agent": "Calendar Agent only",
            "description": "Pure calendar question"
        },
        {
            "query": "What courses can I take after completing CSC201?",
            "expected_agent": "Academic Agent only",
            "description": "Pure course question"
        },
        {
            "query": "When does registration start and what courses are available in the first semester?",
            "expected_agent": "BOTH Calendar + Academic Agents",
            "description": "Combined query requiring multi-agent coordination"
        }
    ]

    # Execute test queries
    for i, test in enumerate(test_queries, 1):
        print("─" * 80)
        print(f"\n📝 TEST QUERY {i} ({test['description']})")
        print(f"Expected: {test['expected_agent']}")
        print("─" * 80)
        print(f"\nStudent Question: \"{test['query']}\"\n")

        # Track execution time
        start_time = datetime.now()

        # Send query to orchestrator
        response = assistant(test['query'])

        end_time = datetime.now()
        execution_time = (end_time - start_time).total_seconds()

        print(f"\n🤖 Response:")
        print(str(response))
        print(f"\n⏱️  Response time: {execution_time:.2f} seconds")
        print()

    print("=" * 80)
    print("✅ DEMO COMPLETE!")
    print("=" * 80)
    print("\n🔍 How Multi-Agent Coordination Works:")
    print("""
1. ORCHESTRATOR receives the student query
2. ORCHESTRATOR analyzes what information is needed:
   - Course info? → Call get_course_info (Academic Agent)
   - Calendar info? → Call get_schedule_info (Calendar Agent)
   - Both? → Call BOTH tools
3. Each SPECIALIST AGENT:
   - Has its own system prompt with domain knowledge
   - Has access to specific data (courses OR calendar)
   - Returns focused, expert responses
4. ORCHESTRATOR combines responses into a complete answer
5. Student gets comprehensive, accurate information

Key Benefits:
✓ Separation of concerns (each agent is an expert in one domain)
✓ Reusable components (@tool functions can be used independently)
✓ Scalable (easy to add new specialist agents)
✓ Clear coordination pattern (orchestrator decides which agents to call)
""")


# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    demo()
