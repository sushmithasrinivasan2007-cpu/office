import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv('backend/.env')

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

print(f"URL: {url}")
print(f"Key: {key[:10]}...")

try:
    supabase = create_client(url, key)
    print("Success: Client created")
except Exception as e:
    print(f"Error: {e}")
