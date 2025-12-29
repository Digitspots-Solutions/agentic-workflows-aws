# 🎓 LAUTECH University Assistant

**Production-ready multi-agent system for Ladoke Akintola University of Technology**

Built with AWS Bedrock AgentCore, this system provides AI-powered assistance for students and staff through multiple interfaces.

---

## 📁 Project Structure

```
strands_agents/lautech/
├── Core
│   ├── lautech_agentcore.py          # AgentCore agent (deployed to AWS)
│   ├── .bedrock_agentcore.yaml        # AgentCore configuration
│   └── requirements.txt               # Core dependencies
│
├── Data Management
│   ├── data/                          # CSV data files
│   │   ├── courses.csv               # Course catalog
│   │   ├── fees.csv                  # Fee structure
│   │   ├── calendar.csv              # Academic calendar
│   │   └── hostels.csv               # Hostel information
│   └── import_data.py                # Data import script
│
├── Web Interfaces
│   ├── web_dashboard.py              # Student dashboard
│   ├── run_dashboard.sh              # Dashboard launcher
│   ├── admin_panel.py                # Staff admin panel
│   └── run_admin.sh                  # Admin launcher
│
├── WhatsApp Bot
│   ├── whatsapp_bot.py               # Twilio integration
│   └── requirements_whatsapp.txt     # WhatsApp dependencies
│
├── Production Scripts
│   └── scripts/
│       ├── migrate_to_rds.py         # SQLite → PostgreSQL migration
│       └── backup_database.py        # Automated backups
│
└── Documentation
    ├── README.md                      # This file
    ├── DATA_GUIDE.md                  # Data management guide
    ├── PRODUCTION.md                  # Production deployment guide
    └── WHATSAPP_BOT.md                # WhatsApp setup guide
```

---

## ⚡ Quick Start

### 1️⃣ Deploy AgentCore Agent

```bash
# Deploy to AWS
agentcore launch

# Test
agentcore invoke '{"prompt": "When is registration?"}'
```

**Agent ID:** `lautech_agentcore-U7qNy1GPsE` (already deployed)

### 2️⃣ Import Data

```bash
# Import all data
python3 import_data.py --all

# View statistics
python3 import_data.py --stats
```

### 3️⃣ Launch Web Dashboard

```bash
# For students
./run_dashboard.sh
# Opens at http://localhost:8501
```

### 4️⃣ Launch Admin Panel

```bash
# For staff
./run_admin.sh
# Opens at http://localhost:8502
```

### 5️⃣ Set Up WhatsApp Bot (Optional)

See [WHATSAPP_BOT.md](WHATSAPP_BOT.md) for complete setup guide.

```bash
# Test
python3 whatsapp_bot.py test

# Run server
python3 whatsapp_bot.py
```

---

## 🏗️ System Architecture

```
Students → [WhatsApp Bot | Web Dashboard]
           ↓
      AgentCore Agent (AWS Lambda)
           ↓
      Multi-Agent System
           ├── Academic Agent
           ├── Calendar Agent
           ├── Financial Agent
           └── Hostel Agent
           ↓
      Database (SQLite → RDS)
           ↓
      AWS Bedrock (Claude Haiku)

Staff → Admin Panel → Database
```

---

## ✨ Features

### 🎯 Multi-Agent System

**4 Specialist Agents:**
- **Academic Agent:** Courses, prerequisites, lecturers
- **Calendar Agent:** Registration, deadlines, events
- **Financial Agent:** Fees, payments, deadlines
- **Hostel Agent:** Accommodation, facilities, applications

**Orchestrator:** Routes queries to appropriate agents

### 📊 Data Management

- **CSV-based import:** No SQL knowledge required
- **Sample data included:** 20 courses, 20 fees, 35 events, 8 hostels
- **Easy updates:** Edit CSV, run import script
- **Documentation:** [DATA_GUIDE.md](DATA_GUIDE.md)

### 🌐 Web Dashboard (Students)

- Beautiful Streamlit interface
- Real-time chat with AI agent
- Quick action buttons
- Session management
- Usage analytics

### 🛠️ Admin Panel (Staff)

- Full CRUD operations for all tables
- CSV import/export
- Database backup
- System statistics
- Authentication (demo: admin/lautech2024)

### 💬 WhatsApp Bot

- Natural conversation via WhatsApp
- Calls deployed AgentCore agent
- Session management
- Broadcast messaging
- Setup guide: [WHATSAPP_BOT.md](WHATSAPP_BOT.md)

### 🏭 Production Ready

- **Database migration:** SQLite → PostgreSQL RDS
- **Automated backups:** Daily to S3
- **Monitoring:** CloudWatch metrics and logs
- **Security:** WAF, VPC, encryption
- **Documentation:** [PRODUCTION.md](PRODUCTION.md)

