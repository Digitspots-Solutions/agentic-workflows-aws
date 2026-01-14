import os
from datetime import datetime
from pathlib import Path

from mcp import StdioServerParameters, stdio_client
from strands import Agent, tool
from strands.models import BedrockModel
from strands.tools.mcp import MCPClient

aws_docs_client = MCPClient(
    lambda: stdio_client(
        StdioServerParameters(
            command="uvx", args=["awslabs.aws-documentation-mcp-server@latest"]
        )
    )
)

aws_diag_client = MCPClient(
    lambda: stdio_client(
        StdioServerParameters(
            command="uvx",
            args=[
                "--with",
                "sarif-om,jschema_to_python",
                "awslabs.aws-diagram-mcp-server@latest",
            ],
        )
    )
)

# PowerPoint MCP Client
ppt_client = MCPClient(
    lambda: stdio_client(
        StdioServerParameters(
            command="uvx",
            args=["--from", "office-powerpoint-mcp-server", "ppt_mcp_server"],
        )
    )
)


bedrock_model = BedrockModel(
    model_id="us.anthropic.claude-sonnet-4-5-20250929-v1:0",
    # model_id="us.anthropic.claude-haiku-4-5-20251001-v1:0",
    temperature=0.7,
)

RESEARCH_AGENT_PROMPT = """
You are an AWS Solutions Architect researching services for cloud migrations.
Research the appropriate AWS services and provide a brief summary of:
- Key AWS services needed
- How they fit together
- Brief rationale for each service choice
Keep your response concise and focused.
"""

DIAGRAM_AGENT_PROMPT = """
You are an AWS Solutions Architect creating architecture diagrams.
Create a clear, professional architecture diagram showing the AWS services and their connections.
Save the diagram to ./shop-easy/architecture.png
Keep the diagram clean and easy to understand.
"""


@tool
def research_aws_services(query: str) -> str:
    """
    Research AWS services needed for the migration.
    Returns: Summary of AWS services and architecture approach.
    """
    with aws_docs_client:
        research_agent = Agent(
            system_prompt=RESEARCH_AGENT_PROMPT,
            tools=aws_docs_client.list_tools_sync(),
            model=bedrock_model,
        )
        response = research_agent(query)
        return str(response)


@tool
def create_architecture_diagram(architecture_summary: str) -> str:
    """
    Create an architecture diagram based on the research.
    Saves diagram to ./shop-easy/architecture.png
    Args:
        architecture_summary: The AWS services and architecture from research
    Returns: Confirmation and diagram path.
    """
    with aws_diag_client:
        diagram_agent = Agent(
            system_prompt=DIAGRAM_AGENT_PROMPT,
            tools=aws_diag_client.list_tools_sync(),
            model=bedrock_model,
        )
        prompt = f"Create an architecture diagram for this design:\n\n{architecture_summary}\n\nSave to ./shop-easy/architecture.png"
        response = diagram_agent(prompt)
        return str(response)


@tool
def presentation_creator(content: str, diagram_path: str = None) -> str:
    """
    Create a 6-slide PowerPoint presentation.
    Saves PowerPoint to ./shop-easy/ folder.
    Args:
        content: The research and architecture content to present
        diagram_path: Optional path to architecture diagram to include
    """
    with ppt_client:
        ppt_agent = Agent(
            system_prompt="""Create a concise 6-slide PowerPoint presentation:
            Slide 1: Title slide - "ShopEasy AWS Migration Plan"
            Slide 2: Current State Overview
            Slide 3: Proposed Architecture (include diagram from ./shop-easy/architecture.png)
            Slide 4: Key Benefits
            Slide 5: Migration Approach
            Slide 6: Next Steps
            
            Keep content brief and visual. Use bullet points (max 5 per slide).
            IMPORTANT: Save the PowerPoint to './shop-easy/migration-plan.pptx'""",
            tools=ppt_client.list_tools_sync(),
            model=bedrock_model,
        )
        
        prompt = f"Create a 6-slide presentation with this content:\n\n{content}"
        prompt += "\n\nInclude the diagram from ./shop-easy/architecture.png on slide 3."
        prompt += "\nSave the PowerPoint as ./shop-easy/migration-plan.pptx"
        
        return str(ppt_agent(prompt))





def create_migration_orchestrator():
    """
    Create the main orchestrator agent for cloud migration planning.
    Streamlined workflow: Research → Diagram → PowerPoint
    """

    MIGRATION_ORCHESTRATOR_PROMPT = """
    You are a Cloud Migration Coordinator. Create a migration plan quickly and efficiently.
    
    Process (execute in this exact order):
    1. Use research_aws_services to research the appropriate AWS services
    2. Use create_architecture_diagram with the research results to create a diagram
    3. Use presentation_creator to create a 6-slide PowerPoint with all the findings
    
    Keep everything concise. The goal is to produce a PowerPoint presentation quickly.
    Pass the full context from each step to the next step.
    """

    orchestrator = Agent(
        system_prompt=MIGRATION_ORCHESTRATOR_PROMPT,
        tools=[
            research_aws_services,
            create_architecture_diagram,
            presentation_creator,
        ],
        model=bedrock_model,
    )

    return orchestrator


def run_cloud_migration_demo():
    """
    Demo: Quick Cloud Migration PowerPoint using Agents as Tools
    
    Streamlined workflow: Research → Diagram → PowerPoint (6 slides)
    """
    print("=" * 70)
    print("Quick Cloud Migration PowerPoint Generator")
    print("=" * 70)
    print("\nWorkflow: Research → Diagram → PowerPoint (6 slides)")
    print("Scenario: E-commerce migration to AWS\n")
    
    # Create output directory
    output_dir = Path("./shop-easy")
    output_dir.mkdir(exist_ok=True)
    print(f"📁 Created output directory: {output_dir.absolute()}\n")

    # Track execution start time
    start_time = datetime.now()

    # Create the orchestrator
    orchestrator = create_migration_orchestrator()

    # Simplified migration request
    migration_request = """
    Create a migration plan PowerPoint for "ShopEasy" e-commerce:
    
    Current: On-premise Java app, MySQL database, 1M daily users
    Goal: Migrate to AWS with high availability and scalability
    
    Create:
    1. Research AWS services needed (ECS, RDS, S3, CloudFront, etc.)
    2. Generate an architecture diagram and save to ./shop-easy/architecture.png
    3. Create a 6-slide PowerPoint presentation and save to ./shop-easy/migration-plan.pptx
    
    Keep it concise and focused on the key points.
    """

    print("📋 Starting migration planning...")
    print("🔍 Step 1: Researching AWS services...")
    print("🎨 Step 2: Creating architecture diagram...")
    print("📊 Step 3: Generating 6-slide PowerPoint...\n")

    # Execute the orchestrated migration planning
    result = orchestrator(migration_request)

    # Track execution end time
    end_time = datetime.now()
    execution_time = (end_time - start_time).total_seconds()

    print(f"\n⏱️  Execution time: {execution_time:.2f} seconds")
    print("\n✅ PowerPoint Generated!")
    print("-" * 70)
    print(result)
    print("-" * 70)
    print("\n� Ohutput files saved to ./shop-easy/ folder:")
    print("   - architecture.png (Architecture diagram)")
    print("   - migration-plan.pptx (PowerPoint presentation)")


run_cloud_migration_demo()
