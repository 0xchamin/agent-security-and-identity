from datetime import datetime

def log_action(user_email, user_name, action, agent_client):
    """Log user actions with identity information"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] User: {user_email} ({user_name}) | Action: {action} | Agent: {agent_client}"
    print(log_entry)
    
    # In production, write to file or send to logging service
    with open('audit.log', 'a') as f:
        f.write(log_entry + '\n')