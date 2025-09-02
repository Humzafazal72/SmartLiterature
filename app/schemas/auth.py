from pydantic import BaseModel, constr, EmailStr

class LoginModel(BaseModel): 
    username: constr(strip_whitespace=True, min_length=3,max_length=20)
    password: constr(min_length=8, max_length=128)

class RegisterModel(BaseModel):
    username: constr(strip_whitespace=True, min_length=3, max_length=50)
    email: EmailStr
    password: constr(min_length=8, max_length=128)