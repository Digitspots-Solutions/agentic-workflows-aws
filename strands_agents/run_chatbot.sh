#!/bin/bash

# LAUTECH University Assistant - Quick Start Script
# This script sets up and runs the chatbot web interface

set -e  # Exit on any error

echo "=========================================="
echo "LAUTECH University Assistant"
echo "Multi-Agent Chatbot Setup"
echo "=========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check Python installation
echo -e "${YELLOW}Checking Python installation...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 is not installed.${NC}"
    echo "Please install Python 3.11 or higher"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo -e "${GREEN}✅ Python ${PYTHON_VERSION} found${NC}"
echo ""

# Check pip installation
echo -e "${YELLOW}Checking pip installation...${NC}"
if ! command -v pip3 &> /dev/null; then
    echo -e "${RED}❌ pip3 is not installed.${NC}"
    echo "Installing pip..."
    curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
    python3 get-pip.py
    rm get-pip.py
fi
echo -e "${GREEN}✅ pip found${NC}"
echo ""

# Install/upgrade dependencies
echo -e "${YELLOW}Installing dependencies...${NC}"
echo "This may take a few minutes..."

pip3 install --upgrade pip > /dev/null 2>&1
pip3 install streamlit strands-agents boto3 --quiet

echo -e "${GREEN}✅ Dependencies installed${NC}"
echo ""

# Check AWS credentials
echo -e "${YELLOW}Checking AWS credentials...${NC}"

if [ -f ~/.aws/credentials ] || [ ! -z "$AWS_ACCESS_KEY_ID" ]; then
    echo -e "${GREEN}✅ AWS credentials found${NC}"
else
    echo -e "${RED}⚠️  AWS credentials not found${NC}"
    echo ""
    echo "Please configure AWS credentials using one of these methods:"
    echo ""
    echo "Option 1 - AWS CLI (recommended):"
    echo "  aws configure"
    echo ""
    echo "Option 2 - Environment variables:"
    echo "  export AWS_ACCESS_KEY_ID='your-key'"
    echo "  export AWS_SECRET_ACCESS_KEY='your-secret'"
    echo "  export AWS_DEFAULT_REGION='us-east-1'"
    echo ""
    echo "Option 3 - Create credentials file:"
    echo "  mkdir -p ~/.aws"
    echo "  cat > ~/.aws/credentials << EOF"
    echo "[default]"
    echo "aws_access_key_id = YOUR_KEY"
    echo "aws_secret_access_key = YOUR_SECRET"
    echo "region = us-east-1"
    echo "EOF"
    echo ""
    read -p "Press Enter after configuring credentials, or Ctrl+C to exit..."
fi

echo ""

# Check if chatbot file exists
if [ ! -f "lautech_chatbot_app.py" ]; then
    echo -e "${RED}❌ lautech_chatbot_app.py not found${NC}"
    echo "Please make sure you're in the strands_agents directory"
    exit 1
fi

# Start the application
echo "=========================================="
echo -e "${GREEN}🚀 Starting LAUTECH University Assistant${NC}"
echo "=========================================="
echo ""
echo "The chatbot will open in your browser automatically."
echo "If it doesn't, visit: http://localhost:8501"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""
echo "=========================================="
echo ""

# Run Streamlit
streamlit run lautech_chatbot_app.py
