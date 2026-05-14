from utils.supabase_client import supabase_admin

def check_columns():
    # Use a dummy query to see the columns in the error message if it fails, 
    # or just select * and see what we get.
    try:
        res = supabase_admin.table('companies').select('*').limit(1).execute()
        if res.data:
            print("Columns found in companies:", res.data[0].keys())
        else:
            print("No data in companies to check columns.")
    except Exception as e:
        print(f"Error checking columns: {e}")

if __name__ == "__main__":
    check_columns()
