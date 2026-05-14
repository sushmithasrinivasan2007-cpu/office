# SmartOS - Complete Setup Guide

## 📋 Table of Contents
1. [Quick Start](#quick-start)
2. [Architecture Overview](#architecture-overview)
3. [Prerequisites](#prerequisites)
4. [Local Development Setup](#local-development-setup)
5. [Configuration](#configuration)
6. [Database Setup](#database-setup)
7. [Production Deployment](#production-deployment)
8. [Docker Deployment](#docker-deployment)
9. [Troubleshooting](#troubleshooting)

---

## 🚀 Quick Start

### Option A: Docker (Recommended - 10 minutes)
```bash
# Clone and setup
git clone <your-repo>
cd smart-office-manager

# Configure environment
cp backend/.env.example backend/.env
# Edit backend/.env with your Supabase & API keys

# Start everything
docker-compose up -d

# Access the app
open http://localhost:3000
```

### Option B: Local Development (30 minutes)
Follow the detailed setup below.

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                        Nginx (Reverse Proxy)               │
│                       Port 80 / 443 (HTTPS)               │
└─────────────────────────────┬───────────────────────────────┘
                              │
        ┌─────────────────────┴──────────────────────┐
        │                                             │
┌───────▼────────┐                          ┌────────▼───────┐
│  Frontend      │                          │  Backend API   │
│  React (Vite)  │                          │  Flask         │
│  Port: 3000    │                          │  Port: 5000    │
└────────────────┘                          └────────┬───────┘
                                                   │
                                   ┌───────────────┼───────────────┐
                                   │               │               │
                         ┌─────────▼──────┐ ┌─────▼──────┐ ┌─────▼──────┐
                         │  PostgreSQL    │ │  Redis     │ │  SocketIO  │
                         │  (Supabase)    │ │  Cache     │ │  Real-time │
                         └────────────────┘ └────────────┘ └────────────┘
```

### Key Components:
- **Frontend**: React 19 + Vite + Tailwind CSS
- **Backend**: Python Flask + Flask-SocketIO
- **Database**: PostgreSQL via Supabase
- **Cache**: Redis for sessions & rate limiting
- **Async**: Celery + Flower for background jobs
- **Realtime**: WebSocket for live notifications
- **AI**: OpenAI GPT-4 / Anthropic Claude integration
- **Payments**: Integrated payment gateway
- **Email**: SMTP (Gmail/SendGrid)

---

## 📋 Prerequisites

### Required Software
- **Node.js** 18+ → https://nodejs.org/
- **Python** 3.11+ → https://python.org/
- **Docker & Docker Compose** (optional) → https://docker.com/
- **Git** → https://git-scm.com/

### Cloud Accounts
1. **Supabase** (Free tier works)
   - Sign up at https://supabase.com
   - Create new project
   - Get `SUPABASE_URL` and `SUPABASE_ANON_KEY`

2. **Payment Gateway** (Optional)
   - Sign up for a payment provider (e.g. Stripe, PayPal, etc.)
   - Get `KEY_ID` and `KEY_SECRET`

3. **OpenAI** (AI features - Optional)
   - Sign up at https://platform.openai.com
   - Get API key

4. **Gmail / SMTP** (Email sending)
   - For Gmail, enable 2FA and create App Password

---

## 💻 Local Development Setup

### Step 1: Clone & Structure
```
smart-office-manager/
├── backend/
│   ├── routes/          # API endpoints
│   ├── services/        # Business logic
│   ├── utils/           # Helpers (Supabase, Email)
│   ├── config.py        # Configuration
│   └── app.py           # Flask app factory
├── frontend/
│   ├── src/
│   │   ├── pages/       # Page components
│   │   ├── components/  # Reusable UI
│   │   └── App.jsx      # Main router
│   └── index.html
├── database_schema_complete.sql
├── docker-compose.yml
└── README.md
```

### Step 2: Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate (Windows)
.\venv\Scripts\activate

# (Mac/Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your actual keys
```

### Step 3: Supabase Database Setup

1. Go to your Supabase project → SQL Editor
2. Paste the contents of `database_schema_complete.sql`
3. Click **Run** to create all tables
4. Wait for confirmation

### Step 4: Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start dev server
npm run dev

# Or build for production
npm run build
```

### Step 5: Configure Environment

Edit `backend/.env`:

```ini
# Required
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=eyxxx...
JWT_SECRET=your-super-secret-jwt-key

# Optional (but enables full features)

OPENAI_API_KEY=sk-xxx
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

### Step 6: Run Backend

```bash
cd backend
python app_socketio.py
```

Access at http://localhost:5000

---

## 🔧 Configuration

### Environment Variables Reference

| Variable | Required | Description |
|----------|----------|-------------|
| `SUPABASE_URL` | Yes | Your Supabase project URL |
| `SUPABASE_KEY` | Yes | Supabase anon/public key |
| `JWT_SECRET` | Yes | Secret for JWT signing (min 32 chars) |
| `SECRET_KEY` | Yes | Flask secret key |

| `OPENAI_API_KEY` | No | For AI task parsing & analysis |
| `ANTHROPIC_API_KEY` | No | Alternative AI provider |
| `SMTP_SERVER` | No | Email server (default: Gmail) |
| `SMTP_PORT` | No | Default 587 |
| `SMTP_USERNAME` | No | Email username |
| `SMTP_PASSWORD` | No | Email password/app-specific |
| `SLACK_BOT_TOKEN` | No | Slack integration token |
| `GITHUB_TOKEN` | No | GitHub integration token |
| `APP_URL` | No | Public URL for email links |
| `FRONTEND_URL` | No | Frontend origin for CORS |

---

## 🗄️ Database Schema

Run this SQL in your Supabase SQL Editor:

```sql
-- See database_schema_complete.sql for full schema
-- Key tables:
--   - companies (multi-tenant)
--   - users (with RBAC)
--   - tasks (geo-tagged)
--   - payments (razorpay)
--   - attendance (geo verified)
--   - ai_logs (AI tracking)
--   - predictions (ML)
--   - integrations (3rd party)
--   - notifications (real-time)
--   - invoices (billing)
```

### Row Level Security (RLS)

Supabase has RLS enabled by default. Add policies:

```sql
-- Enable RLS on tables
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE tasks ENABLE ROW LEVEL SECURITY;
ALTER TABLE payments ENABLE ROW LEVEL SECURITY;

-- Policy: Users can see their own profile
CREATE POLICY "Users can view own profile" ON users
  FOR SELECT USING (auth.uid() = id);

-- Policy: Employees can see assigned tasks
CREATE POLICY "Employees view assigned tasks" ON tasks
  FOR SELECT USING (
    assigned_to = auth.uid() OR
    EXISTS (SELECT 1 FROM users WHERE id = auth.uid() AND role IN ('admin', 'manager'))
  );
```

---

## 🚀 Production Deployment

### Using Docker Compose (Production)

1. **Prepare environment**
```bash
cp backend/.env.example backend/.env
# Fill in ALL values including production keys
```

2. **Build & Deploy**
```bash
# Build images
docker-compose build

# Start services
docker-compose up -d

# Check logs
docker-compose logs -f app

# Verify
curl http://localhost:5000/health
```

3. **Set up HTTPS (SSL)**

Edit `nginx.conf` to include SSL:

```nginx
server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    # ... rest of config
}
```

4. **Set up domain & DNS**
   - Point your domain to the server IP
   - Configure A record

5. **Add SSL Certificate (Let's Encrypt)**

```bash
# Using Certbot
certbot --nginx -d yourdomain.com

# Or manual
# Place certs in ./ssl/ directory
```

6. **Reverse proxy & firewall**
```bash
# Allowports
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 5000
sudo ufw enable
```

### Using PM2 (Alternative to Docker)

```bash
# Install PM2
npm install -g pm2

# Create ecosystem.config.js
module.exports = {
  apps: [{
    name: 'smartos-backend',
    script: 'backend/app_socketio.py',
    instances: 2,
    exec_mode: 'cluster',
    env: { NODE_ENV: 'production' }
  }, {
    name: 'smartos-frontend',
    script: 'npm',
    args: 'start --prefix frontend',
    env: { NODE_ENV: 'production', PORT: '3000' }
  }]
};

# Deploy
pm2 start ecosystem.config.js
pm2 save
pm2 startup
```

---

## 📧 Email Setup

### Gmail (Testing)
1. Enable 2FA on your Gmail account
2. Generate App Password (16 chars)
3. Use in `.env`:
```ini
SMTP_USERNAME=youraccount@gmail.com
SMTP_PASSWORD=your-16-digit-app-password
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
```

### SendGrid (Production - Free tier: 100/day)
```ini
SMTP_SERVER=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USERNAME=apikey
SMTP_PASSWORD=your-sendgrid-api-key
```

---

## 🔔 Webhook & Integration Setup

### Slack Integration
1. Go to https://api.slack.com/apps
2. Create new app → Add features: **Incoming Webhooks**, **Bots**
3. Get Bot Token (`xoxb-...`)
4. Invite bot to channel: `/invite @YourBot`
5. Add to `.env`:
```ini
SLACK_BOT_TOKEN=xoxb-your-token-here
```

### GitHub Integration
1. Personal Access Token (classic) → repo & admin permissions
2. Add to `.env`:
```ini
GITHUB_TOKEN=ghp_xxxxxxxxxxxxx
```

---

## 🧪 Testing

### Run tests
```bash
# Backend
cd backend
pytest tests/

# Or with unittest
python -m unittest discover tests/

# Frontend
cd frontend
npm test

# API testing with curl
curl http://localhost:5000/health
```

### Load testing
```bash
# Locust
pip install locust
locust -f tests/load_test.py

# Or Apache Bench
ab -n 1000 -c 10 http://localhost:5000/api/tasks
```

---

## 🐛 Troubleshooting

### Common Issues

**Issue**: `ModuleNotFoundError: No module named 'flask_socketio'`
```bash
pip install flask-socketio eventlet
```

**Issue**: CORS errors in frontend
- Ensure backend CORS includes your frontend URL
- Check `app.py` CORS settings

**Issue**: Supabase RLS blocking queries
- Go to Supabase → Authentication → Policies
- Temporarily disable RLS for testing

**Issue**: WebSocket connection fails
- Verify `socketio.init_app(app)` is called
- Check Nginx proxy WebSocket config
- Ensure `cors_allowed_origins` includes your frontend

**Issue**: AI features not working
- Verify `OPENAI_API_KEY` is set
- Check API key has credits
- Fallback to simple parser if no key

### Logs

```bash
# Docker logs
docker-compose logs -f app
docker-compose logs -f nginx

# PM2 logs
pm2 logs smartos-backend

# Flask logs
tail -f logs/app.log
```

### Reset Database

```bash
# Drop all tables (Docker)
docker-compose down
docker volume rm smartos-manager_postgres_data
docker-compose up -d
```

---

## 📚 API Documentation

### Authentication
All protected routes require `Authorization: Bearer <token>` header.

### Key Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/auth/register` | POST | Register new user |
| `/api/auth/login` | POST | User login |
| `/api/tasks/create-task` | POST | Create task |
| `/api/tasks/` | GET | List tasks |
| `/api/tasks/:id/complete` | POST | Complete task |
| `/api/geo/verify` | POST | Verify location |
| `/api/payments/create-order` | POST | Initiate payment |
| `/api/ai/parse-task` | POST | AI task parsing |
| `/api/ai/smart-plan` | GET | AI daily plan |
| `/api/analytics/dashboard/:company` | GET | Company metrics |
| `/api/email/daily-summary/:user` | POST | Send email |

---

## 🔐 Security Checklist

- [ ] Change all default passwords
- [ ] Use strong `JWT_SECRET` (32+ random chars)
- [ ] Enable HTTPS (SSL/TLS)
- [ ] Enable 2FA for admin accounts
- [ ] Set up firewall rules
- [ ] Configure CORS properly
- [ ] Enable RLS in Supabase
- [ ] Rotate API keys periodically
- [ ] Monitor logs for suspicious activity

---

## 📞 Support

For issues, feature requests, or questions:
- GitHub Issues: `https://github.com/your-repo/issues`
- Email: support@smartsos.com
- Documentation: https://docs.smartsos.com

---

**Note**: This is a production-ready template. Ensure you:
1. Use strong unique secrets
2. Enable all security features
3. Set up proper monitoring & backups
4. Configure rate limiting
5. Follow GDPR/privacy laws as applicable