# LAUTECH University: Transforming Student Services with AWS Agentic AI

*How we deployed an intelligent multi-agent assistant that handles 70% of student queries automatically*

---

## Executive Summary

LAUTECH (Ladoke Akintola University of Technology) needed to transform their student services to handle over 10,000 students with limited IT staff. We deployed an AI-powered multi-agent system using **Amazon Bedrock** and **AWS AgentCore** that provides 24/7 automated assistance for course information, fees, academic calendar, and hostel queries.

**Results:**
- **<3 second** response times
- **24/7** availability
- **~70%** reduction in routine query handling
- **$15-25/month** operational cost

---

## The Challenge

LAUTECH faced typical higher education challenges:

- **10,000+ students** asking repetitive questions
- **Limited IT staff** overwhelmed during peak registration
- **Inconsistent information** across departments
- **Students expect 24/7 support** like modern digital services

The university needed an intelligent system that could:
- Answer questions about courses, fees, schedules, and hostels
- Work around the clock without human intervention
- Provide accurate, up-to-date information from live databases
- Scale during high-demand periods (registration, exams)

---

## The Solution

We implemented an **Agentic AI system** using AWS's latest AI technologies:

### Architecture

```
┌─────────────────────────────────────────────────┐
│           Student Interfaces                     │
│     (Web Dashboard / WhatsApp / API)            │
└─────────────────┬───────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────┐
│           Amazon Bedrock AgentCore              │
│              (Orchestrator Agent)               │
├─────────────────────────────────────────────────┤
│  📚 Course  │  💰 Finance  │  📅 Calendar │ 🏠 Hostel │
│    Tool     │     Tool     │     Tool     │   Tool   │
├─────────────────────────────────────────────────┤
│          🛡️ Bedrock Guardrails                   │
│     (Content Safety & Responsible AI)           │
└─────────┬─────────────────────────────┬─────────┘
          │                             │
┌─────────▼─────────┐       ┌───────────▼─────────┐
│  Amazon RDS       │       │  AgentCore Memory   │
│  (PostgreSQL)     │       │  (STM + LTM)        │
└───────────────────┘       └─────────────────────┘
```

### AWS Services Used

| Service | Purpose |
|---------|---------|
| **Amazon Bedrock** | Claude 3.5 Haiku for natural language understanding |
| **Bedrock AgentCore** | Serverless agent runtime with auto-scaling |
| **Bedrock Guardrails** | Content filtering, PII protection, topic blocking |
| **Amazon RDS** | PostgreSQL database for university data |
| **AWS ECS Fargate** | Container hosting for web dashboards |
| **AWS Secrets Manager** | Secure credential storage |
| **Amazon CloudWatch** | Monitoring and observability |

---

## Technical Implementation

### Multi-Agent Pattern

We used the **Strands Agents SDK** (AWS's native agent framework) to implement an orchestrator pattern:

1. **Orchestrator Agent**: Routes queries to specialist tools
2. **Course Tool**: Retrieves course information from database
3. **Finance Tool**: Provides tuition and fee details
4. **Calendar Tool**: Returns academic calendar events
5. **Hostel Tool**: Lists accommodation options

### Responsible AI

We implemented comprehensive safety controls:

- **Bedrock Guardrails** with HIGH content filtering
- **Topic blocking** for political, religious, and off-topic queries
- **PII protection** to anonymize sensitive student data
- **Prompt injection defense** against adversarial inputs

### Security

- **IAM roles** with least-privilege access
- **AWS Secrets Manager** for database credentials
- **VPC security groups** for network isolation
- **RDS encryption** at rest and in transit

---

## Results

### Performance Metrics

| Metric | Before | After |
|--------|--------|-------|
| Response Time | Hours (email) | <3 seconds |
| Availability | Business hours | 24/7 |
| Query Handling | 100% manual | ~70% automated |
| Monthly Cost | N/A | ~$20/month |

### Student Feedback

> "I can get answers about my course fees at midnight before registration. No more waiting for the office to open." - Computer Science Student

> "The assistant knows about every course in the university. It even remembers what I asked before." - Engineering Student

---

## Why AWS for Agentic AI?

This project demonstrated AWS's leadership in agentic AI:

1. **Amazon Bedrock** provides access to top foundation models
2. **AgentCore** offers serverless agent deployment with built-in memory
3. **Strands SDK** simplifies agent development with Python
4. **Guardrails** ensure responsible AI out of the box
5. **Native Integration** - All services work seamlessly together

---

## Learn More

**Partner**: [Your Company Name]  
**AWS Partnership**: Agentic AI Consulting Services  
**Contact**: [Your Contact Information]

---

*This case study demonstrates our expertise in deploying production-grade Agentic AI solutions on AWS. We specialize in Amazon Bedrock, AgentCore, and Strands Agents SDK implementations.*

**Tags**: Amazon Bedrock, AgentCore, Strands Agents, Agentic AI, Higher Education, Claude 3.5, Responsible AI
