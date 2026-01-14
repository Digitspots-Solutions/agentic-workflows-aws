# 📱 LAUTECH WhatsApp Bot Setup Guide

**Let students interact with LAUTECH Assistant via WhatsApp**

---

## 🎯 Overview

The WhatsApp bot allows students to:
- Ask questions about courses, fees, registration, hostels
- Get instant responses via WhatsApp
- No app installation required
- Works on any phone with WhatsApp

**Example conversation:**
```
Student: When is registration?
Bot: 📅 Registration for 2024/2025 First Semester:
     • Start: September 1, 2024
     • End: September 15, 2024
     • Late registration: September 16-30 (with penalty)
```

---

## 🚀 Quick Start

### Step 1: Twilio Account Setup

1. **Create Twilio account** (free trial available)
   - Go to: https://www.twilio.com/try-twilio
   - Sign up and verify your phone number

2. **Get credentials**
   ```bash
   # From https://console.twilio.com/
   TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   TWILIO_AUTH_TOKEN=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   ```

3. **Enable WhatsApp Sandbox** (for testing)
   - Go to: https://console.twilio.com/us1/develop/sms/try-it-out/whatsapp-learn
   - Send "join <your-sandbox-code>" to the Twilio WhatsApp number
   - You'll get: `whatsapp:+14155238886` (sandbox number)

4. **For production: Request WhatsApp Business number**
   - Apply for WhatsApp Business API access
   - Get your own WhatsApp number: `whatsapp:+234XXXXXXXXXX`

### Step 2: Install Dependencies

```bash
cd strands_agents/lautech

# Install Python packages
pip install flask twilio boto3

# Or use requirements
pip install -r requirements_whatsapp.txt
```

### Step 3: Configure Environment

```bash
# Set credentials
export TWILIO_ACCOUNT_SID='ACxxxxxxxxxx'
export TWILIO_AUTH_TOKEN='xxxxxxxxxxxxxxxx'
export TWILIO_WHATSAPP_NUMBER='whatsapp:+14155238886'  # Twilio sandbox

# AgentCore configuration
export LAUTECH_AGENT_ID='lautech_agentcore-U7qNy1GPsE'
export AWS_ACCESS_KEY_ID='your-aws-key'
export AWS_SECRET_ACCESS_KEY='your-aws-secret'
export AWS_DEFAULT_REGION='us-east-1'
```

### Step 4: Test Locally

```bash
# Test agent connection
python3 whatsapp_bot.py test

# Run bot server
python3 whatsapp_bot.py
```

Output:
```
LAUTECH WhatsApp Bot
============================================================
✅ Twilio WhatsApp: whatsapp:+14155238886
✅ Agent ID: lautech_agentcore-U7qNy1GPsE

🚀 Starting server...
📱 Webhook URL: http://your-server/webhook
```

### Step 5: Expose Webhook (for testing)

```bash
# Option 1: ngrok (easiest for testing)
ngrok http 5000

# Copy the HTTPS URL: https://xxxx.ngrok.io

# Option 2: Deploy to server (production)
# See deployment section below
```

### Step 6: Configure Twilio Webhook

1. Go to: https://console.twilio.com/us1/develop/sms/settings/whatsapp-sandbox
2. In "When a message comes in" field, enter:
   ```
   https://your-server.com/webhook
   ```
   Or for testing:
   ```
   https://xxxx.ngrok.io/webhook
   ```
3. HTTP Method: `POST`
4. Save

### Step 7: Test with WhatsApp

1. Open WhatsApp on your phone
2. Send message to Twilio sandbox number: `whatsapp:+14155238886`
3. First message: `join <your-sandbox-code>`
4. Then ask questions:
   ```
   When is registration?
   What Computer Science courses are available?
   How much is school fees for 200 level?
   ```

---

## 🚢 Production Deployment

### Option 1: AWS Lambda + API Gateway (Serverless)

```python
# lambda_whatsapp.py
import json
from whatsapp_bot import whatsapp_webhook

def lambda_handler(event, context):
    """Lambda handler for WhatsApp webhook"""

    # Parse API Gateway event
    body = event.get('body', '')
    if event.get('isBase64Encoded'):
        import base64
        body = base64.b64decode(body).decode('utf-8')

    # Simulate Flask request
    from werkzeug.datastructures import ImmutableMultiDict
    from flask import request
    import urllib.parse

    params = urllib.parse.parse_qs(body)
    request.values = ImmutableMultiDict(
        {k: v[0] if v else '' for k, v in params.items()}
    )

    # Call webhook
    response = whatsapp_webhook()

    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'application/xml'},
        'body': response
    }
```

