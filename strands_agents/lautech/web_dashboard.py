"""
LAUTECH Student Assistant - Web Dashboard

A clean, professional interface for the LAUTECH AI assistant.
Calls the deployed AgentCore agent via CLI.
"""

import streamlit as st
import json
import os
import subprocess
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
# CUSTOM CSS - CLEAN, PROFESSIONAL DESIGN
# ============================================================================

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    /* Color Palette */
    :root {
        --bg-primary: #ffffff;
        --bg-secondary: #f8f9fa;
        --bg-tertiary: #f1f3f5;

        --text-primary: #1a1a1a;
        --text-secondary: #6b7280;
        --text-tertiary: #9ca3af;

        --border-light: #e5e7eb;
        --border-medium: #d1d5db;

        --accent-primary: #4f46e5;
        --accent-hover: #4338ca;
        --accent-light: #eef2ff;

        --success: #10b981;
        --error: #ef4444;

        --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.05);
        --shadow-md: 0 4px 6px rgba(0, 0, 0, 0.07);
        --shadow-lg: 0 10px 15px rgba(0, 0, 0, 0.1);
    }

    /* Reset and Base Styles */
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    }

    .stApp {
        background: var(--bg-secondary);
    }

    .block-container {
        max-width: 1100px;
        padding: 2rem 1.5rem 3rem;
    }

    /* Hide Streamlit Branding */
    #MainMenu, footer, header {
        visibility: hidden;
    }

    /* Header */
    .header {
        background: var(--bg-primary);
        border: 1px solid var(--border-light);
        border-radius: 12px;
        padding: 2rem;
        margin-bottom: 1.5rem;
        box-shadow: var(--shadow-sm);
    }

    .header h1 {
        font-size: 1.875rem;
        font-weight: 700;
        color: var(--text-primary);
        margin: 0 0 0.5rem 0;
        letter-spacing: -0.025em;
    }

    .header p {
        font-size: 1rem;
        color: var(--text-secondary);
        margin: 0;
    }

    /* Quick Actions */
    .quick-actions {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
        gap: 1rem;
        margin-bottom: 1.5rem;
    }

    .stButton > button {
        width: 100%;
        background: var(--bg-primary);
        border: 1px solid var(--border-light);
        border-radius: 8px;
        padding: 1rem;
        color: var(--text-primary);
        font-weight: 500;
        font-size: 0.875rem;
        transition: all 0.2s ease;
        box-shadow: var(--shadow-sm);
        height: auto;
        white-space: normal;
        text-align: left;
    }

    .stButton > button:hover {
        border-color: var(--accent-primary);
        background: var(--accent-light);
        box-shadow: var(--shadow-md);
        transform: translateY(-1px);
    }

    .stButton > button:active {
        transform: translateY(0);
    }

    .stButton > button p {
        margin: 0;
        line-height: 1.5;
    }

    /* Chat Container */
    .chat-container {
        background: var(--bg-primary);
        border: 1px solid var(--border-light);
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        max-height: 600px;
        overflow-y: auto;
        box-shadow: var(--shadow-sm);
    }

    /* Chat Messages using Streamlit Native */
    .stChatMessage {
        padding: 1rem;
        margin-bottom: 1rem;
        border-radius: 8px;
    }

    .stChatMessage[data-testid="user-message"] {
        background: var(--accent-light);
        border-left: 3px solid var(--accent-primary);
    }

    .stChatMessage[data-testid="assistant-message"] {
        background: var(--bg-secondary);
        border-left: 3px solid var(--text-tertiary);
    }

    /* Force visible text in chat messages */
    .stChatMessage p,
    .stChatMessage div,
    .stChatMessage span {
        color: var(--text-primary) !important;
    }

    /* Chat Input */
    .stChatInputContainer {
        border-top: 1px solid var(--border-light);
        padding-top: 1rem;
        background: var(--bg-primary);
    }

    .stChatInput > div {
        border: 2px solid var(--border-medium);
        border-radius: 8px;
        transition: all 0.2s ease;
    }

    .stChatInput > div:focus-within {
        border-color: var(--accent-primary);
        box-shadow: 0 0 0 3px var(--accent-light);
    }

    /* Text Input (fallback) */
    .stTextInput input {
        border: 2px solid var(--border-medium);
        border-radius: 8px;
        padding: 0.75rem 1rem;
        font-size: 0.9375rem;
        transition: all 0.2s ease;
        background: var(--bg-primary);
        color: var(--text-primary);
    }

    .stTextInput input:focus {
        border-color: var(--accent-primary);
        box-shadow: 0 0 0 3px var(--accent-light);
        outline: none;
    }

    .stTextInput input::placeholder {
        color: var(--text-tertiary);
    }

    /* Primary Button */
    button[kind="primary"] {
        background: var(--accent-primary) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.625rem 1.5rem !important;
        font-weight: 600 !important;
        transition: all 0.2s ease !important;
        box-shadow: var(--shadow-sm) !important;
    }

    button[kind="primary"]:hover {
        background: var(--accent-hover) !important;
        box-shadow: var(--shadow-md) !important;
        transform: translateY(-1px);
    }

    button[kind="primary"]:active {
        transform: translateY(0);
    }

    /* Secondary Button */
    button[kind="secondary"] {
        background: var(--bg-primary) !important;
        color: var(--text-secondary) !important;
        border: 1px solid var(--border-medium) !important;
        border-radius: 8px !important;
        padding: 0.625rem 1.5rem !important;
        font-weight: 500 !important;
        transition: all 0.2s ease !important;
    }

    button[kind="secondary"]:hover {
        border-color: var(--border-medium) !important;
        background: var(--bg-tertiary) !important;
    }

    /* Stats */
    .stats-container {
        display: flex;
        gap: 1rem;
        margin-bottom: 1.5rem;
    }

    .stat-card {
        flex: 1;
        background: var(--bg-primary);
        border: 1px solid var(--border-light);
        border-radius: 8px;
        padding: 1.25rem;
        box-shadow: var(--shadow-sm);
    }

    .stat-value {
        font-size: 1.875rem;
        font-weight: 700;
        color: var(--text-primary);
        line-height: 1;
        margin-bottom: 0.5rem;
    }

    .stat-label {
        font-size: 0.875rem;
        color: var(--text-secondary);
        font-weight: 500;
    }

    /* Empty State */
    .empty-state {
        text-align: center;
        padding: 2rem 1.5rem;
        color: var(--text-tertiary);
    }

    .empty-state-icon {
        font-size: 2.5rem;
        margin-bottom: 0.75rem;
        opacity: 0.5;
    }

    .empty-state-text {
        font-size: 0.9375rem;
        color: var(--text-secondary);
    }

    /* Typing Indicator */
    .typing-indicator {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        padding: 1rem;
        background: var(--bg-secondary);
        border-left: 3px solid var(--text-tertiary);
        border-radius: 8px;
        margin-bottom: 1rem;
    }

    .typing-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: var(--text-tertiary);
        animation: typing 1.4s infinite;
    }

    .typing-dot:nth-child(2) {
        animation-delay: 0.2s;
    }

    .typing-dot:nth-child(3) {
        animation-delay: 0.4s;
    }

    @keyframes typing {
        0%, 60%, 100% {
            opacity: 0.3;
            transform: scale(0.8);
        }
        30% {
            opacity: 1;
            transform: scale(1);
        }
    }

    /* Footer */
    .footer {
        text-align: center;
        padding: 1.5rem;
        color: var(--text-tertiary);
        font-size: 0.875rem;
    }

    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }

    ::-webkit-scrollbar-track {
        background: var(--bg-tertiary);
        border-radius: 4px;
    }

    ::-webkit-scrollbar-thumb {
        background: var(--border-medium);
        border-radius: 4px;
    }

    ::-webkit-scrollbar-thumb:hover {
        background: var(--text-tertiary);
    }

    /* Responsive */
    @media (max-width: 768px) {
        .block-container {
            padding: 1rem;
        }

        .header h1 {
            font-size: 1.5rem;
        }

        .quick-actions {
            grid-template-columns: 1fr;
        }

        .stats-container {
            flex-direction: column;
        }
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# AGENT INVOCATION
# ============================================================================

AGENT_ID = os.getenv('LAUTECH_AGENT_ID', 'lautech_agentcore-U7qNy1GPsE')

def invoke_agent(prompt: str, session_id: str = None):
    """Invoke the deployed AgentCore agent via CLI"""
    try:
        payload = json.dumps({"prompt": prompt})
        cmd = ['agentcore', 'invoke', payload]

        if session_id:
            cmd.extend(['--session-id', session_id])

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=90
        )

        if result.returncode != 0:
            return f"⚠️ Agent error: {result.stderr}"

        output = result.stdout.strip()

        # Extract response after "Response:" line
        if "Response:" in output:
            return output.split("Response:", 1)[1].strip()

        # Fallback: try JSON parsing
        try:
            data = json.loads(output)
            if isinstance(data, dict):
                return data.get('output') or data.get('response') or data.get('message') or str(data)
            return str(data)
        except json.JSONDecodeError:
            # Remove box characters
            for char in ['╭', '╮', '╰', '╯', '│', '─']:
                output = output.replace(char, '')
            return output.strip()

    except subprocess.TimeoutExpired:
        return "⚠️ Request timeout - please try again with a simpler query."
    except FileNotFoundError:
        return "⚠️ AgentCore CLI not found. Please ensure it's installed and in your PATH."
    except Exception as e:
        return f"⚠️ Error: {str(e)}"

