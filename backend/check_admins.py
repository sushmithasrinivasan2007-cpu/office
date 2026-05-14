import os
from supabase import create_client
from dotenv import load_dotenv

# Load env from parent dir if needed
load_dotenv('../frontend/.env')
url = os.getenv('VITE_SUPABASE_URL') or os.getenv('SUPABASE_URL')
key = os.getenv('VITE_SUPABASE_ANON_KEY') or os.getenv('SUPABASE_KEY')

if not url or not key:
    print("Error: Supabase credentials not found in environment.")
    exit(1)

supabase = create_client(url, key)
res = supabase.table('users').select('name, email, role, last_login').in_('role', ['admin', 'super_admin']).execute()

print("\n--- Registered Admins ---")
if not res.data:
    print("No admins found.")
else:
    for user in res.data:
        status = "Active" if user.get('last_login') else "Never Logged In"
        print(f"Name: {user['name']} | Email: {user['email']} | Role: {user['role']} | Status: {status} (Last: {user['last_login']})")
