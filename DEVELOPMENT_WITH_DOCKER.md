# Development Workflow with Docker

## 🎯 Quick Answer to Your Question

**Question**: "If I continue development, how will new changes reflect in Docker?"

**Answer**: With the development Docker setup, your code changes **reflect INSTANTLY** without rebuilding! Here's how:

### ✅ Development Mode (Instant Changes)
```bash
docker-compose -f docker-compose.dev.yml up
```
- ✅ Edit Python files → **Auto-reloads immediately**
- ✅ Edit React files → **Hot reloads in browser**
- ✅ No rebuild needed
- ✅ Same speed as running locally

### ❌ Production Mode (Requires Rebuild)
```bash
docker-compose -f docker-compose.prod.yml up --build
```
- ❌ Edit files → **Must rebuild image**
- ❌ Slower iteration
- ✅ Optimized for deployment

---

## 🔑 Key Concept: Volume Mounts vs. Image Copies

### Development Mode (Volume Mounts)
Your local files are **mounted** into the container:

```yaml
volumes:
  - ./backend:/app          # Your local folder → Container folder
  - ./frontend:/app         # Changes sync instantly!
```

**What This Means**:
- When you edit `backend/app/api/v1/wizards.py` on your computer
- The change is **immediately visible** inside the Docker container
- Uvicorn's `--reload` flag detects the change
- Backend automatically restarts (< 2 seconds)

**Same for Frontend**:
- Edit `frontend/src/pages/DashboardPage.tsx`
- Webpack dev server detects change
- Browser auto-refreshes with new code

### Production Mode (Image Copy)
Your code is **copied** into the image during build:

```dockerfile
COPY . .    # Copies code INTO image
```

**What This Means**:
- Code is baked into the Docker image
- Changes require rebuilding the entire image
- Optimized for speed, not development

---

## 🚀 Recommended Development Workflow

### Option 1: Continue WITHOUT Docker (Recommended) ⭐

**Keep using your current method**:

**Backend:**
```bash
cd backend
venv\Scripts\python -m uvicorn app.main:app --reload --port 8000
```

**Frontend:**
```bash
cd frontend
npm start
```

