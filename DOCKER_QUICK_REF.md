# 🚀 Docker Quick Reference Card
## Multi-Wizard Platform

---

## Development Commands

```bash
# Start
docker-compose up -d

# Stop
docker-compose down

# Rebuild
docker-compose up -d --build

# Logs
docker-compose logs -f

# Specific service logs
docker-compose logs -f backend
```

---

## Production Commands

```bash
# Start
docker compose -f docker-compose.prod.yml up -d

# Stop
docker compose -f docker-compose.prod.yml down

# Rebuild
docker compose -f docker-compose.prod.yml up -d --build

# Logs
docker compose -f docker-compose.prod.yml logs -f backend

# Status
docker compose -f docker-compose.prod.yml ps

# Restart service
docker compose -f docker-compose.prod.yml restart backend
```

---

## Database Commands

```bash
# Backup
docker exec wizard-db-prod pg_dump -U wizardadmin wizarddb > backup_$(date +%Y%m%d).sql

# Restore
cat backup_20250120.sql | docker exec -i wizard-db-prod psql -U wizardadmin -d wizarddb

# Access psql
docker exec -it wizard-db-prod psql -U wizardadmin -d wizarddb

# Run migration
docker exec -it wizard-backend-prod alembic upgrade head
```

---

## Monitoring

```bash
# Resource usage
docker stats

# Health check
curl http://localhost/health
curl http://localhost:8000/

# Container details
docker inspect wizard-backend-prod
```

---

## Troubleshooting

```bash
# View logs
docker logs wizard-backend-prod --tail=100 -f

# Enter container
docker exec -it wizard-backend-prod bash

# Restart problematic service
docker compose -f docker-compose.prod.yml restart backend

# Clean up
docker system prune -a
```

---

## Environment Variables

**Location**: `.env` file in project root

**Key variables**:
- `POSTGRES_PASSWORD`: Database password
- `SECRET_KEY`: Backend JWT secret
- `REACT_APP_API_URL`: API endpoint URL

---

## URLs

- **Frontend**: http://your-domain.com
- **Backend API**: http://your-domain.com/api
- **API Docs**: http://your-domain.com:8000/docs (dev only)

---

## Emergency

**Full reset** (deletes all data!):
```bash
docker compose -f docker-compose.prod.yml down -v
docker compose -f docker-compose.prod.yml up -d --build
```

**Quick restart**:
```bash
docker compose -f docker-compose.prod.yml restart
```