**Deploy:**
```bash
# Create Lambda function
aws lambda create-function \
  --function-name lautech-whatsapp-bot \
  --runtime python3.11 \
  --handler lambda_whatsapp.lambda_handler \
  --zip-file fileb://function.zip \
  --role arn:aws:iam::ACCOUNT:role/lambda-execution-role \
  --environment Variables="{
    TWILIO_ACCOUNT_SID=xxx,
    TWILIO_AUTH_TOKEN=xxx,
    LAUTECH_AGENT_ID=xxx
  }"

# Create API Gateway
aws apigatewayv2 create-api \
  --name lautech-whatsapp-api \
  --protocol-type HTTP \
  --target arn:aws:lambda:us-east-1:ACCOUNT:function:lautech-whatsapp-bot

# Get API endpoint and configure in Twilio
```

### Option 2: Docker Container (EC2/ECS)

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements_whatsapp.txt .
RUN pip install --no-cache-dir -r requirements_whatsapp.txt

COPY whatsapp_bot.py .

EXPOSE 5000

CMD ["python3", "whatsapp_bot.py"]
```

**Build and run:**
```bash
# Build image
docker build -t lautech-whatsapp-bot .

# Run container
docker run -d \
  -p 5000:5000 \
  -e TWILIO_ACCOUNT_SID='xxx' \
  -e TWILIO_AUTH_TOKEN='xxx' \
  -e TWILIO_WHATSAPP_NUMBER='whatsapp:+14155238886' \
  -e LAUTECH_AGENT_ID='lautech_agentcore-U7qNy1GPsE' \
  -e AWS_ACCESS_KEY_ID='xxx' \
  -e AWS_SECRET_ACCESS_KEY='xxx' \
  --name lautech-whatsapp \
  lautech-whatsapp-bot

# Check logs
docker logs -f lautech-whatsapp
```

### Option 3: EC2 with systemd

```bash
# 1. Copy files to EC2
scp whatsapp_bot.py ubuntu@your-ec2:/home/ubuntu/

# 2. SSH to EC2
ssh ubuntu@your-ec2

# 3. Install dependencies
pip3 install flask twilio boto3

# 4. Create systemd service
sudo nano /etc/systemd/system/lautech-whatsapp.service
```

**Service file:**
```ini
[Unit]
Description=LAUTECH WhatsApp Bot
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu
Environment="TWILIO_ACCOUNT_SID=xxx"
Environment="TWILIO_AUTH_TOKEN=xxx"
Environment="TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886"
Environment="LAUTECH_AGENT_ID=lautech_agentcore-U7qNy1GPsE"
Environment="AWS_ACCESS_KEY_ID=xxx"
Environment="AWS_SECRET_ACCESS_KEY=xxx"
Environment="AWS_DEFAULT_REGION=us-east-1"
ExecStart=/usr/bin/python3 whatsapp_bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Start service:**
```bash
sudo systemctl daemon-reload
sudo systemctl enable lautech-whatsapp
sudo systemctl start lautech-whatsapp
sudo systemctl status lautech-whatsapp

# Check logs
sudo journalctl -u lautech-whatsapp -f
```

**Configure nginx reverse proxy:**
```nginx
server {
    server_name whatsapp.lautech.edu.ng;

    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    listen 443 ssl;
    ssl_certificate /etc/letsencrypt/live/whatsapp.lautech.edu.ng/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/whatsapp.lautech.edu.ng/privkey.pem;
}
```

---

## 📊 Monitoring & Analytics

### Health Check

```bash
curl http://your-server/health
```

Response:
```json
{
  "status": "healthy",
  "timestamp": "2024-12-23T10:30:00",
  "active_sessions": 15,
  "agent_id": "lautech_agentcore-U7qNy1GPsE"
}
```

### Statistics

```bash
curl http://your-server/stats
```

Response:
```json
{
  "total_users": 247,
  "total_messages": 1523,
  "sessions": [
    {
      "phone": "1234",
      "messages": 8,
      "created_at": "2024-12-23T09:15:00"
    }
  ]
}
```

### CloudWatch Metrics

Add to `whatsapp_bot.py`:

```python
import boto3

cloudwatch = boto3.client('cloudwatch')

def log_metric(metric_name, value):
    cloudwatch.put_metric_data(
        Namespace='LAUTECH/WhatsApp',
        MetricData=[{
            'MetricName': metric_name,
            'Value': value,
            'Unit': 'Count'
        }]
    )

# In webhook handler
log_metric('IncomingMessages', 1)
log_metric('ResponseSent', 1)
```

---

## 📢 Broadcast Messages

Send announcements to all users:

```bash
python3 whatsapp_bot.py broadcast "Registration deadline extended to Sept 20!"
```

Or via Python:
```python
from whatsapp_bot import send_broadcast

# Get user phone numbers from database
phone_numbers = [
    'whatsapp:+234XXXXXXXXXX',
    'whatsapp:+234YYYYYYYYYY',
]

message = """
📢 IMPORTANT ANNOUNCEMENT

Registration deadline has been extended to September 20, 2024.

Visit the portal for more details.
"""

results = send_broadcast(message, phone_numbers)
```

**⚠️ Warning:** Use broadcasts sparingly to avoid spam complaints!

---

