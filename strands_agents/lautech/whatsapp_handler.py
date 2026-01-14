"""
LAUTECH WhatsApp Lambda Handler
Production implementation for AWS Lambda + API Gateway
"""

import os
import json
import boto3
import logging
from twilio.twiml.messaging_response import MessagingResponse

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Configuration
AGENT_ID = os.getenv('LAUTECH_AGENT_ID', 'lautech_agentcore-KLZaaW7AR6')
REGION = os.getenv('AWS_REGION', 'us-east-1')

# Initialize Bedrock AgentCore Runtime client
bedrock_client = boto3.client('bedrock-agentcore', region_name=REGION)

def lambda_handler(event, context):
    """
    Main Lambda handler for Twilio webhooks
    """
    try:
        # Twilio sends data as form-encoded in the body
        # For simplicity in Lambda, we assume direct JSON or properly parsed body
        body = event.get('body', '')
        if event.get('isBase64Encoded'):
            import base64
            body = base64.b64decode(body).decode('utf-8')
        
        # Parse Twilio parameters
        from urllib.parse import parse_qs
        params = parse_qs(body)
        
        user_msg = params.get('Body', [''])[0].strip()
        from_number = params.get('From', [''])[0]
        
        logger.info(f"Message from {from_number}: {user_msg}")
        
        if not user_msg:
            return response(200, "No message body found")

        # Invoke AgentCore
        session_id = f"whatsapp-{from_number.replace(':', '-')}"
        
        agent_response = bedrock_client.invoke_agent(
            agentId=AGENT_ID,
            payload={'prompt': user_msg},
            sessionId=session_id
        )
        
        # Extract response text
        response_text = agent_response.get('output', "I'm sorry, I couldn't process that.")
        
        # Create Twilio response
        twiml = MessagingResponse()
        twiml.message(response_text)
        
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/xml'},
            'body': str(twiml)
        }

    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        twiml = MessagingResponse()
        twiml.message("Sorry, I'm having trouble connecting to the university system right now. Please try again later.")
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/xml'},
            'body': str(twiml)
        }

def response(status_code, body):
    return {
        'statusCode': status_code,
        'body': body
    }
