# LAUTECH Student Query Router - Multi-Agent System

A demonstration of multi-agent coordination using the Strands framework and AWS Bedrock.

## 🎯 What This Demonstrates

This project showcases a **multi-agent system** where:

1. **Specialist Agents** are implemented as `@tool` functions
2. An **Orchestrator Agent** intelligently routes student queries to the right specialists
3. Multiple agents can collaborate to answer complex queries

### Agents:

- **📚 Academic Agent** - Handles course information, prerequisites, and schedules
- **📅 Calendar Agent** - Handles registration dates, deadlines, and academic calendar
- **🎯 Orchestrator Agent** - Routes queries to appropriate agents and combines responses

## 🏗️ Architecture Pattern: Agents as Tools

```python
# Each specialist agent is a @tool function
@tool
def get_course_info(query: str) -> str:
    """Academic Agent - handles course queries"""
    agent = Agent(
        system_prompt=ACADEMIC_AGENT_PROMPT,
        model=bedrock_model,
    )
    return str(agent(query))

# Orchestrator has specialist agents as its tools
orchestrator = Agent(
    system_prompt=ORCHESTRATOR_PROMPT,
    tools=[get_course_info, get_schedule_info],
    model=bedrock_model,
)
```

### How It Works:

1. **Student asks a question** → Sent to Orchestrator
2. **Orchestrator analyzes the query** → Decides which specialist(s) to call
3. **Specialist agent(s) respond** → Each with domain-specific knowledge
4. **Orchestrator combines responses** → Returns comprehensive answer

## 📊 Demo Queries

The demo tests three scenarios:

### 1️⃣ Calendar-Only Query
**Query:** "When is registration for the upcoming semester?"
**Agent Used:** Calendar Agent only
**Tests:** Single-agent routing

### 2️⃣ Course-Only Query
**Query:** "What courses can I take after completing CSC201?"
**Agent Used:** Academic Agent only
**Tests:** Single-agent routing with prerequisite logic

### 3️⃣ Multi-Agent Query
**Query:** "When does registration start and what courses are available in the first semester?"
**Agent Used:** BOTH Calendar + Academic Agents
**Tests:** Multi-agent coordination and response combination

## 🚀 Running the Demo

### Prerequisites

1. **Python 3.12+**
2. **AWS Credentials** configured with Bedrock access
3. **Strands framework** installed

### Setup

```bash
# 1. Install dependencies
pip install strands-agents boto3

# 2. Configure AWS credentials (one of these methods):

# Option A: AWS CLI
aws configure

# Option B: Environment variables
export AWS_ACCESS_KEY_ID="your-access-key"
export AWS_SECRET_ACCESS_KEY="your-secret-key"
export AWS_DEFAULT_REGION="us-east-1"

# Option C: AWS credentials file (~/.aws/credentials)
[default]
aws_access_key_id = your-access-key
aws_secret_access_key = your-secret-key
region = us-east-1
```

### Run the Demo

```bash
python strands_agents/lautech_student_assistant.py
```

### Expected Output

```
================================================================================
LAUTECH Student Query Router - Multi-Agent System Demo
================================================================================

This demo shows how the Orchestrator routes queries to specialist agents:
  📚 Academic Agent - Course info, prerequisites, schedules
  📅 Calendar Agent - Registration dates, deadlines, calendar
  🎯 Orchestrator - Routes queries and combines responses

────────────────────────────────────────────────────────────────────────────────

📝 TEST QUERY 1 (Pure calendar question)
Expected: Calendar Agent only
────────────────────────────────────────────────────────────────────────────────

Student Question: "When is registration for the upcoming semester?"

🤖 Response:
[Calendar Agent provides registration dates...]

⏱️  Response time: X.XX seconds

[... continues with TEST QUERY 2 and 3 ...]
```

## 📁 Mock Data

The system uses hardcoded data for demonstration:

### Courses Available:
- **CSC201** - Computer Programming II
- **CSC301** - Database Management Systems (requires CSC201)
- **CSC302** - Operating Systems (requires CSC201)
- **CSC303** - Web Programming (requires CSC201)
- **MTH301** - Discrete Mathematics
- **MTH302** - Numerical Analysis (requires MTH201, CSC201)

