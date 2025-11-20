# 🚂 Deploy to Railway.app - One-Click Deployment

## ⚡ Quick Deploy (5 minutes)

Railway will automatically detect your Docker setup and deploy from GitHub!

---

## 📋 Prerequisites

1. GitHub account with your repo pushed
2. Railway account: https://railway.app (sign up with GitHub)
3. Credit card (Railway gives $5 free credit/month)

---

## 🚀 Step-by-Step Deployment

### Step 1: Create Railway Project

1. Go to https://railway.app
2. Click **"New Project"**
3. Select **"Deploy from GitHub repo"**
4. Choose your repository: `NisarAhamedE/0003_WIZARD`
5. Railway will scan and detect your services

### Step 2: Railway Auto-Detection

Railway will automatically find:
- ✅ `backend/Dockerfile` → Backend service
- ✅ `frontend/Dockerfile` → Frontend service
- ✅ PostgreSQL needed (from docker-compose)

Railway creates 3 services:
1. **PostgreSQL Database** (managed)
2. **Backend** (FastAPI)
3. **Frontend** (React + Nginx)

### Step 3: Configure Environment Variables

**PostgreSQL** (Auto-configured by Railway):
- Railway automatically sets `DATABASE_URL`
- No manual configuration needed! 🎉

**Backend Service** - Add these variables:
```
SECRET_KEY=generate-a-very-long-random-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
ENVIRONMENT=production
```

**Frontend Service** - Add this variable:
```
REACT_APP_API_URL=${{Backend.RAILWAY_PUBLIC_DOMAIN}}/api/v1
```

### Step 4: Configure Build & Deploy

Railway **auto-detects** Docker, so most settings are automatic!

**Backend Service:**
- ✅ Build Command: Auto-detected from Dockerfile
- ✅ Start Command: Auto-detected from Dockerfile CMD
- Root Directory: `backend` (if needed)
- Port: `8000` (Railway auto-detects from EXPOSE)

**Frontend Service:**
- ✅ Build Command: Auto-detected from Dockerfile
- ✅ Start Command: Auto-detected (nginx)
- Root Directory: `frontend` (if needed)
- Port: `80` (Railway auto-detects)

### Step 5: Set Service Dependencies

1. Go to **Backend service settings**
2. Click **Dependencies**
3. Add **PostgreSQL** as dependency
   - This ensures database starts before backend

4. Go to **Frontend service settings**
5. Click **Dependencies**
6. Add **Backend** as dependency
   - This ensures backend starts before frontend

### Step 6: Enable Public URLs

1. Click on **Frontend service**
2. Go to **Settings** → **Networking**
3. Click **Generate Domain**
4. You'll get: `your-app.up.railway.app`

5. Click on **Backend service**
6. Go to **Settings** → **Networking**
7. Click **Generate Domain**
8. You'll get: `your-backend.up.railway.app`

### Step 7: Update Frontend Environment Variable

Now that you have the backend URL:

1. Go to **Frontend service**
2. Update environment variable:
   ```
   REACT_APP_API_URL=https://your-backend.up.railway.app/api/v1
   ```
3. Click **Deploy** to restart with new variable

### Step 8: Run Database Migration

1. Click on **Backend service**
2. Go to **Deployments** tab
3. Find the running deployment
4. Click **"View Logs"** to verify it's running
5. Open **"Shell"** tab (terminal icon)
6. Run migration:
   ```bash
   alembic upgrade head
   ```

### Step 9: Access Your App! 🎉

Your app is now live at:
```
https://your-app.up.railway.app
```

---

## 🎯 Railway Configuration Files (Optional)

Railway works without config files, but you can optimize with these:

### Option 1: Create `railway.toml` (Root directory)

```toml
[build]
builder = "dockerfile"
dockerfilePath = "backend/Dockerfile"

[deploy]
startCommand = "uvicorn app.main:app --host 0.0.0.0 --port $PORT"
healthcheckPath = "/"
healthcheckTimeout = 100
restartPolicyType = "on_failure"
restartPolicyMaxRetries = 10
```

### Option 2: Use Nixpacks (Alternative to Docker)

Railway's Nixpacks can auto-build without Dockerfile:

**For Backend** - Create `nixpacks.toml` in `backend/`:
```toml
[phases.setup]
nixPkgs = ["python311", "postgresql"]

[phases.install]
cmds = ["pip install -r requirements.txt"]

[start]
cmd = "uvicorn app.main:app --host 0.0.0.0 --port $PORT"
```

**For Frontend** - Create `nixpacks.toml` in `frontend/`:
```toml
[phases.setup]
nixPkgs = ["nodejs-18_x"]

[phases.install]
cmds = ["npm ci"]

[phases.build]
cmds = ["npm run build"]

[start]
cmd = "npx serve -s build -l $PORT"
```

**But Docker is recommended** - Your Dockerfiles are production-ready!

---

## 🔧 Railway-Specific Tips

### Automatic Deploys from GitHub

Railway automatically redeploys when you push to GitHub!

1. Go to **Service settings**
2. Enable **"Auto-deploy from GitHub"**
3. Now every `git push` triggers deployment 🚀

### Database Backups

Railway manages PostgreSQL backups:
1. Go to **PostgreSQL service**
2. Click **"Backups"** tab
3. Railway automatically backs up daily
4. Can restore with one click

