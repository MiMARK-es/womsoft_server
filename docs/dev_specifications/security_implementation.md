# Security Implementation

This document describes the security measures implemented in the WomSoft Server application.

## Authentication

### JWT Authentication

WomSoft Server uses JSON Web Tokens (JWT) for authentication:

- **Access Token**: Short-lived token (15 minutes) for API access
- **Refresh Token**: Longer-lived token (7 days) for obtaining new access tokens
- **Token Storage**: 
  - Client-side: HttpOnly cookies with Secure flag
  - Server-side: Refresh tokens are stored in the database with user reference

### Password Handling

- Passwords are never stored in plaintext
- Passwords are hashed using bcrypt with appropriate work factor
- Failed login attempts are rate-limited

### Implementation Details

# Password hashing (pseudo-code)
```
def hash_password(password: str) -> str:
    salt = generate_salt()
    hashed_password = bcrypt.hashpw(password.encode(), salt)
    return hashed_password.decode()
```

# Password verification (pseudo-code)
```
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(
        plain_password.encode(), 
        hashed_password.encode()
    )
```

# Token generation (pseudo-code)
```
def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")
```

## Authorization

### Role-Based Access Control

The application implements role-based access control with the following roles:

- **Admin**: Full access to all features
- **Doctor**: Can submit diagnostics and view patient data
- **Researcher**: Can view anonymized diagnostic data
- **Patient**: Can view only their own data

### Permission Matrix

| Endpoint | Admin | Doctor | Researcher | Patient |
|----------|-------|--------|------------|---------|
| `/api/v1/users/*` | ✓ | ✗ | ✗ | ✗ |
| `/api/v1/diagnostics/create` | ✓ | ✓ | ✗ | ✗ |
| `/api/v1/diagnostics/list` | ✓ | ✓ | ✓ (anonymized) | ✓ (own) |
| `/api/v1/patients/*` | ✓ | ✓ | ✓ (anonymized) | ✓ (own) |
| `/api/v1/health` | ✓ | ✓ | ✓ | ✓ |

### Implementation

Permissions are enforced at the API layer using FastAPI's dependency injection system:

# Permission check (pseudo-code)
```
def require_role(allowed_roles: List[str]):
    def dependency(current_user = Depends(get_current_user)):
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=403, 
                detail="Not enough permissions"
            )
        return current_user
    return dependency
```

# Usage in API endpoint
```
@app.get("/api/v1/users/")
def list_users(current_user = Depends(require_role(["admin"]))):
    # Only admins can get here
    return get_all_users()
```

## API Security

### Input Validation

- All API inputs are validated using Pydantic models
- Validation includes type checking, range validation, and pattern matching
- Custom validators are used for complex validation rules

### Rate Limiting

- API endpoints are protected by rate limiting
- Different limits apply to different endpoints
- Limits are based on IP address and/or authenticated user

### CORS Policy

- Cross-Origin Resource Sharing is configured to allow only specific origins
- Preflight requests are properly handled
- Credentials are allowed only from trusted origins

## Data Protection

### Transport Security

- All communications use TLS 1.2+ encryption
- Secure cipher suites are enforced
- HTTP Strict Transport Security (HSTS) is enabled

### Database Security

- Database connection strings and credentials are not hardcoded
- Parameterized queries prevent SQL injection
- Database is encrypted at rest

### Sensitive Data Handling

- PII is minimized and encrypted where necessary
- Diagnostic data is associated with pseudonymized patient IDs
- Data is compartmentalized based on access needs

## Audit and Logging

### Security Event Logging

The following security events are logged:

- Authentication attempts (success/failure)
- Access to sensitive data
- Permission changes
- Security configuration changes
- Unusual activity patterns

### Log Protection

- Logs do not contain sensitive data
- Logs are protected from unauthorized access
- Log rotation and retention policies are in place

## Vulnerability Management

- Dependencies are regularly updated
- Security patches are applied promptly
- Automated vulnerability scanning of dependencies
- Security code reviews for high-risk changes

## Incident Response

- Security incidents are reported to the security response team
- Incident response procedures are documented
- Post-incident analysis improves security posture

## Security Testing

- Regular penetration testing
- Security-focused unit and integration tests
- Testing of authentication and authorization controls

## Regulatory Compliance

- Security measures align with relevant regulations
- Security implementation is documented for regulatory reviews
- Security controls are validated as part of software validation

## Related QMS Documents

- Security Risk Assessment: <!-- TODO: Add document ID -->
- Incident Response Plan: <!-- TODO: Add document ID -->

## Version History

| Version | Date | Description | Author |
|---------|------|-------------|--------|
| 1.0 | <!-- TODO: Add date --> | Initial security implementation documentation | <!-- TODO: Add author --> |