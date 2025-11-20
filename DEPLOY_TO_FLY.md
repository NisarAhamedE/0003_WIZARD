# ✈️ Deploy to Fly.io - Multi-Region Deployment

## ⚡ Quick Deploy (10 minutes)

Fly.io uses your existing Dockerfiles and runs globally!

---

## 📋 Prerequisites

1. GitHub account with your repo pushed ✅
2. Fly.io account: https://fly.io (sign up free)
3. Credit card (required, but free tier available)
4. Fly CLI installed on your computer

---

## 🔧 Step 1: Install Fly CLI

**Windows:**
```powershell
powershell -Command "iwr https://fly.io/install.ps1 -useb | iex"
```

**Mac/Linux:**
```bash
curl -L https://fly.io/install.sh | sh
```

**Verify installation:**
```bash
fly version
```

---

## 🚀 Step 2: Login to Fly.io

```bash
fly auth login
```

This opens a browser to authenticate.

---

## 📦 Step 3: Create Fly.io Apps

We'll create 3 separate apps (backend, frontend, database):

### Create PostgreSQL Database

```bash
# From project root
fly postgres create --name wizard-db --region iad

# Choose configuration:
# - Development (1GB RAM, 10GB storage) - Free tier
# - Or Production (2GB+ RAM) - Paid
```

**Save the connection string shown!** It looks like:
```
postgres://postgres:password@wizard-db.internal:5432/wizard
```

### Create Backend App

```bash
cd backend
fly launch --name wizard-backend --region iad --no-deploy

# Answer prompts:
# - Choose app name: wizard-backend
# - Choose region: iad (or closest to you)
# - Would you like to set up PostgreSQL? No (we already created it)
# - Would you like to deploy now? No
```

This creates `fly.toml` in the backend folder.

### Create Frontend App

```bash
cd ../frontend
fly launch --name wizard-frontend --region iad --no-deploy

# Answer prompts:
# - Choose app name: wizard-frontend
# - Choose region: iad
# - Would you like to deploy now? No
```

This creates `fly.toml` in the frontend folder.

---

## 🔧 Step 4: Configure Backend

### Edit `backend/fly.toml`

Fly CLI creates this file. Update it:

```toml
app = "wizard-backend"
primary_region = "iad"

[build]
  dockerfile = "Dockerfile"

[env]
  ENVIRONMENT = "production"
  ALGORITHM = "HS256"
  ACCESS_TOKEN_EXPIRE_MINUTES = "30"

[http_service]
  internal_port = 8000
  force_https = true
  auto_stop_machines = true
  auto_start_machines = true
  min_machines_running = 0

[[http_service.checks]]
  grace_period = "10s"
  interval = "30s"
  method = "GET"
  timeout = "5s"
  path = "/"

[[vm]]
  cpu_kind = "shared"
  cpus = 1
  memory_mb = 1024
```

### Set Backend Secrets

```bash
cd backend

# Set database URL (use the connection string from Step 3)
fly secrets set DATABASE_URL="postgres://postgres:password@wizard-db.internal:5432/wizard"

# Generate and set secret key
fly secrets set SECRET_KEY="$(openssl rand -hex 32)"
```

---

## 🔧 Step 5: Configure Frontend

### Edit `frontend/fly.toml`

```toml
app = "wizard-frontend"
primary_region = "iad"

[build]
  dockerfile = "Dockerfile"

[env]
  REACT_APP_API_URL = "https://wizard-backend.fly.dev/api/v1"

[http_service]
  internal_port = 80
  force_https = true
  auto_stop_machines = true
  auto_start_machines = true
  min_machines_running = 0

[[http_service.checks]]
  grace_period = "5s"
  interval = "30s"
  method = "GET"
  timeout = "5s"
  path = "/health"

[[vm]]
  cpu_kind = "shared"
  cpus = 1
  memory_mb = 512
```

**Note**: Replace `wizard-backend.fly.dev` with your actual backend app name.

---

## 🚀 Step 6: Deploy!

### Deploy Backend First

