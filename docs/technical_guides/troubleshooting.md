# Troubleshooting Guide

This document provides solutions for common issues encountered when working with the WomSoft Server application.

## Development Environment Issues

### Database Connection Issues

**Problem**: Unable to connect to the database with errors like "unable to open database file"

**Solutions**:
- Check if the database file exists at the expected location
- Verify file permissions allow read/write access
- Ensure the application configuration points to the correct database path
- For Docker environments, check volume mappings to ensure persistence

**Example Error**:

sqlalchemy.exc.OperationalError: (sqlite3.OperationalError) unable to open database file

**Diagnostic Steps**:
1. Check database file location: `ls -la /path/to/database.db`
2. Check permissions: `stat /path/to/database.db`
3. Verify configuration: `echo $DATABASE_URL`
4. For Docker, check volumes: `docker volume ls` and `docker volume inspect volume_name`

### Docker Container Issues

**Problem**: Docker containers exit immediately or fail to start

**Solutions**:
- Check Docker logs: `docker-compose logs -f [service_name]`
- Verify environment variables are correctly set
- Ensure ports are not already in use by other services
- Check Docker volume permissions

**Example Error**:

ERROR: for womsoft  Cannot start service womsoft: driver failed programming external connectivity on endpoint

**Diagnostic Steps**:
1. Check logs: `docker-compose logs womsoft`
2. Check port usage: `netstat -tuln | grep 8000`
3. Verify Docker configuration: `docker-compose config`

### Test Failures

**Problem**: Tests fail with connection errors to Selenium

**Solutions**:
- Ensure the Chrome container is running and accessible
- Check that tests are using the correct Selenium URL (`http://chrome:4444/wd/hub`)
- Verify networks are properly configured in Docker Compose
- Increase timeouts for UI tests that may be timing out

**Example Error**:

ConnectionError: HTTPConnectionPool(host='chrome', port=4444): Max retries exceeded

**Diagnostic Steps**:
1. Check Chrome container status: `docker ps | grep chrome`
2. Test connection: `curl -I http://chrome:4444/wd/hub`
3. Check network configuration: `docker network inspect test-network`

## Application Runtime Issues

### Authentication Problems

**Problem**: Unable to authenticate or tokens are rejected

**Solutions**:
- Verify JWT secret key is properly set
- Check token expiration settings
- Clear browser cookies and local storage
- Check for clock skew between client and server

**Example Error**:

401 Unauthorized: {"detail":"Could not validate credentials"}

**Diagnostic Steps**:
1. Check configuration: `echo $SECRET_KEY`
2. Verify token: `jwt decode <token>`
3. Check system time: `date`

### Calculation Errors

**Problem**: Diagnostic calculations producing unexpected results

**Solutions**:
- Verify input data is within expected ranges
- Check calculation formulas in the diagnostic service
- Look for potential floating-point precision issues
- Validate against manual calculations with test data

**Example Error**:

ValueError: Protein1 value 12.5 exceeds maximum allowable value of 10.0

**Diagnostic Steps**:
1. Review input data
2. Check calculation logic in `app/diagnostics/service.py`
3. Run manual calculations with the same inputs
4. Check unit tests for the calculation logic

### Performance Issues

**Problem**: Application response times are slow

**Solutions**:
- Check database query performance and add indexes if needed
- Look for N+1 query patterns and optimize
- Verify hardware resources are sufficient
- Consider implementing caching for frequent calculations

**Diagnostic Steps**:
1. Enable SQL query logging
2. Check resource utilization: `top`, `htop`, or Docker stats
3. Profile endpoints with tools like `locust` or `wrk`
4. Review database indexes and query plans

## Deployment Issues

### SSL Certificate Issues

**Problem**: SSL handshake failures or certificate warnings

**Solutions**:
- Check certificate expiration date
- Verify certificate chain is complete
- Ensure private key matches certificate
- Check server configuration for correct certificate paths

**Diagnostic Steps**:
1. Check certificate info: `openssl x509 -in cert.pem -text -noout`
2. Verify certificate chain: `openssl verify -CAfile chain.pem cert.pem`
3. Test SSL configuration: `openssl s_client -connect domain:443`

### Migration Failures

**Problem**: Database migrations fail to apply

**Solutions**:
- Check for errors in migration scripts
- Ensure database user has sufficient privileges
- Check for conflicting migrations or schema changes

**Example Error**:

ERROR [alembic.runtime.migration] Error occurred during migration

**Diagnostic Steps**:
1. Review migration script
2. Check database permissions
3. Review alembic version history: `alembic history`
4. Consider manual intervention if needed

## Logs and Debugging

### Enabling Debug Logging

To enable detailed logging for troubleshooting:

1. Set the environment variable `LOG_LEVEL=DEBUG`
2. Restart the application
3. Check logs for detailed information

### Log Locations

- In development: Console output
- In Docker: Access with `docker-compose logs -f [service_name]`
- In production: `/var/log/womsoft/` <!-- TODO: Verify production log path -->

### Common Log Patterns

**Authentication Failure**:

```
ERROR:app.auth.service:Authentication failed for user "username": Invalid password
```

**Database Error**:

```
ERROR:sqlalchemy.engine.Engine:Error executing statement: no such table: users
```

**API Request Error**:

```
INFO:app.routers:Request failed: 422 Unprocessable Entity for /api/v1/diagnostics
```

## Diagnostic Tools

### Health Check Endpoint

The application provides a health check endpoint at `/api/v1/health` that returns the status of various system components:

``` json
{
  "status": "success",
  "data": {
    "database": "healthy",
    "version": "1.2.3"
  }
}
```

### Database Inspection

To inspect the SQLite database directly:

```
sqlite3 /path/to/database.db
```

Common useful commands:
- `.tables` - List all tables
- `.schema [table]` - Show table schema
- `SELECT COUNT(*) FROM users;` - Count users
- `.quit` - Exit SQLite CLI

## Getting Help

If you cannot resolve an issue using this guide:

1. Open an issue in the GitHub repository with detailed description
2. Contact the development team at <!-- TODO: Add support contact details -->
3. For critical issues, refer to the incident response plan in the QMS

<!-- TODO: Add specific troubleshooting scenarios based on common application errors -->