import os
import sys
from dotenv import load_dotenv

sys.path.append(os.path.join(os.getcwd(), 'backend'))

from utils.supabase_client import supabase_admin

def test_list_users():
    try:
        res = supabase_admin.auth.admin.list_users()
        print(f"Type of res: {type(res)}")
        print(f"First few elements: {res[:2] if isinstance(res, list) else 'not a list'}")
        
        if hasattr(res, 'users'):
            print(f"res has 'users' attribute. Type: {type(res.users)}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_list_users()