---

## 📖 What Students Can Ask

### Academic
- "What Computer Science courses are available?"
- "What are the prerequisites for CSC401?"
- "Who teaches Database Systems?"

### Financial
- "How much is school fees for 200 level?"
- "What are the payment methods?"
- "When is the fee deadline?"

### Calendar
- "When is registration?"
- "What is the exam schedule?"
- "When does first semester start?"

### Hostel
- "How do I apply for hostel?"
- "What hostels are available for males?"
- "What facilities does Ajose Hall have?"

---

## 🚀 Deployment

### Development (Current)

```bash
# Local testing with SQLite
python3 import_data.py --all
./run_dashboard.sh
./run_admin.sh
```

**Cost:** $0/month

### Production

See [PRODUCTION.md](PRODUCTION.md) for complete deployment guide.

**Steps:**
1. Create RDS PostgreSQL instance
2. Migrate database: `python3 scripts/migrate_to_rds.py`
3. Deploy web apps (ECS/EC2)
4. Set up monitoring (CloudWatch)
5. Configure backups (S3)
6. Deploy WhatsApp bot (Lambda)

**Cost:** ~$350-450/month (optimized with Reserved Instances)

---

## 📊 Cost Breakdown

| Component | Development | Production |
|-----------|-------------|------------|
| Database | SQLite (free) | RDS PostgreSQL (~$130) |
| Compute | Local (free) | ECS/EC2 (~$35) |
| AgentCore | Deployed (~$0) | Lambda (~$50) |
| Bedrock | Pay-per-use (~$10) | (~$90) |
| WhatsApp | Sandbox (free) | Twilio (~$170) |
| Monitoring | Logs (free) | CloudWatch (~$15) |
| **Total** | **~$10/month** | **~$400/month** |

---

## 📚 Documentation

| Guide | Purpose | Lines |
|-------|---------|-------|
| [README.md](README.md) | Main documentation | This file |
| [DATA_GUIDE.md](DATA_GUIDE.md) | Data management | 447 |
| [PRODUCTION.md](PRODUCTION.md) | Production deployment | 753 |
| [WHATSAPP_BOT.md](WHATSAPP_BOT.md) | WhatsApp setup | 617 |

---

## 🔧 Common Tasks

### Add/Update Data

```bash
# Edit CSV files in data/
nano data/courses.csv

# Import
python3 import_data.py --courses

# Or import all
python3 import_data.py --all
```

### Backup Database

```bash
# Local backup
python3 scripts/backup_database.py --local

# Backup to S3
python3 scripts/backup_database.py
```

### Migrate to Production Database

```bash
# Dry run
python3 scripts/migrate_to_rds.py --dry-run

# Migrate
python3 scripts/migrate_to_rds.py

# Verify
python3 scripts/migrate_to_rds.py --verify
```

### Update AgentCore Agent

```bash
# Edit lautech_agentcore.py
nano lautech_agentcore.py

# Redeploy
agentcore launch
```

---

## 🎯 Next Steps

### Phase 1 (Completed ✅)
- ✅ Multi-agent system with 4 specialist agents
- ✅ AgentCore deployment to AWS
- ✅ SQLite database with sample data
- ✅ CSV import system
- ✅ Web dashboard for students
- ✅ Admin panel for staff
- ✅ WhatsApp bot integration
- ✅ Production deployment guides
- ✅ Migration and backup scripts

### Phase 2 (Future)
- [ ] Migrate to RDS PostgreSQL
- [ ] Deploy web apps to production
- [ ] Set up monitoring and alerts
- [ ] Integrate real LAUTECH data
- [ ] University SSO authentication
- [ ] SMS notifications
- [ ] Email alerts
- [ ] Mobile app

### Phase 3 (Advanced)
- [ ] Multi-language support (Yoruba, Igbo, Hausa)
- [ ] Voice interface (Alexa/Google)
- [ ] AI course recommendations
- [ ] Grade prediction
- [ ] Alumni network integration

---

## 🆘 Support

### Issues?

1. **Data import fails:** Check CSV format in [DATA_GUIDE.md](DATA_GUIDE.md)
2. **AgentCore errors:** Verify AWS credentials and agent deployment
3. **Dashboard won't start:** Check Python version (3.10+ required)
4. **WhatsApp not working:** Verify Twilio credentials and webhook URL

### Contact

- **GitHub:** Open an issue in the repository
- **IT Support:** Contact LAUTECH IT department

---

## 📜 License

Built for Ladoke Akintola University of Technology (LAUTECH)

---

**Built with AWS Bedrock AgentCore + Strands Agents**

December 2024