**Why This is Better for Development:**
- ✅ Faster startup (no Docker overhead)
- ✅ Easier debugging (direct access to logs)
- ✅ Simpler (what you're used to)
- ✅ Same hot reload behavior
- ✅ Direct access to Python debugger

**When to Use Docker:**
- Testing production setup
- Before deploying to server
- Testing database migrations
- Sharing environment with team

---

### Option 2: Develop WITH Docker

If you prefer to use Docker during development:

**Start development environment:**
```bash
# From project root
docker-compose -f docker-compose.dev.yml up
```

**How Changes Reflect:**

#### Backend Changes (Instant)
```bash
# 1. Edit any Python file
# Example: backend/app/api/v1/wizards.py

# 2. Save the file

# 3. Watch Docker logs:
INFO:     Will watch for changes in these directories: ['/app']
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
INFO:     Detected change in 'app/api/v1/wizards.py'
INFO:     Reloading...
INFO:     Application startup complete.

# 4. Changes are LIVE! (usually < 2 seconds)
```

#### Frontend Changes (Instant)
```bash
# 1. Edit any React file
# Example: frontend/src/pages/DashboardPage.tsx

# 2. Save the file

# 3. Webpack compiles automatically:
Compiling...
Compiled successfully!

# 4. Browser auto-refreshes with changes
```

#### Database Changes (Requires Migration)
```bash
# 1. Edit SQLAlchemy model
# Example: backend/app/models/wizard.py

# 2. Create migration inside running container
docker exec -it wizard-backend-dev bash
alembic revision --autogenerate -m "Add new field"
alembic upgrade head
exit

# 3. Changes applied to database
```

---

## 📋 Development Docker Commands

### Start Development Environment
```bash
# Start all services (db, backend, frontend)
docker-compose -f docker-compose.dev.yml up

# Start in background
docker-compose -f docker-compose.dev.yml up -d

# Start only backend and database
docker-compose -f docker-compose.dev.yml up db backend
```

### Stop Development Environment
```bash
# Stop all services
docker-compose -f docker-compose.dev.yml down

# Stop and remove volumes (reset database)
docker-compose -f docker-compose.dev.yml down -v
```

### View Logs
```bash
# All services
docker-compose -f docker-compose.dev.yml logs -f

# Only backend
docker-compose -f docker-compose.dev.yml logs -f backend

# Only frontend
docker-compose -f docker-compose.dev.yml logs -f frontend
```

### Access Container Shell
```bash
# Backend container
docker exec -it wizard-backend-dev bash

# Frontend container
docker exec -it wizard-frontend-dev sh

# Database container
docker exec -it wizard-db-dev psql -U postgres -d wizarddb
```

### Restart Services
```bash
# Restart backend only (after requirements.txt change)
docker-compose -f docker-compose.dev.yml restart backend

# Restart frontend only (after package.json change)
docker-compose -f docker-compose.dev.yml restart frontend
```

---

## 🔄 When Do You Need to Rebuild?

### ✅ NO Rebuild Needed (Changes Reflect Instantly)

**Backend:**
- Python files (.py)
- Configuration files (config.py)
- Templates
- Any file in `backend/` folder

**Frontend:**
- React components (.tsx, .ts)
- CSS files
- Images
- Any file in `frontend/src/` folder

### ⚠️ Rebuild Required

**Backend:**
- `requirements.txt` changed (new Python package)
  ```bash
  docker-compose -f docker-compose.dev.yml up --build backend
  ```

**Frontend:**
- `package.json` changed (new npm package)
  ```bash
  docker-compose -f docker-compose.dev.yml up --build frontend
  ```

**Docker Configuration:**
- `docker-compose.dev.yml` changed
- `Dockerfile.dev` changed
  ```bash
  docker-compose -f docker-compose.dev.yml up --build
  ```

---

## 🆚 Development vs. Production Comparison

| Feature | Development Mode | Production Mode |
|---------|-----------------|-----------------|
| **File Changes** | Instant (volume mount) | Requires rebuild |
| **Backend Command** | `uvicorn --reload` | `uvicorn --workers 4` |
| **Frontend Build** | Dev server (npm start) | Production build (nginx) |
| **Debugging** | Full logs, source maps | Minimal logs |
| **Startup Time** | ~30 seconds | ~10 seconds |
| **Image Size** | Larger (includes dev tools) | Optimized (< 500MB) |
| **Use Case** | Daily development | Deployment to server |
| **Database** | Development data | Production data |
| **Ports** | Backend: 8000, Frontend: 3000 | Frontend: 80 (+ 443 SSL) |

---

## 💡 Best Practice Recommendations

### For Active Development (Now)
**Use your current local setup** (venv + npm start):
```bash
# Backend terminal
cd backend
venv\Scripts\activate
python -m uvicorn app.main:app --reload --port 8000

# Frontend terminal
cd frontend
npm start
```

**Why:**
- Faster iteration
- Easier debugging
- Direct access to Python debugger (breakpoints)
- Simpler error messages
- Less resource usage on your computer

### Before Deploying (Testing)
**Use Docker to test production setup**:
```bash
# Test production build locally
docker-compose -f docker-compose.prod.yml up --build

# Access at http://localhost (port 80)
# Backend proxied through Nginx
```

**Why:**
- Verify production configuration
- Test Nginx reverse proxy
- Ensure environment variables work
- Test multi-worker backend
- Catch deployment issues early

### For Team Collaboration
**Use development Docker** when:
- New team member onboarding
- Ensuring consistent environment across team
- Testing database migrations
- Reproducing bugs in isolated environment

---

## 🐛 Common Development Issues

### Issue 1: Changes Not Reflecting in Docker

**Symptom**: Edit Python/React file but changes don't appear

**Solutions:**
```bash
# 1. Check volume mounts are correct
docker-compose -f docker-compose.dev.yml config

# 2. Restart the specific service
docker-compose -f docker-compose.dev.yml restart backend

# 3. Check container logs for errors
docker-compose -f docker-compose.dev.yml logs backend

# 4. Nuclear option: rebuild everything
docker-compose -f docker-compose.dev.yml down -v
docker-compose -f docker-compose.dev.yml up --build
```

### Issue 2: Frontend Hot Reload Not Working (Windows)

**Symptom**: React changes require manual browser refresh

**Solution**: The dev compose already includes the fix:
```yaml
environment:
  CHOKIDAR_USEPOLLING: true    # ← This fixes Windows hot reload
  WDS_SOCKET_PORT: 3000
```

### Issue 3: Port Conflicts

**Symptom**: `Error: port 8000 already in use`

**Solution**: Stop your local backend first
```bash
# Stop local Python server
# Press Ctrl+C in backend terminal

# Or kill the process
taskkill /F /IM python.exe

# Then start Docker
docker-compose -f docker-compose.dev.yml up
```

### Issue 4: Database Data Lost

**Symptom**: Database resets when restarting Docker

**Why**: You used `down -v` which deletes volumes

**Solution**: Use `down` without `-v` flag:
```bash
# ✅ GOOD: Preserves database data
docker-compose -f docker-compose.dev.yml down

# ❌ BAD: Deletes database data
docker-compose -f docker-compose.dev.yml down -v
```

---

## 🎯 Your Current Situation

Based on the previous conversation, I see you have:
- ✅ Backend running locally on port 8000 (venv)
- ✅ Frontend running locally on port 3000 (npm start)
- ✅ Wizard protection system fully implemented
- ✅ Docker setup now ready for production deployment

### My Recommendation

**For ongoing development:**
👉 **Keep using your current local setup** (venv + npm start)

**For deployment testing:**
👉 **Use `docker-compose.prod.yml`** to test before deploying

**When to switch to Docker development:**
- When you need isolated testing
- Before merging major features
- To test database migrations in isolation
- If sharing work with another developer

---

## 📚 Quick Reference Card

### Local Development (Current Method) ⭐
```bash
# Backend
cd backend && venv\Scripts\python -m uvicorn app.main:app --reload --port 8000

# Frontend
cd frontend && npm start
```

### Docker Development (Optional)
```bash
# Start
docker-compose -f docker-compose.dev.yml up

# Stop (keep data)
docker-compose -f docker-compose.dev.yml down

# Reset everything
docker-compose -f docker-compose.dev.yml down -v && docker-compose -f docker-compose.dev.yml up --build
```

### Docker Production Testing
```bash
# Build and start
docker-compose -f docker-compose.prod.yml up --build

# Access: http://localhost
# API: http://localhost/api/v1
```

---

## ✅ Summary

**Your Question**: "If I continue development, how will new changes reflect in Docker?"

**Answer**:
1. **With development Docker** (`docker-compose.dev.yml`): Changes reflect **INSTANTLY** due to volume mounts
2. **With production Docker** (`docker-compose.prod.yml`): Changes require **rebuilding the image**
3. **Recommendation**: Continue your current local development method (venv + npm start) for daily work
4. **Use Docker**: For testing production setup before deploying to server

**Key Takeaway**: You now have 3 deployment options:
- 🔧 **Local Dev** (current) - Fastest iteration
- 🐳 **Docker Dev** (optional) - Isolated environment with instant changes
- 🚀 **Docker Prod** (deployment) - Ready for server deployment

---

**Need Help?**
- See [DOCKER_DEPLOYMENT.md](./DOCKER_DEPLOYMENT.md) for production deployment guide
- See [DOCKER_QUICK_REF.md](./DOCKER_QUICK_REF.md) for command cheat sheet
