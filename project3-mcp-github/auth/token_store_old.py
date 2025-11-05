# auth/token_store.py
from typing import Optional
from datetime import datetime

class TokenStore:
    """Simple in-memory token storage (use database in production)"""
    
    def __init__(self):
        self._tokens = {}
    
    def store_token(self, user_id: str, service: str, token: str):
        """Store access token for a user and service"""
        key = f"{user_id}:{service}"
        self._tokens[key] = {
            'token': token,
            'stored_at': datetime.utcnow().isoformat()
        }
    
    def get_token(self, user_id: str, service: str) -> Optional[str]:
        """Retrieve access token for a user and service"""
        key = f"{user_id}:{service}"
        token_data = self._tokens.get(key)
        return token_data['token'] if token_data else None
    
    def delete_token(self, user_id: str, service: str):
        """Remove token from storage"""
        key = f"{user_id}:{service}"
        self._tokens.pop(key, None)

# Global instance
token_store = TokenStore()