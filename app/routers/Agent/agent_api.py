from graph import graph_app
from fastapi import APIRouter
from schemas import AgentInput

router = APIRouter()

router.get("/get_agent")
async def get_agent(input: AgentInput):
    return