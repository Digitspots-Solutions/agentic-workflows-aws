# 🧪 LAUTECH Assistant - Complete Testing Guide

**For users on macOS with Python 3.9** (and everyone else!)

---

## ⚠️ Python Version Issue

**Problem:** Strands-agents requires Python 3.10+
**Your Python:** 3.9 (based on your error)
**Solution:** Two options below ⬇️

---

## 🎯 Quick Testing (Works on Python 3.9!)

### Option 1: Demo Mode (Recommended - No Dependencies!)

```bash
# Navigate to the folder
cd strands_agents

# Run demo mode (works with ANY Python 3.x)
python3 test_assistant_demo.py

# Or use the launcher script
./run_demo.sh
```

**What you'll see:**
- All 7 agents tested
- Multi-agent coordination demo
- Instant responses (no AI, rule-based)
- Perfect for showcasing and validation

**No installation, no AWS, works with Python 3.9!** ✅

---

## 🔧 Option 2: Upgrade Python (For Real AI)

### On macOS (Homebrew method):

```bash
# Install Homebrew (if not installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python 3.11
brew install python@3.11

# Verify
python3.11 --version
# Should show: Python 3.11.x

# Use Python 3.11 for the chatbot
python3.11 -m pip install -r requirements_lautech.txt
python3.11 lautech_assistant_enhanced.py
```

### Alternative: Use pyenv

```bash
# Install pyenv
brew install pyenv

# Add to your shell profile (~/.zshrc or ~/.bash_profile)
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.zshrc
echo 'export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.zshrc
echo 'eval "$(pyenv init -)"' >> ~/.zshrc

# Restart terminal or
source ~/.zshrc

# Install Python 3.11
pyenv install 3.11.6

# Set as global default
pyenv global 3.11.6

# Verify
python --version
# Should show: Python 3.11.6
```

### Alternative: Download from python.org

1. Visit https://www.python.org/downloads/
2. Download Python 3.11+ installer for macOS
3. Run installer
4. Verify: `python3.11 --version`

---

## 📊 Testing Options Comparison

| Option | Python Version | Dependencies | AWS Needed | Speed | AI Quality |
|--------|---------------|--------------|------------|-------|------------|
| **Demo Mode** | Any 3.x (3.9 works!) | None | No | Instant | Rule-based |
| **Real AI** | 3.10+ required | strands-agents, boto3 | Yes | 2-5s | Claude AI |

---

## 🚀 Quick Test Commands

### Test 1: Demo Mode (Python 3.9 compatible)
```bash
cd strands_agents
python3 test_assistant_demo.py
```

**Expected output:**
```
================================================================================
LAUTECH University Assistant - DEMO MODE
================================================================================

Testing 7 queries...
✅ All agents working
✅ Multi-agent coordination working
```

### Test 2: Check Python Version
```bash
python3 --version
# You have: 3.9.x
# Need for real AI: 3.10+
```

### Test 3: Real AI (After Python 3.10+ upgrade)
```bash
# Install dependencies
pip3 install -r requirements_lautech.txt

# Set AWS credentials
export AWS_ACCESS_KEY_ID="your-key"
export AWS_SECRET_ACCESS_KEY="your-secret"
export AWS_DEFAULT_REGION="us-east-1"

# Run with real AI
python3 lautech_assistant_enhanced.py

# Or web interface
streamlit run lautech_chatbot_app.py
```

---

## 🐛 Troubleshooting

### Error: "No matching distribution found for strands-agents"

**Cause:** Python 3.9 (need 3.10+)

**Fix:**
```bash
# Quick solution: Use demo mode
python3 test_assistant_demo.py

# Long-term solution: Upgrade Python to 3.10+
brew install python@3.11
```

### Error: "command not found: python3"

**Fix:**
```bash
# Install Python
brew install python@3.11
```

### Demo mode shows "ModuleNotFoundError"

