# Docker Deployment Guide

## Overview

This application is designed to run in a Dockerized multi-service architecture with three main services:
- **Go Service**: Dictionary scraping service (port 8080)
- **Python Service**: FastAPI backend with authentication and word management (port 8000)
- **Frontend**: Next.js web application (port 3000)

## Service Names

The following service names are used in Docker Compose:

- `vocabulary-app-go-service`: Go scraping service
- `vocabulary-app-python-service`: Python FastAPI backend
- `vocabulary-app-frontend`: Next.js frontend

These service names are used for internal Docker networking.

## Quick Start with Docker Compose

### Prerequisites

- Docker and Docker Compose installed
- MySQL database (can be added to docker-compose.yml)

### 1. Environment Setup

Create a `.env` file in the project root for the Go service (if needed):

```bash
# Go service environment (optional)
```

Create a `.env` file in `backend/python-service/`:

```bash
DB_HOST=localhost  # or your MySQL container name
DB_USER=vocabapp
DB_PASSWORD=your_password
DB_NAME=vocabulary_app
DB_PORT=3306
SECRET_KEY=your-secret-key-here-min-32-chars
```

Create a `.env.local` file in `frontend/` for local development:

```bash
# For local development outside Docker
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000

# This is the default when running inside Docker (no need to set):
# NEXT_PUBLIC_API_URL=http://vocabulary-app-python-service:8000
```

### 2. Start Services

```bash
# Build and start all services
docker-compose up --build

# Or run in detached mode
docker-compose up -d --build
```

### 3. Access the Application

- **Frontend**: http://localhost:3000
- **Python API**: http://localhost:8000
- **Go Scraper**: http://localhost:8080

## Docker Compose Configuration

The `docker-compose.yml` defines three services with proper naming:

```yaml
services:
  vocabulary-app-go-service:
    build: ./backend/go-service
    container_name: vocabulary-app-go-service
    ports:
      - "8080:8080"

  vocabulary-app-python-service:
    build: ./backend/python-service
    container_name: vocabulary-app-python-service
    ports:
      - "8000:8000"

  vocabulary-app-frontend:
    build: ./frontend
    container_name: vocabulary-app-frontend
    ports:
      - "3000:3000"
```

## Proxy Manager Setup (https://vocabulary-app.local)

To run the application behind a proxy manager at `https://vocabulary-app.local`:

### 1. Update CORS Settings

The Python service already includes the proxy URL in CORS origins:

```python
allow_origins=[
    "http://localhost:3000", 
    "http://127.0.0.1:3000", 
    "https://vocabulary-app.local",  # Proxy manager URL
    "http://vocabulary-app.local:3000",
    # ...
]
```

### 2. Configure Your Proxy Manager

Use a reverse proxy like Nginx or Traefik to route traffic:

**Nginx Example:**

```nginx
server {
    listen 443 ssl;
    server_name vocabulary-app.local;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    # Frontend
    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # Python API
    location /api/ {
        proxy_pass http://localhost:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # Go Scraper API
    location /scraper/ {
        proxy_pass http://localhost:8080/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 3. Update Frontend Environment

For production with proxy manager, create `frontend/.env.production`:

```bash
NEXT_PUBLIC_API_URL=https://vocabulary-app.local/api
```

## Service Communication

### Internal Docker Network

Services communicate internally using Docker DNS:
- Go service: `http://vocabulary-app-go-service:8080`
- Python service: `http://vocabulary-app-python-service:8000`
- Frontend (server-side): Uses internal names for API routes

### External Access

External clients access services through exposed ports:
- Go service: `http://localhost:8080`
- Python service: `http://localhost:8000`
- Frontend: `http://localhost:3000`

## Environment Variables

### Python Service

Required environment variables in `backend/python-service/.env`:

| Variable | Description | Example |
|----------|-------------|---------|
| `DB_HOST` | Database host | `localhost` or `mysql` |
| `DB_USER` | Database user | `vocabapp` |
| `DB_PASSWORD` | Database password | `secure_password` |
| `DB_NAME` | Database name | `vocabulary_app` |
| `DB_PORT` | Database port | `3306` |
| `SECRET_KEY` | JWT secret key (32+ chars) | Generate with `openssl rand -hex 32` |

### Frontend

Optional environment variable in `frontend/.env.local`:

| Variable | Description | Default |
|----------|-------------|---------|
| `NEXT_PUBLIC_API_URL` | Backend API URL | `http://vocabulary-app-python-service:8000` (Docker) |

## Development Workflow

### Local Development (Outside Docker)

1. **Backend Services**: Run Python and Go services locally
2. **Frontend**: Set `NEXT_PUBLIC_API_URL=http://127.0.0.1:8000` in `.env.local`
3. **Database**: Run MySQL locally or in Docker

### Docker Development

1. **Volume Mounts**: Code changes auto-reload (configured in docker-compose.yml)
2. **Logs**: View with `docker-compose logs -f [service-name]`
3. **Rebuild**: After dependency changes, run `docker-compose up --build`

## Adding MySQL to Docker Compose

To include MySQL in your stack, add this to `docker-compose.yml`:

```yaml
  mysql:
    image: mysql:8.0
    container_name: vocabulary-app-mysql
    environment:
      MYSQL_ROOT_PASSWORD: root_password
      MYSQL_DATABASE: vocabulary_app
      MYSQL_USER: vocabapp
      MYSQL_PASSWORD: secure_password
    ports:
      - "3306:3306"
    volumes:
      - mysql_data:/var/lib/mysql
      - ./backend/schema.sql:/docker-entrypoint-initdb.d/schema.sql

volumes:
  mysql_data:
```

Then update Python service's `.env`:
```bash
DB_HOST=mysql  # Use Docker service name
```

## Troubleshooting

### Service Can't Connect

**Problem**: Frontend can't reach Python service

**Solution**: 
- Inside Docker: Use `http://vocabulary-app-python-service:8000`
- Outside Docker: Use `http://localhost:8000` or `http://127.0.0.1:8000`

### CORS Errors

**Problem**: CORS blocking requests from proxy

**Solution**: Add your proxy URL to `backend/python-service/main.py` CORS origins:
```python
allow_origins=[
    # ... existing origins
    "https://your-proxy-domain.com",
]
```

### Port Already in Use

**Problem**: Port 3000, 8000, or 8080 already in use

**Solution**: Change the port mapping in `docker-compose.yml`:
```yaml
ports:
  - "3001:3000"  # Map external port 3001 to internal 3000
```

## Production Deployment

### Security Checklist

- [ ] Generate strong `SECRET_KEY` for JWT
- [ ] Use environment-specific database credentials
- [ ] Enable HTTPS with valid SSL certificates
- [ ] Configure proper CORS origins (remove `localhost` in production)
- [ ] Set up firewall rules
- [ ] Enable rate limiting on API endpoints
- [ ] Regular database backups
- [ ] Monitor logs and errors

### Performance Optimization

- [ ] Use CDN for frontend assets
- [ ] Enable caching for API responses
- [ ] Configure database connection pooling
- [ ] Use production builds (no hot reload)
- [ ] Optimize Docker images (multi-stage builds)

## Useful Commands

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f

# Rebuild specific service
docker-compose up -d --build vocabulary-app-python-service

# Execute command in running container
docker-compose exec vocabulary-app-python-service bash

# Check running containers
docker ps

# Clean up unused images
docker system prune -a
```
