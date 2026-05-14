from utils.supabase_client import supabase_admin
import json

def check_db():
    print("Checking companies...")
    comp_res = supabase_admin.table('companies').select('id, name').execute()
    print(f"Companies found: {len(comp_res.data)}")
    for c in comp_res.data:
        print(f" - {c['id']}: {c['name']}")

    print("\nChecking users...")
    user_res = supabase_admin.table('users').select('id, email, company_id').execute()
    print(f"Users found: {len(user_res.data)}")
    for u in user_res.data:
        print(f" - {u['id']}: {u['email']} (Company: {u['company_id']})")

if __name__ == "__main__":
    check_db()
