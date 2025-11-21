# 🚂 Railway Deployment Guide - Multi-Wizard Platform

## Complete End-to-End Deployment Instructions

This guide walks you through deploying the Multi-Wizard Platform to Railway.app with:
- PostgreSQL Database
- FastAPI Backend
- React Frontend

---

## 📋 Prerequisites

1. ✅ GitHub account with repo: `NisarAhamedE/0003_WIZARD`
2. ✅ Railway account: https://railway.app (sign up with GitHub)
3. ✅ Credit card added to Railway (for $5 free credit/month)

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                    RAILWAY PROJECT                       │
│                                                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    │
│  │  PostgreSQL │  │   Backend   │  │  Frontend   │    │
│  │  (Database) │◄─│  (FastAPI)  │◄─│   (React)   │    │
│  │             │  │             │  │   + Nginx   │    │
│  │  Port: 5432 │  │  Port: 8080 │  │  Port: 80   │    │
│  └─────────────┘  └─────────────┘  └─────────────┘    │
│                          │                │            │
│                          ▼                ▼            │
│                   Public URL        Public URL         │
│            xxx.up.railway.app   yyy.up.railway.app    │
└─────────────────────────────────────────────────────────┘
```

---

## 🚀 Step-by-Step Deployment

### Step 1: Create Railway Project

1. Go to https://railway.app
2. Click **"New Project"**
3. Select **"Empty Project"** (we'll add services manually)
4. Name your project (e.g., "wizard-platform")

---

### Step 2: Add PostgreSQL Database

1. In your project, click **"+ New"**
2. Select **"Database"**
3. Choose **"PostgreSQL"**
4. Wait for deployment (~30 seconds)
5. Click on PostgreSQL service → **"Variables"** tab
6. **Copy the `DATABASE_URL`** (you'll need this later)

**Your DATABASE_URL looks like:**
```
postgresql://postgres:xxxxx@postgres.railway.internal:5432/railway
```

---

### Step 3: Deploy Backend Service

#### 3.1 Create Backend Service

1. Click **"+ New"**
2. Select **"GitHub Repo"**
3. Choose: `NisarAhamedE/0003_WIZARD`
4. Railway will start deploying...

#### 3.2 Backend Will Auto-Deploy

Since there's a `Dockerfile` in the root, Railway will use it to build the backend.
Wait for the build to complete.

#### 3.3 Configure Backend Variables

1. Click on your backend service
2. Go to **"Variables"** tab
3. Add these variables:

| Variable | Value |
|----------|-------|
| `DATABASE_URL` | `${{Postgres.DATABASE_URL}}` |
| `SECRET_KEY` | `a8f5f167f44f4964e6c998dee827110c4e7a1c73f68d0a5c4a6f3b8c9d0e1f2a` |
| `ALGORITHM` | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30` |
| `ENVIRONMENT` | `production` |

**Note:** `${{Postgres.DATABASE_URL}}` automatically references the PostgreSQL service.

#### 3.4 Generate Backend Public URL

1. Go to **"Settings"** tab
2. Scroll to **"Networking"** → **"Public Networking"**
3. Enter port: `8080`
4. Click **"Generate Domain"**
5. **Copy your backend URL** (e.g., `0003wizard.up.railway.app`)

---

### Step 4: Deploy Frontend Service

#### 4.1 Create Frontend Service

1. Click **"+ New"**
2. Select **"GitHub Repo"**
3. Choose: `NisarAhamedE/0003_WIZARD` (same repo)
4. **WAIT! Don't deploy yet!**

#### 4.2 Set Root Directory (CRITICAL!)

1. Click on the new service
2. Go to **"Settings"** tab
3. Find **"Source"** section
4. Set **"Root Directory"** to: `frontend`
5. Click outside to save

#### 4.3 Configure Frontend Variables

1. Go to **"Variables"** tab
2. Add this variable:

| Variable | Value |
|----------|-------|
| `REACT_APP_API_URL` | `https://YOUR-BACKEND-URL/api/v1` |

**Replace `YOUR-BACKEND-URL`** with your actual backend URL from Step 3.4.

Example:
```
REACT_APP_API_URL=https://0003wizard.up.railway.app/api/v1
```

#### 4.4 Trigger Redeploy

1. Go to **"Deployments"** tab
2. Click **"Redeploy"** (or the 3 dots → Redeploy)
3. Wait for build to complete

#### 4.5 Generate Frontend Public URL

1. Go to **"Settings"** tab
2. Scroll to **"Networking"** → **"Public Networking"**
3. Enter port: `80`
4. Click **"Generate Domain"**
5. **This is your app URL!** 🎉

---

## 📝 Summary: All Services Configuration

### PostgreSQL Database
| Setting | Value |
|---------|-------|
| Service | Database → PostgreSQL |
| Auto-configured | Yes |

### Backend Service
| Setting | Value |
|---------|-------|
| Source | GitHub: NisarAhamedE/0003_WIZARD |
| Root Directory | (empty - uses root) |
| Dockerfile | `./Dockerfile` (auto-detected) |
| Port | 8080 |

