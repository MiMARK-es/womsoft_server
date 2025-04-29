from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

# Use test database if TEST_MODE environment variable is set
TEST_MODE = os.environ.get("TEST_MODE", "").lower() == "true"
DB_NAME = "womec_test.db" if TEST_MODE else "womec.db"
SQLALCHEMY_DATABASE_URL = f"sqlite:///./{DB_NAME}"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()