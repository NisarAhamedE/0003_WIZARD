# Docker Quick Reference - Multi-Wizard Platform

## 🎯 TL;DR

**For Development**: Keep using your current local setup (venv + npm start)
**For Deployment**: Use Docker production setup
**Changes in Docker**: Instant with dev mode, rebuild needed for prod mode

---

## 🚀 Common Commands

### Local Development (Recommended) ⭐
```bash
# Start backend
cd backend
venv\Scripts\python -m uvicorn app.main:app --reload --port 8000

# Start frontend (new terminal)
cd frontend
npm start
```

### Docker Development (Optional)
```bash
# Start all services with hot reload
docker-compose -f docker-compose.dev.yml up

# Start in background
docker-compose -f docker-compose.dev.yml up -d

# View logs
docker-compose -f docker-compose.dev.yml logs -f

# Stop services (keep data)
docker-compose -f docker-compose.dev.yml down

# Stop and delete data
docker-compose -f docker-compose.dev.yml down -v

# Restart after requirements.txt or package.json change
docker-compose -f docker-compose.dev.yml up --build
```

### Docker Production
```bash
# Build and start
docker-compose -f docker-compose.prod.yml up --build -d

# View logs
docker-compose -f docker-compose.prod.yml logs -f

# Stop
docker-compose -f docker-compose.prod.yml down

# Full restart
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml up --build -d
```

---

## 🔄 Do I Need to Rebuild?

### ✅ NO Rebuild (Instant Changes) - Dev Mode Only

**Backend Changes:**
- ✅ Edit any .py file → Auto-reload (< 2 seconds)
- ✅ Edit config.py → Auto-reload
- ✅ Add new endpoint → Auto-reload
- ✅ Change existing code → Auto-reload

**Frontend Changes:**
- ✅ Edit .tsx/.ts files → Hot-reload (< 1 second)
- ✅ Edit .css files → Hot-reload
- ✅ Add new component → Hot-reload
- ✅ Change existing UI → Hot-reload

### ⚠️ Rebuild Required - Both Dev and Prod

**Package Changes:**
- ❌ Add to requirements.txt → Rebuild backend
  ```bash
  docker-compose -f docker-compose.dev.yml up --build backend
  ```
- ❌ Add to package.json → Rebuild frontend
  ```bash
  docker-compose -f docker-compose.dev.yml up --build frontend
  ```

**Docker Configuration:**
- ❌ Change Dockerfile → Rebuild
- ❌ Change docker-compose.yml → Restart
  ```bash
  docker-compose -f docker-compose.dev.yml down
  docker-compose -f docker-compose.dev.yml up
  ```

**Database Schema:**
- ❌ Change models → Run migration
  ```bash
  # Inside container
  docker exec -it wizard-backend-dev bash
  alembic revision --autogenerate -m "description"
  alembic upgrade head
  exit
  ```

---

## 📋 Useful Docker Commands

### Container Management
```bash
# List running containers
docker ps

# List all containers
docker ps -a

# Access backend shell
docker exec -it wizard-backend-dev bash

# Access frontend shell
docker exec -it wizard-frontend-dev sh

# Access database
docker exec -it wizard-db-dev psql -U postgres -d wizarddb

# View container logs
docker logs wizard-backend-dev
docker logs wizard-frontend-dev

# Follow logs in real-time
docker logs -f wizard-backend-dev
```

### Image Management
```bash
# List images
docker images

# Remove unused images
docker image prune

# Remove specific image
docker rmi wizard-backend

# Build specific service
docker-compose -f docker-compose.dev.yml build backend
```

### Volume Management
```bash
# List volumes
docker volume ls

# Inspect volume
docker volume inspect 0003_wizard_postgres_data_dev

# Remove all unused volumes
docker volume prune

# Remove specific volume
docker volume rm 0003_wizard_postgres_data_dev
```

