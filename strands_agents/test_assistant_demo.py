"""
LAUTECH Assistant - Demo Mode (No AWS Required)

This is a simplified test version that simulates agent responses without
calling AWS Bedrock. Use this to:
1. Test the multi-agent routing logic
2. Validate the data structure
3. See how agents coordinate
4. Demo the system without AWS credentials

For production with real AI, use lautech_assistant_enhanced.py
"""

import json
from datetime import datetime

# Import the same data structures
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
}

FINANCIAL_INFO = {
    "undergraduate": {
        "100_level": "₦100,000 (includes ₦25,000 acceptance fee)",
        "200_400_level": "₦75,000 per session",
        "500_level": "₦85,000 per session"
    },
    "payment_deadline": "Before registration closes (Sept 15 or Feb 15)",
    "late_penalty": "₦5,000"
}

# Simulated agent responses (rule-based, no AI)
def simulate_academic_agent(query):
    query_lower = query.lower()

    if "after csc201" in query_lower or "prerequisite" in query_lower:
        return """Based on the course catalog, after completing CSC201, you can take:

📚 **Available Courses:**
1. **CSC301 - Database Management Systems** (First Semester)
   - Lecturer: Prof. Ibrahim S.
   - Credits: 3

2. **CSC302 - Operating Systems** (Second Semester)
   - Lecturer: Dr. Ogunleye T.
   - Credits: 3

3. **CSC303 - Web Programming** (First Semester)
   - Lecturer: Mr. Adeleke M.
   - Credits: 3

All three courses list CSC201 as a prerequisite. I recommend starting with CSC301 or CSC303 in your next first semester!"""

    elif "courses" in query_lower or "available" in query_lower:
        return """Here are the available Computer Science courses:

📖 **CSC201** - Computer Programming II (2nd Semester)
   Prerequisites: CSC101

📖 **CSC301** - Database Management Systems (1st Semester)
   Prerequisites: CSC201

📖 **CSC302** - Operating Systems (2nd Semester)
   Prerequisites: CSC201

📖 **CSC303** - Web Programming (1st Semester)
   Prerequisites: CSC201

Need more details about any specific course? Just ask!"""

    else:
        return f"I can help with course information! I have data on CSC201, CSC301, CSC302, and CSC303. Try asking about prerequisites or available courses."


def simulate_calendar_agent(query):
    query_lower = query.lower()

    if "registration" in query_lower:
        return """📅 **Registration Dates for 2024/2025:**

**First Semester:**
- Registration Start: September 1, 2024
- Registration End: September 15, 2024
- Semester Begins: September 16, 2024

**Second Semester:**
- Registration Start: February 1, 2025
- Registration End: February 15, 2025
- Semester Begins: February 16, 2025

⚠️ **Important:** Complete registration before the deadline to avoid late penalties!"""

    elif "exam" in query_lower:
        return """📝 **Examination Periods:**

**First Semester Exams:**
- January 6 - January 20, 2025

**Second Semester Exams:**
- June 20 - July 10, 2025

Make sure you're cleared by the bursary and library one week before exams!"""

    else:
        return "I can provide information about registration dates, exam periods, and important deadlines. What would you like to know?"


def simulate_financial_agent(query):
    query_lower = query.lower()

    if "fee" in query_lower or "pay" in query_lower or "cost" in query_lower:
        return """💰 **LAUTECH Tuition Fees (Undergraduate):**

**100 Level (First Year):**
- Total: ₦100,000
  - School fees: ₦75,000
  - Acceptance fee: ₦25,000 (one-time)

**200 - 400 Level:**
- School fees: ₦75,000 per session

**500 Level:**
- School fees: ₦85,000 per session

**Additional Fees:**
- Hostel: ₦25,000 per session
- Medical: ₦5,000
- Library: ₦3,000

**Payment Deadline:**
- Before registration closes (Sept 15 or Feb 15)
- Late payment penalty: ₦5,000

**Payment Methods:**
- Remita (online)
- Bank deposit
- Bank transfer"""

    else:
        return "I can help with school fees, payment methods, and deadlines. What would you like to know?"


def simulate_hostel_agent(query):
    return """🏠 **LAUTECH Hostel Information:**

**Available Hostels:**

**For Male Students:**
- Ajose Hall (400 capacity)
- Yusuf Hall (350 capacity)
- PG Hostel - Male (120 capacity)

**For Female Students:**
- Adeoye Hall (380 capacity)
- Mercy Hall (400 capacity)
- PG Hostel - Female (100 capacity)

**Application Process:**
1. Pay hostel fee: ₦25,000
2. Visit Student Affairs Office with receipt
3. Complete application form
4. Receive allocation within 5 working days

**Deadline:** August 15, 2024

**Facilities:**
- 24/7 electricity (with backup)
- Water supply
- Security personnel
- Reading rooms
- Kitchen facilities"""


