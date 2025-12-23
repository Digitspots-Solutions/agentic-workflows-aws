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

## 🌐 Part C: Production Web Dashboard

**Beautiful web interface that calls the deployed AgentCore agent**

### Quick Start

```bash
cd strands_agents/lautech

# Set AWS credentials (if not already configured)
export AWS_ACCESS_KEY_ID="your-key"
export AWS_SECRET_ACCESS_KEY="your-secret"
export AWS_DEFAULT_REGION="us-east-1"

# Launch dashboard
./run_dashboard.sh
```

Dashboard opens at: **http://localhost:8501**

### Features

- ✅ Calls deployed AgentCore agent (not local Strands)
- ✅ Beautiful LAUTECH branding (green & gold)
- ✅ Mobile responsive design
- ✅ Session management
- ✅ Usage analytics
- ✅ Quick action buttons
- ✅ Real-time chat interface

### Manual Launch

```bash
# Install dependencies
pip3 install streamlit boto3

# Set agent ID (optional, has default)
export LAUTECH_AGENT_ID="lautech_agentcore-U7qNy1GPsE"

# Run
streamlit run web_dashboard.py
```

### Configuration

Edit agent ID in sidebar settings or set environment variable:

```bash
export LAUTECH_AGENT_ID="your-agent-id"
```

Get your agent ID:

```bash
agentcore status
```

### Deploy to Server

**Option 1: Streamlit Cloud (Free)**

1. Push to GitHub
2. Go to https://streamlit.io/cloud
3. Deploy from repo: `strands_agents/lautech/web_dashboard.py`
4. Add secrets:
   ```
   AWS_ACCESS_KEY_ID = "..."
   AWS_SECRET_ACCESS_KEY = "..."
   AWS_DEFAULT_REGION = "us-east-1"
   LAUTECH_AGENT_ID = "..."
   ```

**Option 2: Self-Hosted (EC2/VPS)**

```bash
# Install dependencies
pip3 install streamlit boto3

# Run with nohup
nohup streamlit run web_dashboard.py --server.port 8501 &

# Or use systemd service
sudo nano /etc/systemd/system/lautech-dashboard.service
```

Sample systemd service:

```ini
[Unit]
Description=LAUTECH Dashboard
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/strands_agents/lautech
Environment="AWS_ACCESS_KEY_ID=..."
Environment="AWS_SECRET_ACCESS_KEY=..."
Environment="AWS_DEFAULT_REGION=us-east-1"
Environment="LAUTECH_AGENT_ID=..."
ExecStart=/usr/bin/python3 -m streamlit run web_dashboard.py
Restart=always

[Install]
WantedBy=multi-user.target
```

**Option 3: Docker**

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY web_dashboard.py .

EXPOSE 8501

