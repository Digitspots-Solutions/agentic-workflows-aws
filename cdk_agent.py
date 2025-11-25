from mcp import StdioServerParameters, stdio_client
from strands import Agent
from strands.models import BedrockModel
from strands.tools.mcp import MCPClient

cdk_client = MCPClient(
    lambda: stdio_client(
        StdioServerParameters(
            command="uvx", args=["awslabs.cdk-mcp-server@latest"]
        )
    )
)

bedrock_model = BedrockModel(
    model_id="us.anthropic.claude-sonnet-4-5-20250929-v1:0",
    temperature=0.7,
)

SYSTEM_PROMPT = """
You are an expert AWS CDK developer. Your role is to help customers build infrastructure as code using AWS CDK. You can query CDK documentation, generate CDK code, and provide best practices for infrastructure development.
"""

with cdk_client:
    all_tools = cdk_client.list_tools_sync()
    agent = Agent(tools=all_tools, model=bedrock_model, system_prompt=SYSTEM_PROMPT)

    response = agent(
        "Show me how to set up cross-stack references in CDK, store the code in a file called cross_stack.py and save to the current directory."
    )
