from app.database import User
from app.auth_logic import get_current_user
from fastapi import APIRouter, Depends, HTTPException
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

router = APIRouter()

@router.get("/chat/{chat_id}")
def get_chat(chat_id: str, user: User = Depends(get_current_user)):
    try:
        db_dir = Path("Data")
        db_dir.mkdir(exist_ok=True)
        db_path = str(db_dir / "State.db")
        
        async with AsyncSqliteSaver.from_conn_string(db_path) as checkpointer:
            state = await checkpointer.get_tuple({"configurable": {"thread_id": chat_id}}) 
        
            if state is None:
                raise HTTPException(status_code=500, detail=f"This session doesn't exist.")
        
            return {
                "status": "success",
                "chat_id": chat_id,
                "state": {
                    "values": state[0],  # The actual state values
                    "config": state[2]   # Configuration
                    }
                }    
        
    except e in Exception:
        raise HTTPException(status_code=500, detail=f"{e}")
    
@router.get("/chat")
def get_all_chats(user: User = Depends(get_current_user))
