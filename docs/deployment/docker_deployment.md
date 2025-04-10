# Docker Deployment

This document provides instructions for deploying WomSoft Server using Docker.

## Prerequisites

- Docker Engine (20.10.0+)
- Docker Compose (2.0.0+)
- Access to the Docker image repository (if using private repository)

## Deployment Architecture

The production deployment consists of the following containers:

1. **womsoft**: Main application server running FastAPI
2. **nginx**: Reverse proxy handling SSL termination and static files

## Deployment Steps

### 1. Prepare Environment Configuration

Create a `.env` file in the deployment directory with required environment variables:

# Application Settings
```
APP_ENV=production
LOG_LEVEL=INFO
SECRET_KEY=your-secret-key-here  # Generate a strong secret key
```

# Database Settings
```
DATABASE_URL=sqlite:///./prod.db
```

# Security Settings
```
ALLOWED_HOSTS=yourdomain.com
CORS_ORIGINS=https://yourdomain.com
```

See [environment_variables.md](./environment_variables.md) for a complete list of available variables.

### 2. Prepare Docker Compose File

Create a `docker-compose.prod.yml` file for production deployment:

```
version: '3'

services:
  womsoft:
    image: womsoft-server:latest
    restart: always
    env_file:
      - ./.env
    volumes:
      - ./data:/app/data
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/api/v1/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/conf.d:/etc/nginx/conf.d
      - ./nginx/ssl:/etc/nginx/ssl
      - ./nginx/www:/var/www/html
    depends_on:
      - womsoft
    restart: always
```

### 3. Configure Nginx

Create nginx configuration file `./nginx/conf.d/womsoft.conf`:

```
server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl;
    server_name yourdomain.com;

    ssl_certificate /etc/nginx/ssl/certificate.crt;
    ssl_certificate_key /etc/nginx/ssl/private.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    location / {
        proxy_pass http://womsoft:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 4. SSL Certificates

Place your SSL certificate and private key in `./nginx/ssl/`:
- `certificate.crt`: SSL certificate
- `private.key`: Private key

For development/testing, you can generate self-signed certificates:

```
openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout ./nginx/ssl/private.key -out ./nginx/ssl/certificate.crt
```

### 5. Deploy the Application

Start the containers:

```
docker-compose -f docker-compose.prod.yml up -d
```

### 6. Verify the Deployment

Check if containers are running:

```
docker-compose -f docker-compose.prod.yml ps
```

Verify the application is accessible:

```
curl -k https://yourdomain.com/api/v1/health
```

## Backup and Data Management

### Database Backup

Create regular backups of the database file:

```
docker-compose -f docker-compose.prod.yml exec womsoft cp /app/data/prod.db /app/data/backups/prod_$(date +%Y%m%d_%H%M%S).db
```

### Restore from Backup

To restore from a backup:

```
docker-compose -f docker-compose.prod.yml down
cp ./data/backups/prod_YYYYMMDD_HHMMSS.db ./data/prod.db
docker-compose -f docker-compose.prod.yml up -d
```

## Updating the Application

To deploy a new version:

1. Pull the latest image:
   docker pull womsoft-server:latest

2. Restart the services:
   `docker-compose -f docker-compose.prod.yml down`
   `docker-compose -f docker-compose.prod.yml up -d`

## Monitoring and Logs

View application logs:

```
docker-compose -f docker-compose.prod.yml logs -f womsoft
```

View nginx logs:

```
docker-compose -f docker-compose.prod.yml logs -f nginx
```

## Troubleshooting

### Common Issues

1. **Connection Refused**
   - Check if containers are running
   - Verify nginx configuration
   - Ensure ports are not blocked by firewall

2. **SSL Certificate Issues**
   - Verify certificates are correctly placed
   - Check certificate expiration dates

3. **Application Errors**
   - Check application logs
   - Verify environment variables

<!-- TODO: Add specific troubleshooting for your application -->