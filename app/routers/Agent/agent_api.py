import json
from fastapi import APIRouter, Depends
from sse_starlette.sse import EventSourceResponse
from app.database import User, get_db
from .graph import build_graph
from app.schemas import AgentInput
from app.auth_logic.util import get_current_user
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from app.schemas import AgentEvent

router = APIRouter()

@router.post("/get_agent")  
async def get_agent(input: AgentInput, chat_id: str, 
                    ):
    config = {"configurable": {"thread_id": chat_id}}
    message = HumanMessage(content=input.user_message)

    
    async def event_generator():
        try:
            async with AsyncSqliteSaver.from_conn_string(f"{chat_id}.db") as checkpointer:
                graph_app = build_graph().compile(checkpointer=checkpointer)
                async for event in graph_app.astream({"messages": message}, config=config):
                    for node_name, node_output in event.items():
                        # Create the event payload
                        if node_name=="merger" or node_name=="clarificationAgent":
                            payload = AgentEvent(
                                event="update",
                                node_name=node_name,
                                node_output=str(node_output)  # force string
                            )
                        else:
                            payload = AgentEvent(
                                event="update",
                                node_name=node_name  
                            )

                        # Format as SSE event
                        event_data = f"data: {json.dumps(payload.dict())}\n\n"
                        yield event_data

                # Send completion event
                final_payload = AgentEvent(event="done", data="Pipeline finished")
                yield f"data: {json.dumps(final_payload.dict())}\n\n"

        except Exception as e:
            error_payload = AgentEvent(event="error", data=str(e))
            yield f"data: {json.dumps(error_payload.dict())}\n\n"

    return EventSourceResponse(event_generator(), media_type="text/plain")