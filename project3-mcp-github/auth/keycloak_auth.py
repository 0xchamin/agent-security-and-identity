# auth/keycloak_oauth.py
import os
from authlib.integrations.requests_client import OAuth2Session
from dotenv import load_dotenv

load_dotenv()

class KeycloakOAuth:
    def __init__(self):
        self.client_id = os.getenv('KEYCLOAK_CLIENT_ID')
        self.client_secret = os.getenv('KEYCLOAK_CLIENT_SECRET')
        self.redirect_uri = 'http://127.0.0.1:8000/callback/keycloak'
        self.scope = 'openid profile email'
        
        keycloak_base = 'http://127.0.0.1:8080/realms/agent-demo'
        self.authorization_endpoint = f'{keycloak_base}/protocol/openid-connect/auth'
        self.token_endpoint = f'{keycloak_base}/protocol/openid-connect/token'
        self.userinfo_endpoint = f'{keycloak_base}/protocol/openid-connect/userinfo'
        
        #http://127.0.0.1:8000/callback/keycloak
        #http://localhost:8000/callback/keycloak

    def get_authorization_url(self):
        print(f"DEBUG: redirect_uri = {self.redirect_uri}")
        session = OAuth2Session(
            client_id=self.client_id,
            redirect_uri=self.redirect_uri,
            scope=self.scope
        )
        authorization_url, state = session.create_authorization_url(
            self.authorization_endpoint
        )
        print(f"DEBUG: Full auth URL = {authorization_url}")
        return authorization_url, state
    
    def exchange_code_for_token(self, authorization_response):
        session = OAuth2Session(
            client_id=self.client_id,
            redirect_uri=self.redirect_uri
        )
        token = session.fetch_token(
            self.token_endpoint,
            authorization_response=authorization_response,
            client_secret=self.client_secret
        )
        return token
    
    def get_user_info(self, access_token):
        """Get user details from Keycloak"""
        import requests
        response = requests.get(
            self.userinfo_endpoint,
            headers={'Authorization': f'Bearer {access_token}'}
        )
        return response.json()