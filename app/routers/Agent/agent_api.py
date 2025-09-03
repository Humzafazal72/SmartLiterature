from database import User
from graph import graph_app
from schemas import AgentInput
from fastapi import APIRouter, Depends
from auth.util import get_current_user
from langchain_core.messages import HumanMessage
from sse_starlette.sse import EventSourceResponse


router = APIRouter()

router.post("/get_agent")
async def get_agent(input: AgentInput, chat_id: str, user: User = Depends(get_current_user)):
    config = {"configurable":{"thread_id":chat_id}}
    message = HumanMessage(content = input["user_message"])

    async def event_generator():
        try:
            for event in graph_app.stream({"messages":message}, config=config):
                for node_name, node_output in event.items():
                    yield {
                        "event": "update",
                        "data":{
                            "node_name":node_name,
                            "node_output":node_output
                        }
                    }
            yield {"event": "done", "data": "Pipeline finished"}

        except Exception as e:
             yield {"event": "error", "data": str(e)}

    return EventSourceResponse(event_generator())