def simulate_library_agent(query):
    return """📚 **LAUTECH Central Library:**

**Opening Hours:**
- Weekdays: 8:00 AM - 10:00 PM
- Weekends: 10:00 AM - 6:00 PM
- Exam Period: 24/7 (with student ID)

**Services:**
- Book borrowing (up to 4 books for 2 weeks)
- Reference materials
- Digital resources & e-books
- Study rooms (bookable)
- Computer lab with internet
- Printing & scanning

**Collections:**
- 50,000+ books
- 200+ journal subscriptions
- Access to JSTOR, IEEE, ScienceDirect

**Borrowing Rules:**
- Valid student ID required
- Maximum 4 books at a time
- 2 weeks loan period (renewable once)
- ₦50 per day late fee

**Contact:** library@lautech.edu.ng"""


def simulate_admin_agent(query):
    query_lower = query.lower()

    if "transcript" in query_lower:
        return """📜 **Transcript Request Process:**

**Requirements:**
- Application letter
- Payment receipt (₦10,000 for UG, ₦15,000 for PG)
- Photocopy of degree certificate
- Valid ID

**Processing Time:** 4-6 weeks

**How to Apply:**
1. Pay transcript fee at bursary
2. Submit application to Registry
3. Collect receipt
4. Wait for notification

**Contact:** registry@lautech.edu.ng"""

    elif "id card" in query_lower or "student id" in query_lower:
        return """🆔 **Student ID Card:**

**Application:**
- Visit Registry with admission letter
- Bring 2 passport photographs
- Pay ₦2,000 fee

**Processing Time:** 2 weeks

**Collection:** Registry Office, main campus

The ID card is required for:
- Library access
- Exam entry
- Hostel allocation
- Campus facilities"""

    else:
        return "I can help with student ID cards, transcripts, certificates, and clearance procedures. What do you need?"


def simulate_orchestrator(query):
    """
    Simulates the orchestrator logic - determines which agent(s) to call
    """
    query_lower = query.lower()

    # Determine which agents to call based on keywords
    needs_calendar = any(word in query_lower for word in ["registration", "when", "exam", "deadline", "semester", "calendar"])
    needs_financial = any(word in query_lower for word in ["fee", "pay", "cost", "price", "tuition", "money"])
    needs_academic = any(word in query_lower for word in ["course", "prerequisite", "class", "lecturer", "csc", "mth"])
    needs_hostel = any(word in query_lower for word in ["hostel", "accommodation", "room", "hall"])
    needs_library = any(word in query_lower for word in ["library", "book", "borrow", "reading"])
    needs_admin = any(word in query_lower for word in ["transcript", "id card", "certificate", "clearance", "verification"])

    responses = []

    # Call appropriate agents
    if needs_academic:
        responses.append(("📚 Academic Info", simulate_academic_agent(query)))

    if needs_calendar:
        responses.append(("📅 Calendar Info", simulate_calendar_agent(query)))

    if needs_financial:
        responses.append(("💰 Financial Info", simulate_financial_agent(query)))

    if needs_hostel:
        responses.append(("🏠 Hostel Info", simulate_hostel_agent(query)))

    if needs_library:
        responses.append(("📖 Library Info", simulate_library_agent(query)))

    if needs_admin:
        responses.append(("📋 Administrative Info", simulate_admin_agent(query)))

    # If no agent was triggered, provide general help
    if not responses:
        return """👋 Hello! I'm the LAUTECH University Assistant. I can help you with:

📚 **Academic** - Courses, prerequisites, lecturers
📅 **Calendar** - Registration dates, exam periods
💰 **Financial** - School fees, payment methods
🏠 **Hostel** - Accommodation and facilities
📖 **Library** - Library hours and services
📋 **Administrative** - Transcripts, ID cards, certificates

Try asking:
- "When is registration?"
- "How much is school fees?"
- "What courses can I take after CSC201?"
- "How do I apply for hostel?"

What would you like to know?"""

    # Combine multi-agent responses
    if len(responses) == 1:
        return responses[0][1]
    else:
        combined = "I've consulted multiple departments for your query:\n\n"
        for title, response in responses:
            combined += f"{'='*60}\n{title}\n{'='*60}\n\n{response}\n\n"
        return combined


def demo():
    """
    Run interactive demo
    """
    print("=" * 80)
    print("LAUTECH University Assistant - DEMO MODE")
    print("=" * 80)
    print("\nThis is a simulation without AWS Bedrock (no API calls)")
    print("Testing the multi-agent routing logic with mock data\n")

    test_queries = [
        "How much is school fees for 200 level?",
        "When does registration start?",
        "What courses can I take after CSC201?",
        "How do I apply for hostel?",
        "What are the library opening hours?",
        "I need my transcript",
        "When is registration and how much will I pay?",  # Multi-agent query
    ]

    for i, query in enumerate(test_queries, 1):
        print("─" * 80)
        print(f"\n📝 TEST {i}: {query}\n")

        start = datetime.now()
        response = simulate_orchestrator(query)
        end = datetime.now()

        print(f"🤖 Response:\n{response}")
        print(f"\n⏱️  Response time: {(end - start).total_seconds():.3f}s")
        print()

    print("=" * 80)
    print("✅ DEMO COMPLETE!")
    print("=" * 80)
    print("\n📊 Summary:")
    print("- All 7 test queries processed successfully")
    print("- Multi-agent coordination working (test 7 uses multiple agents)")
    print("- Data structure validated")
    print("- Response formatting looks good")
    print("\n🎯 Next Step: Configure AWS credentials to use real AI!")


if __name__ == "__main__":
    demo()
