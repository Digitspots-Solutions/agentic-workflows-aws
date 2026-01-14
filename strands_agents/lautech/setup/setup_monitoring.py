"""
Production Monitoring for LAUTECH AgentCore
Creates a CloudWatch Dashboard and Alarms
"""

import boto3
import json

REGION = 'us-east-1'
AGENT_NAME = 'lautech_agentcore'
DB_IDENTIFIER = 'lautech-agentcore-db'
DASHBOARD_NAME = 'LAUTECH-Production-Dashboard'

def create_dashboard():
    """Create a CloudWatch Dashboard for the IT team"""
    cw = boto3.client('cloudwatch', region_name=REGION)
    
    # Dashboard configuration
    dashboard_body = {
        "widgets": [
            {
                "type": "metric",
                "x": 0, "y": 0, "width": 12, "height": 6,
                "properties": {
                    "metrics": [
                        ["Bedrock", "InvocationCount", "AgentId", AGENT_NAME]
                    ],
                    "view": "timeSeries",
                    "stacked": False,
                    "region": REGION,
                    "title": "Agent Invocation Count"
                }
            },
            {
                "type": "metric",
                "x": 12, "y": 0, "width": 12, "height": 6,
                "properties": {
                    "metrics": [
                        ["Bedrock", "InvocationLatency", "AgentId", AGENT_NAME, {"stat": "Average"}]
                    ],
                    "view": "timeSeries",
                    "stacked": False,
                    "region": REGION,
                    "title": "Agent Average Latency (ms)"
                }
            },
            {
                "type": "metric",
                "x": 0, "y": 6, "width": 12, "height": 6,
                "properties": {
                    "metrics": [
                        ["AWS/RDS", "CPUUtilization", "DBInstanceIdentifier", DB_IDENTIFIER]
                    ],
                    "view": "timeSeries",
                    "stacked": False,
                    "region": REGION,
                    "title": "RDS CPU Utilization"
                }
            },
            {
                "type": "metric",
                "x": 12, "y": 6, "width": 12, "height": 6,
                "properties": {
                    "metrics": [
                        ["AWS/RDS", "DatabaseConnections", "DBInstanceIdentifier", DB_IDENTIFIER]
                    ],
                    "view": "timeSeries",
                    "stacked": False,
                    "region": REGION,
                    "title": "Active DB Connections"
                }
            }
        ]
    }

    try:
        cw.put_dashboard(
            DashboardName=DASHBOARD_NAME,
            DashboardBody=json.dumps(dashboard_body)
        )
        print(f"✅ Created CloudWatch Dashboard: {DASHBOARD_NAME}")
    except Exception as e:
        print(f"❌ Error creating dashboard: {e}")

def create_alarms():
    """Create Alarms for critical failures"""
    cw = boto3.client('cloudwatch', region_name=REGION)
    
    try:
        # Alarm for Agent Invocations failing
        cw.put_metric_alarm(
            AlarmName="LAUTECH-Agent-Error-Alarm",
            ComparisonOperator="GreaterThanThreshold",
            EvaluationPeriods=1,
            MetricName="InvocationErrors",
            Namespace="Bedrock",
            Period=300,
            Statistic="Sum",
            Threshold=5.0,
            ActionsEnabled=False, # Set to True once SNS topic is created
            AlarmDescription="Alarm if agent invocation errors exceed 5 in 5 minutes",
            Dimensions=[{"Name": "AgentId", "Value": AGENT_NAME}]
        )
        print("✅ Created Agent Error Alarm")
    except Exception as e:
        print(f"❌ Error creating alarms: {e}")

if __name__ == "__main__":
    create_dashboard()
    create_alarms()
