# Architecture Decision Record: Database Selection

## Status
Accepted

## Context
The WomSoft Server application requires a database to store user data, diagnostic results, and system configuration. We needed to select an appropriate database technology that meets our requirements for reliability, ease of deployment, and regulatory compliance.

## Decision
We will use SQLite as the primary database for WomSoft Server.

## Rationale
- **Simplicity**: SQLite is serverless and requires minimal configuration, reducing operational complexity
- **Self-contained**: The entire database is stored in a single file, simplifying backup and deployment
- **Portability**: Easy to deploy across different environments without additional infrastructure
- **Sufficient performance**: For expected load (small to medium user base), SQLite offers sufficient performance
- **Regulatory compliance**: The simplicity of SQLite makes validation and verification more straightforward
- **Data integrity**: SQLite supports ACID transactions ensuring data reliability

## Consequences
### Positive
- Simplified deployment with Docker (no separate database container needed)
- Easier backup and restore procedures
- Lower system requirements for hosting
- Reduced complexity for validation

### Negative
- Limited scalability for very high concurrent usage
- No built-in network access for remote connections
- Less suitable if the application scales to very high volumes

### Mitigations
- If scaling becomes necessary, we have designed the data access layer with abstraction that will allow migration to a client-server database like PostgreSQL with minimal changes to application code

## Related QMS Documents
Software Architecture Document: <!-- TODO: Add document ID -->

## Notes
The database choice aligns with our risk management strategy by reducing system complexity while meeting performance requirements.