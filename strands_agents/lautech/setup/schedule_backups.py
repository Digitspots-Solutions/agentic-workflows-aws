"""
Automated Backups for LAUTECH AgentCore
Schedules the backup script to run daily using AWS EventBridge
"""

import boto3
import json

REGION = 'us-east-1'
RULE_NAME = 'LAUTECH-Daily-RDS-Backup'
LAMBDA_FUNCTION_NAME = 'LAUTECH-AgentCore-Backup-Utility' # Optional: if user wants to run as Lambda

def schedule_eventbridge_rule():
    """Create an EventBridge rule to trigger daily backups"""
    events = boto3.client('events', region_name=REGION)
    
    try:
        # Create the rule (Runs every day at 1:00 AM UTC)
        print(f"🗓️  Creating EventBridge rule: {RULE_NAME}...")
        events.put_rule(
            Name=RULE_NAME,
            ScheduleExpression='cron(0 1 * * ? *)',
            State='ENABLED',
            Description='Daily backup of the LAUTECH RDS database'
        )
        print("✅ EventBridge rule created.")
        print("💡 Note: To complete this, link this rule to a Lambda function running 'backup_database.py'.")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    schedule_eventbridge_rule()
