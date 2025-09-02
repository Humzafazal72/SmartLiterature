import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
load_dotenv()


MYSQL_URL  = f"mysql+mysqlconnector://root:{os.environ['DB_PASSWORD']}@localhost:3306/litreview"
engine =  create_engine(url=MYSQL_URL, connect_args={"charset": "utf8mb4"})

local_session = sessionmaker(bind=engine, autoflush= False, autocommit= False)

Base = declarative_base()

def get_db():
    db = local_session()
    try:
        yield db
    finally:
        db.close()