# 🐳 Docker Deployment Guide
## Multi-Wizard Platform - Production Deployment

---

## 📋 Quick Start

### Development (Local)

1. **Clone & Setup**
```bash
git clone https://github.com/NisarAhamedE/0003_WIZARD.git
cd 0003_WIZARD
cp .env.example .env
```

2. **Edit .env file**
```env
POSTGRES_PASSWORD=your-password
SECRET_KEY=your-secret-key
```

3. **Start**
```bash
docker-compose up -d
```

4. **Access**
- Frontend: http://localhost
- Backend: http://localhost:8000
- API Docs: http://localhost:8000/docs

---

## 🚀 Production Deployment

### Server Requirements
- 2 CPU cores, 4GB RAM, 50GB storage
- Ubuntu 22.04 LTS
- Docker & Docker Compose installed

### Step-by-Step

**1. Install Docker on Server**
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
```

**2. Clone Repository**
```bash
cd /opt
git clone https://github.com/NisarAhamedE/0003_WIZARD.git
cd 0003_WIZARD
```

**3. Configure Environment**
```bash
cp .env.example .env
nano .env
```

Update with production values:
```env
POSTGRES_DB=wizarddb
POSTGRES_USER=wizardadmin
POSTGRES_PASSWORD=VerySecurePassword123
SECRET_KEY=generate-with-openssl-rand-hex-32
REACT_APP_API_URL=https://yourdomain.com/api/v1
ENVIRONMENT=production
```

**4. Build & Start**
```bash
docker compose -f docker-compose.prod.yml build
docker compose -f docker-compose.prod.yml up -d
```

**5. Run Database Migration**
```bash
docker exec -it wizard-backend-prod bash
alembic upgrade head
exit
```

**6. Verify**
```bash
docker compose -f docker-compose.prod.yml ps
docker compose -f docker-compose.prod.yml logs -f
```

---

## 🔒 SSL Setup (Let's Encrypt)

**1. Point domain to server** (DNS A record)

**2. Get SSL certificate**
```bash
docker run -it --rm -v $(pwd)/certbot/conf:/etc/letsencrypt   -v $(pwd)/certbot/www:/var/www/certbot -p 80:80   certbot/certbot certonly --standalone   -d yourdomain.com --email your@email.com --agree-tos
```

**3. Restart with SSL**
```bash
docker compose -f docker-compose.prod.yml restart nginx
```

---

## 🔧 Common Commands

**View logs**
```bash
docker compose -f docker-compose.prod.yml logs -f backend
```

**Restart service**
```bash
docker compose -f docker-compose.prod.yml restart backend
```

**Backup database**
```bash
docker exec wizard-db-prod pg_dump -U wizardadmin wizarddb > backup.sql
```

**Restore database**
```bash
cat backup.sql | docker exec -i wizard-db-prod psql -U wizardadmin -d wizarddb
```

**Update application**
```bash
git pull
docker compose -f docker-compose.prod.yml up -d --build
```

**Stop all**
```bash
docker compose -f docker-compose.prod.yml down
```

---

## 📊 Monitoring

**Check container status**
```bash
docker compose -f docker-compose.prod.yml ps
```

**Resource usage**
```bash
docker stats
```

**Health check**
```bash
curl http://localhost/health
curl http://localhost:8000/
```

---

## 🐛 Troubleshooting

**Container won't start?**
```bash
docker compose -f docker-compose.prod.yml logs backend
docker compose -f docker-compose.prod.yml up -d --build backend
```

**Database connection issues?**
```bash
docker compose -f docker-compose.prod.yml exec backend python -c "from app.database import engine; engine.connect()"
```

**Reset everything** (DANGER - deletes data!)
```bash
docker compose -f docker-compose.prod.yml down -v
docker compose -f docker-compose.prod.yml up -d --build
```

---

## ✅ Security Checklist

- [ ] Change default passwords in .env
- [ ] Generate strong SECRET_KEY (32+ chars)
- [ ] Enable SSL/HTTPS
- [ ] Configure firewall (UFW: allow 80, 443, 22 only)
- [ ] Set up automated database backups
- [ ] Regular system updates
- [ ] Monitor logs for suspicious activity

---

## 💰 Recommended Hosting

**Budget Option ($10-15/month):**
- DigitalOcean Droplet (2GB RAM)
- Linode Nanode
- Vultr Cloud Compute

**Easy Option ($20+/month):**
- Railway (auto-deployment from GitHub)
- Render (managed PostgreSQL included)

**Enterprise:**
- AWS ECS
- Google Cloud Run
- Azure Container Instances

---

## 🔄 CI/CD (Optional)

GitHub Actions example:
```yaml
name: Deploy
on:
  push:
    branches: [main]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to server
        run: |
          ssh user@server 'cd /opt/0003_WIZARD && git pull && docker compose -f docker-compose.prod.yml up -d --build'
```

---

## 📚 Additional Resources

- **Docker Documentation**: https://docs.docker.com
- **FastAPI Docs**: https://fastapi.tiangolo.com
- **React Docs**: https://react.dev
- **Project README**: [README.md](README.md)

---

**Need Help?**  
Open an issue: https://github.com/NisarAhamedE/0003_WIZARD/issues

🎉 **Your Multi-Wizard Platform is now production-ready!**
