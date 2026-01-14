"""
LAUTECH University Assistant - Enhanced Multi-Agent System

A comprehensive university assistant with 7 specialist agents:
1. Academic Agent - Courses, prerequisites, schedules
2. Calendar Agent - Registration dates, deadlines
3. Financial Agent - Tuition, fees, payment info
4. Hostel Agent - Accommodation services
5. Library Agent - Library services and resources
6. Administrative Agent - Transcripts, certificates, ID cards
7. Orchestrator Agent - Routes queries intelligently

This version is designed for web deployment via Streamlit.
"""

import json
from datetime import datetime
from strands import Agent, tool
from strands.models import BedrockModel

# ============================================================================
# MOCK DATA - LAUTECH University Information
# ============================================================================

COURSE_CATALOG = {
    "CSC201": {
        "name": "Computer Programming II",
        "credits": 3,
        "prerequisites": ["CSC101"],
        "description": "Advanced programming concepts, data structures, and algorithms",
        "semester": "Second Semester",
        "lecturer": "Dr. Adeyemi O."
    },
    "CSC301": {
        "name": "Database Management Systems",
        "credits": 3,
        "prerequisites": ["CSC201"],
        "description": "Database design, SQL, normalization, and transaction management",
        "semester": "First Semester",
        "lecturer": "Prof. Ibrahim S."
    },
    "CSC302": {
        "name": "Operating Systems",
        "credits": 3,
        "prerequisites": ["CSC201"],
        "description": "Process management, memory management, file systems, and concurrency",
        "semester": "Second Semester",
        "lecturer": "Dr. Ogunleye T."
    },
    "CSC303": {
        "name": "Web Programming",
        "credits": 3,
        "prerequisites": ["CSC201"],
        "description": "HTML, CSS, JavaScript, backend development, and web frameworks",
        "semester": "First Semester",
        "lecturer": "Mr. Adeleke M."
    },
    "CSC401": {
        "name": "Software Engineering",
        "credits": 4,
        "prerequisites": ["CSC301"],
        "description": "Software development lifecycle, design patterns, testing, and project management",
        "semester": "First Semester",
        "lecturer": "Prof. Olaniyan K."
    },
    "MTH301": {
        "name": "Discrete Mathematics",
        "credits": 3,
        "prerequisites": ["MTH201"],
        "description": "Logic, set theory, graph theory, and combinatorics",
        "semester": "First Semester",
        "lecturer": "Dr. Balogun F."
    },
    "MTH302": {
        "name": "Numerical Analysis",
        "credits": 3,
        "prerequisites": ["MTH201", "CSC201"],
        "description": "Numerical methods for solving mathematical problems using computers",
        "semester": "Second Semester",
        "lecturer": "Prof. Akinola J."
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
    }
}

FINANCIAL_INFO = {
    "tuition_fees": {
        "undergraduate": {
            "100_level": {
                "school_fees": "₦75,000",
                "acceptance_fee": "₦25,000 (one-time)",
                "total_first_year": "₦100,000"
            },
            "200_to_400_level": {
                "school_fees": "₦75,000",
                "acceptance_fee": "N/A",
                "total": "₦75,000"
            },
            "500_level": {
                "school_fees": "₦85,000",
                "acceptance_fee": "N/A",
                "total": "₦85,000"
            }
        },
        "postgraduate": {
            "masters": "₦150,000 per session",
            "phd": "₦200,000 per session"
        }
    },
    "other_fees": {
        "hostel": "₦25,000 per session",
        "medical": "₦5,000 per session",
        "sports": "₦2,000 per session",
        "student_union": "₦1,000 per session",
        "library": "₦3,000 per session"
    },
    "payment_methods": [
        "Bank deposit (any LAUTECH designated bank)",
        "Online payment via Remita",
        "Bank transfer to LAUTECH account"
    ],
    "payment_deadlines": {
        "first_semester": "Before September 15, 2024",
        "second_semester": "Before February 15, 2025",
        "late_payment_penalty": "₦5,000"
    }
}

