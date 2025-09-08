from sqlalchemy import Column, String, ForeignKey
from .db import Base

class User(Base):
    __tablename__ = "User"

    username = Column(String(50), primary_key=True, unique = True, nullable= False)
    password = Column(String(255), nullable = False)
    email = Column(String(100), nullable = False, unique = True)

class Chat(Base):
    __tablename__ = "Chat"
    id = Column(autoincrement="auto", unique=True, primary_key=True, nullable=False)
    username = Column(String(50), ForeignKey("User.username"), nullable=False)
    chat_name = Column(String(100),nullable=False)
    chat_id = Column(String(50),nullable=False, unique=True)