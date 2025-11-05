import ollama
import logging 

import json
import re 

logger = logging.getLogger(__name__)

class OllamaClient:
    def __init__(self, model='qwen2.5:7b'):
        self.model = model 
        logger.info(f"OllamaClient initialized with model: {model}")

    def query(self, prompt: str) -> str:
        """
        Send prompt to Ollama and get response
        """
        logger.info(f"Querying LLM with prompt length : {len(prompt)}")

        response = ollama.chat(
            model = self.model, 
            messages = [{"role": "user", "content": prompt}]
        )

        result = response['message']['content']
        logger.info(f"LLM response length: {len(result)}")

        return result 
    
    # def select_tool(self, user_query: str, available_tools: list) -> dict:
    #     """
    #     Use LLM to select appopriate tools based on user query
    #     """
    #     tools_list = "\n".join([f"-{tool.name}: {tool.description}" for tool in available_tools])

    #     prompt = f"""
    #         You are an AI assistant that selects GitHub tools to answer user queries.
    #         Available tools:
    #         {tools_list}

    #         User query: {user_query}

    #         Respond with JSON ONLY:
    #         {{
    #             "tool_name": "exact_tool_name",
    #             "arguments": {{"param": "value"}}
    #         }}

    #         If no tool matches, respond {{"tool_name": "none", "arguments":{{}} }}
    #         """

    #     response = self.query(prompt)
    #     json_match = re.search(r'\{.*\}', response, re.DOTALL)

    #     if json_match:
    #         return json.loads(json_match.group())
        
    #     return {"tool_name": "none", "arguments": {}}

    def select_tool(self, user_query: str, available_tools: list) -> dict:
        """Use LLM to select appropriate tool based on user query"""
        
        # Build detailed tool descriptions with parameters
        tool_list = []
        for tool in available_tools:
            params = tool.inputSchema.get('properties', {})
            param_str = ", ".join([f"{k}" for k in params.keys()]) if params else "no parameters"
            tool_list.append(f"- {tool.name} (params: {param_str}): {tool.description}")
        
        tools_formatted = "\n".join(tool_list)
        
        prompt = f"""You are an AI assistant. Select ONE tool from the list below to answer the user query.

    Available tools (use EXACT name):
    {tools_formatted}

    User query: {user_query}

    Respond ONLY with valid JSON:
    {{"tool_name": "exact_tool_name_from_list", "arguments": {{"param_name": "value"}}}}

    Use ONLY tool names from the list above. If unsure, respond: {{"tool_name": "none", "arguments": {{}}}}"""
        
        response = self.query(prompt)
        
        import json
        import re
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
        return {"tool_name": "none", "arguments": {}}
        

