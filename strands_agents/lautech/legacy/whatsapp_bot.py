"""
LAUTECH WhatsApp Bot

Allows students to interact with the LAUTECH assistant via WhatsApp.
Uses Twilio for WhatsApp messaging and calls the deployed AgentCore agent.

Setup:
1. Create Twilio account: https://www.twilio.com/console
2. Enable WhatsApp sandbox: https://console.twilio.com/us1/develop/sms/try-it-out/whatsapp-learn
3. Set environment variables:
   - TWILIO_ACCOUNT_SID
   - TWILIO_AUTH_TOKEN
   - TWILIO_WHATSAPP_NUMBER (e.g., whatsapp:+14155238886)
   - LAUTECH_AGENT_ID
   - AWS_ACCESS_KEY_ID
   - AWS_SECRET_ACCESS_KEY

Run:
    python3 whatsapp_bot.py

Deploy:
    - Flask app on EC2/ECS
    - AWS Lambda + API Gateway
    - Docker container

Usage:
    Users send: "join <sandbox-code>" to your Twilio WhatsApp number
    Then they can ask questions directly via WhatsApp
"""

from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client
import boto3
import json
import os
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Twilio configuration
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
TWILIO_WHATSAPP_NUMBER = os.getenv('TWILIO_WHATSAPP_NUMBER', 'whatsapp:+14155238886')

# AgentCore configuration
LAUTECH_AGENT_ID = os.getenv('LAUTECH_AGENT_ID', 'lautech_agentcore-U7qNy1GPsE')
AWS_REGION = os.getenv('AWS_DEFAULT_REGION', 'us-east-1')

# Initialize clients
twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
bedrock_client = boto3.client('bedrock-agentcore', region_name=AWS_REGION)

# Session storage (in production, use Redis or DynamoDB)
user_sessions = {}


def invoke_lautech_agent(prompt, session_id=None):
    """
    Invoke the deployed AgentCore agent

    Args:
        prompt: User's question
        session_id: Optional session ID for context

    Returns:
        Agent's response text
    """
    try:
        params = {
            'agentId': LAUTECH_AGENT_ID,
            'payload': {'prompt': prompt}
        }

        if session_id:
            params['sessionId'] = session_id

        logger.info(f"Invoking agent with prompt: {prompt[:50]}...")

        response = bedrock_client.invoke_agent(**params)

        # Extract response text
        if 'output' in response:
            return response['output']
        elif 'message' in response:
            return response['message']
        else:
            return str(response)

    except Exception as e:
        logger.error(f"Error invoking agent: {e}")
        return f"Sorry, I encountered an error: {str(e)}\n\nPlease try again or contact support."


def get_session_id(phone_number):
    """Get or create session ID for a user"""
    if phone_number not in user_sessions:
        user_sessions[phone_number] = {
            'session_id': f"whatsapp-{phone_number}-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            'created_at': datetime.now(),
            'message_count': 0
        }

    user_sessions[phone_number]['message_count'] += 1
    return user_sessions[phone_number]['session_id']


def format_response_for_whatsapp(response):
    """
    Format agent response for WhatsApp
    - WhatsApp messages have 1600 character limit
    - Split long messages into multiple parts
    """
    MAX_LENGTH = 1500  # Leave some buffer

    if len(response) <= MAX_LENGTH:
        return [response]

    # Split into chunks
    chunks = []
    current_chunk = ""

    for paragraph in response.split('\n\n'):
        if len(current_chunk) + len(paragraph) + 2 > MAX_LENGTH:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = paragraph
        else:
            if current_chunk:
                current_chunk += "\n\n"
            current_chunk += paragraph

    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks


