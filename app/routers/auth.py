from app.database import get_db
from sqlalchemy.orm import Session
from app.auth_logic import login, register
from app.schemas import LoginModel,RegisterModel
from fastapi import HTTPException, Depends, APIRouter

router = APIRouter()

@router.post("/login")
async def signin(form_data: LoginModel, db: Session = Depends(get_db)):
    print("here")
    try:
        return login(form_data, db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{e}")


@router.post("/register")
async def signup(form_data: RegisterModel, db: Session = Depends(get_db)):
    try:
        return register(form_data, db)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Service Error")
