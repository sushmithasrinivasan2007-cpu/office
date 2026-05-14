import os
from supabase import create_client
from dotenv import load_dotenv

# Load env
load_dotenv('../frontend/.env')
url = os.getenv('VITE_SUPABASE_URL') or os.getenv('SUPABASE_URL')
key = os.getenv('VITE_SUPABASE_ANON_KEY') or os.getenv('SUPABASE_KEY')

if not url or not key:
    print("Error: Supabase credentials not found.")
    exit(1)

supabase = create_client(url, key)

# Search for the user sushmithatumkur2127
search_term = "sushmithatumkur2127"
res = supabase.table('users').select('*').ilike('name', f'%{search_term}%').execute()

if res.data:
    user = res.data[0]
    print(f"Found user: {user['name']} ({user['id']}) with current role: {user['role']}")
    
    # Update role to super_admin
    update_res = supabase.table('users').update({'role': 'super_admin'}).eq('id', user['id']).execute()
    
    if update_res.data:
        print(f"SUCCESS: Role updated to super_admin for {user['name']}")
    else:
        print("Failed to update role.")
else:
    # Try searching by email prefix if name search failed
    res = supabase.table('users').select('*').ilike('email', f'%{search_term}%').execute()
    if res.data:
        user = res.data[0]
        update_res = supabase.table('users').update({'role': 'super_admin'}).eq('id', user['id']).execute()
        print(f"SUCCESS: Role updated to super_admin for {user['email']}")
    else:
        print(f"User '{search_term}' not found in database.")
