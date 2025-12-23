# 🚀 LAUTECH Production Deployment Guide

**Complete guide to deploying the LAUTECH system in production**

---

## 📋 Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Database Migration (SQLite → RDS)](#database-migration)
3. [Monitoring & Logging](#monitoring--logging)
4. [Backup & Recovery](#backup--recovery)
5. [Security Hardening](#security-hardening)
6. [Rate Limiting](#rate-limiting)
7. [Performance Optimization](#performance-optimization)
8. [High Availability](#high-availability)
9. [Cost Optimization](#cost-optimization)
10. [Deployment Checklist](#deployment-checklist)

---

## 🏗️ Architecture Overview

### Production Architecture

```
                     ┌─────────────────┐
                     │   CloudFront    │
                     │   (CDN + WAF)   │
                     └────────┬────────┘
                              │
                 ┌────────────┴────────────┐
                 │                         │
        ┌────────▼────────┐      ┌────────▼────────┐
        │  ALB (Students) │      │  ALB (Staff)    │
        │  Port 8501      │      │  Port 8502      │
        └────────┬────────┘      └────────┬────────┘
                 │                         │
        ┌────────▼────────┐      ┌────────▼────────┐
        │  ECS/EC2        │      │  ECS/EC2        │
        │  Web Dashboard  │      │  Admin Panel    │
        └────────┬────────┘      └────────┬────────┘
                 │                         │
                 └────────────┬────────────┘
                              │
                   ┌──────────▼──────────┐
                   │  AWS AgentCore      │
                   │  (Lambda)           │
                   └──────────┬──────────┘
                              │
                   ┌──────────▼──────────┐
                   │  RDS PostgreSQL     │
                   │  (Multi-AZ)         │
                   └─────────────────────┘
                              │
                   ┌──────────▼──────────┐
                   │  S3 (Backups)       │
                   └─────────────────────┘

Monitoring: CloudWatch + X-Ray
Secrets: AWS Secrets Manager
DNS: Route 53
```

### Components

| Component | Development | Production |
|-----------|------------|------------|
| **Database** | SQLite | RDS PostgreSQL (Multi-AZ) |
| **Compute** | Local | ECS Fargate / EC2 Auto Scaling |
| **Agent Runtime** | Local Strands | AWS AgentCore (Lambda) |
| **File Storage** | Local disk | S3 |
| **Monitoring** | Logs | CloudWatch + X-Ray + CloudTrail |
| **Secrets** | .env files | AWS Secrets Manager |
| **Load Balancer** | None | Application Load Balancer |
| **CDN** | None | CloudFront |
| **Backups** | Manual | Automated (S3 + RDS snapshots) |

---

## 🗄️ Database Migration

### Step 1: Create RDS PostgreSQL Instance

```bash
# Create RDS instance
aws rds create-db-instance \
  --db-instance-identifier lautech-db-prod \
  --db-instance-class db.t3.medium \
  --engine postgres \
  --master-username lautechadmin \
  --master-user-password $(aws secretsmanager get-secret-value --secret-id lautech/db/master --query SecretString --output text) \
  --allocated-storage 100 \
  --storage-type gp3 \
  --storage-encrypted \
  --multi-az \
  --db-name lautech_db \
  --vpc-security-group-ids sg-xxxxxxxxx \
  --db-subnet-group-name lautech-db-subnet-group \
  --backup-retention-period 30 \
  --preferred-backup-window "03:00-04:00" \
  --preferred-maintenance-window "sun:04:00-sun:05:00" \
  --enable-cloudwatch-logs-exports '["postgresql"]' \
  --deletion-protection \
  --tags Key=Environment,Value=Production Key=Project,Value=LAUTECH
```

### Step 2: Export SQLite Data

```python
# export_sqlite_to_csv.py
import sqlite3
import csv
from pathlib import Path

DB_PATH = "lautech_data.db"
OUTPUT_DIR = Path("migration_export")
OUTPUT_DIR.mkdir(exist_ok=True)

def export_table(table_name):
    """Export table to CSV"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Get data
    cursor.execute(f"SELECT * FROM {table_name}")
    rows = cursor.fetchall()

    # Get column names
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = [col[1] for col in cursor.fetchall()]

    # Write CSV
    csv_path = OUTPUT_DIR / f"{table_name}.csv"
    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(columns)
        writer.writerows(rows)

    print(f"✅ Exported {len(rows)} rows from {table_name} to {csv_path}")
    conn.close()

# Export all tables
tables = ['courses', 'fees', 'academic_calendar', 'hostels']
for table in tables:
    export_table(table)

print("\n✅ Export complete! Files in migration_export/")
```

### Step 3: Import to PostgreSQL

```python
# import_to_postgres.py
import psycopg2
import csv
import os
from pathlib import Path

# Get RDS credentials from Secrets Manager
def get_db_credentials():
    import boto3
    import json

    client = boto3.client('secretsmanager')
    secret = client.get_secret_value(SecretId='lautech/db/credentials')
    return json.loads(secret['SecretString'])

# Database connection
creds = get_db_credentials()
conn = psycopg2.connect(
    dbname=creds['dbname'],
    host=creds['host'],
    user=creds['username'],
    password=creds['password'],
    port=creds.get('port', 5432)
)
cursor = conn.cursor()

# Create tables
cursor.execute("""
    CREATE TABLE IF NOT EXISTS courses (
        code VARCHAR(20) PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        credits INTEGER,
        prerequisites TEXT,
        description TEXT,
        semester VARCHAR(50),
        lecturer VARCHAR(255),
        department VARCHAR(255),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
""")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS fees (
        id SERIAL PRIMARY KEY,
        level VARCHAR(50) NOT NULL,
        amount INTEGER NOT NULL,
        fee_type VARCHAR(50),
        session VARCHAR(20),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
""")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS academic_calendar (
        id SERIAL PRIMARY KEY,
        event_type VARCHAR(100) NOT NULL,
        event_date DATE NOT NULL,
        semester VARCHAR(50),
        session VARCHAR(20),
        description TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
""")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS hostels (
        id SERIAL PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        gender VARCHAR(20),
        capacity INTEGER,
        status VARCHAR(50),
        facilities TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
""")

# Create indexes
cursor.execute("CREATE INDEX IF NOT EXISTS idx_courses_department ON courses(department)")
cursor.execute("CREATE INDEX IF NOT EXISTS idx_fees_level ON fees(level)")
cursor.execute("CREATE INDEX IF NOT EXISTS idx_calendar_date ON academic_calendar(event_date)")
cursor.execute("CREATE INDEX IF NOT EXISTS idx_hostels_status ON hostels(status)")

conn.commit()

# Import data
def import_csv(table_name, csv_path):
    """Import CSV data to PostgreSQL"""
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)

        if table_name == 'courses':
            for row in rows:
                cursor.execute("""
                    INSERT INTO courses (code, name, credits, prerequisites, description, semester, lecturer, department)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (code) DO UPDATE SET
                        name=EXCLUDED.name,
                        credits=EXCLUDED.credits,
                        prerequisites=EXCLUDED.prerequisites,
                        description=EXCLUDED.description,
                        semester=EXCLUDED.semester,
                        lecturer=EXCLUDED.lecturer,
                        department=EXCLUDED.department,
                        updated_at=CURRENT_TIMESTAMP
                """, (row['code'], row['name'], row['credits'], row['prerequisites'],
                      row['description'], row['semester'], row['lecturer'], row['department']))

        # Similar for other tables...
        conn.commit()
        print(f"✅ Imported {len(rows)} rows to {table_name}")

# Import all tables
MIGRATION_DIR = Path("migration_export")
tables = ['courses', 'fees', 'academic_calendar', 'hostels']
for table in tables:
    csv_path = MIGRATION_DIR / f"{table}.csv"
    if csv_path.exists():
        import_csv(table, csv_path)

print("\n✅ Migration complete!")
conn.close()
```

### Step 4: Update Application Code

```python
# database.py - New database abstraction layer
import os
import psycopg2
from psycopg2.extras import RealDictCursor
import boto3
import json

def get_db_connection():
    """Get database connection (supports both SQLite and PostgreSQL)"""

    # Check environment
    if os.getenv('ENVIRONMENT') == 'production':
        # PostgreSQL (RDS)
        client = boto3.client('secretsmanager')
        secret = client.get_secret_value(SecretId='lautech/db/credentials')
        creds = json.loads(secret['SecretString'])

        return psycopg2.connect(
            dbname=creds['dbname'],
            host=creds['host'],
            user=creds['username'],
            password=creds['password'],
            port=creds.get('port', 5432),
            cursor_factory=RealDictCursor
        )
    else:
        # SQLite (Development)
        import sqlite3
        conn = sqlite3.connect('lautech_data.db')
        conn.row_factory = sqlite3.Row
        return conn

# Update lautech_agentcore.py to use this connection
```

---

## 📊 Monitoring & Logging

### CloudWatch Setup

```python
# cloudwatch_logger.py
import boto3
import json
from datetime import datetime

class CloudWatchLogger:
    def __init__(self, log_group='/aws/lautech', log_stream='app'):
        self.client = boto3.client('logs')
        self.log_group = log_group
        self.log_stream = log_stream

        # Create log group and stream if needed
        try:
            self.client.create_log_group(logGroupName=log_group)
        except:
            pass

        try:
            self.client.create_log_stream(
                logGroupName=log_group,
                logStreamName=log_stream
            )
        except:
            pass

    def log(self, level, message, metadata=None):
        """Send log to CloudWatch"""
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': level,
            'message': message,
            'metadata': metadata or {}
        }

        self.client.put_log_events(
            logGroupName=self.log_group,
            logStreamName=self.log_stream,
            logEvents=[{
                'timestamp': int(datetime.now().timestamp() * 1000),
                'message': json.dumps(log_entry)
            }]
        )

# Usage in agents
logger = CloudWatchLogger()
logger.log('INFO', 'Query processed', {'query': user_input, 'agent': 'academic'})
```

### Metrics Collection

```python
# metrics.py
import boto3
from datetime import datetime

class MetricsCollector:
    def __init__(self):
        self.cloudwatch = boto3.client('cloudwatch')
        self.namespace = 'LAUTECH/Assistant'

    def record_query(self, agent_name, response_time_ms, success=True):
        """Record query metrics"""
        self.cloudwatch.put_metric_data(
            Namespace=self.namespace,
            MetricData=[
                {
                    'MetricName': 'QueryCount',
                    'Value': 1,
                    'Unit': 'Count',
                    'Dimensions': [
                        {'Name': 'Agent', 'Value': agent_name},
                        {'Name': 'Status', 'Value': 'Success' if success else 'Failed'}
                    ]
                },
                {
                    'MetricName': 'ResponseTime',
                    'Value': response_time_ms,
                    'Unit': 'Milliseconds',
                    'Dimensions': [
                        {'Name': 'Agent', 'Value': agent_name}
                    ]
                }
            ]
        )

    def record_error(self, error_type, message):
        """Record error metrics"""
        self.cloudwatch.put_metric_data(
            Namespace=self.namespace,
            MetricData=[{
                'MetricName': 'Errors',
                'Value': 1,
                'Unit': 'Count',
                'Dimensions': [
                    {'Name': 'ErrorType', 'Value': error_type}
                ]
            }]
        )

# Usage
metrics = MetricsCollector()
start = time.time()
try:
    response = agent(query)
    metrics.record_query('academic', (time.time() - start) * 1000, True)
except Exception as e:
    metrics.record_query('academic', (time.time() - start) * 1000, False)
    metrics.record_error(type(e).__name__, str(e))
```

### CloudWatch Dashboard

```json
{
  "widgets": [
    {
      "type": "metric",
      "properties": {
        "metrics": [
          ["LAUTECH/Assistant", "QueryCount", {"stat": "Sum"}]
        ],
        "period": 300,
        "stat": "Sum",
        "region": "us-east-1",
        "title": "Total Queries"
      }
    },
    {
      "type": "metric",
      "properties": {
        "metrics": [
          ["LAUTECH/Assistant", "ResponseTime", {"stat": "Average"}]
        ],
        "period": 300,
        "stat": "Average",
        "region": "us-east-1",
        "title": "Average Response Time (ms)"
      }
    },
    {
      "type": "metric",
      "properties": {
        "metrics": [
          ["LAUTECH/Assistant", "Errors", {"stat": "Sum"}]
        ],
        "period": 300,
        "stat": "Sum",
        "region": "us-east-1",
        "title": "Error Count"
      }
    }
  ]
}
```

---

## 💾 Backup & Recovery

### Automated RDS Snapshots

```bash
# Already enabled in RDS creation:
# --backup-retention-period 30
# --preferred-backup-window "03:00-04:00"
```

### Daily S3 Backups

```python
# backup_to_s3.py
import boto3
import psycopg2
import json
from datetime import datetime
from pathlib import Path

def backup_database_to_s3():
    """Backup database to S3"""

    # Get credentials
    sm = boto3.client('secretsmanager')
    secret = sm.get_secret_value(SecretId='lautech/db/credentials')
    creds = json.loads(secret['SecretString'])

    # Connect to database
    conn = psycopg2.connect(
        dbname=creds['dbname'],
        host=creds['host'],
        user=creds['username'],
        password=creds['password']
    )

    # Export to SQL dump
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = f"lautech_backup_{timestamp}.sql"

    os.system(f"""
        pg_dump \
          -h {creds['host']} \
          -U {creds['username']} \
          -d {creds['dbname']} \
          -F p \
          -f {backup_file}
    """)

    # Upload to S3
    s3 = boto3.client('s3')
    bucket = 'lautech-backups-prod'
    s3_key = f"database/{timestamp}/{backup_file}"

    s3.upload_file(backup_file, bucket, s3_key)

    # Add lifecycle policy for old backups
    s3.put_bucket_lifecycle_configuration(
        Bucket=bucket,
        LifecycleConfiguration={
            'Rules': [{
                'Id': 'DeleteOldBackups',
                'Status': 'Enabled',
                'Expiration': {'Days': 90},
                'Prefix': 'database/'
            }]
        }
    )

    print(f"✅ Backup uploaded to s3://{bucket}/{s3_key}")

    # Clean up local file
    os.remove(backup_file)

    conn.close()

if __name__ == '__main__':
    backup_database_to_s3()
```

### Lambda Function for Automated Backups

```python
# lambda_backup.py
import json
import boto3
import os

def lambda_handler(event, context):
    """Lambda function to trigger daily backups"""

    # Trigger backup script
    ecs = boto3.client('ecs')

    response = ecs.run_task(
        cluster='lautech-cluster',
        taskDefinition='lautech-backup-task',
        launchType='FARGATE',
        networkConfiguration={
            'awsvpcConfiguration': {
                'subnets': os.environ['SUBNET_IDS'].split(','),
                'securityGroups': [os.environ['SECURITY_GROUP']],
                'assignPublicIp': 'DISABLED'
            }
        }
    )

    return {
        'statusCode': 200,
        'body': json.dumps('Backup initiated')
    }
```

### EventBridge Schedule

```bash
# Create EventBridge rule for daily backups
aws events put-rule \
  --name lautech-daily-backup \
  --schedule-expression "cron(0 3 * * ? *)" \
  --state ENABLED

aws events put-targets \
  --rule lautech-daily-backup \
  --targets "Id"="1","Arn"="arn:aws:lambda:us-east-1:ACCOUNT:function:lautech-backup"
```

---

## 🔒 Security Hardening

### WAF Rules

```json
{
  "Name": "LAUTECH-WAF",
  "Rules": [
    {
      "Name": "RateLimitRule",
      "Priority": 1,
      "Statement": {
        "RateBasedStatement": {
          "Limit": 2000,
          "AggregateKeyType": "IP"
        }
      },
      "Action": {"Block": {}},
      "VisibilityConfig": {
        "SampledRequestsEnabled": true,
        "CloudWatchMetricsEnabled": true,
        "MetricName": "RateLimit"
      }
    },
    {
      "Name": "GeoBlockRule",
      "Priority": 2,
      "Statement": {
        "NotStatement": {
          "Statement": {
            "GeoMatchStatement": {
              "CountryCodes": ["NG"]
            }
          }
        }
      },
      "Action": {"Block": {}},
      "VisibilityConfig": {
        "SampledRequestsEnabled": true,
        "CloudWatchMetricsEnabled": true,
        "MetricName": "GeoBlock"
      }
    }
  ]
}
```

### Secrets Manager

```bash
# Store database credentials
aws secretsmanager create-secret \
  --name lautech/db/credentials \
  --secret-string '{
    "username": "lautechadmin",
    "password": "SECURE_PASSWORD_HERE",
    "host": "lautech-db-prod.xxxxxxxxx.us-east-1.rds.amazonaws.com",
    "port": 5432,
    "dbname": "lautech_db"
  }'

# Store admin panel credentials
aws secretsmanager create-secret \
  --name lautech/admin/credentials \
  --secret-string '{
    "admin_users": [
      {"username": "admin1", "password_hash": "..."},
      {"username": "admin2", "password_hash": "..."}
    ]
  }'
```

### VPC Security Groups

```bash
# Database security group (RDS)
aws ec2 create-security-group \
  --group-name lautech-db-sg \
  --description "LAUTECH Database SG" \
  --vpc-id vpc-xxxxxxxxx

# Allow inbound from application security group only
aws ec2 authorize-security-group-ingress \
  --group-id sg-db-xxxxxxxxx \
  --protocol tcp \
  --port 5432 \
  --source-group sg-app-xxxxxxxxx
```

---

## ⏱️ Rate Limiting

### Application-Level Rate Limiting

```python
# rate_limiter.py
from functools import wraps
import time
from collections import defaultdict

class RateLimiter:
    def __init__(self, max_requests=100, window_seconds=60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = defaultdict(list)

    def is_allowed(self, user_id):
        """Check if request is allowed"""
        now = time.time()
        window_start = now - self.window_seconds

        # Remove old requests
        self.requests[user_id] = [
            req_time for req_time in self.requests[user_id]
            if req_time > window_start
        ]

        # Check limit
        if len(self.requests[user_id]) >= self.max_requests:
            return False

        # Add new request
        self.requests[user_id].append(now)
        return True

# Decorator
limiter = RateLimiter(max_requests=100, window_seconds=60)

def rate_limit(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        user_id = kwargs.get('session_id', 'default')

        if not limiter.is_allowed(user_id):
            raise Exception("Rate limit exceeded. Please try again later.")

        return func(*args, **kwargs)

    return wrapper

# Usage in AgentCore
@app.entrypoint
@rate_limit
def lautech_assistant(payload):
    # ... agent logic
    pass
```

---

## 🎯 Deployment Checklist

### Pre-Deployment

- [ ] All code reviewed and tested locally
- [ ] Database migration scripts tested
- [ ] RDS instance created and configured
- [ ] Data migrated from SQLite to PostgreSQL
- [ ] Secrets stored in Secrets Manager
- [ ] IAM roles and policies configured
- [ ] Security groups configured
- [ ] VPC and subnets set up

### Deployment

- [ ] AgentCore agent deployed to production
- [ ] Web dashboards deployed to ECS/EC2
- [ ] Load balancers configured
- [ ] CloudFront distribution created
- [ ] Route 53 DNS configured
- [ ] SSL certificates installed
- [ ] WAF rules enabled
- [ ] CloudWatch dashboards created
- [ ] Alarms configured
- [ ] Backup automation enabled

### Post-Deployment

- [ ] Smoke tests passed
- [ ] Load testing completed
- [ ] Monitoring dashboards showing data
- [ ] Backups verified
- [ ] Documentation updated
- [ ] Staff trained
- [ ] Support procedures documented
- [ ] Rollback plan tested

---

## 💰 Cost Estimation (Monthly)

| Service | Configuration | Cost |
|---------|--------------|------|
| **RDS PostgreSQL** | db.t3.medium, Multi-AZ, 100GB | ~$130 |
| **AgentCore** | Lambda + Runtime | ~$50 |
| **Bedrock (Claude)** | Haiku, 1000 queries/day | ~$90 |
| **ECS Fargate** | 2 tasks (0.5 vCPU, 1GB each) | ~$35 |
| **Application Load Balancer** | Standard | ~$22 |
| **CloudFront** | 100GB transfer | ~$8 |
| **S3 (Backups)** | 50GB storage | ~$1 |
| **CloudWatch** | Logs + Metrics | ~$15 |
| **Secrets Manager** | 2 secrets | ~$1 |
| **Route 53** | Hosted zone + queries | ~$1 |
| **WAF** | Basic rules | ~$10 |
| **Total** | | **~$363/month** |

### Cost Optimization Tips

1. **Use Reserved Instances** for RDS (save 30-40%)
2. **Enable RDS auto-scaling** based on usage
3. **Use Spot Instances** for non-critical workloads
4. **Implement caching** to reduce Bedrock calls
5. **Archive old backups** to Glacier
6. **Right-size resources** based on actual usage

---

**Ready for production!** 🚀

See individual implementation files for detailed code.
