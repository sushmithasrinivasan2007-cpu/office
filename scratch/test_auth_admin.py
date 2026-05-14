import os
from dotenv import load_dotenv
from supabase import create_client
import uuid

load_dotenv('backend/.env')

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

supabase_admin = create_client(url, key)

print(f"Testing auth.admin.create_user...")
try:
    # Use a dummy email
    email = f"test-{uuid.uuid4().hex[:6]}@example.com"
    res = supabase_admin.auth.admin.create_user({
        "email": email,
        "email_confirm": True,
        "password": "TemporaryPassword123!"
    })
    print(f"Success: {res.user.id}")
    
    # Clean up
    supabase_admin.auth.admin.delete_user(res.user.id)
    print("Cleaned up.")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
