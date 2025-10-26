import os
from dotenv import load_dotenv

load_dotenv()


# Keycloak Configuration
KEYCLOAK_URL = "http://localhost:8080"
REALM = "agent-demo"
CLIENT_ID = "ai-agent-client"
REDIRECT_URI = "http://localhost:3000/callback"

# Keycloak endpoints
AUTHORIZATION_ENDPOINT = f"{KEYCLOAK_URL}/realms/{REALM}/protocol/openid-connect/auth"
TOKEN_ENDPOINT = f"{KEYCLOAK_URL}/realms/{REALM}/protocol/openid-connect/token"
USERINFO_ENDPOINT = f"{KEYCLOAK_URL}/realms/{REALM}/protocol/openid-connect/userinfo"
