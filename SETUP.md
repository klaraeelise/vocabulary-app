# Setup Guide

This guide will help you set up the Vocabulary App on your local machine.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Database Setup](#database-setup)
3. [Backend Setup](#backend-setup)
4. [Frontend Setup](#frontend-setup)
5. [Running the Application](#running-the-application)
6. [Troubleshooting](#troubleshooting)

---

## Prerequisites

Ensure you have the following installed:

- **Docker & Docker Compose** (recommended) OR:
  - Python 3.11 or higher
  - Go 1.21 or higher
  - Node.js 18 or higher
  - MySQL 8.0 or higher

---

## Quick Start with Docker

```bash
# 1. Clone the repository
git clone https://github.com/klaraeelise/vocabulary-app.git
cd vocabulary-app

# 2. Create environment file
cp .env.example .env
# Edit .env with your settings

# 3. Start all services
docker-compose up -d

# 4. Check logs
docker-compose logs -f

# Access the application:
# - Frontend: http://localhost:3000
# - Python API: http://localhost:8000
# - Go Scraper: http://localhost:8080
```

---

## Manual Setup

### 1. Database Setup

#### Install MySQL

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install mysql-server
sudo mysql_secure_installation
```

**macOS:**
```bash
brew install mysql
brew services start mysql
```

**Windows:**
Download and install from [MySQL Downloads](https://dev.mysql.com/downloads/installer/)

#### Create Database

```bash
# Login to MySQL
mysql -u root -p

# Create database and user
CREATE DATABASE vocabulary_app;
CREATE USER 'vocabapp'@'localhost' IDENTIFIED BY 'secure_password_here';
GRANT ALL PRIVILEGES ON vocabulary_app.* TO 'vocabapp'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

#### Run Schema

```bash
mysql -u vocabapp -p vocabulary_app < backend/schema.sql
```

#### Verify Schema

```bash
mysql -u vocabapp -p vocabulary_app -e "SHOW TABLES;"
```

You should see:
- languages
- word_types
- users
- words
- meanings
- user_progress
- user_statistics

---

### 2. Backend Setup

#### Python Service

```bash
cd backend/python-service

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On Linux/macOS:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Create .env file
cat > .env << EOF
DB_HOST=localhost
DB_USER=vocabapp
DB_PASSWORD=secure_password_here
DB_NAME=vocabulary_app
DB_PORT=3306
SECRET_KEY=$(python -c "import secrets; print(secrets.token_hex(32))")
EOF

# Test database connection
python -c "from database import get_connection; conn = get_connection(); print('✅ Database connected')"

# Start the service
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The Python service should now be running on http://localhost:8000

#### Go Service

```bash
cd backend/go-service

# Install dependencies
go mod download

# Build the service
go build -o scraper

# Run the service
./scraper
# Or with go run:
go run main.go
```

The Go service should now be running on http://localhost:8080

**Testing Go Service:**
```bash
curl "http://localhost:8080/api/scrape?word=hei"
```

---

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

The frontend should now be running on http://localhost:3000

---

## Running the Application

### Starting All Services

**Terminal 1 - Python Service:**
```bash
cd backend/python-service
source venv/bin/activate
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Go Service:**
```bash
cd backend/go-service
go run main.go
```

**Terminal 3 - Frontend:**
```bash
cd frontend
npm run dev
```

### First-Time Setup

1. **Create an account:**
   - Go to http://localhost:3000/auth/register
   - Enter your email and password
   - Click "Register"

2. **Login:**
   - Go to http://localhost:3000/auth/login
   - Enter your credentials
   - You'll be redirected to the homepage

3. **Add your first word:**
   - Click "Add Flashcard"
   - Fill in word details
   - Add meanings/translations
   - Click "Add Word"

4. **Start learning:**
   - Click "Study" to review words
   - Rate your recall difficulty
   - Build your learning streak!

---

## Testing the API

### Check Python Service

```bash
# Test root endpoint
curl http://localhost:8000/

# Test database connection
curl http://localhost:8000/test-db

# Get languages
curl http://localhost:8000/languages

# Get word types
curl http://localhost:8000/word_types
```

### Check Go Service

```bash
# Test scraper with Norwegian word
curl "http://localhost:8080/api/scrape?word=hei"
```

### Check Frontend

Open browser to http://localhost:3000

---

## Environment Configuration

### Python Service (.env)

Required variables:
```env
DB_HOST=localhost        # Database host
DB_USER=vocabapp        # Database user
DB_PASSWORD=password    # Database password
DB_NAME=vocabulary_app  # Database name
DB_PORT=3306           # MySQL port
SECRET_KEY=<generate>  # JWT secret key (32+ chars)
```

### Generate Secure Secret Key

```bash
# Python method
python -c "import secrets; print(secrets.token_hex(32))"

# OpenSSL method
openssl rand -hex 32

# Node.js method
node -e "console.log(require('crypto').randomBytes(32).toString('hex'))"
```

---

## Troubleshooting

### Common Issues

#### 1. Database Connection Failed

**Error:** `mysql.connector.errors.DatabaseError: 2003`

**Solutions:**
- Check MySQL is running: `sudo systemctl status mysql`
- Verify credentials in .env file
- Check firewall settings
- Ensure database exists: `mysql -u root -p -e "SHOW DATABASES;"`

#### 2. Port Already in Use

**Error:** `Address already in use: 8000` (or 3000, 8080)

**Solutions:**
```bash
# Find process using port
lsof -i :8000

# Kill process
kill -9 <PID>

# Or use different port
uvicorn main:app --port 8001
```

#### 3. Module Not Found (Python)

**Error:** `ModuleNotFoundError: No module named 'fastapi'`

**Solutions:**
```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

#### 4. Go Dependencies Error

**Error:** `package X is not in GOROOT`

**Solutions:**
```bash
# Update Go modules
go mod tidy
go mod download

# Clear module cache
go clean -modcache
```

#### 5. Frontend Build Errors

**Error:** `Module not found: Can't resolve '@/lib/auth'`

**Solutions:**
```bash
# Clear node modules and reinstall
rm -rf node_modules package-lock.json
npm install

# Clear Next.js cache
rm -rf .next
npm run dev
```

#### 6. CORS Errors in Browser

**Error:** `Access-Control-Allow-Origin`

**Solution:**
Check that frontend is accessing correct API URLs and CORS is configured in `main.py`:
```python
allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"]
```

#### 7. JWT Token Expired

**Error:** `401 Unauthorized: Token has expired`

**Solution:**
This is expected after 24 hours. Simply log in again.

#### 8. Go Scraper Times Out

**Error:** Scraper takes too long or fails

**Solutions:**
- Check internet connection
- Verify ordbokene.no is accessible
- Increase timeout in Go service
- Check Chrome/Chromium is installed (required by chromedp)

---

## Production Deployment

### Security Checklist

- [ ] Change SECRET_KEY to a strong random value
- [ ] Use environment-specific database credentials
- [ ] Enable SSL/TLS for database connections
- [ ] Use HTTPS for frontend
- [ ] Configure proper CORS origins
- [ ] Set up firewall rules
- [ ] Enable rate limiting
- [ ] Regular database backups
- [ ] Monitor error logs

### Environment-Specific Settings

**Development:**
```env
DEBUG=True
LOG_LEVEL=DEBUG
```

**Production:**
```env
DEBUG=False
LOG_LEVEL=INFO
ALLOWED_HOSTS=yourdomain.com
```

---

## Updating the Application

```bash
# Pull latest changes
git pull origin main

# Update Python dependencies
cd backend/python-service
source venv/bin/activate
pip install -r requirements.txt

# Update Go dependencies
cd backend/go-service
go mod tidy

# Update Frontend dependencies
cd frontend
npm install

# Update database schema
mysql -u vocabapp -p vocabulary_app < backend/schema.sql
```

---

## Getting Help

- **Documentation:** See README.md, API_DOCUMENTATION.md, ARCHITECTURE.md
- **Issues:** https://github.com/klaraeelise/vocabulary-app/issues
- **Logs:** Check service logs for error messages

---

## Next Steps

After successful setup:

1. Read [API_DOCUMENTATION.md](./API_DOCUMENTATION.md) for API usage
2. Check [ARCHITECTURE.md](./ARCHITECTURE.md) to understand the system
3. Review [ROADMAP.md](./ROADMAP.md) for upcoming features
4. Start building your vocabulary!

---

*Last Updated: December 2024*
