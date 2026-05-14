import requests

# This user was already invited (so they exist in users table and Auth)
url = "http://127.0.0.1:5000/api/auth/register"
data = {
    "email": "test-invite-5a1f78@example.com", 
    "password": "password123",
    "name": "Test User",
    "role": "employee",
    "company_id": "35083752-41cc-4335-b90a-efe2616916da"
}

print(f"Testing registration for INVITED user at {url}...")
try:
    response = requests.post(url, json=data)
    print(f"Status Code: {response.status_code}")
    print(f"Response Body: {response.text}")
except Exception as e:
    print(f"Error: {e}")
