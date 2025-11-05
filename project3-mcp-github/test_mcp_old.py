# from mcp.client import MCPClient 
# from auth.token_store_old import token_store 
# import time 

# client = MCPClient(token_store, 'default_user')
# client.start_server()
# time.sleep(2)

# print("cool")

# if client.test_connection():
#     print("✅ MCP server started successfully")
# else:
#     print("❌ Server failed to start")

import asyncio
from mcp_client.client_old import MCPClient
from auth.token_store import token_store

async def test_list_tools():
    client = MCPClient(token_store, 'default_user')
    tools = await client.list_tools()
    
    print(f"✅ Found {len(tools.tools)} tools:")
    for tool in tools.tools:
        print(f"  - {tool.name}: {tool.description}")

asyncio.run(test_list_tools())
