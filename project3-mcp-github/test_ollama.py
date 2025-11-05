from llm.ollama_client import OllamaClient

client = OllamaClient()
response = client.query("What is 2+2?")
print(f"Response: {response}")