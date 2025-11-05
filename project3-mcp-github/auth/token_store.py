import json
import os

class TokenStore:
    _instance = None
    _token_file = 'tokens.json'
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load_tokens()
        return cls._instance
    
    def _load_tokens(self):
        if os.path.exists(self._token_file):
            with open(self._token_file, 'r') as f:
                self.tokens = json.load(f)
        else:
            self.tokens = {}
    
    def _save_tokens(self):
        print(f"DEBUG: Saving tokens to file {self.tokens}")
        with open(self._token_file, 'w') as f:
            json.dump(self.tokens, f)
        print(f"DEBUG: Tokens saved successfully!")
    
    def store_token(self, user_id, service, token):
        if user_id not in self.tokens:
            self.tokens[user_id] = {}
        self.tokens[user_id][service] = token
        self._save_tokens()
    
    def get_token(self, user_id, service):
        return self.tokens.get(user_id, {}).get(service)
    
    def delete_token(self, user_id, service):
        if user_id in self.tokens and service in self.tokens[user_id]:
            del self.tokens[user_id][service]
            self._save_tokens()

token_store = TokenStore()