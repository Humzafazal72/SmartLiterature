from app.database import get_db
from app.auth import login, register
from sqlalchemy.orm import Session
from app.schemas import LoginModel,RegisterModel
from fastapi import HTTPException, Depends, APIRouter

router = APIRouter()

@router.get("/api/login")
async def login(form_data: LoginModel, db: Session = Depends(get_db)):
    try:
        return login(form_data, db)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Service Error")


@router.get("/api/register")
async def register(form_data: RegisterModel, db: Session = Depends(get_db)):
    try:
        return register(form_data, db)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Service Error")
