import asyncio
from mcp_client.client import MCPClient
from llm.ollama_client import OllamaClient
from auth.token_store import token_store
import logging

from audit.logger import audit_logger 

logger = logging.getLogger(__name__)

class Agent:
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.llm = OllamaClient()
    
    async def process_query(self, user_query: str):
        """Process natural language query and execute appropriate tool"""
        
        async with MCPClient(token_store, self.user_id) as mcp:
            # Get available tools
            tools = await mcp.list_tools()
            
            # LLM selects tool
            decision = self.llm.select_tool(user_query, tools.tools)
            logger.info(f"LLM decision: {decision}")
            
            if decision['tool_name'] == 'none':
                audit_logger.log_query(self.user_id, user_query, 'none', {}, 'no_tool')
                return "I couldn't find an appropriate tool for that query."
            
            try:
                # Execute tool
                result = await mcp.call_tool(decision['tool_name'], decision['arguments'])
                audit_logger.log_query(self.user_id, user_query, 
                                    decision['tool_name'], decision['arguments'], 
                                    'success', str(result))
                return result
            except Exception as e:
                audit_logger.log_query(self.user_id, user_query, 
                                 decision['tool_name'], decision['arguments'], 
                                 'error', str(e))
                raise