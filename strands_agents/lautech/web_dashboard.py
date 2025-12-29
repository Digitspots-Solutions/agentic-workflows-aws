"""
LAUTECH Student Assistant - Web Dashboard

A beautiful, Nigerian-inspired interface for the LAUTECH AI assistant.
Calls the deployed AgentCore agent via boto3.
"""

import streamlit as st
import boto3
import json
import os
from datetime import datetime
import uuid

# ============================================================================
# PAGE CONFIG
# ============================================================================

st.set_page_config(
    page_title="LAUTECH Assistant",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============================================================================
# CUSTOM CSS - NIGERIAN-INSPIRED DESIGN
# ============================================================================

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Crimson+Pro:wght@400;600;700&family=JetBrains+Mono:wght@400;500&family=DM+Sans:wght@400;500;700&display=swap');

    :root {
        --earth-dark: #2C1810;
        --earth-medium: #5C3D2E;
        --terracotta: #D35400;
        --ochre: #E67E22;
        --forest: #1E4620;
        --sage: #52796F;
        --coral: #FF6B6B;
        --cream: #FFF8E7;
        --sand: #F4E8D0;
    }

    /* Reset Streamlit defaults */
    .stApp {
        background: linear-gradient(135deg,
            var(--cream) 0%,
            var(--sand) 50%,
            #FFE5CC 100%
        );
        background-attachment: fixed;
    }

    /* African geometric pattern overlay */
    .stApp::before {
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background-image:
            repeating-linear-gradient(45deg, transparent, transparent 35px, rgba(92, 61, 46, 0.02) 35px, rgba(92, 61, 46, 0.02) 70px),
            repeating-linear-gradient(-45deg, transparent, transparent 35px, rgba(30, 70, 32, 0.02) 35px, rgba(30, 70, 32, 0.02) 70px);
        pointer-events: none;
        z-index: 0;
    }

    /* Main content */
    .block-container {
        max-width: 1200px;
        padding: 3rem 2rem 6rem;
        position: relative;
        z-index: 1;
    }

    /* Hide Streamlit branding */
    #MainMenu, footer, header {visibility: hidden;}

    /* Typography */
    * {
        font-family: 'DM Sans', sans-serif;
    }

    h1, h2, h3 {
        font-family: 'Crimson Pro', serif;
        color: var(--earth-dark);
        font-weight: 700;
        letter-spacing: -0.02em;
    }

    /* Hero Header */
    .hero-header {
        text-align: center;
        padding: 3rem 2rem;
        background: linear-gradient(135deg, var(--forest) 0%, var(--sage) 100%);
        border-radius: 24px;
        box-shadow:
            0 20px 60px rgba(30, 70, 32, 0.3),
            inset 0 1px 0 rgba(255, 255, 255, 0.1);
        margin-bottom: 3rem;
        position: relative;
        overflow: hidden;
        animation: slideDown 0.8s ease-out;
    }

    .hero-header::before {
        content: '';
        position: absolute;
        top: -50%;
        right: -20%;
        width: 400px;
        height: 400px;
        background: radial-gradient(circle, rgba(255, 255, 255, 0.1) 0%, transparent 70%);
        animation: float 6s ease-in-out infinite;
    }

    .hero-title {
        font-size: 3.5rem;
        font-weight: 700;
        color: var(--cream);
        margin: 0;
        text-shadow: 0 2px 20px rgba(0, 0, 0, 0.2);
        animation: fadeIn 1s ease-out 0.2s both;
    }

    .hero-subtitle {
        font-size: 1.25rem;
        color: var(--sand);
        margin-top: 1rem;
        font-weight: 400;
        animation: fadeIn 1s ease-out 0.4s both;
    }

    /* Quick Actions */
    .quick-actions {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 1.5rem;
        margin: 2rem 0 3rem;
        animation: fadeIn 1s ease-out 0.6s both;
    }

    .action-card {
        background: white;
        padding: 1.5rem;
        border-radius: 16px;
        border: 2px solid transparent;
        cursor: pointer;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
        position: relative;
        overflow: hidden;
    }

    .action-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, var(--terracotta), var(--coral));
        transform: scaleX(0);
        transition: transform 0.3s ease;
    }

    .action-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 24px rgba(211, 84, 0, 0.15);
        border-color: var(--terracotta);
    }

    .action-card:hover::before {
        transform: scaleX(1);
    }

    .action-icon {
        font-size: 2rem;
        margin-bottom: 0.75rem;
    }

    .action-title {
        font-family: 'Crimson Pro', serif;
        font-size: 1.25rem;
        font-weight: 600;
        color: var(--earth-dark);
        margin-bottom: 0.5rem;
    }

    .action-desc {
        font-size: 0.9rem;
        color: var(--earth-medium);
        line-height: 1.5;
    }

    /* Chat Interface */
    .chat-container {
        background: white;
        border-radius: 20px;
        padding: 2rem;
        box-shadow:
            0 10px 40px rgba(0, 0, 0, 0.08),
            inset 0 1px 0 rgba(255, 255, 255, 0.5);
        margin: 2rem 0;
        animation: fadeIn 1s ease-out 0.8s both;
    }

    /* Messages */
    .message {
        margin: 1.5rem 0;
        display: flex;
        gap: 1rem;
        animation: messageSlide 0.4s ease-out;
    }

    .message.user {
        flex-direction: row-reverse;
    }

    .message-avatar {
        width: 40px;
        height: 40px;
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.25rem;
        flex-shrink: 0;
    }

    .message.user .message-avatar {
        background: linear-gradient(135deg, var(--terracotta), var(--coral));
    }

    .message.assistant .message-avatar {
        background: linear-gradient(135deg, var(--forest), var(--sage));
    }

    .message-content {
        background: var(--cream);
        padding: 1.25rem 1.5rem;
        border-radius: 16px;
        max-width: 70%;
        font-size: 1rem;
        line-height: 1.7;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
    }

    .message.user .message-content {
        background: linear-gradient(135deg, var(--terracotta), var(--ochre));
        color: white;
        border-bottom-right-radius: 4px;
    }

    .message.assistant .message-content {
        background: white;
        color: var(--earth-dark);
        border: 1px solid rgba(30, 70, 32, 0.1);
        border-bottom-left-radius: 4px;
    }

    /* Input */
    .stTextInput input {
        background: white;
        border: 2px solid var(--sage);
        border-radius: 16px;
        padding: 1rem 1.5rem;
        font-size: 1rem;
        font-family: 'DM Sans', sans-serif;
        transition: all 0.3s ease;
    }

    .stTextInput input:focus {
        border-color: var(--terracotta);
        box-shadow: 0 0 0 3px rgba(211, 84, 0, 0.1);
    }

    /* Buttons */
    .stButton button {
        background: linear-gradient(135deg, var(--terracotta), var(--ochre));
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.875rem 2rem;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 4px 12px rgba(211, 84, 0, 0.3);
        font-family: 'DM Sans', sans-serif;
    }

    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(211, 84, 0, 0.4);
    }

    /* Stats Bar */
    .stats-bar {
        display: flex;
        justify-content: center;
        gap: 3rem;
        padding: 2rem;
        background: white;
        border-radius: 16px;
        margin: 2rem 0;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
        animation: fadeIn 1s ease-out 1s both;
    }

    .stat {
        text-align: center;
    }

    .stat-value {
        font-family: 'JetBrains Mono', monospace;
        font-size: 2rem;
        font-weight: 600;
        color: var(--terracotta);
        display: block;
    }

    .stat-label {
        font-size: 0.875rem;
        color: var(--earth-medium);
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-top: 0.5rem;
    }

    /* Animations */
    @keyframes slideDown {
        from {
            opacity: 0;
            transform: translateY(-30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    @keyframes fadeIn {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    @keyframes messageSlide {
        from {
            opacity: 0;
            transform: translateX(-20px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }

    @keyframes float {
        0%, 100% { transform: translate(0, 0) rotate(0deg); }
        50% { transform: translate(20px, 20px) rotate(5deg); }
    }

    /* Responsive */
    @media (max-width: 768px) {
        .hero-title {
            font-size: 2.5rem;
        }

        .quick-actions {
            grid-template-columns: 1fr;
        }

        .message-content {
            max-width: 85%;
        }

        .stats-bar {
            flex-direction: column;
            gap: 1.5rem;
        }
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# AGENT INVOCATION
# ============================================================================

AGENT_ID = os.getenv('LAUTECH_AGENT_ID', 'lautech_agentcore-U7qNy1GPsE')
AWS_REGION = os.getenv('AWS_DEFAULT_REGION', 'us-east-1')

def invoke_agent(prompt: str, session_id: str = None):
    """Invoke the deployed AgentCore agent"""
    try:
        client = boto3.client('bedrock-agentcore', region_name=AWS_REGION)

        params = {
            'agentId': AGENT_ID,
            'payload': {'prompt': prompt}
        }

        if session_id:
            params['sessionId'] = session_id

        response = client.invoke_agent(**params)

        if 'output' in response:
            return response['output']
        elif 'message' in response:
            return response['message']
        else:
            return str(response)

    except Exception as e:
        return f"⚠️ Error: {str(e)}\n\nPlease check your AWS credentials and agent deployment."

# ============================================================================
# SESSION STATE
# ============================================================================

if 'session_id' not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

if 'messages' not in st.session_state:
    st.session_state.messages = []

if 'query_count' not in st.session_state:
    st.session_state.query_count = 0

# ============================================================================
# HEADER
# ============================================================================

st.markdown("""
<div class="hero-header">
    <h1 class="hero-title">LAUTECH Assistant</h1>
    <p class="hero-subtitle">Your AI-powered guide to Ladoke Akintola University of Technology</p>
</div>
""", unsafe_allow_html=True)

# ============================================================================
# QUICK ACTIONS
# ============================================================================

quick_actions = [
    {
        "icon": "📚",
        "title": "Courses",
        "desc": "Browse available courses and prerequisites",
        "query": "What Computer Science courses are available?"
    },
    {
        "icon": "💰",
        "title": "Fees",
        "desc": "Check school fees and payment info",
        "query": "How much is school fees for 200 level?"
    },
    {
        "icon": "📅",
        "title": "Calendar",
        "desc": "View registration dates and deadlines",
        "query": "When is registration for this semester?"
    },
    {
        "icon": "🏠",
        "title": "Hostels",
        "desc": "Explore accommodation options",
        "query": "What hostels are available and how do I apply?"
    }
]

cols = st.columns(len(quick_actions))
for col, action in zip(cols, quick_actions):
    with col:
        if st.button(
            f"{action['icon']}\n\n**{action['title']}**\n\n{action['desc']}",
            key=f"action_{action['title']}",
            use_container_width=True
        ):
            st.session_state.messages.append({
                "role": "user",
                "content": action['query']
            })

            response = invoke_agent(action['query'], st.session_state.session_id)

            st.session_state.messages.append({
                "role": "assistant",
                "content": response
            })

            st.session_state.query_count += 1
            st.rerun()

# ============================================================================
# CHAT INTERFACE
# ============================================================================

st.markdown('<div class="chat-container">', unsafe_allow_html=True)

# Display messages
for msg in st.session_state.messages:
    avatar = "👤" if msg["role"] == "user" else "🎓"
    msg_class = "user" if msg["role"] == "user" else "assistant"

    st.markdown(f"""
    <div class="message {msg_class}">
        <div class="message-avatar">{avatar}</div>
        <div class="message-content">{msg["content"]}</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# Input
user_input = st.text_input(
    "Ask me anything about LAUTECH...",
    key="user_input",
    placeholder="e.g., When is registration? What courses can I take? How much are fees?",
    label_visibility="collapsed"
)

col1, col2, col3 = st.columns([2, 1, 1])

with col1:
    if st.button("Send", type="primary", use_container_width=True):
        if user_input:
            st.session_state.messages.append({
                "role": "user",
                "content": user_input
            })

            response = invoke_agent(user_input, st.session_state.session_id)

            st.session_state.messages.append({
                "role": "assistant",
                "content": response
            })

            st.session_state.query_count += 1
            st.rerun()

with col2:
    if st.button("Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.session_id = str(uuid.uuid4())
        st.rerun()

# ============================================================================
# STATS
# ============================================================================

st.markdown(f"""
<div class="stats-bar">
    <div class="stat">
        <span class="stat-value">{st.session_state.query_count}</span>
        <span class="stat-label">Queries</span>
    </div>
    <div class="stat">
        <span class="stat-value">{len(st.session_state.messages) // 2}</span>
        <span class="stat-label">Conversations</span>
    </div>
    <div class="stat">
        <span class="stat-value">24/7</span>
        <span class="stat-label">Available</span>
    </div>
</div>
""", unsafe_allow_html=True)

# Footer
st.markdown("""
<div style="text-align: center; padding: 2rem; color: var(--earth-medium); font-size: 0.875rem;">
    <p>Powered by AWS Bedrock AgentCore • LAUTECH © 2024</p>
</div>
""", unsafe_allow_html=True)
