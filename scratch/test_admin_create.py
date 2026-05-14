import sys
import os
from dotenv import load_dotenv

# Add paths
current_file = os.path.abspath(__file__)
project_root = os.path.dirname(os.path.dirname(current_file))
backend_dir = os.path.join(project_root, 'backend')
sys.path.insert(0, project_root)
sys.path.insert(0, backend_dir)

load_dotenv(os.path.join(backend_dir, '.env'))

from backend.utils.supabase_client import supabase_admin

try:
    email = f"test-{os.urandom(4).hex()}@example.com"
    print(f"Testing admin.create_user for {email}...")
    res = supabase_admin.auth.admin.create_user({
        "email": email,
        "password": "password123",
        "email_confirm": True
    })
    print(f"Response type: {type(res)}")
    print(f"User ID: {res.id}")
    
    # Cleanup
    supabase_admin.auth.admin.delete_user(res.id)
    print("Deleted test user.")
except Exception as e:
    print(f"Error: {e}")