HOSTEL_INFO = {
    "available_hostels": {
        "male": [
            {"name": "Ajose Hall", "capacity": 400, "type": "Standard", "status": "Available"},
            {"name": "Yusuf Hall", "capacity": 350, "type": "Standard", "status": "Available"},
            {"name": "Postgraduate Hostel (Male)", "capacity": 120, "type": "PG", "status": "Available"}
        ],
        "female": [
            {"name": "Adeoye Hall", "capacity": 380, "type": "Standard", "status": "Available"},
            {"name": "Mercy Hall", "capacity": 400, "type": "Standard", "status": "Available"},
            {"name": "Postgraduate Hostel (Female)", "capacity": 100, "type": "PG", "status": "Available"}
        ]
    },
    "application_process": [
        "Pay hostel fee of ₦25,000",
        "Visit Student Affairs Office with payment receipt",
        "Complete hostel application form",
        "Receive hostel allocation within 5 working days"
    ],
    "application_deadline": "August 15, 2024",
    "facilities": [
        "24/7 electricity (with backup generator)",
        "Water supply",
        "Security personnel",
        "Common reading rooms",
        "Kitchen facilities"
    ],
    "rules": [
        "No opposite gender allowed after 8 PM",
        "Keep noise levels low after 10 PM",
        "No cooking in rooms (use common kitchen)",
        "Maintain cleanliness"
    ]
}

LIBRARY_INFO = {
    "main_library": {
        "name": "LAUTECH Central Library",
        "location": "Main Campus",
        "opening_hours": {
            "weekdays": "8:00 AM - 10:00 PM",
            "weekends": "10:00 AM - 6:00 PM",
            "exam_period": "24/7 (with student ID)"
        },
        "floors": 4,
        "seating_capacity": 1200
    },
    "services": [
        "Book borrowing (up to 4 books for 2 weeks)",
        "Reference materials (use in library only)",
        "Digital resources and e-books",
        "Study rooms (bookable)",
        "Computer lab with internet",
        "Printing and scanning services",
        "Research assistance"
    ],
    "collections": {
        "books": "Over 50,000 titles",
        "journals": "200+ subscriptions",
        "e_resources": "Access to JSTOR, IEEE, ScienceDirect",
        "theses": "Complete archive of LAUTECH theses"
    },
    "borrowing_rules": [
        "Must have valid student ID",
        "Maximum 4 books at a time",
        "2 weeks borrowing period (renewable once)",
        "₦50 per day fine for late returns"
    ],
    "contact": {
        "email": "library@lautech.edu.ng",
        "phone": "+234 803 XXX XXXX",
        "whatsapp": "+234 803 XXX XXXX"
    }
}

