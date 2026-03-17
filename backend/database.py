from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os 
from dotenv import load_dotenv

# 指定路徑到上層 Safetrack
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "../.env"))

DB_URL = os.getenv("DATABASE_URL")
print("DATABASE_URL =", DB_URL)

engine = create_engine(
    DB_URL,
    pool_size=10,
    max_overflow=20,
    pool_recycle=1800,
    pool_pre_ping=True
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()