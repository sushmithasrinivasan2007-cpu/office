from datetime import datetime
import time

class MockResponse:
    def __init__(self, data=None, error=None):
        self.data = data
        self.error = error

class MockAuth:
    def __init__(self):
        self.admin = self

    def create_user(self, data):
        class MockUser:
            def __init__(self):
                self.id = f"mock-user-{int(time.time())}"
        class MockResult:
            def __init__(self):
                self.user = MockUser()
        return MockResult()

    def update_user_by_id(self, user_id, data):
        return {"id": user_id, "updated": True}

    def sign_in_with_password(self, credentials):
        email = credentials.get('email')
        password = credentials.get('password')
        
        if email == "admin@demo.com" and password == "Admin@123":
            class MockSession:
                def __init__(self):
                    self.access_token = "mock-access-token"
                    self.refresh_token = "mock-refresh-token"
            class MockUser:
                def __init__(self):
                    self.id = "00000000-0000-0000-0000-000000000001"
            class MockResult:
                def __init__(self):
                    self.session = MockSession()
                    self.user = MockUser()
            return MockResult()
        
        # Generic success for any other login in mock mode
        class MockSession:
            def __init__(self):
                self.access_token = "mock-access-token"
                self.refresh_token = "mock-refresh-token"
        class MockUser:
            def __init__(self):
                self.id = "00000000-0000-0000-0000-000000000002" # Generic mock user
        class MockResult:
            def __init__(self):
                self.session = MockSession()
                self.user = MockUser()
        return MockResult()

    def sign_up(self, credentials):
        class MockUser:
            def __init__(self):
                self.id = "00000000-0000-0000-0000-000000000003" # New signup mock
        class MockSession:
            def __init__(self):
                self.access_token = "mock-access-token"
                self.refresh_token = "mock-refresh-token"
        class MockResult:
            def __init__(self):
                self.user = MockUser()
                self.session = MockSession()
        return MockResult()

# Global in-memory storage
MOCK_STORAGE = {
    "users": [
        {"id": "mock-user-id-admin", "email": "admin@demo.com", "name": "Demo Admin", "role": "admin", "company_id": "mock-company-id"},
        {"id": "mock-user-id-emp1", "email": "employee@demo.com", "name": "Demo Employee", "role": "employee", "company_id": "mock-company-id"}
    ],
    "tasks": [
        {"id": "mock-task-1", "title": "Initial Setup", "status": "pending", "priority": "high", "company_id": "mock-company-id", "assigned_to": "mock-user-id-admin", "created_at": datetime.now().isoformat()}
    ],
    "companies": [
        {"id": "mock-company-id", "name": "SmartOffice Solutions", "slug": "smartoffice-solutions"}
    ],
    "attendance": [],
    "activity_logs": []
}

class MockTable:
    def __init__(self, table_name):
        self.table_name = table_name
        self.filters = []

    def select(self, columns="*"): return self
    def insert(self, data):
        if self.table_name not in MOCK_STORAGE: MOCK_STORAGE[self.table_name] = []
        # Store for execute()
        self.pending_data = data if isinstance(data, list) else [data]
        
        # Immediate save to mock storage
        for item in self.pending_data:
            if 'id' not in item: item['id'] = f"mock-{int(time.time()*1000)}"
            MOCK_STORAGE[self.table_name].append(item)
            
        return self

    def update(self, data):
        # Basic update logic
        table_data = MOCK_STORAGE.get(self.table_name, [])
        for item in table_data:
            match = True
            for col, val in self.filters:
                if item.get(col) != val:
                    match = False
                    break
            if match:
                item.update(data)
        return self

    def delete(self): return self
    def upsert(self, data):
        return self.insert(data)
    def eq(self, col, val):
        self.filters.append(('eq', col, val))
        return self
    def in_(self, col, vals):
        self.filters.append(('in', col, vals))
        return self
    def gte(self, col, val):
        self.filters.append(('gte', col, val))
        return self
    def lte(self, col, val):
        self.filters.append(('lte', col, val))
        return self
    def is_(self, col, val):
        self.filters.append(('is', col, val))
        return self
    def order(self, col, desc=False): return self
    def limit(self, count): return self

    def execute(self):
        data = MOCK_STORAGE.get(self.table_name, [])
        filtered_data = data
        for op, col, val in self.filters:
            if op == 'eq':
                filtered_data = [d for d in filtered_data if d.get(col) == val]
            elif op == 'in':
                filtered_data = [d for d in filtered_data if d.get(col) in val]
            elif op == 'gte':
                filtered_data = [d for d in filtered_data if str(d.get(col, '')) >= str(val)]
            elif op == 'lte':
                filtered_data = [d for d in filtered_data if str(d.get(col, '')) <= str(val)]
            elif op == 'is':
                if val == 'null':
                    filtered_data = [d for d in filtered_data if d.get(col) is None or d.get(col) == 'null']
                else:
                    filtered_data = [d for d in filtered_data if d.get(col) == val]
        return MockResponse(data=filtered_data)

class MockClient:
    def __init__(self):
        self.auth = MockAuth()
    def table(self, table_name):
        return MockTable(table_name)

import os
from dotenv import load_dotenv
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY or "your-project" in SUPABASE_URL:
    print("[MOCK] Supabase credentials missing. Persistent Mock Mode active.")
    supabase = MockClient()
    supabase_admin = MockClient()
else:
    try:
        from supabase import create_client
        # Standard client (can be authenticated)
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        # Admin client (uses service role key to bypass RLS)
        supabase_admin = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        # Simple check to verify connection
        print(f"[SUCCESS] Connected to Supabase: {SUPABASE_URL}")
    except Exception as e:
        print(f"[ERROR] Supabase initialization failed: {e}")
        print("[FALLBACK] Switching to Mock Mode due to initialization error.")
        supabase = MockClient()
        supabase_admin = MockClient()
