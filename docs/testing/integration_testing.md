# Integration Testing

This document describes the integration testing approach for the WomSoft Server application.

## Overview

Integration tests verify that different components of the system work correctly together. For WomSoft Server, integration testing focuses on API endpoints, database interactions, and service-to-service communication.

## Technology Stack

- **Testing Framework**: pytest
- **API Testing**: FastAPI TestClient
- **Database Testing**: pytest-asyncio, SQLAlchemy
- **Test Database**: SQLite in-memory database

## Directory Structure

Integration tests are organized in the `tests/integration` directory:

```
tests/integration/
├── conftest.py              # Common test fixtures
├── test_auth_api.py         # Tests for auth endpoints
├── test_users_api.py        # Tests for user management endpoints
├── test_diagnostics_api.py  # Tests for diagnostic endpoints
└── test_database.py         # Tests for database interactions
```

## Test Database Setup

Integration tests use an in-memory SQLite database to avoid affecting development or production data:

``` python 
@pytest.fixture(scope="session")
def test_db():
    # Create in-memory database for testing
    SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    # Use connection for tests
    connection = engine.connect()
    yield connection
    
    # Clean up
    connection.close()
    Base.metadata.drop_all(bind=engine)
```

## API Test Fixtures

Integration tests use the FastAPI TestClient to make requests to the API:

``` python
@pytest.fixture
def client():
    # Create test client with test dependencies
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user
    return TestClient(app)

@pytest.fixture
def admin_token():
    # Generate token for admin user
    return create_test_token("admin")

@pytest.fixture
def user_token():
    # Generate token for regular user
    return create_test_token("user")
```

## Testing API Endpoints

### Authentication Endpoints

``` python
def test_login_valid_credentials(client):
    response = client.post(
        "/api/v1/auth/login",
        json={"username": "testuser", "password": "password123"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()["data"]
    assert "refresh_token" in response.json()["data"]

def test_login_invalid_credentials(client):
    response = client.post(
        "/api/v1/auth/login",
        json={"username": "testuser", "password": "wrongpassword"}
    )
    assert response.status_code == 401
```

### Protected Endpoints

``` python
def test_get_users_authorized(client, admin_token):
    response = client.get(
        "/api/v1/users",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    assert "items" in response.json()["data"]

def test_get_users_unauthorized(client):
    response = client.get("/api/v1/users")
    assert response.status_code == 401

def test_get_users_forbidden(client, user_token):
    response = client.get(
        "/api/v1/users",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == 403
```

### Diagnostic Endpoints

``` python
def test_submit_diagnostic_data(client, user_token):
    response = client.post(
        "/api/v1/diagnostics",
        headers={"Authorization": f"Bearer {user_token}"},
        json={
            "patient_id": "P12345",
            "age": 45,
            "gender": "female",
            "protein1_value": 1.2,
            "protein2_value": 3.4,
            "protein3_value": 5.6
        }
    )
    assert response.status_code == 201
    assert response.json()["data"]["result"] in ["Positive", "Negative", "Borderline"]
    assert "confidence" in response.json()["data"]
```

## Testing Database Interactions

``` python
def test_create_and_retrieve_user(db_session):
    # Create user
    user_data = UserCreate(
        username="integrationtest",
        email="integration@test.com",
        password="testpass123",
        role="user"
    )
    db_user = create_user(db_session, user_data)
    
    # Retrieve user
    retrieved_user = get_user_by_username(db_session, "integrationtest")
    
    # Verify
    assert retrieved_user is not None
    assert retrieved_user.id == db_user.id
    assert retrieved_user.email == "integration@test.com"
```

## Testing Service Integrations

``` python
def test_diagnostic_service_with_db(db_session):
    # Create test patient
    patient = create_test_patient(db_session)
    
    # Submit diagnostic data
    diagnostic_data = DiagnosticCreate(
        patient_id=patient.patient_id,
        protein1_value=1.5,
        protein2_value=2.5,
        protein3_value=3.5
    )
    
    # Process diagnostic with service
    result = process_diagnostic(db_session, diagnostic_data, user_id=1)
    
    # Verify result is stored in DB
    stored_result = get_diagnostic_by_id(db_session, result.id)
    assert stored_result is not None
    assert stored_result.result == result.result
```

## Test Sequences

Integration tests often need to test sequences of operations:

``` python
def test_user_lifecycle(client, admin_token):
    # 1. Create user
    create_response = client.post(
        "/api/v1/users",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "username": "lifecycle_test",
            "email": "lifecycle@test.com",
            "password": "securepass123",
            "role": "user"
        }
    )
    assert create_response.status_code == 201
    user_id = create_response.json()["data"]["id"]
    
    # 2. Retrieve user
    get_response = client.get(
        f"/api/v1/users/{user_id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert get_response.status_code == 200
    assert get_response.json()["data"]["username"] == "lifecycle_test"
    
    # 3. Update user
    update_response = client.put(
        f"/api/v1/users/{user_id}",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "email": "updated@test.com",
            "is_active": True
        }
    )
    assert update_response.status_code == 200
    
    # 4. Verify update
    get_updated_response = client.get(
        f"/api/v1/users/{user_id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert get_updated_response.json()["data"]["email"] == "updated@test.com"
    
    # 5. Delete user
    delete_response = client.delete(
        f"/api/v1/users/{user_id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert delete_response.status_code == 204
    
    # 6. Verify deletion
    get_deleted_response = client.get(
        f"/api/v1/users/{user_id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert get_deleted_response.status_code == 404
```

## Running Integration Tests

Integration tests can be run using:

# Run all integration tests
```
pytest tests/integration/
```

# Run specific test module
```
pytest tests/integration/test_auth_api.py
```

# Run with detailed output
```
pytest tests/integration/ -v
```

## Error Handling Testing

Integration tests should verify error handling across service boundaries:

``` python
def test_error_handling_invalid_data(client, user_token):
    response = client.post(
        "/api/v1/diagnostics",
        headers={"Authorization": f"Bearer {user_token}"},
        json={
            "patient_id": "P12345",
            "age": 45,
            "gender": "female",
            "protein1_value": -1.2,  # Invalid negative value
            "protein2_value": 3.4,
            "protein3_value": 5.6
        }
    )
    assert response.status_code == 422
    assert "protein1_value" in response.json()["error"]["details"]
```

## Integration with CI/CD

Integration tests are run in the CI/CD pipeline:
- On every pull request
- Before deployment to staging
- Daily on the main branch

## Related QMS Documents

- System Integration Test Plan: <!-- TODO: Add document ID -->
- Interface Control Document: <!-- TODO: Add document ID -->

## Version History

| Version | Date | Description | Author |
|---------|------|-------------|--------|
| 1.0 | <!-- TODO: Add date --> | Initial integration testing guidelines | <!-- TODO: Add author --> |