CMD ["streamlit", "run", "web_dashboard.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

```bash
docker build -t lautech-dashboard .
docker run -p 8501:8501 \
  -e AWS_ACCESS_KEY_ID="..." \
  -e AWS_SECRET_ACCESS_KEY="..." \
  -e AWS_DEFAULT_REGION="us-east-1" \
  -e LAUTECH_AGENT_ID="..." \
  lautech-dashboard
```

---

## 🛠️ Part D: Admin Panel for Staff

**Comprehensive management interface for authorized staff**

### Quick Start

```bash
cd strands_agents/lautech

# Launch admin panel
./run_admin.sh
```

Admin panel opens at: **http://localhost:8502**

**Default Credentials:** admin / lautech2024

⚠️ **IMPORTANT:** Change credentials for production!

### Features

#### 📚 Course Management
- View all courses in searchable table
- Add new courses with validation
- Edit existing courses
- Delete courses
- Export to CSV

#### 💰 Fee Management
- View all fee records
- Add new fees (tuition, administrative, lab, etc.)
- Delete fees
- Export to CSV

#### 📅 Calendar Management
- View academic calendar
- Add events (registration, exams, deadlines)
- Delete events
- Export to CSV

#### 🏠 Hostel Management
- View all hostels
- Add new hostels with capacity and facilities
- Update hostel status
- Delete hostels
- Export to CSV

#### 📥 Import/Export
- Export all tables to CSV
- Import CSV files (via import_data.py script)
- Database backup functionality

#### ⚙️ Settings
- View system information
- Database statistics
- Backup management

### Screenshots

**Dashboard:**
- System overview with metrics
- Database health monitoring
- Recent activity log

**Course Management:**
- Tabbed interface: View All | Add New | Edit/Delete
- Form validation
- Inline editing

**Data Export:**
- One-click CSV downloads for all tables
- Backup creation with timestamps

### Authentication

**Current (Demo):**
- Simple username/password (admin/lautech2024)
- Session-based authentication

**Production (Part E TODO):**
- University SSO integration
- LDAP/Active Directory
- Role-based access control (RBAC)
- Multi-factor authentication (MFA)
- Audit logging

### Running Both Dashboards

```bash
# Terminal 1: User dashboard (port 8501)
./run_dashboard.sh

# Terminal 2: Admin panel (port 8502)
./run_admin.sh
```

Users access: http://localhost:8501
Staff access: http://localhost:8502

### Deploy to Production

**Option 1: Same Server, Different Ports**

```bash
# User dashboard
streamlit run web_dashboard.py --server.port 8501 &

# Admin panel (with authentication)
streamlit run admin_panel.py --server.port 8502 &
```

**Option 2: Separate Subdomains**

```nginx
# nginx config
server {
    server_name students.lautech.edu.ng;
    location / {
        proxy_pass http://localhost:8501;
    }
}

server {
    server_name admin.lautech.edu.ng;
    location / {
        proxy_pass http://localhost:8502;
        # Additional IP whitelisting or auth
        allow 10.0.0.0/8;  # Internal network only
        deny all;
    }
}
```

**Option 3: Firewall Protection**

```bash
# Allow admin panel only from campus network
sudo ufw allow from 10.0.0.0/8 to any port 8502
sudo ufw deny 8502
```

### Security Checklist (Production)

- [ ] Replace demo credentials with real authentication
- [ ] Integrate with university SSO/LDAP
- [ ] Enable HTTPS (SSL certificates)
- [ ] Restrict admin access to campus network
- [ ] Add rate limiting
- [ ] Enable audit logging
- [ ] Add input validation and sanitization
- [ ] Implement CSRF protection
- [ ] Regular security updates
- [ ] Database backup automation

### API for Integration

For programmatic access (Part E):

```python
# REST API wrapper around admin functions
from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)

@app.route('/api/courses', methods=['GET', 'POST'])
def manage_courses():
    if request.method == 'GET':
        # Return all courses
        conn = sqlite3.connect('lautech_data.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM courses")
        courses = cursor.fetchall()
        conn.close()
        return jsonify(courses)

    elif request.method == 'POST':
        # Add new course
        data = request.json
        # ... add course logic
        return jsonify({'status': 'success'})
```

---

## 🏭 Part E: Production Hardening

**Enterprise-grade deployment with monitoring, backups, and security**

### Quick Reference

📖 **Full Guide:** See [PRODUCTION.md](PRODUCTION.md) for complete documentation

### Key Components

#### 1. Database Migration (SQLite → RDS PostgreSQL)

```bash
cd strands_agents/lautech

# Dry run (see what would be migrated)
python3 scripts/migrate_to_rds.py --dry-run

# Perform migration
python3 scripts/migrate_to_rds.py

# Verify migration
python3 scripts/migrate_to_rds.py --verify
```

**Prerequisites:**
- RDS PostgreSQL instance created
- Credentials in AWS Secrets Manager (`lautech/db/credentials`)
- Install: `pip install psycopg2-binary`

#### 2. Automated Backups

```bash
# Manual backup to S3
python3 scripts/backup_database.py

# Local backup only
python3 scripts/backup_database.py --local
```

**Automated Schedule:**
- Daily backups at 3 AM (EventBridge + Lambda)
- 30-day retention in S3 Standard
- After 30 days: Move to Glacier
- After 90 days: Auto-delete

#### 3. Monitoring & Logging

**CloudWatch Metrics:**
- Query count by agent
- Response time (average, p95, p99)
- Error rate and types
- Database connections
- Lambda concurrency

**CloudWatch Logs:**
- Application logs with structured JSON
- AgentCore execution logs
- RDS query logs
- Web dashboard access logs

**Alarms:**
- High error rate (>5%)
- Slow response time (>2s average)
- Database connection failures
- High Lambda errors

#### 4. Security Hardening

**Authentication:**
- [ ] University SSO integration
- [ ] LDAP/Active Directory
- [ ] Role-based access control (RBAC)
- [ ] Multi-factor authentication (MFA)
- [ ] Session management with timeout

**Network Security:**
- VPC with private subnets for RDS
- Security groups with least privilege
- WAF with rate limiting and geo-blocking
- SSL/TLS encryption (HTTPS only)
- VPN/Direct Connect for admin access

**Data Security:**
- Database encryption at rest (RDS)
- Secrets Manager for credentials
- S3 encryption for backups
- CloudTrail for audit logging
- Regular security scans

#### 5. Performance Optimization

**Caching:**
- Redis/ElastiCache for frequently accessed data
- CloudFront CDN for static assets
- Application-level caching for agent responses

**Database:**
- Connection pooling
- Query optimization with indexes
- Read replicas for heavy read workload
- Partitioning for large tables

**Application:**
- Async processing for non-blocking operations
- Batch API calls to reduce Bedrock costs
- Lazy loading for admin panel data
- Compression for API responses

#### 6. High Availability

**Multi-AZ Deployment:**
```
Region: us-east-1
├── AZ-1
│   ├── Application (ECS/EC2)
│   ├── RDS Primary
│   └── Cache Primary
└── AZ-2
    ├── Application (ECS/EC2)
    ├── RDS Standby
    └── Cache Replica
```

**Auto Scaling:**
- Application auto-scales based on CPU/memory
- RDS read replicas based on connection count
- Lambda concurrency limits

**Disaster Recovery:**
- RTO: 15 minutes
- RPO: 5 minutes (automated backups)
- Cross-region backup replication
- Documented failover procedures

### Cost Estimation

| Tier | Configuration | Monthly Cost |
|------|--------------|--------------|
| **Starter** | t3.small EC2, db.t3.micro RDS | ~$80 |
| **Standard** | t3.medium EC2, db.t3.medium RDS Multi-AZ | ~$220 |
| **Production** | ECS Fargate, db.m5.large RDS Multi-AZ, Redis | ~$450 |

💡 **Save 30-40%** with Reserved Instances for 1-year commitment

### Deployment Steps

1. **Pre-Production**
   ```bash
   # Test migration locally
   python3 scripts/migrate_to_rds.py --dry-run

   # Create staging environment
   # ... deploy to staging
   # ... run integration tests
   ```

2. **Production Deployment**
   ```bash
   # Migrate database
   python3 scripts/migrate_to_rds.py

   # Update environment
   export DB_TYPE=postgres
   export ENVIRONMENT=production

   # Deploy AgentCore
   agentcore launch

   # Deploy web apps
   # ... ECS/EC2 deployment
   ```

3. **Post-Deployment**
   ```bash
   # Verify backups
   python3 scripts/backup_database.py

   # Check monitoring
   aws cloudwatch get-dashboard --dashboard-name LAUTECH

   # Test critical flows
   # ... smoke tests
   ```

### Monitoring Dashboard

Access CloudWatch dashboard: `LAUTECH-Production`

**Key Metrics:**
- **Availability:** 99.9% uptime target
- **Performance:** <500ms average response time
- **Errors:** <1% error rate
- **Database:** <80% CPU, <85% storage

### Production Checklist

- [ ] RDS Multi-AZ deployed and migrated
- [ ] Automated backups configured
- [ ] CloudWatch monitoring active
- [ ] Security hardening complete
- [ ] SSL certificates installed
- [ ] WAF rules enabled
- [ ] Auto-scaling configured
- [ ] Disaster recovery tested
- [ ] Documentation updated
- [ ] Staff training completed
- [ ] Support procedures documented
- [ ] Load testing passed
- [ ] Penetration testing completed

### Support & Maintenance

**Monitoring:** CloudWatch dashboards
**Alerts:** SNS notifications to ops team
**Logs:** CloudWatch Logs with 30-day retention
**Updates:** Weekly during maintenance window (Sun 2-4 AM)
**Backups:** Automated daily, verified weekly

---

## 💬 Part B: WhatsApp Bot Integration

**Let students interact with LAUTECH Assistant via WhatsApp**

### Quick Start

📖 **Full Guide:** See [WHATSAPP_BOT.md](WHATSAPP_BOT.md) for complete setup

#### 1. Setup Twilio

```bash
# Create account at https://www.twilio.com/try-twilio
# Get credentials from console

export TWILIO_ACCOUNT_SID='ACxxxxxxxxxx'
export TWILIO_AUTH_TOKEN='xxxxxxxxxx'
export TWILIO_WHATSAPP_NUMBER='whatsapp:+14155238886'
```

#### 2. Install & Test

```bash
# Install dependencies
pip install -r requirements_whatsapp.txt

# Test connection
python3 whatsapp_bot.py test

# Run bot server
python3 whatsapp_bot.py
```

#### 3. Expose Webhook

```bash
# For testing: Use ngrok
ngrok http 5000

# For production: Deploy to EC2/ECS/Lambda
# See WHATSAPP_BOT.md for deployment options
```

#### 4. Configure Twilio

1. Go to: https://console.twilio.com/us1/develop/sms/settings/whatsapp-sandbox
2. Set webhook URL: `https://your-server.com/webhook`
3. Method: `POST`
4. Save

#### 5. Test on WhatsApp

```
1. Send to +1 415 523 8886 (Twilio sandbox)
2. Message: "join <your-code>"
3. Then ask: "When is registration?"
```

### Features

✅ **Natural conversation** via WhatsApp
✅ **Instant responses** from AgentCore agent
✅ **Session management** for context
✅ **Message chunking** for long responses
✅ **Broadcast messages** for announcements
✅ **Health monitoring** endpoints
✅ **Rate limiting** to prevent abuse

### Example Conversation

```
Student: When is registration?

Bot: 📅 Registration for 2024/2025 First Semester:
     • Start: September 1, 2024
     • End: September 15, 2024
     • Late registration: September 16-30 (with penalty)

Student: How much is school fees for 200 level?

Bot: 💰 200 Level Tuition Fee: ₦75,000
     Session: 2024/2025

     Payment methods:
     • Bank transfer
     • Online portal
     • Campus bank branches

Student: What CS courses are available?

Bot: 📚 Computer Science Courses (200 Level):

     • CSC201: Programming II (3 credits)
       Prerequisites: CSC101

     • MTH201: Linear Algebra (3 credits)
       Prerequisites: MTH101

     ... [more courses]
```

### Deployment Options

#### Option 1: AWS Lambda (Serverless) ⭐ **Recommended**

```bash
# Package and deploy
zip -r function.zip whatsapp_bot.py

aws lambda create-function \
  --function-name lautech-whatsapp-bot \
  --runtime python3.11 \
  --handler whatsapp_bot.lambda_handler \
  --zip-file fileb://function.zip \
  --environment Variables="{TWILIO_ACCOUNT_SID=xxx,LAUTECH_AGENT_ID=xxx}"

# Create API Gateway endpoint
# Configure in Twilio webhook
```

**Cost:** ~$5/month for 1000 messages/day

#### Option 2: Docker Container

```bash
# Build and run
docker build -t lautech-whatsapp-bot .
docker run -d -p 5000:5000 \
  -e TWILIO_ACCOUNT_SID='xxx' \
  -e LAUTECH_AGENT_ID='xxx' \
  lautech-whatsapp-bot
```

#### Option 3: EC2 with systemd

```bash
# Copy files and create systemd service
sudo systemctl start lautech-whatsapp
sudo systemctl enable lautech-whatsapp

# Configure nginx reverse proxy for HTTPS
```

### Broadcast Messages

Send announcements to all users:

```bash
# Via CLI
python3 whatsapp_bot.py broadcast "Registration deadline extended!"

# Via Python
from whatsapp_bot import send_broadcast
send_broadcast("Important announcement", phone_numbers)
```

### Monitoring

```bash
# Health check
curl http://your-server/health

# Statistics
curl http://your-server/stats
```

Response:
```json
{
  "total_users": 247,
  "total_messages": 1523,
  "active_sessions": 15
}
```

### Cost Estimation

| Component | Cost |
|-----------|------|
| Twilio WhatsApp Business | $15/month |
| Messages (1000/day) | $150/month |
| AWS Lambda | $5/month |
| **Total** | **~$170/month** |

💡 **Sandbox is free** for testing!

### Production Checklist

- [ ] Twilio Business number approved
- [ ] Webhook deployed with HTTPS
- [ ] SSL certificate installed
- [ ] Rate limiting enabled
- [ ] Request validation implemented
- [ ] Monitoring active
- [ ] User guide published
- [ ] Support team trained
- [ ] Load tested

### Student Guide

**How students use it:**

1. **Join**
   - Save: +1 415 523 8886
   - Send: `join lautech-code`

2. **Ask questions**
   - When is registration?
   - What courses are available?
   - How much is fees?

3. **Get help**
   - Send: `help` or `menu`

---

## 🚀 Next Steps

### Phase 1 (Completed ✅)
- ✅ Multi-agent system with 4 specialist agents
- ✅ AgentCore integration (deployed to AWS)
- ✅ Database backend (SQLite → RDS ready)
- ✅ Data management system (CSV import/export)
- ✅ Production web dashboard (Streamlit)
- ✅ Admin panel for staff (full CRUD)
- ✅ Production hardening (monitoring, backups, security)
- ✅ WhatsApp bot integration (Twilio)

### Phase 2 (Future Enhancements)
- [ ] SMS notifications (Twilio SMS)
- [ ] Email alerts (SES)
- [ ] Telegram bot
- [ ] Voice interface (Alexa/Google Assistant)
- [ ] Multi-language support (Yoruba, Igbo, Hausa)
- [ ] Mobile app (React Native)
- [ ] Analytics dashboard
- [ ] Student portal integration
- [ ] Payment integration
- [ ] Document upload/verification

### Phase 3 (Advanced Features)
- [ ] AI-powered course recommendations
- [ ] Automated transcript generation
- [ ] Grade prediction
- [ ] Study group matching
- [ ] Career counseling
- [ ] Alumni network integration

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