## 🔒 Security Best Practices

### 1. Validate Webhook Requests

```python
from twilio.request_validator import RequestValidator

validator = RequestValidator(TWILIO_AUTH_TOKEN)

@app.route('/webhook', methods=['POST'])
def whatsapp_webhook():
    # Validate request is from Twilio
    signature = request.headers.get('X-Twilio-Signature', '')
    url = request.url
    params = request.form

    if not validator.validate(url, params, signature):
        return 'Unauthorized', 403

    # ... rest of webhook code
```

### 2. Rate Limiting

```python
from flask_limiter import Limiter

limiter = Limiter(app, key_func=lambda: request.values.get('From'))

@app.route('/webhook', methods=['POST'])
@limiter.limit("10 per minute")
def whatsapp_webhook():
    # ...
```

### 3. Store Secrets in AWS Secrets Manager

```python
import boto3
import json

def get_twilio_credentials():
    client = boto3.client('secretsmanager')
    secret = client.get_secret_value(SecretId='lautech/twilio')
    return json.loads(secret['SecretString'])

creds = get_twilio_credentials()
TWILIO_ACCOUNT_SID = creds['account_sid']
TWILIO_AUTH_TOKEN = creds['auth_token']
```

---

## 💰 Cost Estimation

### Twilio Costs (Pay-as-you-go)

| Item | Cost |
|------|------|
| WhatsApp Sandbox | Free |
| WhatsApp Business Number | $15/month |
| Incoming messages | $0.005/message |
| Outgoing messages | $0.005/message |
| **Example (1000 msg/day)** | **~$165/month** |

### AWS Costs

| Component | Cost |
|-----------|------|
| Lambda (1000 invocations/day) | ~$5/month |
| API Gateway | ~$3/month |
| AgentCore | ~$50/month |
| **Total AWS** | **~$58/month** |

**Grand Total:** ~$223/month for 1000 messages/day

---

## 🧪 Testing

### Unit Tests

```python
# test_whatsapp_bot.py
import unittest
from whatsapp_bot import format_response_for_whatsapp

class TestWhatsAppBot(unittest.TestCase):

    def test_short_response(self):
        response = "This is a short response"
        chunks = format_response_for_whatsapp(response)
        self.assertEqual(len(chunks), 1)
        self.assertEqual(chunks[0], response)

    def test_long_response(self):
        response = "A" * 2000  # Long response
        chunks = format_response_for_whatsapp(response)
        self.assertGreater(len(chunks), 1)
        for chunk in chunks:
            self.assertLessEqual(len(chunk), 1500)

if __name__ == '__main__':
    unittest.main()
```

### Integration Tests

```bash
# Send test message via Twilio API
curl -X POST https://api.twilio.com/2010-04-01/Accounts/$TWILIO_ACCOUNT_SID/Messages.json \
  --data-urlencode "From=whatsapp:+14155238886" \
  --data-urlencode "To=whatsapp:+234XXXXXXXXXX" \
  --data-urlencode "Body=When is registration?" \
  -u $TWILIO_ACCOUNT_SID:$TWILIO_AUTH_TOKEN
```

---

## 📱 User Guide (For Students)

**How to use LAUTECH WhatsApp Assistant:**

1. **Join the service**
   - Save Twilio number: `+1 415 523 8886`
   - Send: `join <code>` (you'll receive the code from university)

2. **Start asking questions**
   - When is registration?
   - What courses are available for Computer Science?
   - How much is school fees?
   - Tell me about hostels

3. **Get help**
   - Send: `help` or `menu` for commands

4. **Examples**
   ```
   You: When is registration?
   Bot: 📅 Registration starts September 1, 2024

   You: How much is fees for 200 level?
   Bot: 💰 200 Level tuition: ₦75,000 for 2024/2025 session

   You: What CS courses?
   Bot: 📚 Computer Science courses for 200 level:
        - CSC201: Programming II (3 credits)
        - MTH201: Linear Algebra (3 credits)
        ...
   ```

---

## 🎓 Production Readiness Checklist

- [ ] Twilio account created and verified
- [ ] WhatsApp Business number approved (not sandbox)
- [ ] Webhook deployed with HTTPS
- [ ] Twilio webhook URL configured
- [ ] Environment variables secured (Secrets Manager)
- [ ] Rate limiting enabled
- [ ] Request validation implemented
- [ ] Monitoring and logging active
- [ ] Health checks configured
- [ ] Backup webhook URL configured
- [ ] User guide published
- [ ] Support team trained
- [ ] Load tested (1000+ messages)
- [ ] Costs reviewed and approved

---

## 🚀 Next Steps

After WhatsApp bot is running:
1. **Promote to students** - Announce via email, SMS, portal
2. **Monitor usage** - Track metrics and user feedback
3. **Iterate** - Add features based on common questions
4. **Expand** - Add SMS bot, Telegram bot, etc.

---

**Questions?** Check the main [README.md](README.md) or LAUTECH IT Support.
