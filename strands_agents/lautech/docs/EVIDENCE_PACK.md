# LAUTECH AWS AI Competency Evidence Pack

## Submission Package Contents

This document lists all evidence files for the AWS AI Competency - Agentic AI Consulting Services application.

---

## 1. Architecture Documentation

| File | Description | For Requirement |
|------|-------------|-----------------|
| [PRODUCTION.md](./PRODUCTION.md) | Complete architecture guide with diagrams | DOC-001, AGAIPS-001, AGAIPS-004 |
| [README.md](../README.md) | Project overview and deployment details | PS-001 |

---

## 2. Security & Responsible AI

| File | Description | For Requirement |
|------|-------------|-----------------|
| [RESPONSIBLE_AI.md](./RESPONSIBLE_AI.md) | Safety controls, guardrails, testing | QCHK-005, AGAIPS-003 |
| [setup/setup_guardrails.py](../setup/setup_guardrails.py) | Bedrock Guardrails configuration code | QCHK-005 |

---

## 3. Seller Toolkit

| File | Description | For Requirement |
|------|-------------|-----------------|
| [SELLER_ONE_PAGER.md](./SELLER_ONE_PAGER.md) | Customer-facing one-pager | DOC-005 |
| [SELLER_PRESENTATION.md](./SELLER_PRESENTATION.md) | Customer presentation slides | DOC-005 |

---

## 4. Case Study Materials

| File | Description | For Requirement |
|------|-------------|-----------------|
| [CASE_STUDY_BLOG.md](./CASE_STUDY_BLOG.md) | Public case study for website | 2.2 Publicly Available Case Studies |
| [SELF_ASSESSMENT_GUIDE.md](./SELF_ASSESSMENT_GUIDE.md) | Text for spreadsheet fields | 3.1 Self-Assessment |

---

## 5. Technical Implementation

| File | Description | For Requirement |
|------|-------------|-----------------|
| [lautech_agentcore.py](../lautech_agentcore.py) | Main agent with guardrails | QCHK-001, QCHK-002, QCHK-005 |
| [db_utils.py](../db_utils.py) | Database utilities with Secrets Manager | QCHK-004 |
| [setup/deploy_ecs.py](../setup/deploy_ecs.py) | ECS deployment with security groups | QCHK-004, QCHK-006 |
| [setup/setup_monitoring.py](../setup/setup_monitoring.py) | CloudWatch dashboard | OPE-001 |

---

## 6. Data Documentation

| File | Description | For Requirement |
|------|-------------|-----------------|
| [DATA_GUIDE.md](./DATA_GUIDE.md) | Database schema and data structure | DOC-003 |
| [RDS_SETUP_COMPLETE.md](./RDS_SETUP_COMPLETE.md) | RDS configuration details | NETSEC-002 |

---

## PDF Conversion

Run this to create submission-ready PDFs:
```bash
python setup/convert_to_pdf.py
```

Output folder: `submission/`

---

## Quick Reference: AWS Resources

| Resource | Value |
|----------|-------|
| **AgentCore ARN** | `arn:aws:bedrock-agentcore:us-east-1:715841330456:runtime/lautech_agentcore-KLZaaW7AR6` |
| **Memory ID** | `lautech_agentcore_mem-yeGCqwG7EM` |
| **ECR Repository** | `715841330456.dkr.ecr.us-east-1.amazonaws.com/bedrock-agentcore-lautech_agentcore` |
| **RDS Endpoint** | `lautech-agentcore-db.c2x6a0cseynp.us-east-1.rds.amazonaws.com` |
| **Region** | `us-east-1` |

---

## Submission Checklist

- [ ] Convert all docs to PDF using `convert_to_pdf.py`
- [ ] Publish `CASE_STUDY_BLOG.md` to company website
- [ ] Fill Excel spreadsheet using `SELF_ASSESSMENT_GUIDE.md`
- [ ] Upload PDFs to Partner Central
- [ ] Attach architecture diagram image
- [ ] Add Case Study URL to Partner Central
