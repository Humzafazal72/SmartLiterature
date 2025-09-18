from fastapi import FastAPI
from app.routers import auth, agent_api, index

app = FastAPI()

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(agent_api.router, prefix="/agent", tags=["agent"])
app.include_router(index.router, prefix="", tags=["index"])

@app.get("/")
def index():
    return {"message": "App started Successfully", "status_code": 200}