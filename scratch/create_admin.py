import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv('backend/.env')
url = os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_KEY') # Service role key

supabase = create_client(url, key)

email = "admin@neuroops.com"
password = "AdminPassword123!"

try:
    # Create user in Auth
    res = supabase.auth.admin.create_user({
        "email": email,
        "password": password,
        "email_confirm": True
    })
    
    user_id = res.user.id
    print(f"User created in Auth with ID: {user_id}")
    
    # Create company first to avoid foreign key error
    company_res = supabase.table('companies').insert({
        "name": "NeuroOps Master",
        "slug": "neuroops-master"
    }).execute()
    
    company_id = company_res.data[0]['id']
    print(f"Company created with ID: {company_id}")
    
    # Create user profile
    supabase.table('users').upsert({
        "id": user_id,
        "email": email,
        "name": "NeuroOps Admin",
        "role": "super_admin",
        "company_id": company_id,
        "is_active": True
    }).execute()
    
    print("User profile created and elevated to super_admin.")
    print(f"\nLOGIN DETAILS:\nEmail: {email}\nPassword: {password}")

except Exception as e:
    print(f"Error: {e}")
