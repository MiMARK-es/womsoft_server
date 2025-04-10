# Database Schema

This document describes the database schema used in the WomSoft Server application.

## Overview

WomSoft Server uses SQLite as the database engine. The schema is designed to support user management, diagnostic data storage, and application configuration.

## Entity Relationship Diagram

<!-- TODO: Insert ER diagram image -->

## Tables

### Users

| Column | Type | Description | Constraints |
|--------|------|-------------|-------------|
| id | INTEGER | Unique user identifier | PRIMARY KEY |
| username | TEXT | User login name | NOT NULL, UNIQUE |
| email | TEXT | User email address | NOT NULL, UNIQUE |
| hashed_password | TEXT | Securely hashed password | NOT NULL |
| is_active | BOOLEAN | Whether user account is active | DEFAULT TRUE |
| role | TEXT | User role (admin, user, etc.) | NOT NULL |
| created_at | TIMESTAMP | Account creation timestamp | NOT NULL |
| last_login | TIMESTAMP | Last login timestamp | NULL |

### Patients

| Column | Type | Description | Constraints |
|--------|------|-------------|-------------|
| id | INTEGER | Unique patient identifier | PRIMARY KEY |
| patient_id | TEXT | External patient identifier | NOT NULL, UNIQUE |
| age | INTEGER | Patient age in years | NOT NULL |
| gender | TEXT | Patient gender | NOT NULL |
| created_at | TIMESTAMP | Record creation timestamp | NOT NULL |
| created_by | INTEGER | User ID who created record | FOREIGN KEY |

### DiagnosticResults

| Column | Type | Description | Constraints |
|--------|------|-------------|-------------|
| id | INTEGER | Unique result identifier | PRIMARY KEY |
| patient_id | INTEGER | Patient identifier | FOREIGN KEY |
| protein1_value | REAL | Protein1 measurement value | NOT NULL |
| protein2_value | REAL | Protein2 measurement value | NOT NULL |
| protein3_value | REAL | Protein3 measurement value | NOT NULL |
| result | TEXT | Diagnostic result | NOT NULL |
| confidence | REAL | Result confidence score | NOT NULL |
| created_at | TIMESTAMP | Result creation timestamp | NOT NULL |
| created_by | INTEGER | User ID who created result | FOREIGN KEY |

### AuditLog

| Column | Type | Description | Constraints |
|--------|------|-------------|-------------|
| id | INTEGER | Unique log entry identifier | PRIMARY KEY |
| user_id | INTEGER | User who performed action | FOREIGN KEY |
| action | TEXT | Description of action performed | NOT NULL |
| entity_type | TEXT | Type of entity affected | NOT NULL |
| entity_id | INTEGER | ID of entity affected | NULL |
| timestamp | TIMESTAMP | When action occurred | NOT NULL |
| details | TEXT | Additional JSON-encoded details | NULL |

### RefreshTokens

| Column | Type | Description | Constraints |
|--------|------|-------------|-------------|
| id | INTEGER | Unique token identifier | PRIMARY KEY |
| user_id | INTEGER | User associated with token | FOREIGN KEY |
| token | TEXT | Hashed refresh token | NOT NULL |
| expires_at | TIMESTAMP | Token expiration timestamp | NOT NULL |
| created_at | TIMESTAMP | Token creation timestamp | NOT NULL |
| revoked | BOOLEAN | Whether token has been revoked | DEFAULT FALSE |

<!-- TODO: Complete tables with actual schema used in the application -->
<!-- TODO: Add indexes information -->

## Indexes

| Table | Index Name | Columns | Type | Purpose |
|-------|------------|---------|------|---------|
| Users | idx_users_username | username | UNIQUE | Fast user lookup by username |
| Users | idx_users_email | email | UNIQUE | Fast user lookup by email |
| Patients | idx_patients_patient_id | patient_id | UNIQUE | Fast patient lookup by external ID |
| DiagnosticResults | idx_results_patient | patient_id | NORMAL | Fast retrieval of patient results |
| DiagnosticResults | idx_results_created_at | created_at | NORMAL | Time-based result queries |
| AuditLog | idx_audit_user_time | user_id, timestamp | NORMAL | User activity queries |
| RefreshTokens | idx_tokens_user | user_id | NORMAL | User token lookup |

## Database Migrations

Database schema migrations are managed using Alembic. Migration scripts are located in the `migrations/` directory.

To create a new migration:

```
alembic revision --autogenerate -m "Description of change"
```

To apply migrations:

alembic upgrade head

## Schema Creation

The initial database schema is created by the following SQLAlchemy models:

``` python
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Float, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    role = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)
```

# Additional models follow similar pattern

## Data Lifecycle Management

### Backup Procedures

Backups of the SQLite database file are performed daily using:

```
cp /app/data/womsoft.db /app/backups/womsoft_$(date +%Y%m%d).db
```

### Data Retention

- Diagnostic results are retained for <!-- TODO: Add retention period -->
- Audit logs are retained for <!-- TODO: Add retention period -->
- Inactive user accounts are archived after 1 year of inactivity

### Data Archiving

Historical data older than the retention period is archived to:

- Long-term storage database for regulatory compliance
- Anonymized research database for aggregate analysis

<!-- TODO: Add details about archival process and access procedures -->