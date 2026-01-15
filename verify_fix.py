import requests
import sys

# Login to get token
try:
    auth_resp = requests.post('http://localhost:5000/api/login', json={'student_id': '00001111', 'password': 'admin'})
    if auth_resp.status_code != 200:
        print(f"Login failed: {auth_resp.text}")
        sys.exit(1)
    
    token = auth_resp.json().get('token')
    headers = {'Authorization': f'Bearer {token}'}

    # Check stats endpoint
    print("Checking /api/admin/stats...")
    stats_resp = requests.get('http://localhost:5000/api/admin/stats', headers=headers)
    
    if stats_resp.status_code == 200:
        print("Success! /api/admin/stats returned 200 OK")
        print(stats_resp.json())
    else:
        print(f"Error! /api/admin/stats returned {stats_resp.status_code}")
        print(stats_resp.text)
        sys.exit(1)
        
except Exception as e:
    print(f"Exception: {e}")
    sys.exit(1)
