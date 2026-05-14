# 🎯 DEPLOYMENT CHECKLIST

## Pre-Deployment (Docker or VPS)

### 1. Environment Configuration
- [ ] Copy `backend/.env.example` to `backend/.env`
- [ ] Fill in ALL required variables:
  ```
  SUPABASE_URL=your-project.supabase.co
  SUPABASE_KEY=ey...
  JWT_SECRET=minimum-32-random-characters
  SECRET_KEY=another-random-string
  SMTP_USERNAME=your-email@gmail.com
  SMTP_PASSWORD=your-app-password
  RAZORPAY_KEY_ID=rzp_test_xxx
  RAZORPAY_KEY_SECRET=xxx
  ```
- [ ] Copy `frontend/.env.example` to `frontend/.env`
- [ ] Set `VITE_API_URL=http://your-domain.com` (or localhost for dev)

### 2. Database Setup
- [ ] Create Supabase project
- [ ] Run `database_schema_complete.sql` in SQL Editor
- [ ] Enable Row Level Security (RLS) on tables
- [ ] Add auth policies (see SETUP_GUIDE.md)
- [ ] Test connection: `python -c "from utils.supabase_client import supabase; print(supabase.table('companies').select('*').execute())"`

### 3. Docker Build
- [ ] `docker-compose build` (first time only)
- [ ] Verify no build errors

### 4. SSL/TLS Certificates (Production)
- [ ] Obtain SSL cert (Let's Encrypt recommended)
- [ ] Place in `./ssl/` directory as `cert.pem` and `key.pem`
- [ ] Uncomment SSL section in `nginx.conf`

### 5. Domain & DNS
- [ ] Point domain A record to server IP
- [ ] Wait for propagation (5min-48hrs)

### 6. Firewall
```bash
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw enable
```

---

## Deployment Commands

### Docker (Recommended)
```bash
# 1. Build & start
docker-compose up -d

# 2. Check status
docker-compose ps

# 3. View logs
docker-compose logs -f app

# 4. Health check
curl http://localhost:5000/health

# 5. Stop
docker-compose down

# 6. Update (after code changes)
docker-compose build --no-cache
docker-compose up -d
```

### Manual (Development)
```bash
# Terminal 1 - Backend
cd backend
source venv/bin/activate  # or venv\Scripts\activate on Windows
python app_socketio.py

# Terminal 2 - Frontend
cd frontend
npm run dev
```

---

## Post-Deployment Verification

### 1. Health Endpoint
```bash
curl https://yourdomain.com/health
```
Expected: `{"status":"healthy",...}`

### 2. Register Test User
```bash
curl -X POST https://yourdomain.com/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@test.com","password":"Test@123","name":"Admin","role":"admin"}'
```

### 3. Login
```bash
curl -X POST https://yourdomain.com/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@test.com","password":"Test@123"}'
```
Save the `token` from response.

### 4. Create Task
```bash
curl -X POST https://yourdomain.com/api/tasks/create-task \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"Test Task","priority":"high","company_id":"YOUR_COMPANY_ID"}'
```

### 5. Test WebSocket
Open browser console on your site:
```javascript
const socket = io('https://yourdomain.com', {
  query: { user_id: 'YOUR_USER_ID' }
});
socket.on('notification', console.log);
```

### 6. Send Test Email
```bash
curl -X POST https://yourdomain.com/api/email/daily-summary/USER_ID \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## Monitoring

### Check Logs
```bash
# App logs
docker-compose logs -f app

# Nginx logs
docker-compose logs -f nginx

# Database logs
docker-compose logs -f postgres

# Celery worker logs
docker-compose logs -f celery

# Flower dashboard (visit http://yourdomain.com:5555)
```

### Metrics
- **Application:** `/health`, `/api` (info)
- **Database:** Supabase dashboard
- **Redis:** `redis-cli ping`
- **Celery:** Flower UI at `:5555`

---

## Backup Strategy

### Daily Backups
```bash
# Backup database
docker-compose exec postgres pg_dump -U smartos smartos > backup_$(date +%Y%m%d).sql

# Backup volumes
tar -czf smartos-backup-$(date +%Y%m%d).tar.gz docker-volume-*

# Upload to S3/cloud
aws s3 cp backup_*.sql s3://your-backup-bucket/
```

### Automated Cron Job
```bash
# Add to crontab (crontab -e)
0 2 * * * /path/to/backup.sh
```

---

## Scaling

### Horizontal Scaling
```yaml
# docker-compose.yml - scale app
deploy:
  replicas: 3

# Or manually:
docker-compose up -d --scale app=3
```

### Database Read Replicas
- Configure in Supabase dashboard

### Redis Cluster
- Use Redis Cluster mode for high availability

### Load Balancer
- Add more nginx instances
- Use AWS ELB / GCP Load Balancer

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| 502 Bad Gateway | Nginx can't reach app → check `docker-compose logs app` |
| WebSocket disconnect | Check `proxy_set_header Upgrade $http_upgrade;` in nginx.conf |
| 401 Unauthorized | Verify JWT_SECRET is set and app restarted |
| Email not sending | Check SMTP credentials + app password for Gmail |
| AI features fail | Verify OPENAI_API_KEY has credits |
| Razorpay errors | Ensure key/secret are from live/test environment matching |
| Slow queries | Check database indexes in Supabase |
| High memory | Increase Docker limits or scale horizontally |

---

## Security Hardening (Production)

- [ ] Change all default passwords
- [ ] Use strong, unique secrets (32+ chars)
- [ ] Enable HTTPS only (301 redirect HTTP→HTTPS)
- [ ] Set up WAF (Cloudflare recommended)
- [ ] Enable rate limiting (already in nginx.conf)
- [ ] Regular security updates (`docker-compose pull`)
- [ ] Monitor logs for suspicious activity
- [ ] Enable audit logging (activity_logs table)
- [ ] Set up intrusion detection
- [ ] Regular backups (daily minimum)
- [ ] Encrypt sensitive data at rest
- [ ] Network segmentation (VPC)
- [ ] IAM roles with least privilege

---

## Performance Optimization

- [ ] Enable Redis caching (already configured)
- [ ] Add CDN for static assets (Cloudflare)
- [ ] Database connection pooling (pgbouncer)
- [ ] Compress responses (gzip enabled)
- [ ] Optimize images (frontend images)
- [ ] Minify CSS/JS in production (vite build does this)
- [ ] Use materialized views for complex queries
- [ ] Add database read replicas if needed
- [ ] Monitor slow queries (Supabase logs)

---

## Maintenance

### Weekly
- [ ] Review error logs
- [ ] Check disk space
- [ ] Verify backups exist and restore test
- [ ] Update dependencies (`pip list --outdated`, `npm outdated`)

### Monthly
- [ ] Security patches
- [ ] Performance review
- [ ] User feedback analysis
- [ ] Audit log review

### Quarterly
- [ ] Penetration testing
- [ ] Load testing
- [ ] Disaster recovery drill
- [ ] Compliance review

---

## Support Resources

- **Setup Guide:** `SETUP_GUIDE.md` (detailed)
- **Features:** `FEATURES_IMPLEMENTED.md`
- **API Reference:** Auto-generated at `/api` endpoint
- **Logs:** `docker-compose logs -f`
- **DB:** Supabase dashboard → SQL Editor

---

**Deployment Status:** ✅ Ready for Production

**Estimated Deployment Time:**
- Docker: 10-15 minutes
- VPS manual: 30-45 minutes
- Cloud (Railway/Render): 5 minutes

**Post-deployment:** Run verification checklist above, then create first admin user.