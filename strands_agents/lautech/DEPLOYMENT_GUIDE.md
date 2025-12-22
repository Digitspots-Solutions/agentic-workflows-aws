# LAUTECH University Assistant - Deployment Guide

This guide explains how to deploy the LAUTECH University Assistant so students and staff can access it through a web browser.

## 📋 What You're Deploying

A multi-agent chatbot with 7 AI agents that help with:
- 📚 **Academic** - Courses, prerequisites, lecturers
- 📅 **Calendar** - Registration dates, deadlines, exam periods
- 💰 **Financial** - School fees, payment methods, deadlines
- 🏠 **Hostel** - Accommodation application and facilities
- 📖 **Library** - Library hours, borrowing, resources
- 📋 **Administrative** - Student ID, transcripts, certificates
- 🎯 **Orchestrator** - Smart routing to the right agent

## 🚀 Quick Start (Local Testing)

### Step 1: Install Dependencies

```bash
# Navigate to the project directory
cd strands_agents

# Install required packages
pip install streamlit strands-agents boto3
```

### Step 2: Configure AWS Credentials

Choose ONE method:

**Option A: AWS CLI (Recommended)**
```bash
aws configure
# Enter your Access Key ID
# Enter your Secret Access Key
# Enter region: us-east-1
# Enter output format: json
```

**Option B: Environment Variables**
```bash
export AWS_ACCESS_KEY_ID="your-access-key-here"
export AWS_SECRET_ACCESS_KEY="your-secret-key-here"
export AWS_DEFAULT_REGION="us-east-1"
```

**Option C: Create credentials file**
```bash
# Create ~/.aws/credentials
mkdir -p ~/.aws

cat > ~/.aws/credentials << EOF
[default]
aws_access_key_id = YOUR_ACCESS_KEY
aws_secret_access_key = YOUR_SECRET_KEY
region = us-east-1
EOF
```

### Step 3: Run the Web App

```bash
streamlit run lautech_chatbot_app.py
```

The app will open in your browser at `http://localhost:8501`

✅ **Done!** Students can now access it on your local network.

---

## 🌐 Production Deployment Options

### Option 1: AWS EC2 (Recommended for Universities)

**Benefits:**
- Full control over the server
- Can handle many concurrent users
- Always available (24/7)
- Can integrate with university systems

**Steps:**

#### 1. Launch EC2 Instance

```bash
# Launch Ubuntu EC2 instance
# - Instance type: t3.medium (for ~50 concurrent users)
# - Storage: 20GB
# - Security group: Open port 8501 for Streamlit
```

#### 2. Connect and Setup

```bash
# SSH into your instance
ssh -i your-key.pem ubuntu@your-ec2-ip

# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and dependencies
sudo apt install python3-pip -y
pip3 install streamlit strands-agents boto3

# Clone your repository or upload files
git clone your-repo-url
cd agentic-workflows-aws/strands_agents
```

#### 3. Configure AWS Credentials on EC2

**Recommended: Use IAM Role (More Secure)**
```bash
# Attach IAM role to EC2 with Bedrock permissions
# No credentials file needed!
```

**Alternative: Use credentials file**
```bash
aws configure
```

#### 4. Run as a Service (keeps it running 24/7)

```bash
# Create systemd service file
sudo nano /etc/systemd/system/lautech-assistant.service
```

Paste this:
```ini
[Unit]
Description=LAUTECH University Assistant
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/agentic-workflows-aws/strands_agents
ExecStart=/usr/bin/streamlit run lautech_chatbot_app.py --server.port=8501 --server.address=0.0.0.0
Restart=always

[Install]
WantedBy=multi-user.target
```

Start the service:
```bash
sudo systemctl daemon-reload
sudo systemctl enable lautech-assistant
sudo systemctl start lautech-assistant

# Check status
sudo systemctl status lautech-assistant
```