# ============================================================================
# SESSION STATE
# ============================================================================

if 'session_id' not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

if 'messages' not in st.session_state:
    st.session_state.messages = []

if 'query_count' not in st.session_state:
    st.session_state.query_count = 0

if 'is_typing' not in st.session_state:
    st.session_state.is_typing = False

if 'pending_query' not in st.session_state:
    st.session_state.pending_query = None

# ============================================================================
# HEADER
# ============================================================================

st.markdown("""
<div class="header">
    <h1>🎓 LAUTECH Assistant</h1>
    <p>Your AI-powered guide to Ladoke Akintola University of Technology</p>
</div>
""", unsafe_allow_html=True)

# ============================================================================
# QUICK ACTIONS
# ============================================================================

st.markdown('<div class="quick-actions">', unsafe_allow_html=True)

quick_actions = [
    {
        "icon": "📚",
        "title": "Browse Courses",
        "query": "What courses are available? Please show me courses from different departments."
    },
    {
        "icon": "💰",
        "title": "School Fees",
        "query": "Tell me about school fees and payment information."
    },
    {
        "icon": "📅",
        "title": "Academic Calendar",
        "query": "What are the important dates this semester?"
    },
    {
        "icon": "🏠",
        "title": "Accommodation",
        "query": "Tell me about hostels and accommodation options."
    }
]

