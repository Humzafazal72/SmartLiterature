from sqlalchemy import Column, String
from db import Base

class User(Base):
    __tablename__ = "User"

    username = Column(String(50), primary_key=True, unique = True, nullable= False)
    password = Column(String(255), nullable = False)
    email = Column(String(100), nullable = False, unique = True)