### Academic Calendar:
- **2024/2025 First Semester**
  - Registration: Sept 1-15, 2024
  - Semester: Sept 16 - Dec 20, 2024
  - Exams: Jan 6-20, 2025

- **2024/2025 Second Semester**
  - Registration: Feb 1-15, 2025
  - Semester: Feb 16 - June 15, 2025
  - Exams: June 20 - July 10, 2025

## 🔧 Customization

### Add New Courses
Edit the `COURSE_CATALOG` dictionary in `lautech_student_assistant.py`:

```python
COURSE_CATALOG = {
    "CSC401": {
        "name": "Machine Learning",
        "credits": 4,
        "prerequisites": ["CSC301", "MTH301"],
        "description": "Introduction to ML algorithms and applications",
        "semester": "First Semester"
    },
    # ... add more courses
}
```

### Add New Agent Types
Create a new `@tool` function and add it to the orchestrator:

```python
@tool
def get_financial_info(query: str) -> str:
    """Financial Agent - handles tuition, fees, payment info"""
    # ... implementation
    return str(response)

# Add to orchestrator
orchestrator = Agent(
    system_prompt=ORCHESTRATOR_PROMPT,
    tools=[get_course_info, get_schedule_info, get_financial_info],
    model=bedrock_model,
)
```

### Switch to Different Model
Change the model ID in `bedrock_model`:

```python
bedrock_model = BedrockModel(
    # Use Haiku (faster, cheaper)
    model_id="us.anthropic.claude-3-5-haiku-20241022-v1:0",

    # Or use Sonnet (more capable)
    # model_id="us.anthropic.claude-sonnet-4-5-20250929-v1:0",

    temperature=0.7,
)
```

## 🧪 Testing Individual Agents

You can test agents independently:

```python
from lautech_student_assistant import get_course_info, get_schedule_info

# Test Academic Agent directly
response = get_course_info("What are the prerequisites for CSC301?")
print(response)

# Test Calendar Agent directly
response = get_schedule_info("When does the semester start?")
print(response)
```

## 🎓 Key Learning Points

### Multi-Agent Patterns
- ✅ **Separation of Concerns** - Each agent specializes in one domain
- ✅ **Composability** - Agents can be combined via the orchestrator
- ✅ **Reusability** - `@tool` functions can be used independently or together
- ✅ **Scalability** - Easy to add new specialist agents

### Coordination Strategies
- **Single-Agent Routing** - Simple queries go to one specialist
- **Multi-Agent Coordination** - Complex queries use multiple specialists
- **Response Combination** - Orchestrator merges responses coherently

### AWS Bedrock Integration
- **Managed AI Models** - No infrastructure management needed
- **Claude Models** - Haiku for speed/cost, Sonnet for capability
- **Streaming Responses** - Real-time response generation

## 🚀 Next Steps

### 1. Deploy to AWS Lambda
Use AWS Lambda to run agents as serverless functions:
- Each agent as a separate Lambda function
- API Gateway for REST endpoints
- DynamoDB for persistent data

### 2. Add Real Data Sources
Replace mock data with:
- Database queries (RDS, DynamoDB)
- External APIs (Student Information System)
- Document retrieval (Knowledge bases)

### 3. Enhance with Tools
Add MCP tools to agents:
- File system access for student records
- Database queries for live data
- External API calls for integrations

### 4. Build UI
Create interfaces for students:
- Web chatbot (React + API)
- Slack/Discord bot
- WhatsApp integration
- SMS notifications

### 5. Production Hardening
- Add error handling and retries
- Implement rate limiting
- Add logging and monitoring (CloudWatch)
- Set up authentication/authorization
- Cache frequently requested information

## 📚 Further Reading

- [Strands Agents Documentation](https://github.com/awslabs/strands-agents)
- [AWS Bedrock Documentation](https://docs.aws.amazon.com/bedrock/)
- [Multi-Agent Systems Patterns](https://aws.amazon.com/blogs/machine-learning/)
- [MCP (Model Context Protocol)](https://modelcontextprotocol.io/)

## 🤝 Contributing

This is a demonstration project for LAUTECH. To extend:

1. Fork the repository
2. Add new agents or features
3. Test with real LAUTECH data
4. Deploy to production AWS infrastructure

## 📄 License

See repository LICENSE file.

---

**Built with ❤️ for LAUTECH using AWS Bedrock and Strands Agents**
