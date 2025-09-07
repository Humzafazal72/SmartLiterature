import os
import json
import logging
from pathlib import Path
from fastapi import APIRouter, Depends
from sse_starlette.sse import EventSourceResponse
from app.database import User
from .graph import build_graph
from app.schemas import AgentInput
from app.auth_logic.util import get_current_user
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from app.schemas import AgentEvent

router = APIRouter()
logger = logging.getLogger(__name__)

# Pre-compile graph
graph_app = None
db_path = None

async def get_graph_app():
    global graph_app, db_path
    if graph_app is None:
        # Setup database path
        db_dir = Path("Data")
        db_dir.mkdir(exist_ok=True)
        db_path = str(db_dir / "State.db")
        
        async with AsyncSqliteSaver.from_conn_string(db_path) as checkpointer:
            graph_app = build_graph().compile(checkpointer=checkpointer)
    return graph_app

@router.post("/get_agent")  
async def get_agent(input: AgentInput, chat_id: str, 
                    user: User = Depends(get_current_user)):
    # Get pre-compiled graph app
    graph_app = await get_graph_app()
    
    config = {"configurable": {"thread_id": chat_id}}
    message = HumanMessage(content=input.user_message)

    async def event_generator():
        try:
            async for event in graph_app.astream({"messages": message}, config=config):
                for node_name, node_output in event.items():
                    # Create the event payload
                    if node_name in ["merger", "clarificationAgent"]:
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

                    # Format as SSE event with proper event type
                    event_data = f"event: {payload.event}\ndata: {json.dumps(payload.dict())}\n\n"
                    yield event_data

            # Send completion event
            final_payload = AgentEvent(event="done", data="Pipeline finished")
            yield f"event: done\ndata: {json.dumps(final_payload.dict())}\n\n"

        except Exception as e:
            logger.error(f"Error in agent stream: {e}", exc_info=True)
            error_payload = AgentEvent(event="error", data=str(e))
            yield f"event: error\ndata: {json.dumps(error_payload.dict())}\n\n"

    return EventSourceResponse(event_generator(), media_type="text/event-stream")