cols = st.columns(len(quick_actions))
for col, action in zip(cols, quick_actions):
    with col:
        if st.button(f"{action['icon']} {action['title']}", key=f"qa_{action['title']}"):
            st.session_state.messages.append({
                "role": "user",
                "content": action['query']
            })
            st.session_state.pending_query = action['query']
            st.session_state.is_typing = True
            st.rerun()

st.markdown('</div>', unsafe_allow_html=True)

# ============================================================================
# STATS
# ============================================================================

st.markdown(f"""
<div class="stats-container">
    <div class="stat-card">
        <div class="stat-value">{st.session_state.query_count}</div>
        <div class="stat-label">Queries Answered</div>
    </div>
    <div class="stat-card">
        <div class="stat-value">{len(st.session_state.messages) // 2}</div>
        <div class="stat-label">Conversations</div>
    </div>
    <div class="stat-card">
        <div class="stat-value">24/7</div>
        <div class="stat-label">Available</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ============================================================================
# CHAT INTERFACE
# ============================================================================

# Only show chat container when there are messages or typing
if len(st.session_state.messages) > 0 or st.session_state.is_typing:
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)

    # Display all messages
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"], avatar="👤" if msg["role"] == "user" else "🎓"):
            st.markdown(msg["content"])

    # Show typing indicator
    if st.session_state.is_typing:
        st.markdown("""
        <div class="typing-indicator">
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

# ============================================================================
# CHAT INPUT
# ============================================================================

# Use chat_input for automatic enter key handling and text clearing
user_input = st.chat_input(
    "Ask me anything about LAUTECH...",
    key="chat_input"
)

if user_input:
    # Add user message
    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })

    # Set pending query
    st.session_state.pending_query = user_input
    st.session_state.is_typing = True
    st.rerun()

# Clear chat button
col1, col2, col3 = st.columns([1, 1, 3])
with col1:
    if st.button("🗑️ Clear Chat", key="clear", use_container_width=True):
        st.session_state.messages = []
        st.session_state.session_id = str(uuid.uuid4())
        st.session_state.query_count = 0
        st.rerun()

# ============================================================================
# FOOTER
# ============================================================================

st.markdown("""
<div class="footer">
    Powered by AWS Bedrock AgentCore • LAUTECH © 2024
</div>
""", unsafe_allow_html=True)

# ============================================================================
# AGENT INVOCATION - RUNS AT END AFTER UI IS RENDERED
# ============================================================================

if st.session_state.is_typing and st.session_state.pending_query:
    # Get response from agent
    response = invoke_agent(
        st.session_state.pending_query,
        st.session_state.session_id
    )

    # Add response to messages
    st.session_state.messages.append({
        "role": "assistant",
        "content": response
    })

    # Update counter
    st.session_state.query_count += 1

    # Reset typing state
    st.session_state.is_typing = False
    st.session_state.pending_query = None

    # Rerun to show response
    st.rerun()
