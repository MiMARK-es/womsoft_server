import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import Base, get_db
from app.models.user import User
from app.auth.jwt import get_password_hash, ACCESS_TOKEN_EXPIRE_MINUTES, SECRET_KEY  # Import the actual secret
from app.models.audit import AuditLog  # Add this import

# Add this import to debug
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add these overrides before your fixtures:
os.environ["JWT_SECRET_KEY"] = SECRET_KEY  # Ensure tests use the same secret as the app
os.environ["JWT_ACCESS_TOKEN_EXPIRE_MINUTES"] = str(ACCESS_TOKEN_EXPIRE_MINUTES)

SQLALCHEMY_DATABASE_URL ="sqlite:///./womec_test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def setup_test_db():
    Base.metadata.create_all(bind=engine)
    # Explicitly ensure the audit_logs table exists
    if not inspect(engine).has_table("audit_logs"):
        AuditLog.__table__.create(engine)

@pytest.fixture(scope="function")
def db_engine():
    """Create a SQLAlchemy engine for tests"""
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False}
    )
    
    # Create tables before each test
    Base.metadata.create_all(bind=engine)
    setup_test_db()  # Ensure audit_logs table is created
    
    yield engine
    
    # Clean up
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def db_session(db_engine):
    """Create a SQLAlchemy session for tests"""
    # Create session factory
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)
    
    # Create session
    session = SessionLocal()
    
    try:
        yield session
    finally:
        session.close()

@pytest.fixture(scope="function")
def client(db_session):
    # Override the get_db dependency
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as client:
        yield client
    
    # Clean up the dependencies
    app.dependency_overrides = {}

@pytest.fixture(scope="function")
def admin_user(db_session):
    """Create admin user - MUST BE CREATED FIRST with ID 1"""
    # Force admin to always be ID 1
    admin = User(
        id=1,  # Force ID 1 for admin
        username="adminuser",
        email="admin@example.com",
        hashed_password=get_password_hash("admin123")
    )
    db_session.add(admin)
    db_session.flush()
    db_session.commit()
    logger.info(f"Created admin user with ID: {admin.id}")
    return admin

@pytest.fixture(scope="function")
def test_user(db_session, admin_user):  # Make this depend on admin_user
    """Create a regular test user - AFTER admin user created"""
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password=get_password_hash("password123")
    )
    db_session.add(user)
    db_session.flush()
    db_session.commit()
    logger.info(f"Created test user: {user.username}, ID: {user.id}")
    return user

@pytest.fixture(scope="function")
def token_headers(client, test_user):
    # Get a token for the test user
    login_data = {
        "username": "testuser",
        "password": "password123"
    }
    response = client.post("/api/auth/login", data=login_data)
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}