from fastapi import FastAPI, Header, HTTPException
from typing import Optional
import uvicorn

api = FastAPI()

@api.get("/api/calendar")
async def get_calendar(authorization: Optional[str] = Header(None)):
    """Protected calendar endpoint - requires valid access token"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid token")
    
    # In production, you'd validate the token with Keycloak
    # For now, just check it exists
    token = authorization.replace("Bearer ", "")
    
    return {
        "events": [
            {"time": "9:00 AM", "title": "Team Standup"},
            {"time": "2:00 PM", "title": "Client Meeting"},
            {"time": "4:00 PM", "title": "Code Review"}
        ]
    }

if __name__ == "__main__":
    uvicorn.run(api, host="0.0.0.0", port=8000)