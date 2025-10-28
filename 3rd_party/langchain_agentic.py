import subprocess
import sys
from typing import Annotated

from langchain.agents import create_agent
from langchain_aws import ChatBedrock
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.messages import HumanMessage
from langchain_core.tools import tool
from langgraph.graph import START, StateGraph, MessagesState
from langgraph.types import Command


# Tool definitions
def setup_tools():
    """Set up and return the tools used by the agents."""
    duck_duck_go_tool = DuckDuckGoSearchRun(max_results=5)

    @tool
    def python_repl(
        code: Annotated[str, "The python code to execute to generate your chart."],
    ):
        """Execute Python code and return the result."""
        try:
            result = subprocess.run(
                [sys.executable, "-c", code],
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode != 0:
                return f"Failed to execute. Error: {result.stderr}"
            output = result.stdout if result.stdout else "Code executed successfully"
            return f"Successfully executed:\n```python\n{code}\n```\nStdout: {output}"
        except subprocess.TimeoutExpired:
            return "Execution timed out after 30 seconds"
        except Exception as e:
            return f"Failed to execute. Error: {repr(e)}"

    return [duck_duck_go_tool, python_repl]


# Handoff tool creation
def create_handoff_tool(*, agent_name: str, description: str):
    """Create a tool that transfers control to another agent."""
    name = f"transfer_to_{agent_name}"
    
    @tool(name, description=description)
    def handoff_tool() -> Command:
        return Command(
            goto=agent_name,
            graph=Command.PARENT,
        )
    return handoff_tool


def setup_workflow(llm, tools):
    """Set up and return the workflow graph using modern LangGraph patterns."""
    
    # Create handoff tools
    transfer_to_chart = create_handoff_tool(
        agent_name="chart_generator",
        description="Transfer to chart generator when you have data ready for visualization"
    )
    transfer_to_research = create_handoff_tool(
        agent_name="Researcher",
        description="Transfer to researcher when you need more data or information"
    )
    
    # Create agents using create_agent (LangGraph v1)
    research_agent = create_agent(
        llm,
        tools=[tools[0], transfer_to_chart],  # DuckDuckGo + handoff
        system_prompt="You are a research assistant. Your job is to find accurate data. "
                     "Once you have the data, transfer to the chart generator.",
        name="Researcher"
    )
    
    chart_agent = create_agent(
        llm,
        tools=[tools[1], transfer_to_research],  # Python REPL + handoff
        system_prompt="You are a chart generator. Create visualizations using matplotlib. "
                     "If you need more data, transfer to the researcher.",
        name="chart_generator"
    )
    
    # Set up the workflow
    workflow = StateGraph(MessagesState)
    workflow.add_node(research_agent)
    workflow.add_node(chart_agent)
    workflow.add_edge(START, "Researcher")
    
    return workflow.compile()


# Main execution
def main():
    # Set up the LLM
    llm = ChatBedrock(
        model_id="us.anthropic.claude-haiku-4-5-20251001-v1:0",
        model_kwargs=dict(temperature=0),
        region_name="us-west-2",
    )

    # Set up tools
    tools = setup_tools()

    # Set up the workflow
    graph = setup_workflow(llm, tools)

    # Execute the workflow
    print("Starting multi-agent workflow...")
    print("=" * 60)
    
    events = graph.stream(
        {
            "messages": [
                HumanMessage(
                    content="Fetch the UK's GDP over the past 5 years, "
                    "then create a bar graph for me to see. "
                    "Once you code it up, save the bar graph as a png"
                )
            ],
        },
        {"recursion_limit": 150},
    )

    # Print the results
    for s in events:
        print(s)
        print("-" * 60)


if __name__ == "__main__":
    main()
