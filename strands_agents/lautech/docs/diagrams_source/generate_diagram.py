"""
Generate AWS Architecture Diagram for LAUTECH
Requires: pip install diagrams
System Requirement: Graphviz (brew install graphviz)
"""

from diagrams import Diagram, Cluster, Edge
from diagrams.aws.compute import Fargate, Lambda
from diagrams.aws.database import RDS, Dynamodb
from diagrams.aws.network import ELB, CloudFront, VPC, PrivateSubnet, PublicSubnet
from diagrams.aws.security import SecretsManager, IAM, WAF
from diagrams.aws.ml import Bedrock
from diagrams.aws.management import Cloudwatch
from diagrams.onprem.client import User, Client
from diagrams.saas.chat import Slack as Whatsapp

with Diagram("LAUTECH Agentic AI Architecture", show=False, filename="submission_txt/LAUTECH_Architecture_Diagram", direction="LR"):
    
    user = User("Student")
    browser = Client("Web Browser")
    whatsapp = Whatsapp("WhatsApp")

    with Cluster("AWS Cloud (us-east-1)"):
        
        with Cluster("Security & Management"):
            cw = Cloudwatch("CloudWatch Logs")
            iam_role = IAM("Agent Role")
            waf = WAF("Web App Firewall")

        with Cluster("VPC"):
            
            with Cluster("Public Subnet"):
                alb = ELB("ALB")
                
                with Cluster("ECS Cluster"):
                    dashboard = Fargate("Streamlit Dashboard")

            with Cluster("Agent Core Service"):
                # Bedrock Logic
                bedrock = Bedrock("Bedrock AgentCore")
                guardrail = Bedrock("Guardrails")
                model = Bedrock("Claude 3.5 Haiku")
                memory = Dynamodb("Agent Memory")
                
                # Grouping agent components
                bedrock - Edge(style="dotted") - guardrail
                bedrock - Edge(style="dotted") - model
                bedrock - Edge(style="dotted") - memory

            with Cluster("Specialist Tools (Lambda Layer)"):
                tools = [
                    Lambda("Course Tool"),
                    Lambda("Finance Tool"),
                    Lambda("Calendar Tool"),
                    Lambda("Hostel Tool")
                ]

            with Cluster("Private Subnet"):
                rds = RDS("PostgreSQL (Student DB)")
                secrets = SecretsManager("DB Credentials")

    # Relationships
    user >> Edge(label="HTTPS") >> alb
    browser >> Edge(label="HTTPS") >> alb
    user >> Edge(label="Message") >> whatsapp
    
    whatsapp >> Edge(label="Webhook") >> bedrock
    alb >> Edge(label="Forward") >> dashboard
    dashboard >> Edge(label="InvokeAgent") >> bedrock
    
    bedrock >> Edge(label="Orchestrate") >> tools
    
    for tool in tools:
        tool >> Edge(label="SQL") >> rds
        tool >> Edge(style="dashed") >> secrets
        
    # Logging
    bedrock >> Edge(style="dotted") >> cw
    dashboard >> Edge(style="dotted") >> cw

print("✅ Diagram generated: submission_txt/LAUTECH_Architecture_Diagram.png")
