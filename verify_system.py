#!/usr/bin/env python3
"""
SmartOS - Simple System Verification
Checks if all required files exist
"""

import os
from pathlib import Path

def check_file(path, description):
    exists = Path(path).exists()
    status = "[OK]" if exists else "[MISSING]"
    print(f"  {status} {description}: {path}")
    return exists

def main():
    print("\n" + "="*60)
    print("  SmartOS System Verification")
    print("="*60 + "\n")

    base = Path(__file__).parent
    results = {'passed': 0, 'failed': 0}

    print("[1] Project Structure")
    checks = [
        (base / 'backend', 'Backend directory'),
        (base / 'frontend', 'Frontend directory'),
        (base / 'database_schema_complete.sql', 'Database schema'),
        (base / 'docker-compose.yml', 'Docker Compose'),
        (base / 'Dockerfile', 'Dockerfile'),
        (base / 'README.md', 'Main README'),
    ]
    for path, desc in checks:
        if check_file(path, desc):
            results['passed'] += 1
        else:
            results['failed'] += 1

    print("\n[2] Backend Core Files")
    backend_files = [
        ('backend/app_socketio.py', 'Main app'),
        ('backend/config.py', 'Configuration'),
        ('backend/requirements.txt', 'Dependencies'),
        ('backend/routes/auth_routes.py', 'Auth routes'),
        ('backend/routes/task_routes.py', 'Task routes'),
        ('backend/routes/geo_routes.py', 'Geo routes'),
        ('backend/routes/payment_routes.py', 'Payment routes'),
        ('backend/routes/ai_routes.py', 'AI routes'),
        ('backend/routes/analytics_routes.py', 'Analytics'),
        ('backend/routes/email_routes.py', 'Email routes'),
        ('backend/routes/integration_routes.py', 'Integration'),
        ('backend/routes/company_routes.py', 'Company routes'),
        ('backend/routes/user_routes.py', 'User routes'),
        ('backend/routes/client_routes.py', 'Client/CRM'),
        ('backend/routes/hr_routes.py', 'HR routes'),
        ('backend/routes/invoice_routes.py', 'Invoice routes'),
        ('backend/services/ai_service.py', 'AI Service'),
        ('backend/services/payment_service.py', 'Payment Service'),
        ('backend/services/analytics_service.py', 'Analytics Service'),
        ('backend/services/task_routing_service.py', 'Routing Service'),
        ('backend/services/email_automation_service.py', 'Email Service'),
        ('backend/services/integration_service.py', 'Integration Service'),
        ('backend/services/websocket_service.py', 'WebSocket Service'),
        ('backend/utils/supabase_client.py', 'Supabase client'),
    ]
    for path, desc in backend_files:
        if check_file(path, desc):
            results['passed'] += 1
        else:
            results['failed'] += 1

    print("\n[3] Frontend Components")
    frontend_files = [
        ('frontend/src/App.jsx', 'Main App'),
        ('frontend/src/index.css', 'Global styles'),
        ('frontend/src/pages/Dashboard.jsx', 'Dashboard'),
        ('frontend/src/pages/Tasks.jsx', 'Tasks'),
        ('frontend/src/pages/Team.jsx', 'Team'),
        ('frontend/src/pages/Analytics.jsx', 'Analytics'),
        ('frontend/src/pages/Billing.jsx', 'Billing'),
        ('frontend/src/pages/Invoices.jsx', 'Invoices'),
        ('frontend/src/pages/CRM.jsx', 'CRM'),
        ('frontend/src/pages/HR.jsx', 'HR'),
        ('frontend/src/pages/Settings.jsx', 'Settings'),
        ('frontend/src/pages/AIChat.jsx', 'AI Chat'),
        ('frontend/src/pages/Profile.jsx', 'Profile'),
        ('frontend/src/pages/Login.jsx', 'Login'),
        ('frontend/src/pages/Register.jsx', 'Register'),
        ('frontend/src/components/TaskCard.jsx', 'TaskCard'),
        ('frontend/src/components/TaskDetailModal.jsx', 'TaskDetail'),
        ('frontend/src/components/CreateTaskModal.jsx', 'CreateTask'),
    ]
    for path, desc in frontend_files:
        if check_file(path, desc):
            results['passed'] += 1
        else:
            results['failed'] += 1

    print("\n[4] Documentation")
    docs = [
        ('README.md', 'Main README'),
        ('SETUP_GUIDE.md', 'Setup guide'),
        ('FEATURES_IMPLEMENTED.md', 'Features list'),
        ('IMPLEMENTATION_COMPLETE.md', 'Summary'),
        ('backend/.env.example', 'Backend env template'),
        ('frontend/.env.example', 'Frontend env template'),
    ]
    for path, desc in docs:
        if check_file(path, desc):
            results['passed'] += 1
        else:
            results['failed'] += 1

    # Summary
    print("\n" + "="*60)
    total = results['passed'] + results['failed']
    pct = (results['passed'] / total * 100) if total > 0 else 0
    print(f"Results: {results['passed']}/{total} checks passed ({pct:.0f}%)")

    if results['failed'] == 0:
        print("\n[SUCCESS] All components verified!")
        print("\nNext steps:")
        print("  1. Copy backend/.env.example -> backend/.env")
        print("  2. Add your Supabase URL & API key")
        print("  3. Run: docker-compose up -d  OR  python app_socketio.py")
        print("  4. Open http://localhost:5173 (frontend) or http://localhost:5000 (API)")
        print("\nDemo credentials (after setup):")
        print("  admin@demo.com / Admin@123")
        print()
        return 0
    else:
        print(f"\n[WARNING] {results['failed']} check(s) failed.")
        print("Please install missing components.\n")
        return 1

if __name__ == '__main__':
    import sys
    sys.exit(main())