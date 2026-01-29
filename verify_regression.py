import requests
import json
import sys

BASE_URL = "http://127.0.0.1:5000/api"
REGISTER_URL = "http://127.0.0.1:5000/api/register" # Note: Register is often at /api/register or just /register. Checking routes.py: @bp.route('/api/register', methods=['POST'])

# Test Data
STUDENT_ID = "reg_test_01"
PASSWORD = "password123"
HEADERS = {"Content-Type": "application/json"}

def log(msg):
    print(f"[TEST] {msg}")

def run_tests():
    session = requests.Session()

    # 1. Register User (Idempotent-ish check)
    log("Registering test user...")
    try:
        res = requests.post(REGISTER_URL, json={
            "student_id": STUDENT_ID,
            "username": f"User {STUDENT_ID}",
            "email": f"{STUDENT_ID}@example.com",
            "password": PASSWORD
        }, headers=HEADERS)
        if res.status_code == 201:
            log("User registered.")
        elif res.status_code == 400 and "already registered" in res.text:
            log("User already exists, proceeding.")
        else:
            log(f"Registration failed: {res.status_code} {res.text}")
            return
    except Exception as e:
        log(f"Connection failed: {e}")
        return

    # 2. Login to get Token
    log("Logging in...")
    res = requests.post(f"{BASE_URL}/login", json={
        "student_id": STUDENT_ID,
        "password": PASSWORD
    }, headers=HEADERS)
    
    if res.status_code != 200:
        log(f"Login failed: {res.status_code} {res.text}")
        return
    
    token = res.json().get('token')
    log("Login successful, token received.")
    auth_headers = HEADERS.copy()
    auth_headers["Authorization"] = f"Bearer {token}"

    # 3. Test QR Token Generation (New Feature)
    log("Testing GET /api/qr_token...")
    res = requests.get(f"{BASE_URL}/qr_token", headers=auth_headers)
    if res.status_code == 200:
        qr_token = res.json().get('token')
        log("QR Token generated successfully.")
    else:
        log(f"QR Token generation failed: {res.status_code} {res.text}")
        qr_token = None

    # 4. Test Record Attendance with QR Token (New Feature)
    if qr_token:
        log("Testing POST /api/record_attendance with QR Token...")
        # Simulate Raspi (Auth via Token for now due to unknown API Key, but logic path is shared for body parsing)
        # Note: server checks API Key OR Token. Using Token is easiest for test script.
        # We need to spoof 'recorded_by' to ensure logic holds.
        res = requests.post(f"{BASE_URL}/record_attendance", json={
            "qr_token": qr_token,
            "recorded_by": "test_script_qr"
        }, headers=auth_headers)
        
        if res.status_code == 200:
            log("Attendance recorded with QR Token: SUCCESS")
        else:
             # It might fail if time slot doesn't match? Or if user already attended?
             # But 200 is expected for 'success' or 'updated'.
             log(f"Attendance with QR Token result: {res.status_code} {res.text}")

    # 5. Test Record Attendance with Student ID (LEGACY REGRESSION CHECK)
    log("Testing POST /api/record_attendance with Student ID (Legacy)...")
    res = requests.post(f"{BASE_URL}/record_attendance", json={
        "student_id": STUDENT_ID,
        "recorded_by": "test_script_legacy"
    }, headers=auth_headers)

    if res.status_code == 200:
        log("Legacy Attendance recorded: SUCCESS (Regression Passed)")
    else:
        log(f"Legacy Attendance failed: {res.status_code} {res.text}")
        print("!!! REGRESSION DETECTED: Manual attendance with student_id failed !!!")

if __name__ == "__main__":
    run_tests()
