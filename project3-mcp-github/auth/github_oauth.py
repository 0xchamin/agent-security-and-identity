import os 
from authlib.integrations.requests_client import OAuth2Session
from dotenv import load_dotenv 

load_dotenv()

class GitHubOAuth:
    def __init__(self):
        self.client_id = os.getenv('GITHUB_CLIENT_ID')
        self.client_secret = os.getenv('GITHUB_CLIENT_SECRET')
        self.redirect_uri = os.getenv('http://localhost:8000/callback/github')
        self.scope = 'repo read:user'

        self.authorization_endpoint = 'https://github.com/login/oauth/authorize'
        self.token_endpoint = 'https://github.com/login/oauth/access_token'

    
    def get_authorization_url(self):
        """
        Generate the URL to redirect user for authoriztion
        """
        session = OAuth2Session(
            client_id=self.client_id,
            redirect_uri=self.redirect_uri,
            scope=self.scope
        )
        authorization_url, state = session.create_authorization_url(
            self.authorization_endpoint
        )
        return authorization_url, state 
    

    def exchange_code_for_token(self, authorization_response):
        """
        Exchange authorization token for access token
        """
        session = OAuth2Session(
            client_id=self.client_id,
            redirect_uri=self.redirect_uri
        )

        token = session.fetch_access_token(
            self.token_endpoint,
            authorization_response=authorization_response,
            client_secret = self.client_secret
        )
        return token['access_token']
