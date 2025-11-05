import subprocess
import os
from auth.token_store_old import TokenStore 
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

class MCPClient:
    def __init__(self, token_store: TokenStore, user_id: str):
        self.token_store = token_store
        self.user_id = user_id
        self.process = None 
        
    def start_server(self):
        """
        Start GitHub MCP server with the user's token
        """
        token = self.token_store.get_token(self.user_id, 'github')
        if not token:
            raise ValueError("No GitHub token found")

        env = os.environ.copy()
        env['GITHUB_TOKEN'] = token 

        # Start MCP Server Process
        self.process = subprocess.Popen(
            ['npx', '@modelcontextprotocol/server-github'],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env 
        )

    async def list_tools(self):
        """
        Discover available tools from MCP server
        """
        server_params = StdioServerParameters(
            command="npx",
            args=["@modelcontextprotocol/server-github"],
            env={"GITHUB_TOKEN": self.token_store.get_token(self.user_id, 'github')}

        )

        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                tools = await session.list_tools()
                return tools 

    def test_connection(self):
        """Test if server is running"""
        if self.process and self.process.poll() is None:
            return True
        return False