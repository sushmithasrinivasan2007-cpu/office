import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv('../frontend/.env')
url = os.getenv('VITE_SUPABASE_URL') or os.getenv('SUPABASE_URL')
key = os.getenv('VITE_SUPABASE_ANON_KEY') or os.getenv('SUPABASE_KEY')

supabase = create_client(url, key)
res = supabase.table('users').select('id, name, email, role').execute()

print("\n--- User List ---")
for user in res.data:
    print(f"ID: {user['id']} | Name: {user['name']} | Email: {user['email']} | Role: {user['role']}")
