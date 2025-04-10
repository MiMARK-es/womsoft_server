# API Overview

This document provides an overview of the WomSoft Server API design principles and architecture.

## API Design Principles

1. **RESTful Design**: The API follows REST principles with resource-based URLs, appropriate HTTP methods, and standard status codes.

2. **Security First**: All endpoints are protected with appropriate authentication and authorization controls.

3. **Consistent Structure**: Response formats and error handling follow consistent patterns across all endpoints.

4. **Versioning**: API versioning is incorporated in the URL path to ensure backward compatibility.

5. **Documentation**: All endpoints are documented with OpenAPI/Swagger specifications.

## API Base URL

- Development: `http://localhost:8000/api/v1`
- Production: `https://<production-domain>/api/v1` <!-- TODO: Add production domain -->

## Authentication

The API uses JSON Web Tokens (JWT) for authentication:

1. Client requests access by providing credentials to `/api/v1/auth/login`
2. Server returns an access token and refresh token
3. Client includes access token in the `Authorization` header for subsequent requests
4. When access token expires, client can use refresh token to get a new access token

## Response Format

### Success Response

```
{
  "status": "success",
  "data": {
    // Response data here
  }
}
```

### Error Response

```
{
  "status": "error",
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": {} // Optional additional error details
  }
}
```

## Rate Limiting

<!-- TODO: Document rate limiting policy if implemented -->

## Cross-Origin Resource Sharing (CORS)

CORS is enabled for the following origins:
- Development: `localhost:<port>`
- Production: `https://<production-domain>` <!-- TODO: Add production domain -->

## Related Documentation

- For detailed endpoint documentation, see [endpoints.md](./endpoints.md)
- For example requests and responses, see the [examples](./examples) directory
- For API security implementation details, see [../dev_specifications/security_implementation.md](../dev_specifications/security_implementation.md)