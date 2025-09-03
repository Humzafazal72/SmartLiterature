from pydantic import BaseModel, EmailStr, Field

class LoginModel(BaseModel): 
    username: str = Field(..., min_length=3, max_length=20)
    password: str = Field(..., min_length=8, max_length=128)

class RegisterModel(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)

class AgentInput(BaseModel):
    user_message: str
