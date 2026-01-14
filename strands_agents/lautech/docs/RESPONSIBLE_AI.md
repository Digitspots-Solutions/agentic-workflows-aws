# LAUTECH Responsible AI Framework

## Overview

This document describes the Responsible AI controls implemented in the LAUTECH University Assistant to ensure safe, ethical, and trustworthy AI operations.

**AWS AI Competency Reference**: QCHK-005, AGAIPS-003

---

## 1. Safety Controls

### Amazon Bedrock Guardrails

| Control Type | Implementation | Purpose |
|-------------|---------------|---------|
| **Content Filtering** | HIGH strength filters for sexual, violence, hate, misconduct | Prevent harmful content generation |
| **Topic Blocking** | Political, religious debates, illegal activities, personal advice | Keep responses on-topic and appropriate |
| **PII Protection** | Anonymize emails/phones, block financial data | Protect student privacy |
| **Word Filters** | Block jailbreak attempts and profanity | Prevent prompt injection attacks |
| **Prompt Attack Defense** | HIGH strength filter | Protect against adversarial inputs |

### Blocked Topics

1. **Political Content** - No political party discussions, election opinions
2. **Religious Debates** - No religious comparisons or proselytizing
3. **Illegal Activities** - No exam cheating, document forgery, hacking assistance
4. **Personal Advice** - No medical, legal, or relationship advice

---

## 2. Input/Output Validation

### Input Validation
- Pre-processing through Bedrock Guardrails before model inference
- Query sanitization to prevent SQL injection in database tools
- Session ID and Actor ID validation for user tracking

### Output Validation
- Post-processing through Bedrock Guardrails after model response
- Factual grounding through database-backed tool responses
- System prompt instructions for accurate information delivery

---

## 3. Safety Assessment

### Pre-Deployment Testing

| Test Case | Status | Result |
|-----------|--------|--------|
| Normal university queries | ✅ Pass | Accurate responses |
| Political content requests | ✅ Pass | Blocked with appropriate message |
| Jailbreak attempts | ✅ Pass | Blocked with appropriate message |
| PII in responses | ✅ Pass | Anonymized or blocked |
| Offensive language | ✅ Pass | Filtered out |

### Testing Script

Run guardrails tests with:
```bash
python setup/setup_guardrails.py
```

---

## 4. Monitoring & Continuous Improvement

### CloudWatch Metrics
- Guardrail invocation counts
- Block rate by category
- Response latency with guardrails

### Feedback Loop
1. Monitor blocked requests for false positives
2. Review user feedback on response quality
3. Update guardrail configuration monthly
4. Retrain/adjust topic definitions as needed

---

## 5. User Communication

### Blocked Request Messages

**Input Blocked**:
> "I apologize, but I cannot assist with that request. I am the LAUTECH University Assistant, designed to help with academic information, course registration, fees, and campus services. Please ask me about university-related topics."

**Output Blocked**:
> "I apologize, but I cannot provide that information. Let me help you with university-related queries instead. You can ask about courses, fees, academic calendar, or hostel information."

---

## 6. Compliance Summary

| Requirement | Control | Status |
|------------|---------|--------|
| QCHK-005 Responsible AI | Bedrock Guardrails | ✅ Implemented |
| AGAIPS-003 Safety Assessment | This document | ✅ Documented |
| Content Moderation | Content filters (HIGH) | ✅ Enabled |
| PII Protection | Sensitive info filters | ✅ Enabled |
| Prompt Injection Defense | Prompt attack filter | ✅ Enabled |

---

## 7. Configuration Reference

### Environment Variables

```bash
# Guardrail Configuration
BEDROCK_GUARDRAIL_ID=<guardrail-id>
BEDROCK_GUARDRAIL_VERSION=<version>
```

### Deployment Command

```bash
agentcore launch \
  --env USE_POSTGRES=true \
  --env DB_SECRET_NAME=lautech/rds/credentials \
  --env BEDROCK_GUARDRAIL_ID=<guardrail-id> \
  --env BEDROCK_GUARDRAIL_VERSION=1 \
  --env AWS_REGION=us-east-1
```

---

*Document Version: 1.0*  
*Last Updated: January 2026*  
*AWS AI Competency: Agentic AI Consulting Services*
