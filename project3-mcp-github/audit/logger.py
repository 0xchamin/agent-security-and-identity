import json
import os
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class AuditLogger:
    _instance = None
    _audit_file = 'audit_log.json'
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load_logs()
        return cls._instance
    
    def _load_logs(self):
        if os.path.exists(self._audit_file):
            with open(self._audit_file, 'r') as f:
                self.logs = json.load(f)
        else:
            self.logs = []
    
    def _save_logs(self):
        with open(self._audit_file, 'w') as f:
            json.dump(self.logs, f, indent=2)
    
    def log_query(self, user_id: str, query: str, tool_name: str, 
                  arguments: dict, status: str, result: str = None):
        """Log an agent query and tool execution"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "user_id": user_id,
            "query": query,
            "tool_name": tool_name,
            "arguments": arguments,
            "status": status,  # "success" or "error"
            "result_preview": str(result)[:200] if result else None
        }
        self.logs.append(entry)
        self._save_logs()
        logger.info(f"Audit log: {user_id} -> {tool_name} ({status})")
    
    def get_logs(self, limit: int = 50):
        """Get recent audit logs"""
        return self.logs[-limit:]
    
    def get_user_logs(self, user_id: str, limit: int = 50):
        """Get logs for specific user"""
        user_logs = [log for log in self.logs if log['user_id'] == user_id]
        return user_logs[-limit:]

audit_logger = AuditLogger()