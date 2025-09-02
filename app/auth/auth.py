from database import User
from sqlalchemy.orm import Session
from fastapi import HTTPException
from schemas import LoginModel, RegisterModel
from util import verify_pw,generate_hash, create_access_token


def login(login_data: LoginModel, db: Session):
    try:
        user = db.query(User).get(User.username == login_data.username)

        if user and verify_pw(login_data.password, user.password):
            return create_access_token(data = {"sub":user.username})         
        else:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
    except:
        raise HTTPException(status_code=500, detail="Something went wrong")


def register(register_data: RegisterModel, db: Session):
    try:    
        user = db.query(User).get(User.username == register_data.username) 

        if user:
            raise HTTPException(status_code=400, detail="Username already exists")

        new_user = User(username = register_data.username, password = generate_hash(register_data.password), email = register_data.email)
        db.add(new_user)
        db.commit

        return {"message": "User Created Successfully", "status_code": 201}
    except:
        raise HTTPException(status_code=500, detail="Internal Server Error")
    