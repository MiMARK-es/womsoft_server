# Data Flow

This document describes the data flow within the WomSoft Server application.

## Overview

The WomSoft Server processes biomarker data to generate diagnostic results. This document outlines how data moves through the system, from input to storage and output.

## High-Level Data Flow Diagram

```
                   ┌───────────────┐
                   │               │
             ┌─────►   Web UI      │
             │     │               │
             │     └───────┬───────┘
             │             │
             │             │ HTTP
             │             ▼
┌────────────┴───┐   ┌───────────────┐   ┌───────────────┐
│                │   │               │   │               │
│  API Client    ◄───►   API Layer   ├───►   Service     │
│                │   │               │   │    Layer      │
└────────────────┘   └───────┬───────┘   └───────┬───────┘
                             │                   │
                             │                   │
                     ┌───────▼───────┐   ┌───────▼───────┐
                     │               │   │               │
                     │  Data Layer   ├───►   Database    │
                     │               │   │               │
                     └───────────────┘   └───────────────┘
```

## User Authentication Flow

1. User submits credentials through UI or API
2. API layer validates credential format
3. Auth service verifies credentials against stored hash
4. On success, JWT token is generated and returned
5. User includes token in subsequent requests
6. API layer validates token before processing requests

## Diagnostic Data Flow

1. User submits biomarker data (Protein1, Protein2, Protein3)
2. API layer validates data format and ranges
3. Diagnostic service processes biomarker values
4. Diagnostic algorithm calculates result and confidence
5. Result is stored in database
6. Result is returned to user

## Data Persistence

### Database Tables and Relationships

```
┌───────────────┐     ┌───────────────┐     ┌───────────────┐
│    Users      │     │   Patients    │     │  Diagnostic   │
│               │     │               │     │   Results     │
│ PK: id        │     │ PK: id        │     │ PK: id        │
│ username      │     │ patient_id    │     │ FK: patient_id│
│ email         │     │ age           │     │ protein1_value│
│ hashed_pwd    │     │ gender        │     │ protein2_value│
│ role          │     │ FK: created_by│     │ protein3_value│
└───────┬───────┘     └───────┬───────┘     │ result        │
        │                     │             │ confidence    │
        │                     │             │ FK: created_by│
        └───────┐     ┌───────┘             └───────────────┘
                │     │
                ▼     ▼
          ┌───────────────┐
          │  Audit Log    │
          │               │
          │ PK: id        │
          │ action        │
          │ timestamp     │
          │ FK: user_id   │
          └───────────────┘
```

## Data Validation Rules

| Data Point | Validation Rule | Error Handling |
|------------|-----------------|----------------|
| Protein1 | 0.0 - 10.0, numeric | Return 422 with error message |
| Protein2 | 0.0 - 10.0, numeric | Return 422 with error message |
| Protein3 | 0.0 - 10.0, numeric | Return 422 with error message |
| Patient ID | Alphanumeric, max 20 chars | Return 422 with error message |
| Age | 18-120, integer | Return 422 with error message |
| Gender | "male", "female", "other" | Return 422 with error message |

## Error Handling

1. **Validation Errors**: Returned as HTTP 422 with details about invalid fields
2. **Authentication Errors**: Returned as HTTP 401 for invalid credentials/tokens
3. **Authorization Errors**: Returned as HTTP 403 for insufficient permissions
4. **Processing Errors**: Logged and returned as HTTP 500 with generic message

## Data Security

- Personally identifiable information is minimized
- Patient IDs are externally generated identifiers, not containing PHI
- Authentication tokens are short-lived
- Database is encrypted at rest
- All API communications use TLS encryption

## Audit Trail

All significant data operations are recorded in an audit log:
- User authentication (success/failure)
- Diagnostic submission
- User management operations
- Patient data access

## Data Retention

- Diagnostic results: <!-- TODO: Define retention period -->
- Audit logs: <!-- TODO: Define retention period -->
- User data: Retained until account deletion

## Related QMS Documents

- Data Management Plan: <!-- TODO: Add document ID -->
- Risk Analysis: <!-- TODO: Add document ID -->

## Version History

| Version | Date | Description | Author |
|---------|------|-------------|--------|
| 1.0 | <!-- TODO: Add date --> | Initial data flow documentation | <!-- TODO: Add author --> |