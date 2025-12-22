#!/bin/bash

# LAUTECH Assistant - Demo Mode Launcher
# Works with ANY Python 3.x version (no dependencies needed!)

echo "=========================================="
echo "LAUTECH University Assistant - DEMO MODE"
echo "=========================================="
echo ""
echo "This demo works with ANY Python 3.x version"
echo "No AWS credentials or dependencies needed!"
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed"
    exit 1
fi

PYTHON_VERSION=$(python3 --version)
echo "✅ $PYTHON_VERSION found"
echo ""
echo "Starting demo..."
echo ""

# Run the demo
python3 test_assistant_demo.py
