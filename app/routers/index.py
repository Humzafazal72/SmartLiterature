import string
import random
from pathlib import Path
from sqlalchemy.orm import Session
from app.database import User, get_db, Chat
from app.auth_logic import get_current_user
from fastapi import APIRouter, Depends, HTTPException
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

def generate_random_alphanumeric(length):
    """
    Generates a random alphanumeric string.
    """
    characters = string.ascii_letters + string.digits
    return ''.join(random.choices(characters, k=length))

router = APIRouter()

@router.get("/chat/{chat_id}", status_code=201)
async def get_chat(chat_id: str, user: User = Depends(get_current_user)):
    try:
        db_dir = Path("Data")
        db_dir.mkdir(exist_ok=True)
        db_path = str(db_dir / "State.db")
        
        async with AsyncSqliteSaver.from_conn_string(db_path) as checkpointer:
            state = await checkpointer.get_tuple({"configurable": {"thread_id": chat_id}}) 
        
            if state is None:
                raise HTTPException(status_code=500, detail=f"This session doesn't exist.")
        
            return {
                "chat_id": chat_id,
                "state": {
                    "values": state[0],  # The actual state values
                    "next": state[1], # next state to execute
                    "config": state[2]   # Configuration
                    }
                }    
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{e}")


@router.get("/chat", status_code=201)
async def get_all_chats(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        user_data = db.query(Chat).filter(Chat.username == user.username).all()
        chats = {}
        for chat in user_data:
            chats[chat.chat_id] = chat.chat_name

        return chats

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{e}")


@router.post("/create_new_chat", status_code=201)
def create_new(chat_name: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        user_data = db.query(Chat).filter(Chat.username == user.username).all()
        chat_ids = []
        for chat in user_data:
            chat_ids.append(chat.chat_id)
        
        chat_id = generate_random_alphanumeric(length=50)
        new_chat = Chat(username = user.username, chat_id = chat_id, chat_name = chat_name)
        db.add(new_chat)
        db.commit()
        
        return {"message": "Chat created successfully", "chat_id": chat_id}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{e}")