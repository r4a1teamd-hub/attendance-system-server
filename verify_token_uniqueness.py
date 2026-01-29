import requests
import jwt
import sys

BASE_URL = "http://127.0.0.1:5000/api"
# Hardcoded default secret key from config.py for decoding verification
SECRET_KEY = "a-very-secret-string-for-jwt" 

def register_and_login(student_id):
    # Register
    requests.post(f"{BASE_URL}/register", json={
        "student_id": student_id,
        "username": f"User {student_id}",
        "email": f"{student_id}@test.com",
        "password": "password"
    })
    
    # Login
    res = requests.post(f"{BASE_URL}/login", json={
        "student_id": student_id,
        "password": "password"
    })
    
    if res.status_code != 200:
        print(f"Login failed for {student_id}: {res.text}")
        return None
        
    return res.json()['token']

def get_qr_token(auth_token):
    res = requests.get(f"{BASE_URL}/qr_token", headers={
        "Authorization": f"Bearer {auth_token}"
    })
    if res.status_code == 200:
        return res.json()['token']
    return None

def verify():
    print("--- Verifying QR Token Uniqueness ---")
    
    # User A
    token_a = register_and_login("unique_test_a")
    qr_a = get_qr_token(token_a)
    print(f"User A QR Token (prefix): {qr_a[:20]}...")
    
    # User B
    token_b = register_and_login("unique_test_b")
    qr_b = get_qr_token(token_b)
    print(f"User B QR Token (prefix): {qr_b[:20]}...")
    
    if qr_a == qr_b:
        print("\n[FAIL] Tokens are IDENTICAL!")
    else:
        print("\n[PASS] Tokens are different.")

    # Decode check
    try:
        decoded_a = jwt.decode(qr_a, SECRET_KEY, algorithms=['HS256'])
        decoded_b = jwt.decode(qr_b, SECRET_KEY, algorithms=['HS256'])
        
        print(f"\nDecoded A sub: {decoded_a['sub']}")
        print(f"Decoded B sub: {decoded_b['sub']}")
        
        if decoded_a['sub'] != decoded_b['sub']:
            print("[PASS] Payload 'sub' (User ID) is different.")
        else:
            print("[FAIL] Payload 'sub' is SAME!")
            
    except Exception as e:
        print(f"Decode error (SECRET_KEY might be different on server): {e}")

if __name__ == "__main__":
    verify()
