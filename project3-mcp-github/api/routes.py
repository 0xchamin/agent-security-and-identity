from fastapi import APIRouter, Request 
from fastapi.responses import RedirectResponse, HTMLResponse
from auth.github_oauth import GitHubOAuth 
from auth.token_store import TokenStore
from auth.keycloak_auth import KeycloakOAuth 

router = APIRouter()
github_oauth = GitHubOAuth()
token_store = TokenStore()
keycloak_oauth = KeycloakOAuth()

## temp storage for OAuth state (to use session storage in production)
oauth_state = {}

@router.get('/')
async def home():
    return HTMLResponse("""
        <h1>MCP Agent - Project 3</h1>
        <a href="/login/github">Login with GitHub</a>
        """)

@router.get("/login/github")
async def login_github():
    """
    Redirects user to GitHub for Authorization
    """
    authorization_url, state = github_oauth.get_authorization_url()
    oauth_state['state'] = state 
    return RedirectResponse(authorization_url)

@router.get("/callback/github")
async def callback_github(request: Request):
    """
    Handle GitHub OAuth callback
    """
    authorization_response = str(request.url)
    access_token = github_oauth.exchange_code_for_token(authorization_response)

    #DEBUG
    print(f"DEBUG: in GitHub callback: oauth_state = {oauth_state}")

    # Store token (using 'default_user' for now, will use real user ID in Phase 5)
    #token_store.store_token('default_user', 'github', access_token)
    
    # Get user_id (from Keycloak login or fallback to default)
    user_id = oauth_state.get('current_user', 'default_user')
    print(f"DEBUG: Using user_id = {user_id}")

    # Store token for this user
    token_store.store_token(user_id, 'github', access_token)

    print("Access token: ", access_token)
    print("Type : ", type(access_token))
    #return {"debug : ", str(access_token)}
    # return {
    #     "message": "GitHub authentication successful!", 
    #     "token_stored": True,
    #     "token_preview": access_token[:10] + "..."
    # }
    #http://localhost:8000/success?user=%7Buser_id%7D
    return RedirectResponse(url=f"/success?user={user_id}")


@router.get("/token/status")
async def token_status():
    """Check if GitHub token exists"""
    token = token_store.get_token('default_user', 'github')
    return {
        "has_token": token is not None,
        "token_preview": token[:10] + "..." if token else None
    }

# @router.get("/success")
# async def success():
#     return HTMLResponse("""
#         <h1>✅ GitHub Connected!</h1>
#         <p>Your GitHub account has been successfully authorized.</p>
#         <a href="/">Back to Home</a>
#     """)
@router.get("/success")
async def success(user: str = "default_user"):
    return HTMLResponse(f"""
        <h1>✅ GitHub Connected!</h1>
        <p>Logged in as : {user}</p>
        <p>Your GitHub account has been successfully authorized.</p>
        <a href="/chat?user={user}">Go to Chat Interface</a> | <a href="/">Back to Home</a>
    """)


### Keycloak OAuth
@router.get("/login")
async def login(user: str = "default_user"):
    """Start with Keycloak authentication"""
    return HTMLResponse("""
        <h1>MCP Agent - Login</h1>
        <a href="/login/keycloak">Login with Keycloak</a>
    """)

@router.get("/login/keycloak")
async def login_keycloak():
    authorization_url, state = keycloak_oauth.get_authorization_url()
    print(f"Authorization URL: {authorization_url}")
    print(f"Redirect URI in code: {keycloak_oauth.redirect_uri}")
    oauth_state['keycloak_state'] = state
    return RedirectResponse(authorization_url)

@router.get("/callback/keycloak")
async def callback_keycloak(request: Request):
    authorization_response = str(request.url)
    token = keycloak_oauth.exchange_code_for_token(authorization_response)
    
    # Get user info
    user_info = keycloak_oauth.get_user_info(token['access_token'])
    user_id = user_info['preferred_username']  # e.g., 'sarah'

    print(f"DEBUG: User info = {user_info}" )
    print(f"DEBUG: User ID = {user_id}")
    
    # Store user session (simple approach)
    oauth_state['current_user'] = user_id
    print(f"DEBUG: oauth_state = {oauth_state}")
    
    # Now redirect to GitHub OAuth
    return RedirectResponse("/login/github")


