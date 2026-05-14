import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv('../frontend/.env')
url = os.getenv('VITE_SUPABASE_URL') or os.getenv('SUPABASE_URL')
key = os.getenv('VITE_SUPABASE_ANON_KEY') or os.getenv('SUPABASE_KEY')

supabase = create_client(url, key)

# Fetch all users
res = supabase.table('users').select('id, email').execute()

if res.data:
    for user in res.data:
        print(f"Elevating {user['email']}...")
        supabase.table('users').update({'role': 'super_admin'}).eq('id', user['id']).execute()
    print("DONE: All users elevated to super_admin.")
else:
    print("No users found.")