**Fix:**
```bash
# Demo mode has ZERO dependencies
# Should work with pure Python 3.x
# If failing, check Python installation:
python3 --version
```

---

## 📝 What Each File Does

| File | Purpose | Python Required | Dependencies |
|------|---------|----------------|--------------|
| `test_assistant_demo.py` | Demo mode | Any 3.x | None |
| `lautech_assistant_enhanced.py` | Real AI | 3.10+ | strands-agents, boto3 |
| `lautech_chatbot_app.py` | Web UI | 3.10+ | streamlit, strands-agents |
| `run_demo.sh` | Demo launcher | Any 3.x | None |
| `run_chatbot.sh` | Web app launcher | 3.10+ | All dependencies |

---

## ✅ Recommended Testing Flow

### For Python 3.9 Users (Like You):

```bash
# Step 1: Test demo mode (works now!)
cd strands_agents
python3 test_assistant_demo.py
# ✅ See all 7 agents working

# Step 2: Decide on Python upgrade
# Option A: Keep 3.9, use demo for showcasing
# Option B: Upgrade to 3.10+, use real AI

# Step 3: If upgrading
brew install python@3.11
python3.11 -m pip install -r requirements_lautech.txt

# Step 4: Test with real AI
export AWS_ACCESS_KEY_ID="your-key"
export AWS_SECRET_ACCESS_KEY="your-secret"
export AWS_DEFAULT_REGION="us-east-1"

python3.11 lautech_assistant_enhanced.py

# Step 5: Run web interface
python3.11 -m streamlit run lautech_chatbot_app.py
```

---

## 🎓 What Works on Python 3.9 (Your Current Version)

✅ **Demo mode** (`test_assistant_demo.py`)
- All 7 agents
- Multi-agent coordination
- Perfect for presentations
- No dependencies needed

❌ **Real AI mode** (requires Python 3.10+)
❌ **Web interface** (requires Python 3.10+)

---

## 💡 Recommendations

### For Today (Quick Win):
```bash
# Use demo mode - works perfectly on Python 3.9
cd strands_agents
python3 test_assistant_demo.py
```

### For Production (This Week):
```bash
# Upgrade Python to 3.11
brew install python@3.11

# Then run with real AI
python3.11 lautech_assistant_enhanced.py
```

---

## 🔍 Verify Your Setup

### Check 1: Python Version
```bash
python3 --version
# Current: Python 3.9.x
# Need: Python 3.10+ for real AI
# OK for demo: Any 3.x
```

### Check 2: Demo Mode Works
```bash
cd strands_agents
python3 test_assistant_demo.py
# Should run successfully!
```

### Check 3: Dependencies (After Python 3.10+ upgrade)
```bash
pip3 list | grep -E "strands|streamlit|boto3"
# Should show installed packages
```

---

## 🚀 Production Deployment

**For deployment to a server:**
- Server must have Python 3.10+
- Most Linux servers: `apt install python3.11`
- Check with: `python3 --version`
- See DEPLOYMENT_GUIDE.md for full instructions

---

## 📞 Need Help?

**Python Version Issues:**
- Check: `python3 --version`
- Upgrade guide: This file (above)
- Homebrew: https://brew.sh

**Demo Mode Issues:**
- Should work on ANY Python 3.x
- No dependencies required
- Just run: `python3 test_assistant_demo.py`

**Real AI Issues:**
- Requires Python 3.10+
- Requires AWS credentials
- See QUICK_START.md

---

## 🎯 TL;DR - Just Run This

### On Python 3.9 (Your Case):
```bash
cd strands_agents
python3 test_assistant_demo.py
```

### After Upgrading to Python 3.11:
```bash
brew install python@3.11
cd strands_agents
python3.11 -m pip install -r requirements_lautech.txt
python3.11 lautech_assistant_enhanced.py
```

---

**The demo mode works perfectly right now - give it a try!** 🚀