ADMINISTRATIVE_INFO = {
    "student_id_card": {
        "application": "Visit Registry with admission letter and 2 passport photos",
        "processing_time": "2 weeks",
        "fee": "₦2,000",
        "collection": "Registry Office, main campus"
    },
    "transcript_request": {
        "undergraduate": {
            "fee": "₦10,000 (official)",
            "processing_time": "4-6 weeks",
            "requirements": [
                "Application letter",
                "Payment receipt",
                "Photocopy of degree certificate",
                "Valid ID"
            ]
        },
        "postgraduate": {
            "fee": "₦15,000 (official)",
            "processing_time": "4-6 weeks"
        }
    },
    "certificate_collection": {
        "processing_time": "6 months after final exams",
        "notification": "Via email and notice board",
        "requirements": [
            "Clearance from all departments",
            "No outstanding fees",
            "Valid student ID"
        ]
    },
    "verification_letter": {
        "fee": "₦5,000",
        "processing_time": "3-5 working days",
        "purpose": "For employment, NYSC, further studies"
    },
    "clearance": {
        "departments": [
            "Library (no outstanding books/fines)",
            "Bursary (no outstanding fees)",
            "Hostel (if applicable)",
            "Department (project submission)",
            "ICT (return access cards)"
        ],
        "deadline": "Before certificate collection"
    },
    "contacts": {
        "registry": "registry@lautech.edu.ng",
        "student_affairs": "studentaffairs@lautech.edu.ng",
        "bursary": "bursary@lautech.edu.ng"
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
    Use for: course details, prerequisites, lecturers, course recommendations
    """
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
- Mention the semester when courses are offered and the lecturer
- Be encouraging and supportive
- If a course isn't in the catalog, politely say so

Answer the student's question using the course catalog provided.
"""

    academic_agent = Agent(
        system_prompt=ACADEMIC_AGENT_PROMPT,
        model=bedrock_model,
    )

    response = academic_agent(query)
    return str(response)


@tool
def get_schedule_info(query: str) -> str:
    """
    Calendar Agent - Handles registration dates, deadlines, and academic calendar.
    Use for: registration dates, semester dates, exam periods, important deadlines
    """
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

    calendar_agent = Agent(
        system_prompt=CALENDAR_AGENT_PROMPT,
        model=bedrock_model,
    )

    response = calendar_agent(query)
    return str(response)


@tool
def get_financial_info(query: str) -> str:
    """
    Financial Agent - Handles tuition fees, payment methods, and financial matters.
    Use for: school fees, payment deadlines, payment methods, financial aid
    """
    financial_context = json.dumps(FINANCIAL_INFO, indent=2)

    FINANCIAL_AGENT_PROMPT = f"""
You are a Financial Advisor for Ladoke Akintola University of Technology (LAUTECH).
You help students with tuition fees, payment information, and financial matters.

FINANCIAL INFORMATION:
{financial_context}

Guidelines:
- Be clear about fees and amounts (use ₦ for Naira)
- Explain payment methods and deadlines
- Remind about late payment penalties
- Be understanding and helpful with financial concerns
- Provide complete information about all applicable fees

Answer the student's question using the financial information provided.
"""

    financial_agent = Agent(
        system_prompt=FINANCIAL_AGENT_PROMPT,
        model=bedrock_model,
    )

    response = financial_agent(query)
    return str(response)


@tool
def get_hostel_info(query: str) -> str:
    """
    Hostel Agent - Handles accommodation services and hostel information.
    Use for: hostel application, room allocation, hostel fees, hostel facilities
    """
    hostel_context = json.dumps(HOSTEL_INFO, indent=2)

    HOSTEL_AGENT_PROMPT = f"""
You are a Hostel Administrator for Ladoke Akintola University of Technology (LAUTECH).
You help students with hostel accommodation, applications, and facilities.

HOSTEL INFORMATION:
{hostel_context}

Guidelines:
- Provide information about available hostels and their capacity
- Explain the application process step by step
- Mention facilities and rules
- Be helpful with accommodation concerns
- Remind about application deadlines

Answer the student's question using the hostel information provided.
"""

    hostel_agent = Agent(
        system_prompt=HOSTEL_AGENT_PROMPT,
        model=bedrock_model,
    )

    response = hostel_agent(query)
    return str(response)


@tool
def get_library_info(query: str) -> str:
    """
    Library Agent - Handles library services, hours, and resources.
    Use for: library hours, book borrowing, study spaces, library resources
    """
    library_context = json.dumps(LIBRARY_INFO, indent=2)

    LIBRARY_AGENT_PROMPT = f"""
You are a Library Services Coordinator for Ladoke Akintola University of Technology (LAUTECH).
You help students with library services, resources, and facilities.

LIBRARY INFORMATION:
{library_context}

Guidelines:
- Provide information about library hours and services
- Explain borrowing rules and procedures
- Mention available resources and facilities
- Be helpful with research and study needs
- Provide contact information when relevant

Answer the student's question using the library information provided.
"""

    library_agent = Agent(
        system_prompt=LIBRARY_AGENT_PROMPT,
        model=bedrock_model,
    )

    response = library_agent(query)
    return str(response)


@tool
def get_administrative_info(query: str) -> str:
    """
    Administrative Agent - Handles transcripts, certificates, ID cards, and administrative services.
    Use for: student ID, transcripts, certificates, clearance, verification letters
    """
    admin_context = json.dumps(ADMINISTRATIVE_INFO, indent=2)

    ADMIN_AGENT_PROMPT = f"""
You are an Administrative Officer for Ladoke Akintola University of Technology (LAUTECH).
You help students with administrative services like transcripts, certificates, and ID cards.

ADMINISTRATIVE INFORMATION:
{admin_context}

Guidelines:
- Explain procedures clearly step by step
- Mention fees, processing times, and requirements
- Provide contact information for relevant departments
- Be patient and thorough with administrative processes
- Remind about necessary clearances and deadlines

Answer the student's question using the administrative information provided.
"""

    admin_agent = Agent(
        system_prompt=ADMIN_AGENT_PROMPT,
        model=bedrock_model,
    )

    response = admin_agent(query)
    return str(response)


# ============================================================================
# ORCHESTRATOR AGENT
# ============================================================================

def create_university_assistant():
    """
    Create the Orchestrator Agent that coordinates all specialist agents.

    The orchestrator intelligently routes queries to the appropriate specialists:
    - Academic questions → get_course_info
    - Calendar/dates → get_schedule_info
    - Financial matters → get_financial_info
    - Hostel/accommodation → get_hostel_info
    - Library services → get_library_info
    - Administrative services → get_administrative_info

    Can call multiple agents for complex queries.

    Returns:
        Agent: The orchestrator agent
    """

    ORCHESTRATOR_PROMPT = """
You are the LAUTECH University Assistant. You help students and staff with all
university-related queries by coordinating with specialist agents.

Your specialist agents:
1. get_course_info - Course details, prerequisites, lecturers, recommendations
2. get_schedule_info - Registration dates, semester dates, exam periods, deadlines
3. get_financial_info - Tuition fees, payment methods, deadlines, financial aid
4. get_hostel_info - Hostel application, facilities, rules, accommodation
5. get_library_info - Library hours, borrowing, resources, study spaces
6. get_administrative_info - Student ID, transcripts, certificates, clearance

How to handle queries:
- Analyze the query to identify what information is needed
- Call the appropriate specialist agent(s)
- If a query needs multiple types of information, call multiple agents
- Combine responses into a clear, organized answer
- Always be helpful, friendly, and professional

Examples:
- "How much is school fees?" → get_financial_info
- "When is registration?" → get_schedule_info
- "What courses can I take?" → get_course_info
- "I need a transcript" → get_administrative_info
- "Tell me about the library" → get_library_info
- "How do I apply for hostel?" → get_hostel_info
- "When is registration and how much is the fee?" → get_schedule_info AND get_financial_info

Be warm, supportive, and provide complete information. You represent LAUTECH!
"""

    orchestrator = Agent(
        system_prompt=ORCHESTRATOR_PROMPT,
        tools=[
            get_course_info,
            get_schedule_info,
            get_financial_info,
            get_hostel_info,
            get_library_info,
            get_administrative_info,
        ],
        model=bedrock_model,
    )

    return orchestrator


# ============================================================================
# HELPER FUNCTIONS FOR WEB INTERFACE
# ============================================================================

def get_assistant():
    """Get or create the university assistant (for web interface)"""
    return create_university_assistant()


def ask_question(question: str) -> str:
    """
    Ask a question to the university assistant.
    This is the main function used by the web interface.

    Args:
        question: The user's question

    Returns:
        str: The assistant's response
    """
    assistant = get_assistant()
    response = assistant(question)
    return str(response)


# ============================================================================
# DEMO FUNCTION (for testing)
# ============================================================================

def demo():
    """
    Test the enhanced multi-agent system with various queries
    """
    print("=" * 80)
    print("LAUTECH University Assistant - Enhanced Multi-Agent System")
    print("=" * 80)
    print("\nSpecialist Agents:")
    print("  📚 Academic Agent - Courses and prerequisites")
    print("  📅 Calendar Agent - Dates and deadlines")
    print("  💰 Financial Agent - Fees and payments")
    print("  🏠 Hostel Agent - Accommodation")
    print("  📖 Library Agent - Library services")
    print("  📋 Administrative Agent - Documents and clearance")
    print("  🎯 Orchestrator - Intelligent routing\n")

    assistant = create_university_assistant()

    test_queries = [
        "How much is the school fee for a 200 level student?",
        "When does registration start for the first semester?",
        "What courses can I take after CSC201?",
        "How do I apply for hostel accommodation?",
        "What are the library opening hours?",
        "How do I get my transcript?",
        "I'm a new student. When should I pay my fees and when is registration?" # Multi-agent
    ]

    for i, query in enumerate(test_queries, 1):
        print("─" * 80)
        print(f"\n📝 TEST {i}: {query}\n")

        start_time = datetime.now()
        response = assistant(query)
        end_time = datetime.now()

        print(f"🤖 Response:\n{response}")
        print(f"\n⏱️  Time: {(end_time - start_time).total_seconds():.2f}s\n")

    print("=" * 80)
    print("✅ Demo Complete!")
    print("=" * 80)


if __name__ == "__main__":
    demo()