@router.get("/chat")
async def chat_interface(user: str = "sarah"):
    """Chat interface for interacting with agent"""
    return HTMLResponse(f"""
<!DOCTYPE html>
<html>
<head>
    <title>MCP Agent Chat</title>
    <style>
        body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; }}
        #chat-box {{ border: 1px solid #ccc; height: 400px; overflow-y: scroll; padding: 10px; margin-bottom: 20px; background: #f9f9f9; }}
        .message {{ margin: 10px 0; padding: 10px; border-radius: 5px; }}
        .user {{ background: #e3f2fd; text-align: right; }}
        .agent {{ background: #f1f8e9; }}
        #input-form {{ display: flex; gap: 10px; }}
        #query-input {{ flex: 1; padding: 10px; font-size: 16px; }}
        #send-btn {{ padding: 10px 20px; background: #4CAF50; color: white; border: none; cursor: pointer; font-size: 16px; }}
        #send-btn:hover {{ background: #45a049; }}
        .loading {{ color: #666; font-style: italic; }}
    </style>
</head>
<body>
    <h1>🤖 MCP Agent Chat</h1>
    <p>Logged in as: <strong>{user}</strong> | <a href="/audit">View Audit Logs</a></p>
    
    <div id="chat-box"></div>
    
    <form id="input-form">
        <input type="text" id="query-input" placeholder="Ask me to do something on GitHub..." required>
        <button type="submit" id="send-btn">Send</button>
    </form>

    <script>
        const userId = '{user}';
        const chatBox = document.getElementById('chat-box');
        const form = document.getElementById('input-form');
        const input = document.getElementById('query-input');
        const sendBtn = document.getElementById('send-btn');

        function addMessage(text, sender) {{
            const msg = document.createElement('div');
            msg.className = 'message ' + sender;
            msg.textContent = text;
            chatBox.appendChild(msg);
            chatBox.scrollTop = chatBox.scrollHeight;
        }}

        form.addEventListener('submit', async (e) => {{
            e.preventDefault();
            const query = input.value.trim();
            if (!query) return;

            addMessage(query, 'user');
            input.value = '';
            sendBtn.disabled = true;
            addMessage('Processing...', 'agent loading');

            try {{
                const response = await fetch('/query', {{
                    method: 'POST',
                    headers: {{'Content-Type': 'application/json'}},
                    body: JSON.stringify({{query: query, user_id: userId}})
                }});
                
                const data = await response.json();
                chatBox.lastChild.remove();
                addMessage(JSON.stringify(data.result, null, 2), 'agent');
            }} catch (error) {{
                chatBox.lastChild.remove();
                addMessage('Error: ' + error.message, 'agent');
            }} finally {{
                sendBtn.disabled = false;
                input.focus();
            }}
        }});
    </script>
</body>
</html>
    """)


@router.get("/chat2")
async def chat_interface(user: str = "sarah"):
    """Chat interface for interacting with agent"""
    return HTMLResponse("""
<!DOCTYPE html>
<html>
<head>
    <title>MCP Agent Chat</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; }
        #chat-box { border: 1px solid #ccc; height: 400px; overflow-y: scroll; padding: 10px; margin-bottom: 20px; background: #f9f9f9; }
        .message { margin: 10px 0; padding: 10px; border-radius: 5px; }
        .user { background: #e3f2fd; text-align: right; }
        .agent { background: #f1f8e9; }
        #input-form { display: flex; gap: 10px; }
        #query-input { flex: 1; padding: 10px; font-size: 16px; }
        #send-btn { padding: 10px 20px; background: #4CAF50; color: white; border: none; cursor: pointer; font-size: 16px; }
        #send-btn:hover { background: #45a049; }
        .loading { color: #666; font-style: italic; }
    </style>
</head>
<body>
    <h1>🤖 MCP Agent Chat</h1>
    <p>Logged in as: <strong id="user-id">{user}</strong> | <a href="/audit">View Audit Logs</a></p>
    
    <div id="chat-box"></div>
    
    <form id="input-form">
        <input type="text" id="query-input" placeholder="Ask me to do something on GitHub..." required>
        <button type="submit" id="send-btn">Send</button>
    </form>

    <script>
        const userId = '{user}'
        const chatBox = document.getElementById('chat-box');
        const form = document.getElementById('input-form');
        const input = document.getElementById('query-input');
        const sendBtn = document.getElementById('send-btn');

        function addMessage(text, sender) {
            const msg = document.createElement('div');
            msg.className = 'message ' + sender;
            msg.textContent = text;
            chatBox.appendChild(msg);
            chatBox.scrollTop = chatBox.scrollHeight;
        }

        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            const query = input.value.trim();
            if (!query) return;

            // Show user message
            addMessage(query, 'user');
            input.value = '';
            sendBtn.disabled = true;
            addMessage('Processing...', 'agent loading');

            try {
                const response = await fetch('/query', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({query: query, user_id: userId})
                });
                
                const data = await response.json();
                
                // Remove loading message
                chatBox.lastChild.remove();
                
                // Show agent response
                addMessage(JSON.stringify(data.result, null, 2), 'agent');
            } catch (error) {
                chatBox.lastChild.remove();
                addMessage('Error: ' + error.message, 'agent');
            } finally {
                sendBtn.disabled = false;
                input.focus();
            }
        });
    </script>
</body>
</html>
    """)

@router.post("/query")
async def process_query(request: dict):
    """Process user query via agent"""
    from llm.agent import Agent
    
    query = request.get('query')
    user_id = request.get('user_id', 'sarah')
    
    agent = Agent(user_id)
    result = await agent.process_query(query)
    
    return {"result": result}

@router.get("/audit")
async def audit_logs():
    """Display audit logs"""
    from audit.logger import audit_logger
    logs = audit_logger.get_logs(limit=100)
    
    return HTMLResponse(f"""
<!DOCTYPE html>
<html>
<head>
    <title>Audit Logs</title>
    <style>
        body {{ font-family: Arial, sans-serif; max-width: 1200px; margin: 20px auto; padding: 20px; }}
        table {{ width: 100%; border-collapse: collapse; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #4CAF50; color: white; }}
        tr:nth-child(even) {{ background-color: #f2f2f2; }}
        .success {{ color: green; }}
        .error {{ color: red; }}
    </style>
</head>
<body>
    <h1>🔍 Audit Logs</h1>
    <p><a href="/chat">Back to Chat</a></p>
    <table>
        <tr>
            <th>Timestamp</th>
            <th>User</th>
            <th>Query</th>
            <th>Tool</th>
            <th>Status</th>
        </tr>
        {''.join([f'''
        <tr>
            <td>{log['timestamp']}</td>
            <td>{log['user_id']}</td>
            <td>{log['query']}</td>
            <td>{log['tool_name']}</td>
            <td class="{log['status']}">{log['status']}</td>
        </tr>
        ''' for log in reversed(logs)])}
    </table>
</body>
</html>
    """)