**Variables:**
```
DATABASE_URL=${{Postgres.DATABASE_URL}}
SECRET_KEY=a8f5f167f44f4964e6c998dee827110c4e7a1c73f68d0a5c4a6f3b8c9d0e1f2a
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
ENVIRONMENT=production
```

### Frontend Service
| Setting | Value |
|---------|-------|
| Source | GitHub: NisarAhamedE/0003_WIZARD |
| Root Directory | `frontend` |
| Dockerfile | `frontend/Dockerfile` (auto-detected) |
| Port | 80 |

**Variables:**
```
REACT_APP_API_URL=https://YOUR-BACKEND-URL/api/v1
```

---

## 🔧 Troubleshooting

### Problem: "Railpack could not determine how to build"

**Solution:** Railway isn't finding the Dockerfile.
1. For backend: Dockerfile is in root ✅
2. For frontend: Set Root Directory to `frontend`

### Problem: Frontend builds with wrong Dockerfile

**Cause:** Root Directory not set correctly.
**Solution:**
1. Go to frontend service → Settings
2. Set Root Directory: `frontend`
3. Redeploy

### Problem: "COPY backend/app" error in frontend build

**Cause:** Frontend is using root Dockerfile instead of frontend/Dockerfile.
**Solution:** Set Root Directory to `frontend` and redeploy.

### Problem: Backend can't connect to database

**Cause:** DATABASE_URL not set correctly.
**Solution:**
1. Check PostgreSQL service is running
2. Use `${{Postgres.DATABASE_URL}}` syntax
3. Or copy the actual URL from PostgreSQL Variables tab

### Problem: Frontend can't reach backend API

**Cause:** REACT_APP_API_URL wrong or missing.
**Solution:**
1. Verify backend has a public URL
2. Set `REACT_APP_API_URL=https://BACKEND-URL/api/v1`
3. Redeploy frontend

### Problem: Health check failing

**Solution:**
1. Backend: Uses port 8080, health check on `/`
2. Frontend: Uses port 80, health check on `/health`
3. Verify these ports in Networking settings

---

## 🔄 Redeployment & Updates

### Automatic Deploys
Railway auto-deploys when you push to GitHub:
```bash
git add .
git commit -m "update"
git push origin main
# Railway auto-deploys! ✨
```

### Manual Redeploy
1. Go to service → Deployments tab
2. Click 3 dots (⋮) on latest deployment
3. Click "Redeploy"

### Rebuild from Scratch
1. Go to service → Deployments tab
2. Click 3 dots (⋮)
3. Click "Rebuild" (clears cache)

---

## 💰 Cost Estimation

Railway Pricing:
- **Free tier:** $5 credit/month
- **Usage-based:** Pay for CPU, RAM, network

**Estimated costs for this app:**
| Service | Estimated Cost |
|---------|---------------|
| PostgreSQL | ~$2-3/month |
| Backend | ~$2-3/month |
| Frontend | ~$1-2/month |
| **Total** | **~$5-8/month** |

With $5 free credit, small apps often run free!

---

## ✅ Deployment Checklist

### PostgreSQL Database
- [ ] Created PostgreSQL service
- [ ] Database is running (green status)
- [ ] DATABASE_URL is available

### Backend Service
- [ ] Created from GitHub repo
- [ ] Root Directory: (empty/root)
- [ ] Variables configured:
  - [ ] DATABASE_URL
  - [ ] SECRET_KEY
  - [ ] ALGORITHM
  - [ ] ACCESS_TOKEN_EXPIRE_MINUTES
  - [ ] ENVIRONMENT
- [ ] Build succeeded
- [ ] Public URL generated (port 8080)
- [ ] API accessible: `https://xxx.up.railway.app/`

### Frontend Service
- [ ] Created from GitHub repo
- [ ] Root Directory: `frontend`
- [ ] Variables configured:
  - [ ] REACT_APP_API_URL
- [ ] Build succeeded
- [ ] Public URL generated (port 80)
- [ ] App accessible in browser

---

## 🎉 Success!

Once everything is deployed, you'll have:

| Service | URL |
|---------|-----|
| **Frontend** | `https://xxx-frontend.up.railway.app` |
| **Backend API** | `https://xxx-backend.up.railway.app/api/v1` |
| **API Docs** | `https://xxx-backend.up.railway.app/docs` |

### Test Your Deployment

1. Open frontend URL in browser
2. You should see the login page
3. Register a new account
4. Login and start using the app!

---

## 📚 Additional Resources

- Railway Docs: https://docs.railway.app
- Railway Discord: https://discord.gg/railway
- Project Issues: https://github.com/NisarAhamedE/0003_WIZARD/issues

---

## 🔐 Security Notes

Before going to production:

1. **Change SECRET_KEY** to a unique random value
2. **Set ENVIRONMENT=production** (disables debug mode)
3. **Enable Railway's automatic HTTPS** (enabled by default)
4. **Review public access** to database (should be internal only)

---

**Congratulations! Your Multi-Wizard Platform is now live on Railway!** 🚂🎉
