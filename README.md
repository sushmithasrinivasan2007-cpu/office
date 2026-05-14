# 🚀 SmartOS - Intelligent Office Management System

> A production-ready, multi-tenant SaaS platform that acts as a mini operating system for companies, automatically handling task execution, workload balancing, employee accountability, and office coordination.

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Python](https://img.shields.io/badge/python-3.11+-blue)
![React](https://img.shields.io/badge/react-19+-61dafb)
![Supabase](https://img.shields.io/badge/supabase-postgres-3ecf8e)

---

## 🌟 Features

### Core System
- ✅ **Geo-tagged Tasks** - Location verification with 100m radius, OpenStreetMap integration
- ✅ **Smart Payments** - Integration for task-based payouts
- ✅ **Accountability Engine** - Track deadline adherence, completion rates, reassignments
- ✅ **Auto-Routing** - AI-powered task assignment based on workload, skills, availability
- ✅ **Automated Emails** - Daily summaries, weekly reports, overdue reminders via SMTP
- ✅ **Invoice & Billing** - PDF generation, payment links, tax calculation
- ✅ **Attendance + Tasks** - Location-based check-in required for task completion
- ✅ **Multi-tenant SaaS** - Isolated company data with RBAC
- ✅ **Real-time Notifications** - WebSocket-powered live updates

### AI & Intelligence
- 🤖 **AI Task Parser** - Convert "Call client tomorrow" → structured task
- 📊 **Smart Plan** - Daily prioritized task list per employee
- 🔮 **Risk Prediction** - Predict delays before they happen
- 📈 **Performance Insights** - Auto-generate executive summaries
- 💬 **Conversational AI** - Chat with your data

### Modules
- **CRM** - Client management & relationship tracking
- **HR** - Leave requests, attendance, employee records
- **Finance** - Payments, expenses, invoices, reports
- **Analytics** - Dashboards, benchmarks, KPI tracking

### Integrations
- 💬 **Slack** - Real-time notifications in channels
- 📹 **Zoom** - Auto-create meeting links
- 📁 **Google Drive** - File attachments
- 💻 **GitHub** - Link issues to tasks

---

## 🏗️ Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│   React     │────▶│   Flask      │────▶│  PostgreSQL │
│   Frontend  │     │   Backend    │     │  (Supabase) │
│   Vite      │     │   REST API   │     │   + RLS     │
└─────────────┘     └──────┬───────┘     └─────────────┘
                          │
                   ┌──────▼───────┐
                   │   Redis      │
                   │   Cache      │
                   └──────┬───────┘
                          │
                   ┌──────▼───────┐
                   │   SocketIO   │
                   │  Real-time   │
                   └──────────────┘
```

**Tech Stack:**
- **Frontend:** React 19, Vite, Lucide Icons, Custom CSS (no heavy framework)
- **Backend:** Python Flask, Flask-SocketIO, Gunicorn
- **Database:** PostgreSQL via Supabase (Auth + DB)
- **Cache:** Redis
- **Queue:** Celery + Flower (async jobs)
- **AI:** OpenAI GPT-4 / Anthropic Claude (optional)
- **Payments:** Integrated Payment Gateway
- **Deployment:** Docker + Nginx (production)

---

## 📦 What's Included

### Backend (`backend/`)
```
backend/
├── routes/              # API blueprints
│   ├── auth_routes.py       # Register, login, 2FA
│   ├── task_routes.py       # Task CRUD + smart ops
│   ├── geo_routes.py        # Location verification
│   ├── payment_routes.py    # Payment integration
│   ├── ai_routes.py         # AI endpoints
│   ├── analytics_routes.py  # Reports & metrics
│   ├── email_routes.py      # SMTP automation
│   ├── integration_routes.py # Slack, Zoom, etc.
│   ├── company_routes.py    # Multi-tenant
│   ├── user_routes.py       # Profile, check-in
│   ├── client_routes.py     # CRM
│   ├── hr_routes.py         # Leave & attendance
│   └── invoice_routes.py    # Billing
├── services/            # Business logic
│   ├── ai_service.py
│   ├── payment_service.py
│   ├── analytics_service.py
│   ├── task_routing_service.py
│   ├── email_automation_service.py
│   ├── integration_service.py
│   └── websocket_service.py
├── utils/               # Helpers
│   ├── supabase_client.py
│   └── email_service.py
├── config.py            # Settings
├── app_socketio.py      # Flask factory + SocketIO
└── requirements.txt     # Python dependencies
```

### Frontend (`frontend/`)
```
frontend/
├── src/
│   ├── pages/
│   │   ├── Dashboard.jsx    # Overview + KPIs
│   │   ├── Tasks.jsx        # Task management
│   │   ├── Team.jsx         # Member management
│   │   ├── Analytics.jsx    # Reports & charts
│   │   ├── Billing.jsx      # Invoice overview
│   │   ├── Invoices.jsx     # Invoice details
│   │   ├── CRM.jsx          # Client management
│   │   ├── HR.jsx           # Leave & attendance
│   │   ├── Settings.jsx     # Company config
│   │   ├── AIChat.jsx       # AI assistant
│   │   ├── Profile.jsx      # User settings
│   │   └── Login/Register.jsx
│   ├── components/
│   │   ├── TaskCard.jsx
│   │   ├── TaskDetailModal.jsx
│   │   ├── CreateTaskModal.jsx
│   │   ├── AISummary.jsx
│   │   └── PerformanceChart.jsx
│   ├── App.jsx           # Router + layout
│   ├── index.css         # Global styles
│   └── main.jsx          # Entry point
└── package.json
```

### Database Schema
- **18 tables** with relationships & indexes
- Row Level Security (RLS) enabled
- Materialized views for performance
- Auto-updating timestamps
- Proper foreign key constraints

See `database_schema_complete.sql` for full DDL.

---

## 🚦 Quick Start

### Prerequisites
- Node.js 18+ & npm
- Python 3.11+
- Supabase account (free tier works)

### 30-Second Setup (Docker)

```bash
# Clone repo
git clone <your-repo>
cd smart-office-manager

# Configure
cp backend/.env.example backend/.env
# Edit backend/.env → add Supabase keys

# Start everything
docker-compose up -d

# Open browser
open http://localhost:3000
# Login: admin@demo.com / Admin@123
```

### Manual Setup (for development)

**Backend:**
```bash
cd backend
python -m venv venv
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

pip install -r requirements.txt
cp .env.example .env  # edit with your keys
python app_socketio.py
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
# → http://localhost:5173
```

**Database:**
1. Create Supabase project
2. Copy `database_schema_complete.sql`
3. Paste into Supabase SQL Editor → Run

---

## ⚙️ Configuration

### Environment Variables (`.env`)

| Variable | Required | Purpose |
|----------|----------|---------|
| `SUPABASE_URL` | ✅ | Supabase project URL |
| `SUPABASE_KEY` | ✅ | Supabase anon key |
| `JWT_SECRET` | ✅ | Sign JWT tokens (32+ chars) |
| `SECRET_KEY` | ✅ | Flask session secret |

| `OPENAI_API_KEY` | ⭕ | AI features (GPT-4) |
| `SMTP_USERNAME` | ⭕ | Email sending |
| `SMTP_PASSWORD` | ⭕ | Email password |
| `SLACK_BOT_TOKEN` | ⭕ | Slack notifications |
| `GITHUB_TOKEN` | ⭕ | GitHub integration |

✅ Required | ⭕ Optional

---

## 📡 API Endpoints

### Authentication
```
POST   /api/auth/register
POST   /api/auth/login
POST   /api/auth/logout
POST   /api/auth/refresh
POST   /api/auth/2fa/enable
POST   /api/auth/2fa/verify
```

### Tasks
```
GET    /api/tasks/                    # List all
GET    /api/tasks/?user_id=           # Filter by user
POST   /api/tasks/create-task         # Manual create
POST   /api/tasks/create-from-ai      # AI parsing
PUT    /api/tasks/<id>                # Update
POST   /api/tasks/<id>/complete       # Mark complete
POST   /api/tasks/<id>/assign         # Assign employee
GET    /api/tasks/metrics             # Dashboard stats
```

### Geo
```
POST   /api/geo/verify                 # Distance check
GET    /api/geo/reverse-geocode        # coords → address
GET    /api/geo/geocode                # address → coords
```

### AI
```
POST   /api/ai/parse-task              # NLP → structured task
POST   /api/ai/summarize               # Project summary
POST   /api/ai/extract                 # Document extraction
GET    /api/ai/predict-risk/<task_id>  # Delay prediction
GET    /api/ai/smart-plan              # Daily plan
POST   /api/ai/ask                     # Chat assistant
POST   /api/ai/auto-assign/<task_id>   # Auto route
```

### Analytics
```
GET    /api/analytics/dashboard/<company_id>
GET    /api/analytics/employee/<employee_id>
GET    /api/analytics/benchmark/<company_id>
GET    /api/analytics/at-risk-tasks/<company_id>
```

### Email
```
POST   /api/email/daily-summary/<user_id>
POST   /api/email/weekly-report/<company_id>
POST   /api/email/overdue-reminder/<task_id>
```

### Integrations
```
POST   /api/integrations/connect
POST   /api/integrations/slack/task-notification
POST   /api/integrations/zoom/create-meeting
POST   /api/integrations/github/link
```

### Others
```
GET    /api/users/profile/<id>
POST   /api/users/checkin
POST   /api/users/checkout
GET    /api/company/<id>/team
POST   /api/company/<id>/invite
GET/POST /api/clients/
GET/POST /api/invoices/
POST   /api/invoices/<id>/send
GET    /api/hr/leave-requests
POST   /api/hr/leave-requests
```

---

## 🎯 Use Cases

### For Managers
1. **Create tasks** with AI assistance
2. **Review team performance** via analytics dashboard
3. **Approve task completions** → auto-trigger payments
4. **Monitor risk alerts** for at-risk projects
5. **Generate invoices** from completed work

### For Employees
1. **View smart plan** - AI-prioritized daily task list
2. **Check in** at office via GPS
3. **Complete tasks** with location verification
4. **Track earnings** in real-time
5. **Request leave** via HR module

### For Admins
1. **Manage company settings** (email templates, working hours, geo radius)
2. **Invite/remove team members**
3. **Configure integrations** (Slack, Zoom, GitHub)
4. **View financial reports** (revenue, expenses, disbursements)
5. **Set up 2FA** for security

---

## 🔐 Security Highlights

- ✅ JWT authentication with refresh tokens
- ✅ Two-factor authentication (TOTP)
- ✅ Role-based access control (5 roles)
- ✅ Row Level Security (Supabase)
- ✅ Activity logging (full audit trail)
- ✅ Rate limiting (API + Nginx)
- ✅ HTTPS enforcement (production)
- ✅ SQL injection prevention (parameterized)
- ✅ XSS protection headers
- ✅ CORS whitelisting

---

## 📊 Database Design

**18 Tables:**
- Core: companies, users, tasks, attendance, payments
- AI: ai_logs, predictions
- CRM: clients
- Finance: invoices, expenses
- HR: leave_requests
- System: activity_logs, company_settings, integrations, notifications, documents, webhooks

**Views:**
- `employee_performance` - Aggregated metrics
- `daily_attendance_summary` - Attendance rollup

All tables have:
- `id` UUID primary key
- `created_at`, `updated_at` timestamps
- Foreign key constraints
- Appropriate indexes

---

## 🧪 Testing

```bash
# Backend unit tests
cd backend
pytest tests/

# Frontend tests
cd frontend
npm test

# API test with curl
curl http://localhost:5000/health
curl -H "Authorization: Bearer $TOKEN" http://localhost:5000/api/tasks/

# Load testing (Locust)
locust -f tests/load_test.py
```

---

## 📦 Deployment

### Production Checklist

- [x] Docker configuration (multi-stage build)
- [x] Nginx reverse proxy with SSL
- [x] Environment variables configured
- [x] Database backups scheduled
- [x] Logging & monitoring
- [x] Health checks `/health`
- [x] Rate limiting enabled
- [x] Security headers set
- [x] Celery workers for async tasks
- [x] Flower dashboard for monitoring

### Deploy to Cloud

**Railway / Render / Fly.io** (simplest):
```bash
# Push to GitHub
git push origin main

# Connect repo to platform
# Add environment variables
# Deploy!
```

**AWS / GCP / Azure** (manual):
```bash
# Build Docker image
docker build -t smartos .

# Push to registry
docker tag smartos gcr.io/your-project/smartos:latest
docker push gcr.io/your-project/smartos:latest

# Deploy to Kubernetes / ECS / Cloud Run
```

See `SETUP_GUIDE.md` for complete deployment instructions.

---

## 🤝 Contributing

We welcome contributions! Please:

1. Fork the repo
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit (`git commit -m 'Add amazing feature'`)
4. Push (`git push origin feature/amazing-feature`)
5. Open Pull Request

---

## 📄 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file.

---

## 🙏 Acknowledgments

- **Supabase** - Amazing backend-as-a-service with Postgres
- **Flask** - Simple yet powerful Python web framework
- **React** - Component-based UI library
- **OpenAI / Anthropic** - Cutting-edge AI models
- **Razorpay** - Developer-friendly payments (India)
- **Lucide** - Beautiful icon set

---

## 📞 Support

- **Docs:** https://docs.smartsos.com (coming soon)
- **Issues:** https://github.com/your-repo/issues
- **Email:** support@smartsos.com
- **Discord:** Join our community (link coming soon)

---

## 🎯 Roadmap

**Phase 1 (Current) - Core Platform**
- ✅ All core features
- ✅ AI assistant
- ✅ Multi-tenant SaaS
- ✅ Real-time notifications

**Phase 2 (Q3 2024) - Mobile & Advanced**
- 📱 React Native mobile apps
- 🎙️ Voice-to-task (speech recognition)
- 📅 Calendar integration (Google Calendar)
- 🔄 Advanced sync (bidirectional)

**Phase 3 (Q4 2024) - Enterprise**
- 🏢 SSO / SAML / LDAP
- 📊 Advanced BI & custom reports
- 🔌 Marketplace for integrations
- 🤝 Customer portal

---

**Built with ❤️ for teams that move fast.**

*SmartOS — Your office, intelligently automated.*