# Fly.io Deployment Guide

This guide covers deploying the Multi-Wizard Platform to Fly.io.

## Architecture

- **Backend**: `0003-wizard-dyttbg.fly.dev` - FastAPI + PostgreSQL
- **Frontend**: `0003-wizard-frontend.fly.dev` - React + Nginx

## Prerequisites

1. Install Fly CLI:
   ```bash
   # Windows (PowerShell)
   powershell -Command "iwr https://fly.io/install.ps1 -useb | iex"

   # macOS/Linux
   curl -L https://fly.io/install.sh | sh
   ```

2. Login to Fly.io:
   ```bash
   fly auth login
   ```

## Step 1: Create PostgreSQL Database

```bash
# Create a Postgres cluster (choose a region close to your app)
fly postgres create --name wizard-db --region iad

# After creation, note the connection string displayed
# It will look like: postgres://postgres:PASSWORD@wizard-db.flycast:5432/wizard_db
```

## Step 2: Deploy Backend

```bash
cd backend

# Create the app (skip if already created)
fly apps create 0003-wizard-dyttbg

# Set secrets (required)
fly secrets set DATABASE_URL="postgres://postgres:PASSWORD@wizard-db.flycast:5432/wizard_db" --app 0003-wizard-dyttbg
fly secrets set SECRET_KEY="your-super-secure-secret-key-min-32-chars" --app 0003-wizard-dyttbg

# Optional: Set additional CORS origins
fly secrets set CORS_ORIGINS="https://0003-wizard-frontend.fly.dev,http://localhost:3000" --app 0003-wizard-dyttbg

# Deploy
fly deploy
```

## Step 3: Attach Database to Backend

```bash
# Attach the Postgres cluster to your backend app
fly postgres attach wizard-db --app 0003-wizard-dyttbg
```

This automatically sets the `DATABASE_URL` secret.

## Step 4: Deploy Frontend

```bash
cd frontend

# Create the app (skip if already created)
fly apps create 0003-wizard-frontend

# Deploy (VITE_API_URL is set in fly.toml build args)
fly deploy
```

## Environment Variables

### Backend Secrets (set via `fly secrets set`)

| Variable | Required | Description |
|----------|----------|-------------|
| `DATABASE_URL` | Yes | PostgreSQL connection string |
| `SECRET_KEY` | Yes | JWT signing key (min 32 chars) |
| `CORS_ORIGINS` | No | Comma-separated allowed origins |

### Backend Environment (set in fly.toml)

| Variable | Value | Description |
|----------|-------|-------------|
| `ENVIRONMENT` | production | App environment |
| `ALGORITHM` | HS256 | JWT algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | 30 | Token expiry |
| `DEBUG` | false | Debug mode |

### Frontend Build Args (set in fly.toml)

| Variable | Value | Description |
|----------|-------|-------------|
| `VITE_API_URL` | https://0003-wizard-dyttbg.fly.dev/api/v1 | Backend API URL |

## Useful Commands

```bash
# View logs
fly logs --app 0003-wizard-dyttbg
fly logs --app 0003-wizard-frontend

# SSH into container
fly ssh console --app 0003-wizard-dyttbg

# Check app status
fly status --app 0003-wizard-dyttbg

# View secrets
fly secrets list --app 0003-wizard-dyttbg

# Scale machines
fly scale count 2 --app 0003-wizard-dyttbg

# View machine resources
fly scale show --app 0003-wizard-dyttbg

# Open app in browser
fly open --app 0003-wizard-dyttbg

# Restart app
fly apps restart 0003-wizard-dyttbg
```

## Database Management

```bash
# Connect to database via proxy
fly proxy 5432 -a wizard-db

# Then connect with psql
psql postgres://postgres:PASSWORD@localhost:5432/wizard_db

# Or use fly postgres connect
fly postgres connect -a wizard-db
```

## Troubleshooting

### Health Check Failures

The backend health check hits `/` which returns API info. If health checks fail:

```bash
# Check logs for errors
fly logs --app 0003-wizard-dyttbg

# Verify the app is running
fly status --app 0003-wizard-dyttbg
```

### CORS Errors

If you see CORS errors in the browser console:

1. Update CORS_ORIGINS secret:
   ```bash
   fly secrets set CORS_ORIGINS="https://0003-wizard-frontend.fly.dev,https://your-domain.com" --app 0003-wizard-dyttbg
   ```

2. Redeploy or restart:
   ```bash
   fly apps restart 0003-wizard-dyttbg
   ```

### Database Connection Issues

1. Verify DATABASE_URL is set:
   ```bash
   fly secrets list --app 0003-wizard-dyttbg
   ```

2. Check if database is attached:
   ```bash
   fly postgres attach wizard-db --app 0003-wizard-dyttbg
   ```

### Frontend Not Loading API

1. Verify VITE_API_URL in build args points to correct backend URL
2. Rebuild frontend:
   ```bash
   fly deploy --app 0003-wizard-frontend
   ```

## Deployment Checklist

- [ ] Fly CLI installed and authenticated
- [ ] PostgreSQL cluster created
- [ ] Backend app created
- [ ] DATABASE_URL secret set
- [ ] SECRET_KEY secret set
- [ ] Backend deployed successfully
- [ ] Frontend app created
- [ ] Frontend deployed successfully
- [ ] Both apps accessible via fly.dev URLs
- [ ] Login/registration working
- [ ] CORS properly configured

## URLs

After successful deployment:

- **Backend API**: https://0003-wizard-dyttbg.fly.dev
- **API Docs**: https://0003-wizard-dyttbg.fly.dev/api/docs
- **Frontend**: https://0003-wizard-frontend.fly.dev