### Network Management
```bash
# List networks
docker network ls

# Inspect network
docker network inspect 0003_wizard_wizard-network

# Remove unused networks
docker network prune
```

### System Cleanup
```bash
# Remove all stopped containers, unused networks, dangling images
docker system prune

# Remove everything (including volumes)
docker system prune -a --volumes

# Check disk usage
docker system df
```

---

## 🐛 Troubleshooting

### Backend Not Starting
```bash
# Check logs
docker logs wizard-backend-dev

# Common fixes:
# 1. Database not ready → Wait for health check
docker-compose -f docker-compose.dev.yml up db
# Wait for "database system is ready to accept connections"

# 2. Port conflict → Kill local backend
taskkill /F /IM python.exe

# 3. Code error → Check logs for Python traceback
docker logs wizard-backend-dev --tail 50
```

### Frontend Not Starting
```bash
# Check logs
docker logs wizard-frontend-dev

# Common fixes:
# 1. Port 3000 in use → Kill local frontend
taskkill /F /PID <process_id>

# 2. Build errors → Rebuild
docker-compose -f docker-compose.dev.yml up --build frontend

# 3. Hot reload not working (Windows) → Already fixed in docker-compose.dev.yml
# CHOKIDAR_USEPOLLING: true
```

### Database Connection Errors
```bash
# Test database connectivity
docker exec wizard-backend-dev psql -U postgres -h db -d wizarddb

# Check database is running
docker ps | findstr wizard-db

# Restart database
docker-compose -f docker-compose.dev.yml restart db

# Reset database (DELETES ALL DATA!)
docker-compose -f docker-compose.dev.yml down -v
docker-compose -f docker-compose.dev.yml up db
```

### Changes Not Reflecting
```bash
# 1. Verify volume mounts
docker-compose -f docker-compose.dev.yml config

# 2. Check if container is running
docker ps

# 3. Restart the service
docker-compose -f docker-compose.dev.yml restart backend

# 4. Nuclear option: full rebuild
docker-compose -f docker-compose.dev.yml down -v
docker-compose -f docker-compose.dev.yml up --build
```

### Out of Disk Space
```bash
# Check disk usage
docker system df

# Clean up
docker system prune -a --volumes

# Remove old images
docker image prune -a

# Remove unused volumes
docker volume prune
```

---

## 🌐 Accessing Services

### Local Development
```
Frontend:   http://localhost:3000
Backend:    http://localhost:8000
API Docs:   http://localhost:8000/docs
Database:   localhost:5432
```

### Docker Development
```
Frontend:   http://localhost:3000
Backend:    http://localhost:8000
API Docs:   http://localhost:8000/docs
Database:   localhost:5432 (accessible from host)
```

### Docker Production
```
Frontend:   http://localhost (port 80)
Backend:    http://localhost/api/v1 (proxied through Nginx)
API Docs:   http://localhost/docs
Database:   Not accessible from host (internal only)
```

---

## 🔐 Environment Variables

### Required Variables (.env file)
```bash
# Database
POSTGRES_DB=wizarddb
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your-secure-password

# Backend
SECRET_KEY=your-very-long-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
ENVIRONMENT=development

# Frontend
REACT_APP_API_URL=http://localhost:8000/api/v1
```

### Copy Template
```bash
# Create .env file from template
cp .env.example .env

# Edit with your values
notepad .env
```

---

## 📊 Health Checks

### Check Backend Health
```bash
# Using curl (in Git Bash or WSL)
curl http://localhost:8000/

# Using PowerShell
Invoke-WebRequest -Uri http://localhost:8000/

# Using Docker health check
docker inspect --format='{{.State.Health.Status}}' wizard-backend-dev
```

### Check Frontend Health
```bash
# Using curl
curl http://localhost:3000/

# Using Docker health check
docker inspect --format='{{.State.Health.Status}}' wizard-frontend-dev
```

