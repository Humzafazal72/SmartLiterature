from fastapi import FastAPI
from app.routers import auth, agent_api, main

app = FastAPI()

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(agent_api.router, prefix="/agent", tags=["agent"])
app.include_router(main.router, prefix="", tags=["main"])

@app.get("/")
def main():
    return {"message": "App started Successfully", "status_code": 200}