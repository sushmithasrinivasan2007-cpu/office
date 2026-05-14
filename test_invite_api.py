import requests
import json

def test_invite():
    url = "http://localhost:5000/api/company/2975c75b-7310-48ae-ae52-0821456d25ed/invite"
    payload = {
        "email": "test@example.com",
        "name": "Test User",
        "role": "employee",
        "invited_by": "00000000-0000-0000-0000-000000000000"
    }
    headers = {'Content-Type': 'application/json'}
    
    print(f"Calling {url}...")
    res = requests.post(url, data=json.dumps(payload), headers=headers)
    print(f"Status Code: {res.status_code}")
    print(f"Response: {res.text}")

if __name__ == "__main__":
    test_invite()