### Check Database Health
```bash
# Using Docker health check
docker inspect --format='{{.State.Health.Status}}' wizard-db-dev

# Using psql
docker exec wizard-db-dev pg_isready -U postgres
```

---

## 🔄 Database Operations

### Run Migrations
```bash
# Inside backend container
docker exec -it wizard-backend-dev bash
alembic upgrade head
exit

# Or from host (if alembic installed locally)
cd backend
venv\Scripts\alembic upgrade head
```

### Create Migration
```bash
# Inside backend container
docker exec -it wizard-backend-dev bash
alembic revision --autogenerate -m "Add new field"
exit
```

### Database Backup
```bash
# Dump database to file
docker exec wizard-db-dev pg_dump -U postgres wizarddb > backup.sql

# Restore from file
docker exec -i wizard-db-dev psql -U postgres wizarddb < backup.sql
```

### Access Database Shell
```bash
# PostgreSQL shell
docker exec -it wizard-db-dev psql -U postgres -d wizarddb

# Common queries:
\dt              # List tables
\d wizards       # Describe wizards table
SELECT * FROM wizards LIMIT 5;
\q               # Quit
```

---

## 📦 Production Deployment

### Pre-Deployment Checklist
```bash
# 1. Update .env with production values
# 2. Test production build locally
docker-compose -f docker-compose.prod.yml up --build

# 3. Verify all services healthy
docker ps

# 4. Test API endpoints
curl http://localhost/api/v1/wizards

# 5. Test frontend
# Open http://localhost in browser

# 6. Check logs for errors
docker-compose -f docker-compose.prod.yml logs
```

### Deploy to Server
```bash
# 1. Copy files to server
scp -r . user@server:/path/to/app

# 2. SSH into server
ssh user@server

# 3. Navigate to app directory
cd /path/to/app

# 4. Create .env file with production values
nano .env

# 5. Start production containers
docker-compose -f docker-compose.prod.yml up -d

# 6. Check status
docker ps
docker-compose -f docker-compose.prod.yml logs
```

---

## 🎯 Quick Decision Guide

**I want to...**

- 🔧 **Add a new feature** → Use local dev (venv + npm start)
- 🐛 **Fix a bug** → Use local dev (fastest debugging)
- 🧪 **Test database migration** → Use Docker dev (isolated environment)
- 🚀 **Deploy to production** → Use Docker prod
- 👥 **Onboard new developer** → Give them Docker dev setup
- 🔍 **Debug production issue** → Use Docker prod locally
- ⚡ **Fastest iteration** → Use local dev
- 🔒 **Test production build** → Use Docker prod

---

## 📚 Documentation Files

- **DEVELOPMENT_WITH_DOCKER.md** - Comprehensive development guide
- **DOCKER_DEVELOPMENT_WORKFLOW.md** - Visual workflow diagrams
- **DOCKER_DEPLOYMENT.md** - Production deployment guide
- **DOCKER_QUICK_REF.md** - Full command reference
- **DOCKER_CHEAT_SHEET.md** - This file (quick lookup)

---

## ✅ Your Current Recommended Setup

**For Daily Work:**
```bash
# Terminal 1: Backend
cd C:\000_PROJECT\0003_WIZARD\backend
venv\Scripts\python -m uvicorn app.main:app --reload --port 8000

# Terminal 2: Frontend
cd C:\000_PROJECT\0003_WIZARD\frontend
npm start
```

**Before Deploying:**
```bash
# Test production build
cd C:\000_PROJECT\0003_WIZARD
docker-compose -f docker-compose.prod.yml up --build
```

---

**Need More Help?**
- See full documentation in [DEVELOPMENT_WITH_DOCKER.md](./DEVELOPMENT_WITH_DOCKER.md)
- Visual workflow guide: [DOCKER_DEVELOPMENT_WORKFLOW.md](./DOCKER_DEVELOPMENT_WORKFLOW.md)
- Production deployment: [DOCKER_DEPLOYMENT.md](./DOCKER_DEPLOYMENT.md)