### Viewing Logs

Real-time logs for debugging:
1. Click on any service
2. Go to **"Deployments"** tab
3. Click on running deployment
4. View **"Logs"** tab

### Scaling (if needed)

Railway allows vertical scaling:
1. Go to **Service settings**
2. Click **"Resources"**
3. Adjust CPU/Memory (costs more)

### Custom Domain (Optional)

Add your own domain:
1. Go to **Frontend service**
2. Click **"Settings"** → **"Domains"**
3. Add custom domain (e.g., `wizards.yourdomain.com`)
4. Update DNS with CNAME record Railway provides

---

## 💰 Railway Pricing

**Free Tier:**
- $5 credit/month (free forever)
- Enough for small apps with light traffic
- Sleeps after inactivity (can disable with paid plan)

**Paid Plans:**
- Developer: $5/month + usage
- Team: $20/month + usage
- Pay only for what you use

**Estimated Cost for This App:**
- Small traffic: ~$5-10/month
- Medium traffic: ~$15-25/month
- PostgreSQL: Included in usage

---

## 🐛 Troubleshooting

### Build Fails: "Cannot find Dockerfile"

**Solution**: Set Root Directory in service settings
1. Go to service **Settings**
2. Set **Root Directory** to `backend` or `frontend`
3. Redeploy

### Backend Can't Connect to Database

**Solution**: Check DATABASE_URL is set
1. Railway auto-sets `${{Postgres.DATABASE_URL}}`
2. Make sure backend depends on PostgreSQL service
3. Check logs for connection errors

### Frontend Can't Reach Backend API

**Solution**: Update REACT_APP_API_URL
1. Get backend public URL from Railway
2. Update frontend environment variable
3. Must include `/api/v1` at the end
4. Redeploy frontend

### Port Binding Error

**Solution**: Railway provides `$PORT` variable
1. Your Dockerfile should use `PORT` env variable
2. Current setup uses port 8000/80 (works on Railway)
3. Railway automatically maps to public URL

### Health Check Failing

**Solution**: Verify health check endpoint
1. Railway checks `/` endpoint by default
2. Your backend has health check at `/`
3. Frontend nginx has `/health` endpoint
4. Adjust in service settings if needed

### Database Migration Not Applied

**Solution**: Run migration manually first time
1. Open backend service **Shell**
2. Run: `alembic upgrade head`
3. For future deploys, can add to Dockerfile:
   ```dockerfile
   CMD alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```

---

## 🔄 Deployment Workflow

### Initial Deployment (One-time)
```
1. Push code to GitHub
2. Create Railway project from GitHub
3. Configure environment variables
4. Set service dependencies
5. Generate public domains
6. Run database migration
7. Access your app!
```

### Updates (Automatic)
```
1. Make changes locally
2. git add . && git commit -m "update"
3. git push
4. Railway auto-deploys! ✨
```

---

## 📊 Monitoring Your Deployment

### Railway Dashboard

1. **Metrics** - CPU, Memory, Network usage
2. **Logs** - Real-time application logs
3. **Deployments** - History of all deployments
4. **Build Logs** - Docker build output
5. **Activity** - All changes and events

### Health Checks

Railway automatically monitors:
- Service uptime
- Health check endpoint responses
- Resource usage
- Restarts on failures

---

## 🎯 Production Checklist

Before going live:

- [ ] Set strong `SECRET_KEY` (32+ characters)
- [ ] Set secure `POSTGRES_PASSWORD`
- [ ] Enable auto-deploy from GitHub
- [ ] Test all API endpoints
- [ ] Test frontend functionality
- [ ] Run database migration
- [ ] Check logs for errors
- [ ] Set up custom domain (optional)
- [ ] Enable Railway backups
- [ ] Test wizard creation and execution
- [ ] Verify user authentication works

---

## 🆚 Railway vs Other Platforms

### Railway Advantages ✅
- ✅ **Easiest Docker deployment** - Auto-detects everything
- ✅ **GitHub integration** - Auto-deploy on push
- ✅ **Managed PostgreSQL** - Automatic backups, no setup
- ✅ **$5 free credit/month** - Perfect for testing
- ✅ **No configuration needed** - Works out of the box
- ✅ **Great developer experience** - Beautiful dashboard

### When NOT to Use Railway ❌
- ❌ Very high traffic (expensive at scale)
- ❌ Need advanced networking (use AWS/GCP)
- ❌ Need multi-region deployment (Railway is single-region)
- ❌ Require 99.99% SLA (Railway is best-effort)

---

## 📚 Additional Resources

- **Railway Docs**: https://docs.railway.app
- **Railway Discord**: https://discord.gg/railway
- **Dockerfile Reference**: https://docs.railway.app/deploy/dockerfiles
- **Environment Variables**: https://docs.railway.app/develop/variables

---

## 🎉 Success!

Your Multi-Wizard Platform is now live on Railway! 🚂

**Next Steps:**
1. Share your app URL with users
2. Monitor logs and metrics
3. Set up custom domain
4. Enable analytics (optional)

**Your App URL:**
```
https://your-app.up.railway.app
```

---

**Need Help?**
- Railway Community: https://discord.gg/railway
- Project Issues: https://github.com/NisarAhamedE/0003_WIZARD/issues
