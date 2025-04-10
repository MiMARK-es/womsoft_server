# Unit Testing

This document describes the unit testing approach for the WomSoft Server application.

## Overview

Unit tests focus on testing individual functions, methods, and classes in isolation from the rest of the system. The goal is to verify that each unit of code works as expected.

## Technology Stack

- **Testing Framework**: pytest
- **Mocking Library**: pytest-mock, unittest.mock
- **Coverage Tool**: pytest-cov
- **Fixture Management**: pytest fixtures

## Directory Structure

Unit tests are organized in the `tests/unit` directory, mirroring the structure of the application code:

```
tests/unit/
├── conftest.py              # Common test fixtures
├── auth/
│   ├── test_service.py      # Tests for auth service functions
│   └── test_security.py     # Tests for security utilities
├── users/
│   ├── test_models.py       # Tests for user models
│   └── test_service.py      # Tests for user service functions
├── diagnostics/
│   ├── test_models.py       # Tests for diagnostic models
│   └── test_service.py      # Tests for diagnostic algorithms
└── utils/
    └── test_helpers.py      # Tests for utility functions
```

## Writing Unit Tests

### Test File Naming

Test files should be named with the prefix `test_` followed by the name of the module being tested.

### Test Function Naming

Test functions should be named to clearly describe what they are testing:

```
def test_calculate_diagnostic_result_positive_case():
    ...

def test_user_creation_with_valid_data():
    ...

def test_password_hashing_is_secure():
    ...
```

### Basic Test Structure

Each test should follow the Arrange-Act-Assert pattern:

```
def test_calculate_confidence_score():
    # Arrange
    protein_values = [1.2, 3.4, 5.6]
    expected_score = 0.85
    
    # Act
    actual_score = calculate_confidence_score(protein_values)
    
    # Assert
    assert abs(actual_score - expected_score) < 0.001
```

### Mocking Dependencies

Use mocking to isolate the unit being tested:

```
def test_user_service_creates_user(mocker):
    # Arrange
    mock_repo = mocker.patch('app.users.repository.UserRepository')
    mock_repo.create_user.return_value = User(id=1, username='test')
    user_service = UserService(repository=mock_repo)
    user_data = {"username": "test", "password": "secret"}
    
    # Act
    result = user_service.create_user(user_data)
    
    # Assert
    assert result.username == "test"
    mock_repo.create_user.assert_called_once_with(user_data)
```

## Test Fixtures

Use pytest fixtures for common test setup:

```
@pytest.fixture
def sample_user_data():
    return {
        "username": "testuser",
        "email": "test@example.com",
        "password": "securepass123"
    }

@pytest.fixture
def mock_user_repository(mocker):
    return mocker.patch('app.users.repository.UserRepository')

def test_create_user(sample_user_data, mock_user_repository):
    # Test with the fixtures...
```

## Testing Error Cases

Test both happy path and error conditions:

```
def test_protein_validation_rejects_negative_values():
    # Arrange
    invalid_value = -1.5
    
    # Act & Assert
    with pytest.raises(ValueError) as excinfo:
        validate_protein_value(invalid_value)
    
    assert "must be positive" in str(excinfo.value)
```

## Parametrized Tests

Use parametrization to test multiple scenarios:

```
@pytest.mark.parametrize("protein1, protein2, protein3, expected", [
    (1.2, 3.4, 5.6, "Positive"),
    (0.5, 0.8, 1.2, "Negative"),
    (0.9, 4.2, 3.1, "Borderline"),
])
def test_diagnostic_result_classification(protein1, protein2, protein3, expected):
    result = classify_diagnostic_result(protein1, protein2, protein3)
    assert result == expected
```

## Test Coverage

Run tests with coverage reporting:

```
pytest tests/unit/ --cov=app --cov-report=html
```

Coverage targets:
- Overall code coverage: >80%
- Critical components (auth, diagnostic algorithms): >90%

## Critical Unit Tests

The following components require particularly thorough unit testing due to their importance:

1. **Diagnostic Algorithm**
   - Test with all possible result categories
   - Test boundary values
   - Test invalid inputs
   - Test calculation precision

2. **Authentication Logic**
   - Test password hashing and verification
   - Test token generation and validation
   - Test expiration handling
   - Test invalid scenarios

3. **Data Validation**
   - Test all validation rules
   - Test boundary values
   - Test invalid input handling

## Integration with CI/CD

Unit tests are run automatically in the CI/CD pipeline:
- On every pull request
- Before merge to main branch
- On scheduled daily runs

## Related QMS Documents

- Software Verification Plan: <!-- TODO: Add document ID -->
- Risk Management File: <!-- TODO: Add document ID -->

## Version History

| Version | Date | Description | Author |
|---------|------|-------------|--------|
| 1.0 | <!-- TODO: Add date --> | Initial unit testing guidelines | <!-- TODO: Add author --> |