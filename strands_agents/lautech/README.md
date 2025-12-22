# 🎓 LAUTECH University Assistant - Complete Solution

**Production-ready multi-agent system for Ladoke Akintola University of Technology**

All LAUTECH code is now organized in this dedicated folder following best practices.

---

## 📁 What's In This Folder

```
strands_agents/lautech/
├── lautech_agentcore.py          # ⭐ AgentCore version (deploy to AWS)
├── lautech_assistant_enhanced.py  # Strands version (local/testing)
├── lautech_chatbot_app.py         # Streamlit web interface
├── lautech_student_assistant.py   # Original demo version
├── test_assistant_demo.py         # Demo mode (no AWS needed)
├── .bedrock_agentcore.yaml        # AgentCore config
├── requirements.txt               # Production dependencies
├── requirements_lautech.txt       # All dependencies
├── README.md                      # This file
├── DEPLOYMENT_GUIDE.md            # Full deployment guide
├── QUICK_START.md                 # Quick start guide
├── README_LAUTECH.md              # Technical documentation
└── README_CHATBOT.md              # User guide
```

---

## 🚀 Quick Start (Choose Your Version)

### Option 1: AgentCore (Production AWS Deployment) ⭐ **RECOMMENDED**

```bash
# 1. Configure AgentCore
agentcore configure --entrypoint lautech_agentcore.py

# 2. Test locally
agentcore launch -l
agentcore invoke --local '{"prompt": "When is registration?"}'

# 3. Deploy to AWS
agentcore launch

# 4. Invoke in cloud
agentcore invoke '{"prompt": "How much is school fees?"}'
```

**Benefits:**
- ✅ Serverless (AWS Lambda)
- ✅ Auto-scaling
- ✅ Production-ready
- ✅ Built-in monitoring
- ✅ Session management
- ✅ No server maintenance

---

### Option 2: Streamlit Web App (Local/Self-Hosted)

```bash
# Set AWS credentials
export AWS_ACCESS_KEY_ID="your-key"
export AWS_SECRET_ACCESS_KEY="your-secret"
export AWS_DEFAULT_REGION="us-east-1"

# Run web interface
python3 -m streamlit run lautech_chatbot_app.py

# Opens at http://localhost:8501
```

**Benefits:**
- ✅ Beautiful web UI
- ✅ Quick to deploy
- ✅ Easy customization
- ✅ Good for internal use

---

### Option 3: Demo Mode (No AWS Needed)

```bash
python3 test_assistant_demo.py
```

**Benefits:**
- ✅ No AWS credentials needed
- ✅ Perfect for testing
- ✅ Great for demos
- ✅ Instant responses

---

## 🏗️ Architecture

### AgentCore Version (Recommended for Production)

```
Student Query
    ↓
AWS API Gateway
    ↓
AgentCore Runtime (Lambda)
    ↓
Orchestrator Agent
    ↓
┌──────────┬───────────┬────────────┬───────────┐
│ Academic │ Calendar  │ Financial  │  Hostel   │
│  Agent   │  Agent    │   Agent    │   Agent   │
└──────────┴───────────┴────────────┴───────────┘
    ↓
SQLite Database (→ RDS for production)
    ↓
Claude AI (AWS Bedrock)
    ↓
Response to Student
```

**Key Features:**
- Multi-agent system with intelligent routing
- Database-backed (SQLite → RDS ready)
- Real AI via AWS Bedrock
- Deployed as serverless Lambda
- Auto-scaling and monitoring

---

## 📊 Agent Capabilities

| Agent | What It Does | Example Query |
|-------|--------------|---------------|
| **Academic** | Courses, prerequisites, schedules | "What courses after CSC201?" |
| **Calendar** | Registration dates, deadlines | "When is registration?" |
| **Financial** | Tuition fees, payment methods | "How much is school fees?" |
| **Hostel** | Accommodation, facilities | "How do I apply for hostel?" |
| **Orchestrator** | Routes to right agent(s) | Handles all queries intelligently |

---

## 🎯 Deployment Guide

### Step 1: Install AgentCore

```bash
pip install bedrock-agentcore
```

### Step 2: Configure

```bash
cd strands_agents/lautech

# Configure with your IAM role
agentcore configure --entrypoint lautech_agentcore.py \
  -er arn:aws:iam::YOUR_ACCOUNT:role/agentcore-role
```

### Step 3: Test Locally

```bash
# Launch locally
agentcore launch -l

# In another terminal, test it
agentcore invoke --local '{"prompt": "When is registration?"}'
```

### Step 4: Deploy to AWS

```bash
# Deploy to AWS Lambda
agentcore launch

# Check status
agentcore status

# Test in cloud
agentcore invoke '{"prompt": "How much is school fees for 200 level?"}'
```

### Step 5: Integrate with Your App

```python
import boto3

bedrock_agent = boto3.client('bedrock-agentcore')

response = bedrock_agent.invoke_agent(
    agentId='your-agent-id',
    payload={'prompt': 'When is registration?'}
)

print(response['output'])
```

---

## 📚 Database

### Current: SQLite (Development)

```bash
# View database
sqlite3 lautech_data.db
SELECT * FROM courses;
.quit
```

### Production: Upgrade to RDS

```python
# Update connection in lautech_agentcore.py
import psycopg2

conn = psycopg2.connect(
    dbname="lautech_db",
    host=os.environ['RDS_HOST'],
    user=os.environ['RDS_USER'],
    password=os.environ['RDS_PASSWORD']
)
```

---

## 🔧 Adding Real LAUTECH Data

### Method 1: SQL Insert

```sql
INSERT INTO courses VALUES (
    'CSC401',
    'Software Engineering',
    4,
    'CSC301',
    'SDLC, design patterns, testing',
    'First Semester',
    'Prof. Olaniyan',
    'Computer Science'
);
```

