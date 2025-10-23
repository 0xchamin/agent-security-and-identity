import secrets
import hashlib
import base64

from config import AUTHORIZATION_ENDPOINT, CLIENT_ID, REDIRECT_URI
import urllib.parse

import requests
from config import TOKEN_ENDPOINT

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
import uvicorn



def generate_pkce_pair():
    """Generate PKCE code_verifier and code_challenge"""
    code_verifier = base64.urlsafe_b64encode(secrets.token_bytes(32)).decode('utf-8').rstrip('=')
    code_challenge = base64.urlsafe_b64encode(
        hashlib.sha256(code_verifier.encode('utf-8')).digest()
    ).decode('utf-8').rstrip('=')
    return code_verifier, code_challenge


def build_authorization_url(code_challenge):
    """Build the OAuth authorization URL with PKCE"""
    params = {
        'client_id': CLIENT_ID,
        'redirect_uri': REDIRECT_URI,
        'response_type': 'code',
        'scope': 'openid',
        'code_challenge': code_challenge,
        'code_challenge_method': 'S256'
    }
    return f"{AUTHORIZATION_ENDPOINT}?{urllib.parse.urlencode(params)}"




def exchange_code_for_token(code, code_verifier):
    """Exchange authorization code for access token using PKCE verifier"""
    data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': REDIRECT_URI,
        'client_id': CLIENT_ID,
        'code_verifier': code_verifier
    }
    response = requests.post(TOKEN_ENDPOINT, data=data)
    return response.json()



app = FastAPI()

# Store these temporarily (in production, use proper session management)
pkce_verifier = None
access_token = None

@app.get("/")
async def home():
    """Start the OAuth flow"""
    global pkce_verifier
    
    # Generate PKCE pair
    pkce_verifier, code_challenge = generate_pkce_pair()
    
    # Build authorization URL
    auth_url = build_authorization_url(code_challenge)
    
    return HTMLResponse(f"""
        <h1>AI Agent OAuth Demo</h1>
        <p>Click below to authorize the agent:</p>
        <a href="{auth_url}">Authorize Agent</a>
    """)

@app.get("/callback")
async def callback(code: str):
    """Handle OAuth callback with authorization code"""
    global pkce_verifier, access_token
    
    # Exchange code for token
    token_response = exchange_code_for_token(code, pkce_verifier)
    access_token = token_response.get('access_token')
    
    return HTMLResponse(f"""
        <h1>Authorization Successful!</h1>
        <p>Access token received (first 20 chars): {access_token[:20]}...</p>
        <a href="/calendar">View Calendar</a>
    """)


@app.get("/calendar")
async def view_calendar():
    """Agent calls the calendar API on behalf of user"""
    global access_token
    
    if not access_token:
        return HTMLResponse("<h1>Error: Not authorized yet</h1>")
    
    # Call the resource API with the access token
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get("http://localhost:8000/api/calendar", headers=headers)
    
    events = response.json().get("events", [])
    events_html = "<br>".join([f"{e['time']}: {e['title']}" for e in events])
    
    return HTMLResponse(f"""
        <h1>Your Calendar</h1>
        {events_html}
    """)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=3000)