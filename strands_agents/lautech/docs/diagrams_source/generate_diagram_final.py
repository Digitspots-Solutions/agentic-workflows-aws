from diagrams import Diagram, Cluster
from diagrams.onprem.client import Users, Client
from diagrams.aws.network import ALB
from diagrams.aws.compute import ECS, Fargate, Lambda
from diagrams.aws.ml import Bedrock
from diagrams.aws.database import Dynamodb, RDSPostgresqlInstance
from diagrams.aws.security import SecretsManager
from diagrams.aws.management import Cloudwatch

# Using the code provided by the MCP Agent
with Diagram("LAUTECH Agentic AI Architecture", show=False, filename="submission_txt/LAUTECH_Architecture_Diagram", direction="LR"):
    # External Users
    users = Users("Students")
    whatsapp = Client("WhatsApp Users")
    
    # Frontend & Load Balancer
    alb = ALB("Application\nLoad Balancer")
    
    with Cluster("Application Tier"):
        dashboard = ECS("Streamlit\nDashboard")
        fargate = Fargate("ECS Fargate")
        dashboard - fargate
    
    with Cluster("Serverless Layer"):
        bedrock_agent = Lambda("Bedrock\nAgentCore")
        bedrock = Bedrock("Amazon Bedrock\n(Claude 3.5)")
        
        with Cluster("Tool Functions"):
            course_lambda = Lambda("Course Tool")
            finance_lambda = Lambda("Finance Tool")
            calendar_lambda = Lambda("Calendar Tool")
            hostel_lambda = Lambda("Hostel Tool")
    
    with Cluster("Data Layer"):
        dynamodb = Dynamodb("Session State")
        rds = RDSPostgresqlInstance("PostgreSQL DB")
        secrets = SecretsManager("Secrets\nManager")
    
    # Monitoring
    cloudwatch = Cloudwatch("CloudWatch\nMonitoring")
    
    # Connections
    users >> alb
    whatsapp >> alb
    alb >> dashboard
    
    dashboard >> bedrock_agent
    bedrock_agent >> bedrock
    bedrock_agent >> dynamodb
    
    bedrock_agent >> course_lambda
    bedrock_agent >> finance_lambda
    bedrock_agent >> calendar_lambda
    bedrock_agent >> hostel_lambda
    
    course_lambda >> rds
    finance_lambda >> rds
    calendar_lambda >> rds
    hostel_lambda >> rds
    
    [course_lambda, finance_lambda, calendar_lambda, hostel_lambda] >> secrets
    
    # Monitoring connections
    cloudwatch << dashboard
    cloudwatch << bedrock_agent
    cloudwatch << rds
    cloudwatch << dynamodb

print("✅ Diagram generated: submission_txt/LAUTECH_Architecture_Diagram.png")
