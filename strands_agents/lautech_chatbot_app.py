"""
LAUTECH University Assistant - Streamlit Web Interface

A user-friendly chatbot interface for students and staff to interact with
the multi-agent university assistant system.

Students can ask questions about:
- Courses and academic programs
- Registration dates and deadlines
- Tuition fees and payments
- Hostel accommodation
- Library services
- Administrative procedures

No coding knowledge required - just type your question!
"""

import streamlit as st
from datetime import datetime
import sys
import os

# Add the current directory to Python path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the assistant (only import if available)
try:
    from lautech_assistant_enhanced import ask_question
    ASSISTANT_AVAILABLE = True
except ImportError as e:
    ASSISTANT_AVAILABLE = False
    import_error = str(e)

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="LAUTECH University Assistant",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# CUSTOM CSS STYLING
# ============================================================================

st.markdown("""
<style>
    /* Main header styling */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }

    /* Chat message styling */
    .user-message {
        background-color: #e3f2fd;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        border-left: 4px solid #2196f3;
    }

    .assistant-message {
        background-color: #f3e5f5;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        border-left: 4px solid #9c27b0;
    }

    /* Quick action buttons */
    .stButton > button {
        width: 100%;
        border-radius: 5px;
        padding: 0.5rem;
        font-weight: 500;
    }

    /* Info boxes */
    .info-box {
        background-color: #fff3cd;
        border-left: 4px solid #ffc107;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# SESSION STATE INITIALIZATION
# ============================================================================

if 'messages' not in st.session_state:
    st.session_state.messages = []

if 'query_count' not in st.session_state:
    st.session_state.query_count = 0

# ============================================================================
# SIDEBAR
# ============================================================================

with st.sidebar:
    st.markdown("### 🎓 LAUTECH Assistant")
    st.markdown("---")

    st.markdown("#### What can I help you with?")

    # Quick action buttons
    st.markdown("**📚 Academic Questions:**")
    if st.button("📖 Course Information"):
        st.session_state.quick_query = "What courses are available?"
    if st.button("📝 Prerequisites"):
        st.session_state.quick_query = "What are the prerequisites for CSC301?"

    st.markdown("**💰 Financial Questions:**")
    if st.button("💵 School Fees"):
        st.session_state.quick_query = "How much is school fees?"
    if st.button("💳 Payment Methods"):
        st.session_state.quick_query = "How can I pay my school fees?"

    st.markdown("**📅 Important Dates:**")
    if st.button("📆 Registration Dates"):
        st.session_state.quick_query = "When is registration?"
    if st.button("🗓️ Academic Calendar"):
        st.session_state.quick_query = "Show me the academic calendar"

    st.markdown("**🏠 Hostel & Services:**")
    if st.button("🏘️ Hostel Application"):
        st.session_state.quick_query = "How do I apply for hostel?"
    if st.button("📚 Library Services"):
        st.session_state.quick_query = "What are the library opening hours?"

    st.markdown("**📋 Administrative:**")
    if st.button("🆔 Student ID Card"):
        st.session_state.quick_query = "How do I get my student ID card?"
    if st.button("📜 Transcript Request"):
        st.session_state.quick_query = "How do I request my transcript?"

    st.markdown("---")

    # Statistics
    st.markdown("#### Session Statistics")
    st.metric("Questions Asked", st.session_state.query_count)

    st.markdown("---")

    # Clear chat button
    if st.button("🗑️ Clear Chat History"):
        st.session_state.messages = []
        st.session_state.query_count = 0
        st.rerun()

    st.markdown("---")

    # About section
    with st.expander("ℹ️ About"):
        st.markdown("""
        **LAUTECH University Assistant** is a multi-agent AI system that helps
        students and staff with university-related queries.

        **Powered by:**
        - AWS Bedrock (Claude AI)
        - Strands Agents Framework
        - 6 Specialist Agents

        **Need Help?**
        - Just type your question naturally
        - Use the quick action buttons
        - Ask about multiple topics in one query

        **Example Questions:**
        - "When is registration and how much is the fee?"
        - "What courses can I take after CSC201?"
        - "How do I apply for hostel?"
        """)

# ============================================================================
# MAIN INTERFACE
# ============================================================================

# Header
st.markdown("""
<div class="main-header">
    <h1>🎓 LAUTECH University Assistant</h1>
    <p>Your AI-powered guide to Ladoke Akintola University of Technology</p>
</div>
""", unsafe_allow_html=True)

# Check if assistant is available
if not ASSISTANT_AVAILABLE:
    st.error("⚠️ **Assistant Not Available**")
    st.markdown(f"""
    The university assistant could not be loaded. Please check:

    1. **AWS Credentials** are configured properly
    2. **Dependencies** are installed: `pip install strands-agents boto3`
    3. **Import Error:** `{import_error}`

    **To fix:**
    ```bash
    # Configure AWS credentials
    aws configure

    # Or set environment variables
    export AWS_ACCESS_KEY_ID="your-key"
    export AWS_SECRET_ACCESS_KEY="your-secret"
    export AWS_DEFAULT_REGION="us-east-1"
    ```
    """)
    st.stop()

# Welcome message (shown only on first load)
if len(st.session_state.messages) == 0:
    st.markdown("""
    <div class="info-box">
        👋 <strong>Welcome to LAUTECH University Assistant!</strong><br>
        I can help you with courses, registration, fees, hostel, library, and administrative services.
        <br><br>
        💡 <strong>Try asking:</strong><br>
        • "When does registration start?"<br>
        • "How much is school fees for 200 level?"<br>
        • "What courses can I take after CSC201?"<br>
        • "How do I apply for hostel accommodation?"<br>
    </div>
    """, unsafe_allow_html=True)

# Display chat messages
for message in st.session_state.messages:
    role = message["role"]
    content = message["content"]
    timestamp = message.get("timestamp", "")

    if role == "user":
        st.markdown(f"""
        <div class="user-message">
            <strong>👤 You</strong> <small>({timestamp})</small><br>
            {content}
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="assistant-message">
            <strong>🤖 LAUTECH Assistant</strong> <small>({timestamp})</small><br>
            {content}
        </div>
        """, unsafe_allow_html=True)

# Handle quick query from sidebar
if 'quick_query' in st.session_state and st.session_state.quick_query:
    query = st.session_state.quick_query
    st.session_state.quick_query = None  # Clear it

    # Process the query (will be handled below)
    st.session_state.pending_query = query
    st.rerun()

# Chat input
user_question = st.chat_input("💬 Ask me anything about LAUTECH...", key="chat_input")

# Process pending query or new input
query_to_process = None
if 'pending_query' in st.session_state and st.session_state.pending_query:
    query_to_process = st.session_state.pending_query
    st.session_state.pending_query = None
elif user_question:
    query_to_process = user_question

if query_to_process:
    # Get current timestamp
    timestamp = datetime.now().strftime("%I:%M %p")

    # Add user message to chat
    st.session_state.messages.append({
        "role": "user",
        "content": query_to_process,
        "timestamp": timestamp
    })

    # Show user message immediately
    st.markdown(f"""
    <div class="user-message">
        <strong>👤 You</strong> <small>({timestamp})</small><br>
        {query_to_process}
    </div>
    """, unsafe_allow_html=True)

    # Show loading spinner
    with st.spinner("🤔 Thinking..."):
        try:
            # Get response from the assistant
            response = ask_question(query_to_process)

            # Get timestamp for response
            response_timestamp = datetime.now().strftime("%I:%M %p")

            # Add assistant response to chat
            st.session_state.messages.append({
                "role": "assistant",
                "content": response,
                "timestamp": response_timestamp
            })

            # Increment query count
            st.session_state.query_count += 1

            # Rerun to display the response
            st.rerun()

        except Exception as e:
            error_timestamp = datetime.now().strftime("%I:%M %p")
            error_message = f"""
            ❌ **Error:** I encountered an issue processing your question.

            **Details:** {str(e)}

            **Please check:**
            - AWS credentials are configured
            - You have internet connection
            - Bedrock service is accessible

            Try asking your question again or use a quick action button.
            """

            st.session_state.messages.append({
                "role": "assistant",
                "content": error_message,
                "timestamp": error_timestamp
            })

            st.rerun()

# ============================================================================
# FOOTER
# ============================================================================

st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 1rem;">
    <small>
        🎓 LAUTECH University Assistant | Powered by AWS Bedrock & Strands Agents<br>
        💡 This is an AI assistant. For official matters, please contact the appropriate department.<br>
        📧 Questions or issues? Contact IT Support
    </small>
</div>
""", unsafe_allow_html=True)