```bash
cd backend
fly deploy

# This will:
# 1. Build Docker image
# 2. Push to Fly.io registry
# 3. Deploy to your region
# 4. Run health checks
```

**Wait for deployment to finish** (2-3 minutes)

Verify backend is running:
```bash
fly status
fly logs
```

### Run Database Migration

```bash
# Connect to backend via SSH
fly ssh console

# Inside the container:
alembic upgrade head
exit
```

### Deploy Frontend

```bash
cd ../frontend
fly deploy
```

**Wait for deployment to finish** (2-3 minutes)

---

## 🌐 Step 7: Access Your App!

Your apps are now live at:

```
Frontend: https://wizard-frontend.fly.dev
Backend:  https://wizard-backend.fly.dev
API Docs: https://wizard-backend.fly.dev/docs
```

---

## 📝 Fly.io Configuration Files

### Backend `fly.toml` (Complete Example)

```toml
# backend/fly.toml
app = "wizard-backend"
primary_region = "iad"

[build]
  dockerfile = "Dockerfile"

[env]
  ENVIRONMENT = "production"
  ALGORITHM = "HS256"
  ACCESS_TOKEN_EXPIRE_MINUTES = "30"

[http_service]
  internal_port = 8000
  force_https = true
  auto_stop_machines = true
  auto_start_machines = true
  min_machines_running = 0

  [[http_service.checks]]
    grace_period = "10s"
    interval = "30s"
    method = "GET"
    timeout = "5s"
    path = "/"

[[vm]]
  cpu_kind = "shared"
  cpus = 1
  memory_mb = 1024

[deploy]
  release_command = "alembic upgrade head"  # Auto-run migrations!
```

### Frontend `fly.toml` (Complete Example)

```toml
# frontend/fly.toml
app = "wizard-frontend"
primary_region = "iad"

[build]
  dockerfile = "Dockerfile"

[env]
  REACT_APP_API_URL = "https://wizard-backend.fly.dev/api/v1"

[http_service]
  internal_port = 80
  force_https = true
  auto_stop_machines = true
  auto_start_machines = true
  min_machines_running = 0

  [[http_service.checks]]
    grace_period = "5s"
    interval = "30s"
    method = "GET"
    timeout = "5s"
    path = "/health"

[[vm]]
  cpu_kind = "shared"
  cpus = 1
  memory_mb = 512
```

---

## 🔄 GitHub Actions CI/CD (Optional)

Automatically deploy when you push to GitHub!

Create `.github/workflows/fly-deploy.yml`:

```yaml
name: Deploy to Fly.io

on:
  push:
    branches: [main]

jobs:
  deploy-backend:
    name: Deploy Backend
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - uses: superfly/flyctl-actions/setup-flyctl@master

      - name: Deploy Backend
        run: flyctl deploy --remote-only
        working-directory: ./backend
        env:
          FLY_API_TOKEN: ${{ secrets.FLY_API_TOKEN }}

  deploy-frontend:
    name: Deploy Frontend
    runs-on: ubuntu-latest
    needs: deploy-backend
    steps:
      - uses: actions/checkout@v3

      - uses: superfly/flyctl-actions/setup-flyctl@master

      - name: Deploy Frontend
        run: flyctl deploy --remote-only
        working-directory: ./frontend
        env:
          FLY_API_TOKEN: ${{ secrets.FLY_API_TOKEN }}
```

**Setup:**
1. Get Fly API token: `fly auth token`
2. Add to GitHub Secrets: Settings → Secrets → Actions → New secret
3. Name: `FLY_API_TOKEN`
4. Value: (paste your token)

Now every push to `main` deploys automatically! 🚀

---

## 🔧 Fly.io Commands Cheat Sheet

### Deployment
```bash
# Deploy current directory
fly deploy

# Deploy with specific Dockerfile
fly deploy --dockerfile Dockerfile.prod

# Deploy without cache
fly deploy --no-cache

# Deploy specific region
fly deploy --region iad
```