@app.route('/webhook', methods=['POST'])
def whatsapp_webhook():
    """
    Twilio WhatsApp webhook endpoint

    Receives incoming WhatsApp messages and responds with agent's answer
    """
    try:
        # Get incoming message
        incoming_msg = request.values.get('Body', '').strip()
        from_number = request.values.get('From', '')

        logger.info(f"Received message from {from_number}: {incoming_msg[:50]}...")

        # Handle commands
        if incoming_msg.lower() in ['help', 'start', 'menu']:
            response_text = """
🎓 *LAUTECH Assistant*

I can help you with:
📚 Courses & Prerequisites
💰 School Fees
📅 Registration & Deadlines
🏠 Hostel Information
📖 Library Services
📋 Administrative Procedures

*Examples:*
• When is registration?
• What CS courses are available?
• How much is school fees for 200 level?
• Tell me about hostels

Just send your question!
            """

            resp = MessagingResponse()
            resp.message(response_text.strip())
            return str(resp)

        # Get or create session
        session_id = get_session_id(from_number)

        # Get response from AgentCore agent
        agent_response = invoke_lautech_agent(incoming_msg, session_id)

        # Format response for WhatsApp
        response_chunks = format_response_for_whatsapp(agent_response)

        # Send first chunk via TwiML response
        resp = MessagingResponse()
        resp.message(response_chunks[0])

        # Send additional chunks (if any) via Twilio API
        if len(response_chunks) > 1:
            for chunk in response_chunks[1:]:
                twilio_client.messages.create(
                    from_=TWILIO_WHATSAPP_NUMBER,
                    body=chunk,
                    to=from_number
                )

        # Log interaction
        logger.info(f"Sent response to {from_number} ({len(response_chunks)} chunks)")

        return str(resp)

    except Exception as e:
        logger.error(f"Error in webhook: {e}", exc_info=True)

        # Send error message to user
        resp = MessagingResponse()
        resp.message(
            "❌ Sorry, I encountered an error. Please try again later or contact support."
        )
        return str(resp)


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for monitoring"""
    return {
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'active_sessions': len(user_sessions),
        'agent_id': LAUTECH_AGENT_ID
    }


@app.route('/stats', methods=['GET'])
def get_stats():
    """Get bot statistics (for admin monitoring)"""
    total_messages = sum(session['message_count'] for session in user_sessions.values())

    return {
        'total_users': len(user_sessions),
        'total_messages': total_messages,
        'sessions': [
            {
                'phone': phone[-4:],  # Last 4 digits only for privacy
                'messages': session['message_count'],
                'created_at': session['created_at'].isoformat()
            }
            for phone, session in user_sessions.items()
        ]
    }


def send_broadcast(message, phone_numbers):
    """
    Send broadcast message to multiple users
    Useful for announcements (use sparingly to avoid spam)

    Args:
        message: Message to send
        phone_numbers: List of phone numbers (with whatsapp: prefix)
    """
    logger.info(f"Sending broadcast to {len(phone_numbers)} users")

    results = []
    for phone in phone_numbers:
        try:
            msg = twilio_client.messages.create(
                from_=TWILIO_WHATSAPP_NUMBER,
                body=f"📢 *LAUTECH Alert*\n\n{message}",
                to=phone
            )
            results.append({'phone': phone, 'status': 'sent', 'sid': msg.sid})
        except Exception as e:
            results.append({'phone': phone, 'status': 'failed', 'error': str(e)})

    return results


# CLI for testing
if __name__ == '__main__':
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == 'test':
        # Test mode - simulate a query
        print("=" * 60)
        print("LAUTECH WhatsApp Bot - Test Mode")
        print("=" * 60)
        print()

        # Check configuration
        if not TWILIO_ACCOUNT_SID or not TWILIO_AUTH_TOKEN:
            print("❌ Error: Twilio credentials not set")
            print("\nSet environment variables:")
            print("  export TWILIO_ACCOUNT_SID='your-account-sid'")
            print("  export TWILIO_AUTH_TOKEN='your-auth-token'")
            print("  export TWILIO_WHATSAPP_NUMBER='whatsapp:+14155238886'")
            sys.exit(1)

        print(f"✅ Twilio configured: {TWILIO_WHATSAPP_NUMBER}")
        print(f"✅ Agent ID: {LAUTECH_AGENT_ID}")
        print()

        # Test query
        test_query = "When is registration?"
        print(f"Test query: {test_query}")
        print()

        response = invoke_lautech_agent(test_query)
        print("Response:")
        print(response)
        print()

        print("✅ Test completed successfully!")

    elif len(sys.argv) > 1 and sys.argv[1] == 'broadcast':
        # Broadcast mode
        if len(sys.argv) < 3:
            print("Usage: python3 whatsapp_bot.py broadcast 'Your message here'")
            sys.exit(1)

        message = sys.argv[2]

        # Get phone numbers (from database or file)
        # For demo, using sample numbers - replace with actual user list
        phone_numbers = [
            'whatsapp:+234XXXXXXXXXX',
            # Add more numbers
        ]

        print(f"📢 Broadcasting to {len(phone_numbers)} users...")
        results = send_broadcast(message, phone_numbers)

        success = sum(1 for r in results if r['status'] == 'sent')
        failed = len(results) - success

        print(f"✅ Sent: {success}")
        print(f"❌ Failed: {failed}")

    else:
        # Run Flask server
        print("=" * 60)
        print("LAUTECH WhatsApp Bot")
        print("=" * 60)
        print()
        print(f"✅ Twilio WhatsApp: {TWILIO_WHATSAPP_NUMBER}")
        print(f"✅ Agent ID: {LAUTECH_AGENT_ID}")
        print()
        print("🚀 Starting server...")
        print("📱 Webhook URL: http://your-server/webhook")
        print()
        print("💡 Configure this URL in Twilio Console:")
        print("   https://console.twilio.com/us1/develop/sms/settings/whatsapp-sandbox")
        print()

        # Run Flask app
        app.run(
            host='0.0.0.0',
            port=int(os.getenv('PORT', 5000)),
            debug=os.getenv('DEBUG', 'False').lower() == 'true'
        )
