# API Endpoints

This document details all available endpoints in the WomSoft Server API.

## Authentication Endpoints

### Login

**Endpoint:** `POST /api/v1/auth/login`

**Description:** Authenticates a user and returns access and refresh tokens.

**Request Body:**
``` json
{
  "username": "string",
  "password": "string"
}
```

**Response:**
``` json
{
  "status": "success",
  "data": {
    "access_token": "string",
    "refresh_token": "string",
    "token_type": "bearer"
  }
}
```

**Status Codes:**
- 200: Success
- 401: Invalid credentials
- 422: Validation error

### Refresh Token

**Endpoint:** `POST /api/v1/auth/refresh`

**Description:** Generates new access token using refresh token.

**Request Body:**
``` json
{
  "refresh_token": "string"
}
```

**Response:**
``` json
{
  "status": "success",
  "data": {
    "access_token": "string",
    "token_type": "bearer"
  }
}
```

**Status Codes:**
- 200: Success
- 401: Invalid refresh token
- 422: Validation error

## User Endpoints

### Get Current User

**Endpoint:** `GET /api/v1/users/me`

**Description:** Returns information about the currently authenticated user.

**Response:**
``` json
{
  "status": "success",
  "data": {
    "id": "integer",
    "username": "string",
    "email": "string",
    "role": "string",
    "is_active": "boolean"
  }
}
```

**Status Codes:**
- 200: Success
- 401: Unauthorized

### Create User

**Endpoint:** `POST /api/v1/users`

**Description:** Creates a new user (admin only).

**Request Body:**
``` json
{
  "username": "string",
  "email": "string",
  "password": "string",
  "role": "string",
  "is_active": "boolean"
}
```

**Response:**
``` json
{
  "status": "success",
  "data": {
    "id": "integer",
    "username": "string",
    "email": "string",
    "role": "string",
    "is_active": "boolean"
  }
}
```

**Status Codes:**
- 201: Created
- 401: Unauthorized
- 403: Forbidden (non-admin user)
- 409: Username or email already exists
- 422: Validation error

## Diagnostic Endpoints

### Submit Diagnostic Data

**Endpoint:** `POST /api/v1/diagnostics`

**Description:** Submits biomarker data for analysis and returns diagnostic results.

**Request Body:**
``` json
{
  "patient_id": "string",
  "protein1_value": "number",
  "protein2_value": "number",
  "protein3_value": "number"
}
```

**Response:**
``` json
{
  "status": "success",
  "data": {
    "diagnostic_id": "string",
    "result": "string",
    "confidence": "number",
    "recommendation": "string",
    "timestamp": "string (ISO format)"
  }
}
```


**Status Codes:**
- 201: Created
- 401: Unauthorized
- 422: Validation error
- 500: Internal server error

### Get Diagnostic History

**Endpoint:** `GET /api/v1/diagnostics`

**Description:** Retrieves diagnostic history for all patients (paginated).

**Query Parameters:**
- `page`: Page number (default: 1)
- `limit`: Items per page (default: 10)
- `patient_id`: Filter by patient ID (optional)

**Response:**
``` json
{
  "status": "success",
  "data": {
    "items": [
      {
        "diagnostic_id": "string",
        "patient_id": "string",
        "result": "string",
        "confidence": "number",
        "timestamp": "string (ISO format)"
      }
    ],
    "total": "integer",
    "page": "integer",
    "limit": "integer",
    "pages": "integer"
  }
}
```

**Status Codes:**
- 200: Success
- 401: Unauthorized

<!-- TODO: Add additional endpoints as implemented -->

## Health Check Endpoint

**Endpoint:** `GET /api/v1/health`

**Description:** Returns system health status.

**Response:**
``` json
{
  "status": "success",
  "data": {
    "database": "healthy",
    "version": "string"
  }
}
```

**Status Codes:**
- 200: Success
- 503: Service unavailable

## API Documentation Endpoint

**Endpoint:** `GET /docs`

**Description:** OpenAPI/Swagger documentation for interactive API exploration.

## Notes

For detailed example requests and responses, see the [examples](./examples) directory.