### Monitoring
```bash
# View app status
fly status

# View real-time logs
fly logs

# View logs from specific instance
fly logs -i instance-id

# SSH into running app
fly ssh console

# Run command in app
fly ssh console -C "alembic upgrade head"
```

### Scaling
```bash
# Scale to 2 instances
fly scale count 2

# Scale memory
fly scale memory 2048

# Scale to specific regions
fly scale count 2 --region iad,lax
```

### Database
```bash
# Connect to PostgreSQL
fly postgres connect -a wizard-db

# Check database status
fly postgres db list -a wizard-db

# Create database backup
fly postgres backup create -a wizard-db
```

### Secrets Management
```bash
# Set secret
fly secrets set KEY=value

# List secrets
fly secrets list

# Remove secret
fly secrets unset KEY

# Import secrets from .env
fly secrets import < .env.production
```

### App Management
```bash
# Open app in browser
fly open

# View dashboard
fly dashboard

# Restart app
fly apps restart

# Destroy app (careful!)
fly apps destroy wizard-backend
```

---

## 💰 Fly.io Pricing

**Free Tier (Generous):**
- 3 shared-cpu-1x VMs with 256MB RAM each
- 3GB persistent volume storage
- 160GB outbound data transfer/month

**Paid Usage:**
- Shared CPU: ~$0.0000021/second (~$5.50/month per VM)
- Memory: $0.0000021/MB/second
- Persistent storage: $0.15/GB/month
- Data transfer: $0.02/GB

**Estimated Cost for This App:**
- Small traffic: **FREE** (within free tier)
- Medium traffic: ~$10-15/month
- High traffic: ~$25-40/month

**PostgreSQL:**
- Development (1GB RAM, 10GB storage): **FREE**
- Production: ~$10-30/month depending on size

---

## 🌍 Multi-Region Deployment

Fly.io's killer feature: Deploy globally!

### Add More Regions

```bash
# Clone app to multiple regions
fly scale count 1 --region iad  # US East
fly scale count 1 --region lax  # US West
fly scale count 1 --region fra  # Europe
fly scale count 1 --region syd  # Australia

# Your app now runs in 4 regions!
# Users connect to the nearest one automatically
```

### Available Regions

```bash
# List all regions
fly platform regions

# Popular regions:
# - iad (US East - Virginia)
# - lax (US West - Los Angeles)
# - fra (Europe - Frankfurt)
# - syd (Asia Pacific - Sydney)
# - nrt (Asia - Tokyo)
# - lhr (Europe - London)
```

---

## 🐛 Troubleshooting

### Deployment Fails: "health checks failing"

**Solution**: Check health check endpoint
```bash
# View logs during deployment
fly logs

# Check if your app is listening on correct port
# Backend should listen on 0.0.0.0:8000
# Frontend nginx should listen on port 80
```

### Can't Connect to Database

**Solution**: Verify DATABASE_URL secret
```bash
# Check secrets are set
fly secrets list

# Update DATABASE_URL if needed
fly secrets set DATABASE_URL="postgres://..."

# Restart app
fly apps restart
```

### Frontend Can't Reach Backend

**Solution**: Update REACT_APP_API_URL
1. Edit `frontend/fly.toml`
2. Update `REACT_APP_API_URL` with correct backend URL
3. Redeploy: `fly deploy`

### Out of Memory Errors

**Solution**: Increase memory allocation
```bash
# Scale to 1GB memory
fly scale memory 1024

# Or edit fly.toml:
# memory_mb = 1024
```

### SSL Certificate Errors

Fly.io auto-provisions SSL certificates!

**If having issues:**
```bash
# Check certificate status
fly certs show

# Add custom domain
fly certs add yourdomain.com

# Check DNS configuration
fly certs check yourdomain.com
```

### Database Migration Not Running

**Solution**: Run manually or add to fly.toml
```bash
# Manual:
fly ssh console -C "alembic upgrade head"

# Or add to backend/fly.toml:
[deploy]
  release_command = "alembic upgrade head"
```

---

## 🔐 Security Best Practices

### Use Secrets for Sensitive Data

