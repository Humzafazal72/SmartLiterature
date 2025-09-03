from sqlalchemy.orm import Session
from app import login, register, get_db
from app.schemas import LoginModel,RegisterModel
from fastapi import HTTPException, Depends, APIRouter

router = APIRouter()

@router.get("login")
async def login(form_data: LoginModel, db: Session = Depends(get_db)):
    try:
        return login(form_data, db)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Service Error")


@router.post("register")
async def register(form_data: RegisterModel, db: Session = Depends(get_db)):
    try:
        return register(form_data, db)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Service Error")
