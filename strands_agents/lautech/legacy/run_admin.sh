#!/bin/bash

# LAUTECH Admin Panel Launcher
# Staff-only interface for managing university data

echo "=========================================="
echo "LAUTECH Admin Panel"
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

# Check if streamlit is installed
if ! python3 -c "import streamlit" 2>/dev/null; then
    echo "📦 Installing dependencies..."
    pip3 install streamlit pandas
    echo ""
fi

# Check if database exists
if [ ! -f "lautech_data.db" ]; then
    echo "⚠️  WARNING: Database not found!"
    echo ""
    echo "Please import data first:"
    echo "   python3 import_data.py --all"
    echo ""
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo "🔐 Admin Panel Access"
echo "   Default credentials: admin / lautech2024"
echo ""
echo "⚠️  IMPORTANT: This is for authorized staff only!"
echo ""
echo "🚀 Launching admin panel..."
echo "   URL: http://localhost:8502"
echo ""
echo "Press Ctrl+C to stop"
echo ""

# Run on different port than user dashboard
python3 -m streamlit run admin_panel.py --server.port 8502
