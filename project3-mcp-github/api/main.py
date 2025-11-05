from fastapi import FastAPI
from api.routes import router
#from routes import router

app = FastAPI(title= "MCP Agent - GitHub OAuth")
app.include_router(router=router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)