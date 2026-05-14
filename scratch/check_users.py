import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv('backend/.env')
url = os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_KEY')

supabase = create_client(url, key)
res = supabase.table('users').select('email, role').execute()
print(res.data)