```bash
# Never put secrets in fly.toml!
# Use fly secrets instead:

fly secrets set SECRET_KEY="$(openssl rand -hex 32)"
fly secrets set POSTGRES_PASSWORD="secure-password"
fly secrets set DATABASE_URL="postgres://..."
```

### Enable Fly.io Private Network

Your apps can communicate privately:

```toml
# In fly.toml
[env]
  # Use .internal domain for private communication
  DATABASE_HOST = "wizard-db.internal"
  BACKEND_URL = "wizard-backend.internal:8000"
```

### Restrict Public Access (Optional)

```toml
# Only allow specific IPs
[[http_service]]
  [[http_service.ip_filters]]
    action = "allow"
    ip = "203.0.113.0/24"
```

---

## 🎯 Production Checklist

Before going live:

- [ ] Deploy backend successfully
- [ ] Deploy frontend successfully
- [ ] Run database migration
- [ ] Test all API endpoints
- [ ] Test frontend functionality
- [ ] Set all secrets (SECRET_KEY, DATABASE_URL)
- [ ] Enable HTTPS (automatic on Fly.io)
- [ ] Configure health checks
- [ ] Test wizard creation and execution
- [ ] Set up GitHub Actions (optional)
- [ ] Add custom domain (optional)
- [ ] Configure backups for PostgreSQL
- [ ] Monitor logs for errors
- [ ] Test multi-region (optional)

---

## 🆚 Fly.io vs Railway

### Fly.io Advantages ✅
- ✅ **Multi-region deployment** - Run globally
- ✅ **More generous free tier** - 3 VMs free
- ✅ **Better for high traffic** - More cost-effective at scale
- ✅ **Private networking** - Apps communicate privately
- ✅ **More control** - Advanced configuration options

### Railway Advantages ✅
- ✅ **Easier setup** - No CLI needed
- ✅ **Better UI** - More visual, beginner-friendly
- ✅ **Auto-detects from GitHub** - No manual app creation
- ✅ **Simpler workflow** - Less configuration

### Choose Fly.io If:
- Need multi-region deployment
- Want more free tier resources
- Expect high traffic
- Comfortable with CLI

### Choose Railway If:
- Want easiest deployment
- Prefer visual dashboard
- Small to medium traffic
- Want GitHub auto-deploy

---

## 📚 Additional Resources

- **Fly.io Docs**: https://fly.io/docs
- **Fly.io Community**: https://community.fly.io
- **Django on Fly**: https://fly.io/docs/django/
- **FastAPI on Fly**: https://fly.io/docs/languages-and-frameworks/python/
- **PostgreSQL on Fly**: https://fly.io/docs/postgres/

---

## 🎉 Success!

Your Multi-Wizard Platform is now live on Fly.io! ✈️

**Your App URLs:**
```
Frontend: https://wizard-frontend.fly.dev
Backend:  https://wizard-backend.fly.dev
API Docs: https://wizard-backend.fly.dev/docs
```

**Next Steps:**
1. Add custom domain
2. Set up multi-region deployment
3. Configure GitHub Actions for auto-deploy
4. Monitor metrics and logs

---

## 🔄 Deployment Workflow

### Initial Setup (One-time)
```bash
1. Install Fly CLI
2. fly auth login
3. Create PostgreSQL: fly postgres create
4. Create backend app: fly launch (in backend/)
5. Create frontend app: fly launch (in frontend/)
6. Set secrets: fly secrets set
7. Deploy backend: fly deploy (in backend/)
8. Deploy frontend: fly deploy (in frontend/)
9. Run migration: fly ssh console -C "alembic upgrade head"
```

### Updates (Every time)
```bash
# Option 1: Manual
cd backend && fly deploy
cd frontend && fly deploy

# Option 2: Automated (with GitHub Actions)
git add . && git commit -m "update" && git push
# Fly.io auto-deploys! ✨
```

---

**Need Help?**
- Fly.io Community: https://community.fly.io
- Project Issues: https://github.com/NisarAhamedE/0003_WIZARD/issues
