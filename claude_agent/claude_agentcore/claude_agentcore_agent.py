"""
AgentCore Agent - Simple query handler using Claude Agent SDK
"""
import asyncio
from claude_agent_sdk import ClaudeSDKClient, AssistantMessage, TextBlock
from bedrock_agentcore.runtime import BedrockAgentCoreApp

app = BedrockAgentCoreApp()

@app.entrypoint
def invoke(payload, context):
    """
    Handle any query passed to the agent using Claude Agent SDK.
    
    Args:
        payload: Dictionary containing 'prompt' key with user query
        context: AgentCore runtime context
    
    Returns:
        Dictionary with 'response' key containing agent's answer
    """
    # Extract the user's query from the payload
    user_query = payload.get("prompt", "")
    
    if not user_query:
        return {"error": "No prompt provided. Please include a 'prompt' field in your request."}
    
    # Run async Claude SDK client
    response_text = asyncio.run(query_claude(user_query))
    
    return {"response": response_text}

async def query_claude(query: str) -> str:
    """
    Query Claude using the Claude Agent SDK.
    
    Args:
        query: User's question or prompt
        
    Returns:
        Claude's response as a string
    """
    async with ClaudeSDKClient() as client:
        # Send the query
        await client.query(query)
        
        # Collect the response
        response_parts = []
        async for message in client.receive_response():
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        response_parts.append(block.text)
        
        return " ".join(response_parts)

if __name__ == "__main__":
    app.run()
