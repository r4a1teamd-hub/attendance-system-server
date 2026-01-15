import requests
import json
import os

SERVER_URL = "http://localhost:5000/api"
API_KEY = "default-insecure-api-key"

def test_api_key_auth():
    print("\n--- Testing API Key Authentication ---")
    headers = {
        'Content-Type': 'application/json',
        'X-API-KEY': API_KEY
    }
    # テストユーザーID (Admin Teacher)
    # 事前に確認した check_user.py の結果より 00001111 を使用
    payload = {
        'student_id': '00001111',
        'status': 'present',
        'recorded_by': 'verification_script_apikey'
    }
    
    try:
        response = requests.post(f"{SERVER_URL}/record_attendance", json=payload, headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        if response.status_code == 201:
            print("RESULT: SUCCESS")
        else:
            print("RESULT: FAILED")
    except Exception as e:
        print(f"Error: {e}")

def test_jwt_auth():
    print("\n--- Testing JWT Authentication ---")
    
    # 1. Login to get JWT
    login_payload = {
        'student_id': '99999999',
        'password': 'password123'
    }
    
    try:
        login_resp = requests.post(f"{SERVER_URL}/login", json=login_payload)
        if login_resp.status_code != 200:
            print("Login failed. Cannot proceed with JWT test.")
            return

        token = login_resp.json().get('token')
        print(f"Login successful. Got token: {token[:10]}...")
        
        # 2. Use JWT to record attendance
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {token}'
        }
        # JWT認証の場合、student_idは省略可能（トークンから取得）だが、明示しても良い
        payload = {
            'status': 'present',
            'recorded_by': 'verification_script_jwt'
        }
        
        response = requests.post(f"{SERVER_URL}/record_attendance", json=payload, headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 201:
            print("RESULT: SUCCESS")
        else:
            print("RESULT: FAILED")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_api_key_auth()
    test_jwt_auth()
