#!/bin/bash

# LAUTECH Production Web Dashboard Launcher
# This dashboard calls the deployed AgentCore agent (not local Strands)

echo "=========================================="
echo "LAUTECH Production Web Dashboard"
echo "=========================================="
echo ""

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | grep -oP '(?<=Python )\d+\.\d+')
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

# Check if streamlit is installed
if ! python3 -c "import streamlit" 2>/dev/null; then
    echo "📦 Installing Streamlit..."
    pip3 install streamlit boto3
    echo ""
fi

# Check AWS credentials
if [ -z "$AWS_ACCESS_KEY_ID" ] || [ -z "$AWS_SECRET_ACCESS_KEY" ]; then
    echo "⚠️  WARNING: AWS credentials not set"
    echo ""
    echo "The dashboard needs AWS credentials to call the AgentCore agent."
    echo "Please set them:"
    echo ""
    echo "   export AWS_ACCESS_KEY_ID=\"your-key\""
    echo "   export AWS_SECRET_ACCESS_KEY=\"your-secret\""
    echo "   export AWS_DEFAULT_REGION=\"us-east-1\""
    echo ""
    echo "Or configure using: aws configure"
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
