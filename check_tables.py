import sys
import os
from pathlib import Path

# Add backend to path
sys.path.append(str(Path(__file__).parent / "backend"))

try:
    from utils.supabase_client import supabase_admin
    import postgrest
except ImportError:
    print("Error: Could not import backend modules. Make sure you are in the root directory.")
    sys.exit(1)

def check_tables():
    required_tables = [
        'companies', 'users', 'tasks', 'attendance', 'payments', 
        'clients', 'invoices', 'expenses', 'leave_requests', 
        'ai_logs', 'predictions', 'activity_logs', 'integrations', 
        'notifications', 'documents', 'company_settings'
    ]
    
    print("Checking for required database tables...\n")
    missing = []
    
    for table in required_tables:
        try:
            # Try to select 0 rows from the table
            supabase_admin.table(table).select('*').limit(0).execute()
            print(f" [OK] Table '{table}' exists.")
        except Exception as e:
            if "PGRST204" in str(e) or "PGRST205" in str(e) or "not find" in str(e).lower():
                print(f" [MISSING] Table '{table}' is missing!")
                missing.append(table)
            else:
                print(f" [ERROR] Could not verify table '{table}': {e}")
    
    if missing:
        print("\nSUMMARY: Your database is missing some tables.")
        print("Please run the SQL schema in your Supabase dashboard.")
    else:
        print("\nSUMMARY: All required tables found!")

if __name__ == "__main__":
    check_tables()
