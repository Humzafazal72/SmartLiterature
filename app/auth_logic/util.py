import os
import bcrypt
from dotenv import load_dotenv
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from app.database import User, get_db
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer

load_dotenv()


ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
SECRET_KEY = os.environ["SECRET_KEY"]

oauth2_scheme = OAuth2PasswordBearer("login")

def generate_hash(password: str) -> str:
    hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    return hashed.decode("utf-8")   # store as string in DB


def verify_pw(password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})

    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


# used to verify the user and also returns the current user.
def get_current_user( db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)) -> User:
    try:
        data = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = data.get("sub")
    
        if not username:
            raise HTTPException(status_code=401, detail="Access to the endpoint is not authroized")
    
    except JWTError:
        raise HTTPException(status_code=401, detail="Access to the endpoint is not authroized")

    try:
        user = db.query(User).get(User.username == username)

        if not user:
            raise HTTPException(status_code=401, detail="Access to the endpoint is not authroized")
        return user
    
    except:
        raise HTTPException(status_code=501, detail="Internal Server Error")