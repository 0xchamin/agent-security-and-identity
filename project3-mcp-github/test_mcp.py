import asyncio
from mcp_client.client import MCPClient
from auth.token_store import token_store

async def test_mcp():
    async with MCPClient(token_store, 'default_user') as client:
        # List tools
        tools = await client.list_tools()
        print(f"✅ Found {len(tools.tools)} tools\n")
        
        # Test a tool call
        print("Testing search_repositories...")
        result = await client.call_tool(
            "search_repositories",
            {"query": "fastapi", "maxResults": 3}
        )
        print(f"✅ Tool call successful!")
        print(result)

asyncio.run(test_mcp())