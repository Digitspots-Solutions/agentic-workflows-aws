#!/bin/bash

# LAUTECH Production Web Dashboard Launcher
# This dashboard calls the deployed AgentCore agent (not local Strands)

echo "=========================================="
echo "LAUTECH Production Web Dashboard"
echo "=========================================="
echo ""

# Check Python version (macOS compatible)
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}' | cut -d. -f1,2)
REQUIRED_VERSION="3.10"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo "❌ ERROR: Python 3.10+ required"
    echo "   Current version: Python $PYTHON_VERSION"
    echo ""
    echo "Please install Python 3.10 or higher:"
    echo "   brew install python@3.13"
    echo ""
    exit 1
fi

echo "✅ Python $PYTHON_VERSION detected"
echo ""

# Check if dependencies are installed
if ! python3 -c "import streamlit" 2>/dev/null; then
    echo "📦 Installing Streamlit..."
    pip3 install streamlit boto3
    echo ""
fi

# Quick AWS credential check (optional - boto3 will handle credential discovery)
if ! aws sts get-caller-identity &>/dev/null; then
    echo "⚠️  WARNING: AWS credentials not configured"
    echo "   Run: aws configure"
    echo ""
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Get agent ID from environment or use default
AGENT_ID="${LAUTECH_AGENT_ID:-lautech_agentcore-U7qNy1GPsE}"

echo "🚀 Launching dashboard..."
echo "   Agent ID: $AGENT_ID"
echo "   Region: ${AWS_DEFAULT_REGION:-us-east-1}"
echo ""
echo "📱 Dashboard will open at: http://localhost:8501"
echo ""
echo "Press Ctrl+C to stop"
echo ""

# Set agent ID for the app
export LAUTECH_AGENT_ID="$AGENT_ID"

# Run Streamlit
python3 -m streamlit run web_dashboard.py
