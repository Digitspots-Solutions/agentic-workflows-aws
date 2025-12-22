# 🎓 LAUTECH University Assistant - Web Chatbot

**An AI-powered chatbot for students and staff** - No coding required!

![Multi-Agent System](https://img.shields.io/badge/Multi--Agent-System-purple)
![AWS Bedrock](https://img.shields.io/badge/AWS-Bedrock-orange)
![Streamlit](https://img.shields.io/badge/Streamlit-Web%20App-red)

## 🌟 What Is This?

The LAUTECH University Assistant is a **friendly chatbot** that helps students and university staff get instant answers to their questions. Just type your question in plain English and get immediate, accurate responses!

### Who Can Use This?

- ✅ **Students** - Ask about courses, fees, registration, hostel, etc.
- ✅ **Staff** - Help students quickly with common queries
- ✅ **Parents** - Get information about the university
- ✅ **Prospective Students** - Learn about LAUTECH

### What Can It Answer?

The assistant has **7 AI agents** that specialize in different areas:

| Agent | What It Helps With | Example Questions |
|-------|-------------------|-------------------|
| 📚 **Academic** | Courses, prerequisites, lecturers | "What courses can I take after CSC201?" |
| 📅 **Calendar** | Registration dates, exam periods | "When does registration start?" |
| 💰 **Financial** | School fees, payment methods | "How much is school fees for 200 level?" |
| 🏠 **Hostel** | Accommodation services | "How do I apply for hostel?" |
| 📖 **Library** | Library hours, borrowing books | "What are the library opening hours?" |
| 📋 **Administrative** | Transcripts, ID cards, certificates | "How do I get my transcript?" |
| 🎯 **Orchestrator** | Routes to the right agent | Handles all queries intelligently |

## 🚀 Quick Start (3 Easy Steps!)

### For Students (Using the Web Interface)

1. **Visit the URL** provided by your IT department
   ```
   Example: https://assistant.lautech.edu.ng
   ```

2. **Type your question** in the chat box
   ```
   "When is registration for first semester?"
   ```

3. **Get instant answer!** 🎉

That's it! No installation, no setup, just use it!

---

### For IT Staff (Setting Up the Server)

#### Option 1: One-Command Setup (Easiest)

```bash
# Navigate to the folder
cd strands_agents

# Run the setup script
./run_chatbot.sh
```

That's it! The script will:
- ✅ Check Python installation
- ✅ Install dependencies
- ✅ Check AWS credentials
- ✅ Start the web server

The chatbot opens automatically at `http://localhost:8501`

#### Option 2: Manual Setup

```bash
# 1. Install dependencies
pip install -r requirements_lautech.txt

# 2. Configure AWS credentials
aws configure
# Enter your AWS Access Key ID
# Enter your AWS Secret Access Key
# Enter region: us-east-1

# 3. Run the chatbot
streamlit run lautech_chatbot_app.py
```

---

## 📸 Screenshots

### Main Chat Interface
```
┌─────────────────────────────────────────┐
│  🎓 LAUTECH University Assistant        │
│  Your AI-powered guide to LAUTECH       │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│ 👤 You (2:30 PM)                        │
│ How much is school fees?                │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│ 🤖 LAUTECH Assistant (2:30 PM)          │
│                                         │
│ For undergraduate students:             │
│ • 100 Level: ₦100,000 (includes        │
│   acceptance fee)                       │
│ • 200-400 Level: ₦75,000               │
│ • 500 Level: ₦85,000                   │
│                                         │
│ Payment deadline: September 15, 2024    │
└─────────────────────────────────────────┘

💬 Ask me anything about LAUTECH...
```

### Sidebar Quick Actions
```
┌────────────────────────┐
│ 🎓 LAUTECH Assistant   │
├────────────────────────┤
│ What can I help with?  │
│                        │
│ 📚 Academic Questions  │
│ • Course Information   │
│ • Prerequisites        │
│                        │
│ 💰 Financial Questions │
│ • School Fees          │
│ • Payment Methods      │
│                        │
│ 📅 Important Dates     │
│ • Registration Dates   │
│ • Academic Calendar    │
│                        │
│ 🏠 Hostel & Services   │
│ • Hostel Application   │
│ • Library Services     │
└────────────────────────┘
```

---

## 💡 Example Questions

### Academic
- "What courses are available for computer science students?"
- "What are the prerequisites for CSC301?"
- "Who teaches Web Programming?"
- "What courses can I take in the first semester?"

### Financial
- "How much is school fees for 300 level?"
- "What are the payment methods?"
- "When is the payment deadline?"
- "What happens if I pay late?"

### Calendar & Dates
- "When is registration?"
- "When do exams start?"
- "Show me the academic calendar"
- "When is the add/drop deadline?"

### Hostel
- "How do I apply for hostel?"
- "What hostels are available for male students?"
- "What are the hostel rules?"
- "How much is hostel accommodation?"

### Library
- "What are the library opening hours?"
- "How many books can I borrow?"
- "Is the library open on weekends?"
- "How do I access e-books?"

### Administrative
- "How do I get my student ID card?"
- "I need my transcript, what should I do?"
- "How long does it take to get a transcript?"
- "What is the clearance process?"

### Complex (Multi-Agent)
- "When is registration and how much will I pay?"
- "I'm a new student, what do I need to know?"
- "Tell me about hostel application and fees"

---

## 🏗️ How It Works (Technical Overview)

### Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Student/User                         │
│                  (Web Browser)                          │
└─────────────────────┬───────────────────────────────────┘
                      │
                      │ Question: "How much is school fees?"
                      │
                      ▼
┌─────────────────────────────────────────────────────────┐
│              Streamlit Web Interface                    │
│              (lautech_chatbot_app.py)                   │
└─────────────────────┬───────────────────────────────────┘
                      │
                      │
                      ▼
┌─────────────────────────────────────────────────────────┐
│            🎯 Orchestrator Agent                        │
│         (Analyzes question & routes)                    │
└─────┬────────┬────────┬────────┬────────┬──────────────┘
      │        │        │        │        │
      ▼        ▼        ▼        ▼        ▼
    ┌───┐   ┌───┐   ┌───┐   ┌───┐   ┌────┐
    │📚 │   │📅 │   │💰 │   │🏠 │   │📋  │
    │Aca│   │Cal│   │Fin│   │Hos│   │Adm │
    │dem│   │end│   │anc│   │tel│   │in  │
    └───┘   └───┘   └───┘   └───┘   └────┘
      │        │        │        │        │
      └────────┴────────┴────────┴────────┘
                      │
                      │ "For 200 level: ₦75,000..."
                      │
                      ▼
┌─────────────────────────────────────────────────────────┐
│              AWS Bedrock (Claude AI)                    │
│         Processes with university knowledge             │
└─────────────────────────────────────────────────────────┘
```

### Multi-Agent Coordination Example

**User asks:** *"When is registration and how much is the fee?"*

1. **Orchestrator** receives the question
2. **Analyzes** - This needs both calendar AND financial info
3. **Calls TWO agents** simultaneously:
   - Calendar Agent → Gets registration dates
   - Financial Agent → Gets fee information
4. **Combines responses** into one coherent answer
5. **Returns to user** → "Registration is Sept 1-15, 2024. Fees are..."

### Technology Stack

- **Frontend:** Streamlit (Python web framework)
- **AI Engine:** AWS Bedrock (Claude Haiku 3.5)
- **Agent Framework:** Strands Agents
- **Backend:** Python 3.11+
- **Data:** JSON (mock data for demo, can connect to real databases)

---

## 📁 Project Structure

```
strands_agents/
├── lautech_chatbot_app.py           # Web interface (Streamlit)
├── lautech_assistant_enhanced.py    # AI agents (7 specialist agents)
├── run_chatbot.sh                   # Quick start script
├── requirements_lautech.txt         # Dependencies
├── DEPLOYMENT_GUIDE.md              # Full deployment instructions
├── README_CHATBOT.md                # This file
└── README_LAUTECH.md                # Technical documentation
```

### Key Files

| File | Purpose | Who Needs It |
|------|---------|--------------|
| `lautech_chatbot_app.py` | Web interface | Everyone (this is the app) |
| `lautech_assistant_enhanced.py` | AI brain | Developers only |
| `run_chatbot.sh` | Easy startup | IT staff |
| `DEPLOYMENT_GUIDE.md` | Server setup | IT staff |
| `README_CHATBOT.md` | User guide | Students & staff |

---

## 🔧 Configuration

### Changing the AI Model

Edit `lautech_assistant_enhanced.py`:

```python
bedrock_model = BedrockModel(
    # Current: Claude Haiku (fast & cheap)
    model_id="us.anthropic.claude-3-5-haiku-20241022-v1:0",

    # Alternative: Claude Sonnet (more capable, slower)
    # model_id="us.anthropic.claude-sonnet-4-5-20250929-v1:0",

    temperature=0.7,
)
```

### Adding University Data

Replace mock data with real information:

```python
# In lautech_assistant_enhanced.py

# Connect to your database
import mysql.connector

def get_real_courses():
    db = mysql.connector.connect(
        host="your-db-host",
        user="your-username",
        password="your-password",
        database="lautech_db"
    )
    cursor = db.cursor()
    cursor.execute("SELECT * FROM courses")
    return cursor.fetchall()

# Use in agents...
```

### Customizing Appearance

Edit colors and styling in `lautech_chatbot_app.py`:

```python
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        # Change colors here
    }
</style>
""", unsafe_allow_html=True)
```

---

## 🌐 Deployment Options

### For Testing (Local)
```bash
./run_chatbot.sh
# Access at: http://localhost:8501
```

### For Small Campus (Single Server)
- Deploy on one server (EC2, VPS)
- Students access via campus network
- ~50 concurrent users
- Cost: ~$30-50/month

### For Full University (Production)
- Multiple servers with load balancer
- Public domain with HTTPS
- ~500+ concurrent users
- Cost: ~$200-300/month

**See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for complete instructions**

---

## 🔒 Privacy & Security

### Data Privacy
- ✅ Questions are processed by AWS Bedrock (secure, encrypted)
- ✅ No data is stored permanently
- ✅ Conversation history stays in browser session only
- ✅ Compliant with data protection standards

### Security Features
- 🔐 HTTPS encryption (when deployed with SSL)
- 🔐 AWS IAM role-based access
- 🔐 No hardcoded credentials
- 🔐 Rate limiting to prevent abuse

### Recommendations for Production
1. Add authentication (student login)
2. Enable audit logging
3. Set up monitoring and alerts
4. Regular security updates
5. Backup conversation data (if stored)

---

## 📊 Usage Statistics

After deployment, track:
- **Total questions asked**
- **Most common queries**
- **Response times**
- **User satisfaction**
- **Peak usage hours**

Add analytics to improve the service!

---

## 🐛 Troubleshooting

### "Unable to locate credentials"
**Solution:**
```bash
aws configure
# Then enter your AWS credentials
```

### App won't start
**Solution:**
```bash
# Check dependencies
pip install -r requirements_lautech.txt

# Check Python version (need 3.11+)
python3 --version
```

### Slow responses
**Possible causes:**
- Slow internet connection
- Many users at once
- Need larger server

**Solutions:**
- Upgrade server (EC2 instance type)
- Use faster AI model
- Add caching for common questions

### Error messages in chat
**Solution:**
- Check AWS credentials are valid
- Check internet connection
- Restart the application

---

## 💰 Cost Estimation

### Monthly Costs (Approximate)

**Small Deployment (50 concurrent users)**
- AWS EC2 t3.small: $15/month
- AWS Bedrock (500 queries/day): $45/month
- Data transfer: $5/month
- **Total: ~$65/month**

**Medium Deployment (200 concurrent users)**
- AWS EC2 t3.medium: $30/month
- AWS Bedrock (2000 queries/day): $180/month
- Load balancer: $20/month
- Data transfer: $10/month
- **Total: ~$240/month**

**Large Deployment (500+ users)**
- AWS EC2 t3.large (x2): $120/month
- AWS Bedrock (5000 queries/day): $450/month
- Load balancer + Auto-scaling: $50/month
- Data transfer: $30/month
- **Total: ~$650/month**

*Costs reduce significantly if using reserved instances or AWS education credits*

---

## 🚀 Future Enhancements

### Phase 1 (Current)
- ✅ 7 specialist agents
- ✅ Web chat interface
- ✅ Mock university data
- ✅ Multi-agent coordination

### Phase 2 (Planned)
- 🔜 WhatsApp bot integration
- 🔜 SMS notifications for deadlines
- 🔜 Voice input/output
- 🔜 Multi-language support (Yoruba, Igbo)

### Phase 3 (Future)
- 🔜 Real database integration
- 🔜 Student portal integration
- 🔜 Document upload and analysis
- 🔜 Personalized recommendations
- 🔜 Analytics dashboard for admin

### Phase 4 (Advanced)
- 🔜 Mobile app (iOS/Android)
- 🔜 Integration with course management system
- 🔜 AI-powered academic advising
- 🔜 Automated email responses

---

## 👥 Getting Help

### For Students
- 📧 **Email:** it-support@lautech.edu.ng
- 📱 **WhatsApp:** +234 XXX XXX XXXX
- 🌐 **Portal:** student.lautech.edu.ng

### For IT Staff
- 📖 **Documentation:** See DEPLOYMENT_GUIDE.md
- 💬 **Technical Support:** GitHub Issues
- 📹 **Video Tutorials:** [Coming soon]

---

## 📄 License

This project is developed for Ladoke Akintola University of Technology (LAUTECH).
See repository LICENSE file for details.

---

## 🙏 Acknowledgments

Built with:
- **AWS Bedrock** - AI model hosting
- **Anthropic Claude** - AI language model
- **Strands Agents** - Multi-agent framework
- **Streamlit** - Web interface
- **LAUTECH IT Team** - Support and feedback

---

## 📞 Contact

**Project Maintainer:** LAUTECH IT Department
**Email:** it-support@lautech.edu.ng
**Website:** www.lautech.edu.ng

---

<div align="center">

**🎓 Built for LAUTECH Students with ❤️**

*Making university information accessible to everyone, anytime, anywhere*

![LAUTECH](https://img.shields.io/badge/LAUTECH-University%20Assistant-green)
![Status](https://img.shields.io/badge/Status-Ready%20for%20Deployment-blue)
![AI](https://img.shields.io/badge/Powered%20by-AI-purple)

</div>
