import asyncio
from llm.agent import Agent

async def test():
    agent = Agent('sarah')  # Use sarah's GitHub token
    result = await agent.process_query("search for fastapi repositories")
    print(result)

asyncio.run(test())