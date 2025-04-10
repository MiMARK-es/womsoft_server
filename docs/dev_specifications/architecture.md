# WomSoft Server Architecture

This document describes the technical architecture of the WomSoft Server application.

## Overview

WomSoft Server is built using a layered architecture pattern with the following layers:

1. **API Layer**: FastAPI web framework handling HTTP requests
2. **Service Layer**: Business logic and application services
3. **Data Layer**: Data access and persistence using SQLAlchemy and SQLite

## Component Diagram

```
                  ┌─────────────────┐
                  │  Client Browser │
                  └────────┬────────┘
                           │
                  ┌────────▼────────┐
                  │     FastAPI     │
                  │                 │
┌─────────────┐   │ ┌─────────────┐ │   ┌─────────────┐
│ Auth Router ├───┼─┤ User Router ├─┼───┤ Diagnostic  │
│             │   │ │             │ │   │   Router    │
└──────┬──────┘   │ └──────┬──────┘ │   └──────┬──────┘
       │          └────────┼────────┘          │
       │                   │                   │
┌──────▼──────┐   ┌────────▼──────┐    ┌───────▼──────┐
│ Auth Service│   │ User Service  │    │ Diagnostic   │
│             │   │               │    │   Service    │
└──────┬──────┘   └───────┬───────┘    └────────┬─────┘
       │                  │                    │
       └──────────────────┼────────────────────┘
                          │
                  ┌───────▼────────┐
                  │   Data Layer   │
                  │                │
                  │┌──────────────┐│
                  ││ SQLAlchemy   ││
                  ││    ORM       ││
                  │└──────────────┘│
                  └───────┬────────┘
                          │
                  ┌───────▼────────┐
                  │SQLite Database │
                  └────────────────┘
```

## Key Components

### API Layer

- **FastAPI Framework**: Handles HTTP requests, input validation, and response formatting
- **Route Handlers**: Define endpoints for different resource types
- **Authentication**: JWT-based authentication for securing endpoints

### Service Layer

- **User Service**: Manages user operations (create, read, update, delete)
- **Authentication Service**: Handles user authentication and authorization
- **Diagnostic Service**: Processes biomarker data and calculates diagnostic results

### Data Layer

- **SQLAlchemy ORM**: Object-Relational Mapping for database access
- **Models**: Define database schema and relationships
- **Data Access Functions**: Abstract database operations

### Cross-Cutting Concerns

- **Logging**: Application-wide logging system
- **Error Handling**: Centralized error handling and reporting
- **Configuration Management**: Environment-specific configuration

## Technology Stack

- **Backend Framework**: FastAPI (Python)
- **ORM**: SQLAlchemy
- **Database**: SQLite
- **Authentication**: JWT (JSON Web Tokens)
- **Testing**: Pytest, Selenium
- **Containerization**: Docker
- **Web Server**: Uvicorn (development), Gunicorn (production)

## Directory Structure

```
app/
├── __init__.py
├── main.py                  # Application entry point
├── database.py              # Database configuration
├── config.py                # Application configuration
├── auth/                    # Authentication components
│   ├── __init__.py
│   ├── router.py            # Authentication endpoints
│   └── service.py           # Authentication logic
├── users/                   # User management components
│   ├── __init__.py
│   ├── models.py            # User data models
│   ├── router.py            # User endpoints
│   ├── schemas.py           # User data schemas
│   └── service.py           # User business logic
├── diagnostics/             # Diagnostic components
│   ├── __init__.py
│   ├── models.py            # Diagnostic data models
│   ├── router.py            # Diagnostic endpoints
│   ├── schemas.py           # Diagnostic data schemas
│   └── service.py           # Diagnostic algorithms
└── utils/                   # Utility functions and helpers
    ├── __init__.py
    ├── logging.py           # Logging setup
    └── security.py          # Security helpers
```

## Request Flow

1. HTTP request arrives at FastAPI application
2. FastAPI validates request data against defined schemas
3. Router passes validated data to appropriate service
4. Service implements business logic, interacting with data layer as needed
5. Service returns processed data
6. Router formats response and returns to client

## Security Architecture

- **Authentication**: JWT-based token authentication
- **Authorization**: Role-based access control
- **Data Protection**: Input validation, parameterized queries, error handling
- **API Security**: Rate limiting, CORS configuration, security headers

## Performance Considerations

- Database indexing for frequently accessed fields
- Pagination for large result sets
- Optimized query patterns
- Caching where appropriate

## Error Handling Strategy

- Consistent error response format across all endpoints
- Appropriate HTTP status codes
- Detailed error messages in development, generic in production
- Structured logging of errors for troubleshooting

## Monitoring and Observability

- Health check endpoints
- Structured logging
- Performance metrics collection
- Error tracking

## Related QMS Documents

For formal architecture documentation, refer to the Software Architecture Document in the QMS:
- Document ID: <!-- TODO: Add document ID -->

## Version History

| Version | Date | Description | Author |
|---------|------|-------------|--------|
| 1.0 | <!-- TODO: Add date --> | Initial architecture documentation | <!-- TODO: Add author --> |