import requests

url = "http://localhost:5000/api/company/35083752-41cc-4335-b90a-efe2616916da/invite"
data = {
    "email": "test-invite-5a1f78@example.com", # Existing email
    "name": "Test User"
}

print(f"Sending DUPLICATE invite request to {url}...")
try:
    response = requests.post(url, json=data)
    print(f"Status Code: {response.status_code}")
    print(f"Response Body: {response.text}")
except Exception as e:
    print(f"Error: {e}")
