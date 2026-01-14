"""
Generate LAUTECH Architecture Diagram using AWS Diagram MCP Server
Usage: python setup/generate_diagram_mcp.py
"""
import os
import sys
from mcp import StdioServerParameters, stdio_client
from strands import Agent
from strands.models import BedrockModel
from strands.tools.mcp import MCPClient

# Ensure we have the API keys or settings if needed
# Assuming environment is already set up for Bedrock access

def main():
    print("🚀 Initializing AWS Diagram MCP Client...")
    
    # Initialize the MCP Client for the AWS Diagram Server
    aws_diag_client = MCPClient(
        lambda: stdio_client(
            StdioServerParameters(
                command="uvx",
                args=["awslabs.aws-diagram-mcp-server"],
                env={"FASTMCP_LOG_LEVEL": "ERROR", **os.environ},
            )
        )
    )

    # Initialize Bedrock Model (using the one from the reference or Haiku for speed)
    bedrock_model = BedrockModel(
        model_id="us.anthropic.claude-3-5-sonnet-20241022-v2:0", # Using Sonnet for better tool use capability
        temperature=0.0,
    )

    SYSTEM_PROMPT = """
    You are an expert AWS Solutions Architect. Your goal is to generate a high-quality AWS architecture diagram using the available tools.
    
    CRITICAL INSTRUCTIONS:
    1. First, use `list_icons` to find the correct identifiers for these services:
       - Users / Students (User icon)
       - Web Browser (Client icon)
       - WhatsApp (Mobile or Chat icon)
       - Application Load Balancer
       - ECS Fargate
       - Bedrock / Bedrock Agent
       - Lambda
       - RDS (PostgreSQL)
       - DynamoDB
       - Secrets Manager
       - CloudWatch
       - VPC / Subnets
       
    2. Then, use `generate_diagram` to create the diagram.
       - Title: "LAUTECH Agentic AI Architecture"
       - The diagram must show:
         - Student Users and WhatsApp Users connecting from outside.
         - An Application Load Balancer (ALB) acting as the entry point.
         - Streamlit Dashboard running on ECS Fargate.
         - Bedrock AgentCore (Serverless) orchestating the logic.
         - Amazon Bedrock (Claude 3.5 Haiku) for inference.
         - AgentCore Memory (DynamoDB) for session state.
         - Four Lambda Functions (Course, Finance, Calendar, Hostel) as tools.
         - Amazon RDS (PostgreSQL) as the primary database in a private subnet.
         - Secrets Manager for credentials.
         - CloudWatch for monitoring.
    3. RETURN THE PYTHON CODE for the diagram in your response, wrapped in a python code block.
    """

    print("🤖 Creating Strands Agent...")
    with aws_diag_client:
        # Get tools from the MCP server
        print("🛠️  Listing MCP tools...")
        diag_tools = aws_diag_client.list_tools_sync()
        
        agent = Agent(
            tools=diag_tools, 
            model=bedrock_model, 
            system_prompt=SYSTEM_PROMPT
        )

        print("🎨 Generating Architecture Diagram...")
        response = agent(
            "Generate the LAUTECH Agentic AI architecture diagram. Logic: Find icons -> Generate Diagram. IMPORTANT: Please output the full python code you used to generate the diagram."
        )
        
        print("\n✅ Agent Response:")
        print(response)
        
        print("\n📂 Current Directory Contents:")
        print(os.listdir("."))

if __name__ == "__main__":
    main()