### Method 2: CSV Import

```bash
# Prepare courses.csv
sqlite3 lautech_data.db
.mode csv
.import courses.csv courses
.quit
```

### Method 3: Python Script

```python
import sqlite3

conn = sqlite3.connect('lautech_data.db')
cursor = conn.cursor()

courses = [
    ("CSC401", "Software Engineering", 4, "CSC301", "...", "First Semester", "Prof. K", "CS"),
]

cursor.executemany("INSERT INTO courses VALUES (?, ?, ?, ?, ?, ?, ?, ?)", courses)
conn.commit()
```

---

## 💰 Cost Estimation

### AgentCore Deployment

| Component | Cost |
|-----------|------|
| Lambda execution | ~$0.20/million requests |
| AgentCore runtime | ~$0.10/hour active |
| Bedrock (Claude Haiku) | ~$0.003/1K tokens |
| RDS (t3.micro) | ~$15/month |
| **Total (100 students, 500 queries/day)** | **~$50-75/month** |

### Self-Hosted (EC2)

| Component | Cost |
|-----------|------|
| EC2 t3.small | ~$15/month |
| Bedrock (Claude Haiku) | ~$45/month (500 queries/day) |
| **Total** | **~$60/month** |

---

## 🧪 Testing

### Test AgentCore Locally

```bash
# Launch local runtime
agentcore launch -l

# Test in another terminal
agentcore invoke --local '{"prompt": "What courses are available?"}'
agentcore invoke --local '{"prompt": "How much is tuition?"}'
agentcore invoke --local '{"prompt": "When does registration start?"}'
```

### Test Web Interface

```bash
streamlit run lautech_chatbot_app.py
# Visit http://localhost:8501
```

### Test Demo Mode

```bash
python3 test_assistant_demo.py
```

---

## 📱 Integration Options

### WhatsApp Bot

```python
from twilio.rest import Client

# Send query to AgentCore
response = bedrock_agent.invoke_agent(
    agentId='your-agent-id',
    payload={'prompt': user_message}
)

# Send response via WhatsApp
client.messages.create(
    from_='whatsapp:+14155238886',
    body=response['output'],
    to=f'whatsapp:{user_phone}'
)
```

### REST API

```python
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/api/ask', methods=['POST'])
def ask_question():
    question = request.json['question']

    response = bedrock_agent.invoke_agent(
        agentId='your-agent-id',
        payload={'prompt': question}
    )

    return jsonify({'answer': response['output']})
```

### Slack Bot

```python
from slack_bolt import App

@app.message()
def handle_message(message, say):
    response = bedrock_agent.invoke_agent(
        agentId='your-agent-id',
        payload={'prompt': message['text']}
    )

    say(response['output'])
```

---

## 🔒 Security Best Practices

### IAM Role (Minimum Permissions)

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "bedrock:InvokeModel",
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "*"
    }
  ]
}
```

### Environment Variables

```bash
# Don't hardcode credentials!
export AWS_ACCESS_KEY_ID="..."
export AWS_SECRET_ACCESS_KEY="..."
export DB_PASSWORD="..."
```

### Database Security

```python
# Use parameterized queries
cursor.execute("SELECT * FROM courses WHERE code = ?", (user_input,))
# NOT: cursor.execute(f"SELECT * FROM courses WHERE code = '{user_input}'")
```

---

## 📈 Monitoring

### CloudWatch Logs

```bash
# View logs
aws logs tail /aws/lambda/lautech-assistant --follow
```

### Metrics

```bash
# Get invocation metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda \
  --metric-name Invocations \
  --dimensions Name=FunctionName,Value=lautech-assistant \
  --start-time 2024-01-01T00:00:00Z \
  --end-time 2024-01-02T00:00:00Z \
  --period 3600 \
  --statistics Sum
```

---

## 🎓 Production Checklist

Before going live:

- [ ] Test all 4 agents thoroughly
- [ ] Add real LAUTECH data to database
- [ ] Configure production RDS database
- [ ] Set up monitoring and alerts
- [ ] Configure backup strategy
- [ ] Test error handling
- [ ] Set up CI/CD pipeline
- [ ] Document for staff
- [ ] Train support team
- [ ] Perform load testing
- [ ] Set up staging environment
- [ ] Configure rate limiting

---

## 🚀 Next Steps

### Phase 1 (Current)
- ✅ Multi-agent system
- ✅ AgentCore integration
- ✅ Database backend
- ✅ Web interface

### Phase 2 (Next)
- [ ] WhatsApp integration
- [ ] SMS notifications
- [ ] Email alerts
- [ ] Admin dashboard

### Phase 3 (Future)
- [ ] Voice interface
- [ ] Multi-language support
- [ ] Mobile app
- [ ] Analytics dashboard
- [ ] Student portal integration

---

## 📞 Support

**Questions?**
- Check DEPLOYMENT_GUIDE.md for detailed instructions
- See QUICK_START.md for quick setup
- Review prod_agent/ folder for AgentCore examples

**Issues?**
- Test AWS credentials: `aws sts get-caller-identity`
- Check logs: `agentcore logs`
- Test locally first: `agentcore launch -l`

---

## 🎉 Summary

| File | Purpose | When to Use |
|------|---------|-------------|
| `lautech_agentcore.py` | AgentCore version | Production AWS deployment |
| `lautech_chatbot_app.py` | Web UI | Local/self-hosted |
| `test_assistant_demo.py` | Demo mode | Testing without AWS |
| `lautech_assistant_enhanced.py` | Strands only | Development |

**Recommended:** Use `lautech_agentcore.py` for production deployment to AWS!

---

**Built for LAUTECH with ❤️ using AWS Bedrock AgentCore + Strands Agents**
