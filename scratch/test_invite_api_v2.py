import requests
import uuid

url = "http://localhost:5000/api/company/35083752-41cc-4335-b90a-efe2616916da/invite"
data = {
    "email": f"test-invite-{uuid.uuid4().hex[:6]}@example.com",
    "name": "Test User"
}

print(f"Sending invite request to {url}...")
try:
    response = requests.post(url, json=data)
    print(f"Status Code: {response.status_code}")
    print(f"Response Body: {response.text}")
except Exception as e:
    print(f"Error: {e}")
