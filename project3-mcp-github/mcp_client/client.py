import os
import logging
from auth.token_store import TokenStore
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MCPClient:
    def __init__(self, token_store: TokenStore, user_id: str):
        self.token_store = token_store
        self.user_id = user_id
        self.session = None
        self._context = None
        logger.info(f"MCPClient initialized for user: {user_id}")
        
    async def __aenter__(self):
        """Async context manager entry"""
        token = self.token_store.get_token(self.user_id, 'github')
        if not token:
            logger.error(f"No GitHub token found for user: {self.user_id}")
            raise ValueError("No GitHub token found")
        
        logger.info("Starting MCP server connection...")
        server_params = StdioServerParameters(
            command="npx",
            args=["@modelcontextprotocol/server-github"],
            env={"GITHUB_TOKEN": token}
        )
        
        self._context = stdio_client(server_params)
        read, write = await self._context.__aenter__()
        self.session = ClientSession(read, write)
        await self.session.__aenter__()
        await self.session.initialize()
        logger.info("MCP server connection established")
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Cleanup on exit"""
        logger.info("Closing MCP server connection...")
        if self.session:
            await self.session.__aexit__(exc_type, exc_val, exc_tb)
        if self._context:
            await self._context.__aexit__(exc_type, exc_val, exc_tb)
        logger.info("MCP server connection closed")
    
    async def list_tools(self):
        """List available tools"""
        if not self.session:
            raise RuntimeError("Client not initialized")
        
        logger.info("Discovering available tools...")
        tools = await self.session.list_tools()
        logger.info(f"Discovered {len(tools.tools)} tools")
        return tools

    async def call_tool(self, tool_name: str, arguments: dict):
        """Call a specific tool with error handling"""
        if not self.session:
            raise RuntimeError("Client not initialized")
        
        logger.info(f"Calling tool: {tool_name}")
        logger.debug(f"Arguments: {arguments}")
        
        try:
            result = await self.session.call_tool(tool_name, arguments)
            logger.info(f"Tool call successful: {tool_name}")
            return result
        except Exception as e:
            logger.error(f"Tool call failed: {tool_name} - {str(e)}")
            raise