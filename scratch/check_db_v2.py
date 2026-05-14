import os
import sys
from dotenv import load_dotenv

# Add project root to sys.path
current_file = os.path.abspath(__file__)
project_root = os.path.dirname(os.path.dirname(current_file))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

try:
    from backend.utils.supabase_client import supabase_admin
except ImportError as e:
    print(f"[ERROR] Could not find 'backend.utils.supabase_client'.")
    print(f"Project root: {project_root}")
    raise e

def check_users_table():
    try:
        # Check users table
        res = supabase_admin.table('users').select('*').limit(1).execute()
        if res.data:
            print("Columns in 'users' table:", list(res.data[0].keys()))
        else:
            print("'users' table is empty.")
            
        # Check companies table
        res = supabase_admin.table('companies').select('*').limit(1).execute()
        if res.data:
            print("Columns in 'companies' table:", list(res.data[0].keys()))
        else:
            print("'companies' table is empty.")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_users_table()
