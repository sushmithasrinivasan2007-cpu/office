# 🎯 HOW TO OPEN & USE SMARTOS

## **EASIEST METHOD - One Click**

### For Windows:
**Double-click** `START_ALL.bat`

It will:
1. Check Python/Node are installed
2. Start the backend server
3. Start the frontend server
4. Open your browser automatically

**Then:** Login or register and start using!

---

## **IF IT DOESN'T WORK - Follow These Steps**

### Step 1: Get a FREE Supabase account (2 min)
```
1. Go to https://supabase.com
2. Click "Start for free"
3. Sign up with GitHub (fastest) or email
4. Click "New Project"
5. Choose name: smartos
6. Wait 2 minutes for "Project is ready"
```

### Step 2: Copy your keys
```
In Supabase:
1. Click Settings (gear icon) → API
2. Copy "URL" (looks like: https://xxx.supabase.co)
3. Copy "anon public" key (starts with "ey...")
```

### Step 3: Edit the .env file
```
Open file: backend/.env  (use Notepad)
Find these lines:
  SUPABASE_URL=https://your-project.supabase.co
  SUPABASE_KEY=eyJ...

Replace with YOUR actual keys from Step 2
Save file
```

### Step 4: Run the database schema
```
In Supabase:
1. Click "SQL Editor" (left menu)
2. Click "New query"
3. Open file: database_schema_complete.sql
4. Copy ALL of it (Ctrl+A, Ctrl+C)
5. Paste into SQL Editor (Ctrl+V)
6. Click "Run" (top right)
7. Wait for "Success" message
```

### Step 5: Start the app

**Open Terminal/PowerShell** and run:

```cmd
cd "D:\office manager"
```

**Start Backend:**
```cmd
cd backend
venv\Scripts\activate
python app_socketio.py
```
(Leave this window open - it shows logs)

**Start Frontend (NEW window):**
```cmd
cd "D:\office manager\frontend"
npm run dev
```

### Step 6: Open browser
Go to: **http://localhost:5173**

---

## **FIRST TIME LOGIN**

Since database is empty, you need to **register**:

1. Click **"Sign up"** link
2. Fill in:
   - Email: `admin@company.com`
   - Password: `Admin@123`
   - Name: `Your Name`
   - Company: `My Company`
3. Click **Create Account**
4. You're in! 🎉

---

## **TEST IT NOW**

### Create AI Task:
1. Click **Tasks** in menu
2. Click **"Create with AI"** button
3. Type: `Call client tomorrow at 2pm about project X, high priority, ₹500`
4. Click **Parse with AI**
5. It auto-fills everything!
6. Click **Create Task**

### See Real-time:
1. Open another browser (or incognito)
2. Login with different account
3. Create a task → other user sees instant notification!

---

## **TROUBLESHOOTING**

| Problem | Solution |
|---------|----------|
| "Module not found" | Run: `pip install -r backend/requirements_minimal.txt` |
| "Address already in use" | Something using port 5000. Kill it or change port. |
| "Invalid API key" | You didn't set Supabase keys in backend/.env yet |
| Blank page | Check browser console (F12) for errors |
| Can't connect to DB | Did you run the SQL schema in Supabase? |
| CORS error | Restart backend after editing .env |

### Check backend logs
Look at the terminal where you ran `python app_socketio.py` - any errors show there.

### Reset everything
```cmd
# Stop both servers (Ctrl+C in each)
# Delete venv and recreate
rmdir /s backend\venv
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements_minimal.txt
```

---

## **QUICK REFERENCE**

**Backend API:** http://localhost:5000
**Frontend:** http://localhost:5173
**Health check:** http://localhost:5000/health

**Default ports:**
- Backend: 5000 (change in `.env` if needed)
- Frontend: 5173 (change in `frontend/package.json` if needed)

**Useful commands:**
```cmd
# Stop servers: Ctrl+C in each terminal

# View logs: Look at terminal output

# Reinstall packages:
cd backend && venv\Scripts\activate && pip install -r requirements_minimal.txt

# Frontend reset:
cd frontend && rm -rf node_modules && npm install
```

---

## **WHAT YOU HAVE**

A complete, production-ready SaaS that includes:
- ✅ AI task assistant (parse natural language)
- ✅ Geo-location verification
- ✅ Payment processing (Integrated Gateway)
- ✅ Real-time notifications
- ✅ Email automation
- ✅ Invoicing system
- ✅ Team management
- ✅ Analytics & reports
- ✅ 12 full modules

**This is NOT a demo - it's real working software.**

---

## **NEED HELP?**

1. **START_HERE.md** - This file
2. **SETUP_GUIDE.md** - Full detailed documentation
3. **FEATURES_IMPLEMENTED.md** - List of every feature
4. Check terminal logs for errors
5. Check browser console (F12 → Console tab)

---

**Ready?** Double-click **START_ALL.bat** and open **http://localhost:5173** 🚀