#### 5. Setup Domain and HTTPS (Optional but Recommended)

```bash
# Install Nginx
sudo apt install nginx -y

# Configure reverse proxy
sudo nano /etc/nginx/sites-available/lautech-assistant
```

Add:
```nginx
server {
    listen 80;
    server_name assistant.lautech.edu.ng;

    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

Enable and install SSL:
```bash
sudo ln -s /etc/nginx/sites-available/lautech-assistant /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

# Install Let's Encrypt SSL (free HTTPS)
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d assistant.lautech.edu.ng
```

✅ **Done!** Students access at `https://assistant.lautech.edu.ng`

---

### Option 2: Streamlit Cloud (Easiest, Free Tier Available)

**Benefits:**
- No server management
- Free for public apps
- Automatic HTTPS
- Easy deployment

**Steps:**

1. **Push code to GitHub**
   ```bash
   git add .
   git commit -m "Add LAUTECH assistant"
   git push
   ```

2. **Go to [share.streamlit.io](https://share.streamlit.io)**

3. **Connect your GitHub repo**

4. **Add secrets** (AWS credentials)
   - Go to App settings → Secrets
   - Add:
   ```toml
   AWS_ACCESS_KEY_ID = "your-key"
   AWS_SECRET_ACCESS_KEY = "your-secret"
   AWS_DEFAULT_REGION = "us-east-1"
   ```

5. **Deploy!**

✅ **Done!** Get a URL like `lautech-assistant.streamlit.app`

**Limitations:**
- Free tier: Limited resources
- Public by default (anyone can access)
- May sleep after inactivity

---

### Option 3: AWS Amplify

**Benefits:**
- Integrated with AWS
- Auto-scaling
- CI/CD built-in

**Steps:**

1. **Create `requirements.txt`**
   ```
   streamlit
   strands-agents
   boto3
   ```

2. **Create `startup.sh`**
   ```bash
   #!/bin/bash
   streamlit run lautech_chatbot_app.py --server.port=8501 --server.address=0.0.0.0
   ```

3. **Deploy via Amplify Console**
   - Connect GitHub repo
   - Configure build settings
   - Deploy

---

### Option 4: Docker Container (Any Cloud Provider)

**Benefits:**
- Works anywhere (AWS, Azure, GCP)
- Consistent environment
- Easy updates

**Steps:**

1. **Create Dockerfile**

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy application files
COPY lautech_chatbot_app.py .
COPY lautech_assistant_enhanced.py .

# Expose Streamlit port
EXPOSE 8501

# Run the app
CMD ["streamlit", "run", "lautech_chatbot_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

2. **Create requirements.txt**
```
streamlit==1.31.0
strands-agents
boto3
```

3. **Build and run**
```bash
# Build image
docker build -t lautech-assistant .

# Run container
docker run -p 8501:8501 \
  -e AWS_ACCESS_KEY_ID=your-key \
  -e AWS_SECRET_ACCESS_KEY=your-secret \
  -e AWS_DEFAULT_REGION=us-east-1 \
  lautech-assistant
```

4. **Deploy to any cloud**
   - AWS ECS/Fargate
   - Azure Container Instances
   - Google Cloud Run
   - DigitalOcean App Platform

---

## 🔒 Security Best Practices

### 1. Secure AWS Credentials

**❌ Never do this:**
```python
# DON'T hardcode credentials in code
aws_key = "AKIAIOSFODNN7EXAMPLE"
```

**✅ Instead:**
- Use IAM roles (for EC2/ECS)
- Use environment variables
- Use AWS Secrets Manager
- Rotate credentials regularly

### 2. Add Authentication (for production)

**Option A: Basic Auth with Streamlit**

```python
# Add to chatbot_app.py
import streamlit as st

def check_password():
    """Returns `True` if the user had a correct password."""
    def password_entered():
        if st.session_state["password"] == "lautech2024":
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.text_input("Password", type="password", on_change=password_entered, key="password")
        return False
    elif not st.session_state["password_correct"]:
        st.text_input("Password", type="password", on_change=password_entered, key="password")
        st.error("😕 Password incorrect")
        return False
    else:
        return True

if not check_password():
    st.stop()

# Rest of your app...
```

**Option B: Integration with University SSO**
- Use SAML/OAuth for university login
- Integrate with existing student portal

### 3. Rate Limiting

Add to prevent abuse:

```python
# In chatbot_app.py
import time

if 'last_query_time' not in st.session_state:
    st.session_state.last_query_time = 0

# Before processing query
current_time = time.time()
if current_time - st.session_state.last_query_time < 2:  # 2 seconds between queries
    st.warning("Please wait a moment before asking another question.")
    st.stop()

st.session_state.last_query_time = current_time
```

---

## 📊 Monitoring and Maintenance

### View Logs

**EC2:**
```bash
sudo journalctl -u lautech-assistant -f
```

**Check Application Health:**
```bash
curl http://localhost:8501/_stcore/health
```

### Update the Application

```bash
# Pull latest changes
git pull

# Restart service
sudo systemctl restart lautech-assistant
```

### Monitor Costs

- **AWS Bedrock:** ~$0.003 per 1K tokens (Claude Haiku)
- **EC2 t3.medium:** ~$30/month
- **Bandwidth:** Usually negligible

**Cost Estimation:**
- 100 students, 5 questions/day = 500 queries/day
- ~1000 tokens per query = 500K tokens/day
- Cost: ~$1.50/day or ~$45/month for AI
- Total (AI + server): ~$75/month

---

## 🔧 Troubleshooting

### Issue: "Unable to locate credentials"

**Solution:**
```bash
# Check if credentials are set
aws sts get-caller-identity

# If not, configure them
aws configure
```

### Issue: "Module not found"

**Solution:**
```bash
pip install -r requirements.txt
```

### Issue: Port 8501 already in use

**Solution:**
```bash
# Find process using port
sudo lsof -i :8501

# Kill it
sudo kill -9 <PID>

# Or use different port
streamlit run lautech_chatbot_app.py --server.port=8502
```

### Issue: Slow responses

**Solutions:**
- Upgrade EC2 instance type
- Add caching for common questions
- Switch to Claude Haiku (faster/cheaper)

---

## 📱 Mobile Access

The Streamlit app is mobile-responsive! Students can access it from:
- Smartphones (iOS/Android)
- Tablets
- Desktop browsers

**Bonus: Create a PWA (Progressive Web App)**

Students can "install" it on their phones:
1. Visit the URL in mobile browser
2. Tap "Add to Home Screen"
3. Use like a native app!

---

## 🚀 Next Steps After Deployment

### 1. Add Real University Data

Replace mock data with:
- Database connections (MySQL, PostgreSQL)
- API integrations (Student Information System)
- Real-time course availability

### 2. Add More Features

- **File Upload:** Students upload documents for processing
- **Notifications:** Email/SMS alerts for deadlines
- **Multi-language:** Yoruba, Igbo support
- **Voice Input:** Speech-to-text queries
- **Analytics Dashboard:** Track common questions

### 3. Integration Options

- **WhatsApp Bot:** Use Twilio API
- **Telegram Bot:** Use Telegram Bot API
- **SMS Service:** For students without internet
- **USSD:** *123# codes for basic phones

### 4. Scale for More Users

- Use load balancer (AWS ALB)
- Multiple EC2 instances
- Auto-scaling groups
- CDN for static assets (CloudFront)

---

## 📞 Support

For deployment assistance:
- 📧 Email: it-support@lautech.edu.ng
- 📱 WhatsApp: +234 XXX XXX XXXX
- 🌐 Documentation: [Your wiki link]

---

## 📄 License

See repository LICENSE file.

**Built for LAUTECH students and staff with ❤️**
