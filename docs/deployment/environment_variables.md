# Environment Variables

This document provides information about the environment variables used in the WomSoft Server application.

## Required Variables

These variables must be set for the application to function properly:

| Variable | Description | Default | Example |
|----------|-------------|---------|---------|
| `SECRET_KEY` | Secret key for securing JWT tokens and cookies | None | `a-very-secret-key-value` |
| `DATABASE_URL` | Database connection string | `sqlite:///./app.db` | `sqlite:///./prod.db` |

## Application Settings

These variables control general application behavior:

| Variable | Description | Default | Example |
|----------|-------------|---------|---------|
| `APP_ENV` | Application environment | `development` | `production` |
| `APP_NAME` | Application name | `WomSoft Server` | `WomSoft Server` |
| `LOG_LEVEL` | Logging level | `INFO` | `DEBUG`, `INFO`, `WARNING`, `ERROR` |
| `WORKERS` | Number of gunicorn workers in production | `1` | `4` |
| `PORT` | Port to run the application on | `8000` | `8080` |

## Security Settings

These variables control security-related settings:

| Variable | Description | Default | Example |
|----------|-------------|---------|---------|
| `ALLOWED_HOSTS` | Comma-separated list of allowed hosts | `localhost,127.0.0.1` | `api.example.com,www.example.com` |
| `CORS_ORIGINS` | Comma-separated list of allowed CORS origins | `http://localhost:3000` | `https://app.example.com` |
| `TOKEN_EXPIRATION_MINUTES` | Access token expiration time in minutes | `15` | `30` |
| `REFRESH_TOKEN_EXPIRATION_DAYS` | Refresh token expiration time in days | `7` | `30` |

## Diagnostic Settings

These variables control the diagnostic algorithm behavior:

| Variable | Description | Default | Example |
|----------|-------------|---------|---------|
| `PROTEIN1_THRESHOLD` | Threshold value for Protein1 | `1.5` | `1.2` |
| `PROTEIN2_THRESHOLD` | Threshold value for Protein2 | `2.5` | `2.8` |
| `PROTEIN3_THRESHOLD` | Threshold value for Protein3 | `3.5` | `3.2` |
| `DIAGNOSTIC_MODEL_VERSION` | Version of the diagnostic model to use | `1.0` | `2.0` |

## Email Settings

These variables are used for email notifications:

| Variable | Description | Default | Example |
|----------|-------------|---------|---------|
| `SMTP_SERVER` | SMTP server address | None | `smtp.gmail.com` |
| `SMTP_PORT` | SMTP server port | `587` | `465` |
| `SMTP_USERNAME` | SMTP username | None | `notifications@example.com` |
| `SMTP_PASSWORD` | SMTP password | None | `password123` |
| `EMAIL_FROM` | Email sender address | `noreply@example.com` | `support@example.com` |
| `EMAIL_ENABLED` | Enable/disable email sending | `False` | `True` |

## Development Settings

These variables are only relevant in development environments:

| Variable | Description | Default | Example |
|----------|-------------|---------|---------|
| `DEBUG` | Enable debug mode | `False` | `True` |
| `RELOAD` | Enable auto-reload on code changes | `False` | `True` |
| `MOCK_DIAGNOSTIC` | Use mock diagnostic results | `False` | `True` |

## Environment Variable Precedence

Environment variables are loaded in the following order (later sources override earlier ones):

1. Default values in code
2. `.env` file in project root
3. Environment variables set in the system/container
4. Command line arguments

## Environment Configuration Files

For different environments, create different `.env` files:

- `.env.development` - Development environment variables
- `.env.test` - Test environment variables
- `.env.production` - Production environment variables

## Security Notes

- Never commit `.env` files with secrets to version control
- Use a secure method to manage production secrets
- Rotate secrets regularly, especially `SECRET_KEY`

<!-- TODO: Add application-specific environment variables -->