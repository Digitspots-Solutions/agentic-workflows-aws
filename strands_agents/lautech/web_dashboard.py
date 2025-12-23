"""
LAUTECH University Assistant - Production Web Dashboard

This dashboard calls the deployed AgentCore agent (not local Strands).
Perfect for students and staff to use in production.

Features:
- Calls AWS AgentCore agent
- Beautiful modern UI
- Mobile responsive
- Session management
- Usage analytics
"""

import streamlit as st
import boto3
import json
from datetime import datetime
import os

# ============================================================================
# PAGE CONFIG
# ============================================================================

st.set_page_config(
    page_title="LAUTECH Assistant",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# CUSTOM CSS - LAUTECH BRANDING
# ============================================================================

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;600;700&family=Inter:wght@400;500;600&display=swap');

    :root {
        --lautech-green: #2D5016;
        --lautech-gold: #D4AF37;
        --lautech-dark: #1A1A1A;
        --accent-blue: #3B82F6;
    }

    * {
        font-family: 'Inter', sans-serif;
    }

    h1, h2, h3 {
        font-family: 'Space Grotesk', sans-serif;
    }

    .block-container {
        padding-top: 3rem;
        max-width: 1200px;
    }

    /* Header */
    .main-header {
        background: linear-gradient(135deg, var(--lautech-green) 0%, var(--lautech-dark) 100%);
        padding: 2rem;
        border-radius: 12px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }

    .header-title {
        font-size: 2rem;
        font-weight: 700;
        color: var(--lautech-gold);
        margin: 0;
    }

    .header-subtitle {
        color: #ffffff;
        opacity: 0.9;
        margin-top: 0.5rem;
    }

    /* Messages */
    .user-message {
        background: linear-gradient(135deg, #EBF8FF 0%, #E0E7FF 100%);
        border-left: 4px solid var(--accent-blue);
        padding: 1.25rem;
        border-radius: 8px;
        margin: 1rem 0;
    }

    .assistant-message {
        background: #FFFFFF;
        border-left: 4px solid var(--lautech-gold);
        padding: 1.25rem;
        border-radius: 8px;
        margin: 1rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }

    .message-label {
        font-weight: 600;
        font-size: 0.875rem;
        margin-bottom: 0.5rem;
        color: var(--lautech-dark);
    }

    .message-time {
        font-size: 0.75rem;
        opacity: 0.6;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: var(--lautech-dark);
    }

    [data-testid="stSidebar"] * {
        color: #ffffff !important;
    }

    /* Buttons */
    .stButton > button {
        background: transparent;
        border: 2px solid var(--lautech-gold);
        color: #ffffff;
        font-weight: 600;
        border-radius: 6px;
        padding: 0.75rem 1.5rem;
        transition: all 0.3s;
    }

    .stButton > button:hover {
        background: var(--lautech-gold);
        color: var(--lautech-dark);
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(212,175,55,0.3);
    }

    /* Status badge */
    .status-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 600;
        background: #10B981;
        color: white;
    }

    /* Quick actions */
    .quick-action {
        background: rgba(255,255,255,0.05);
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid rgba(255,255,255,0.1);
        margin-bottom: 0.75rem;
        cursor: pointer;
        transition: all 0.2s;
    }

    .quick-action:hover {
        background: rgba(255,255,255,0.1);
        border-color: var(--lautech-gold);
    }

    /* Info box */
    .info-box {
        background: linear-gradient(135deg, #FEF3C7 0%, #FDE68A 100%);
        border-left: 4px solid var(--lautech-gold);
        padding: 1.5rem;
        border-radius: 8px;
        margin: 1.5rem 0;
    }

    /* Metrics */
    [data-testid="stMetric"] {
        background: rgba(255,255,255,0.05);
        padding: 1rem;
        border-radius: 8px;
    }

    [data-testid="stMetricValue"] {
        color: var(--lautech-gold);
        font-size: 2rem;
        font-weight: 700;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# AGENTCORE CLIENT
# ============================================================================

def get_agentcore_client():
    """Initialize Bedrock AgentCore client"""
    return boto3.client('bedrock-agentcore', region_name='us-east-1')

def invoke_agent(prompt: str, agent_id: str, session_id: str = None):
    """
    Invoke the deployed AgentCore agent

    Args:
        prompt: User's question
        agent_id: AgentCore agent ID
        session_id: Optional session ID for context

    Returns:
        Agent's response text
    """
    try:
        client = get_agentcore_client()

        params = {
            'agentId': agent_id,
            'payload': {'prompt': prompt}
        }

        if session_id:
            params['sessionId'] = session_id

        response = client.invoke_agent(**params)

        # Extract text from response
        if 'output' in response:
            return response['output']
        elif 'message' in response:
            return response['message']
        else:
            return str(response)

    except Exception as e:
        return f"❌ Error: {str(e)}\n\nPlease check:\n- AWS credentials are configured\n- AgentCore agent is deployed\n- Agent ID is correct"

# ============================================================================
# SESSION STATE
# ============================================================================

if 'messages' not in st.session_state:
    st.session_state.messages = []

if 'query_count' not in st.session_state:
    st.session_state.query_count = 0

if 'session_id' not in st.session_state:
    st.session_state.session_id = f"web-{datetime.now().strftime('%Y%m%d%H%M%S')}"

if 'agent_id' not in st.session_state:
    # Default agent ID - update this with your deployed agent
    st.session_state.agent_id = os.getenv('LAUTECH_AGENT_ID', 'lautech_agentcore-U7qNy1GPsE')

# ============================================================================
# SIDEBAR
# ============================================================================

with st.sidebar:
    st.markdown("### 🎓 LAUTECH ASSISTANT")
    st.markdown('<div class="status-badge">● LIVE</div>', unsafe_allow_html=True)
    st.markdown("---")

    # Agent Configuration
    with st.expander("⚙️ Configuration"):
        agent_id = st.text_input(
            "AgentCore Agent ID",
            value=st.session_state.agent_id,
            help="Get this from: agentcore status"
        )
        if agent_id != st.session_state.agent_id:
            st.session_state.agent_id = agent_id
            st.success("Agent ID updated!")

    st.markdown("---")

    # Quick Actions
    st.markdown("#### 🚀 QUICK ACTIONS")

    quick_queries = {
        "📚 Browse Courses": "What Computer Science courses are available?",
        "💰 Check Fees": "How much is school fees for 200 level?",
        "📅 Registration": "When does registration start?",
        "🏠 Hostel Info": "Tell me about hostel accommodation",
        "📖 Library Hours": "What are the library opening hours?",
        "📋 Get Transcript": "How do I request my transcript?",
    }

    for label, query in quick_queries.items():
        if st.button(label, key=f"quick_{label}"):
            st.session_state.pending_query = query

    st.markdown("---")

    # Statistics
    st.markdown("#### 📊 STATISTICS")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Queries", st.session_state.query_count)
    with col2:
        st.metric("Session", "Active")

    st.markdown("---")

    # Clear Chat
    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.session_state.query_count = 0
        st.rerun()

    st.markdown("---")

    # About
    with st.expander("ℹ️ About"):
        st.markdown("""
        **LAUTECH Assistant v3.0**

        Production system powered by:
        - AWS Bedrock AgentCore
        - Claude AI (Haiku 3.5)
        - Multi-agent system
        - Database backend

        **Need Help?**
        Contact IT Support
        """)

# ============================================================================
# MAIN INTERFACE
# ============================================================================

# Header
st.markdown("""
<div class="main-header">
    <h1 class="header-title">LAUTECH University Assistant</h1>
    <p class="header-subtitle">Your AI-powered guide to university services</p>
</div>
""", unsafe_allow_html=True)

# Welcome message
if len(st.session_state.messages) == 0:
    st.markdown("""
    <div class="info-box">
        <strong>👋 Welcome to LAUTECH Assistant!</strong><br><br>
        I can help you with:<br>
        • 📚 Course information and prerequisites<br>
        • 💰 Tuition fees and payment details<br>
        • 📅 Registration dates and academic calendar<br>
        • 🏠 Hostel accommodation<br>
        • 📖 Library services<br>
        • 📋 Administrative procedures<br><br>
        <strong>💡 Try asking:</strong> "When is registration?" or use the quick action buttons!
    </div>
    """, unsafe_allow_html=True)

# Display messages
for message in st.session_state.messages:
    role = message["role"]
    content = message["content"]
    timestamp = message.get("timestamp", "")

    if role == "user":
        st.markdown(f"""
        <div class="user-message">
            <div class="message-label">You <span class="message-time">{timestamp}</span></div>
            {content}
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="assistant-message">
            <div class="message-label">LAUTECH Assistant <span class="message-time">{timestamp}</span></div>
            {content}
        </div>
        """, unsafe_allow_html=True)

# Handle pending query from sidebar
if 'pending_query' in st.session_state and st.session_state.pending_query:
    query = st.session_state.pending_query
    st.session_state.pending_query = None
    # Will be processed below

# Chat input
user_question = st.chat_input("💬 Ask me anything about LAUTECH...")

# Process query
query_to_process = None
if 'pending_query' in st.session_state and st.session_state.get('pending_query'):
    query_to_process = st.session_state.pending_query
    st.session_state.pending_query = None
elif user_question:
    query_to_process = user_question

if query_to_process:
    timestamp = datetime.now().strftime("%H:%M")

    # Add user message
    st.session_state.messages.append({
        "role": "user",
        "content": query_to_process,
        "timestamp": timestamp
    })

    # Show immediately
    st.markdown(f"""
    <div class="user-message">
        <div class="message-label">You <span class="message-time">{timestamp}</span></div>
        {query_to_process}
    </div>
    """, unsafe_allow_html=True)

    # Get AI response
    with st.spinner("🤔 Thinking..."):
        try:
            response = invoke_agent(
                prompt=query_to_process,
                agent_id=st.session_state.agent_id,
                session_id=st.session_state.session_id
            )

            response_timestamp = datetime.now().strftime("%H:%M")

            st.session_state.messages.append({
                "role": "assistant",
                "content": response,
                "timestamp": response_timestamp
            })

            st.session_state.query_count += 1
            st.rerun()

        except Exception as e:
            error_timestamp = datetime.now().strftime("%H:%M")
            error_message = f"""
            ❌ **Error**: {str(e)}

            **Troubleshooting:**
            1. Check if AgentCore agent is deployed: `agentcore status`
            2. Verify agent ID in sidebar settings
            3. Ensure AWS credentials are configured
            4. Check CloudWatch logs for details

            **Get agent ID:**
            ```bash
            cd strands_agents/lautech
            agentcore status
            ```
            """

            st.session_state.messages.append({
                "role": "assistant",
                "content": error_message,
                "timestamp": error_timestamp
            })

            st.rerun()

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 1rem;">
    🎓 LAUTECH University Assistant | Powered by AWS Bedrock AgentCore<br>
    <small>For official matters, please contact the appropriate department</small>
</div>
""", unsafe_allow_html=True)
