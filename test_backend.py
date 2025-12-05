import requests
import json
import time

BASE_URL = 'http://127.0.0.1:5000'

def test_backend():
    print("--- バックエンドAPIテスト開始 ---")

    # 1. 学生の登録
    print("\n1. 学生登録 (Register Student)...")
    student_data = {
        "student_id": "test_student_01",
        "username": "テスト学生",
        "email": "test@example.com",
        "password": "password123"
    }
    try:
        res = requests.post(f"{BASE_URL}/register", json=student_data)
        print(f"Status: {res.status_code}")
        print(f"Response: {res.json()}")
        if res.status_code == 201 or "already registered" in res.text:
            print("OK")
        else:
            print("FAILED")
    except Exception as e:
        print(f"FAILED: {e}")

    # 2. 学生ログイン
    print("\n2. 学生ログイン (Login Student)...")
    login_data = {
        "student_id": "test_student_01",
        "password": "password123"
    }
    token = None
    try:
        res = requests.post(f"{BASE_URL}/login", json=login_data)
        print(f"Status: {res.status_code}")
        if res.status_code == 200:
            token = res.json().get('token')
            print("Token取得: OK")
        else:
            print(f"FAILED: {res.text}")
    except Exception as e:
        print(f"FAILED: {e}")

    if not token:
        print("トークンがないためテストを中断します")
        return

    headers = {"Authorization": f"Bearer {token}"}

    # 3. 自分の情報取得
    print("\n3. ユーザー情報取得 (Get Me)...")
    try:
        res = requests.get(f"{BASE_URL}/me", headers=headers)
        print(f"Status: {res.status_code}")
        print(f"Response: {res.json()}")
    except Exception as e:
        print(f"FAILED: {e}")

    # 4. 出席記録 (RasPiからの送信をシミュレート)
    print("\n4. 出席記録送信 (Record Attendance)...")
    attendance_data = {
        "student_id": "test_student_01",
        "status": "present",
        "recorded_by": "test_script"
    }
    try:
        res = requests.post(f"{BASE_URL}/api/record_attendance", json=attendance_data)
        print(f"Status: {res.status_code}")
        print(f"Response: {res.json()}")
    except Exception as e:
        print(f"FAILED: {e}")

    # 5. 自分の出席履歴取得
    print("\n5. 出席履歴確認 (Get My Attendance)...")
    try:
        res = requests.get(f"{BASE_URL}/api/attendance/me", headers=headers)
        print(f"Status: {res.status_code}")
        print(f"Response: {res.json()}")
        if len(res.json()) > 0:
             print("データ確認: OK")
        else:
             print("データなし: FAILED")
    except Exception as e:
        print(f"FAILED: {e}")

    print("\n--- テスト完了 ---")

if __name__ == "__main__":
    test_backend()
