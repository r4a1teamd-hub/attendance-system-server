import requests
import json

BASE_URL = 'http://localhost:5000/api'
ADMIN_ID = '00001111'
ADMIN_PASS = 'admin'

# 1. Login as Admin
print("--- 1. Login as Admin ---")
resp = requests.post(f'{BASE_URL}/login', json={'student_id': ADMIN_ID, 'password': ADMIN_PASS})
if resp.status_code != 200:
    print(f"Admin login failed: {resp.text}")
    exit(1)
admin_token = resp.json()['token']
print("Admin logged in.")

# 2. Register New Student
print("\n--- 2. Register New Student ---")
new_student_id = "99990001"
requests.post(f'{BASE_URL}/admin/reset_password', json={'user_id': 9999}, headers={'Authorization': f'Bearer {admin_token}'}) # Cleanup attempt just in case (will fail usually but thats ok)

# Need to find if user exists to delete, or just ignore error on Create
# Let's try to create
reg_data = {
    'student_id': new_student_id,
    'username': 'Test Student 99',
    'email': 'test99@school.edu'
}
resp = requests.post(f'{BASE_URL}/admin/users', json=reg_data, headers={'Authorization': f'Bearer {admin_token}'})
if resp.status_code == 201:
    print("User created.")
    user_id = resp.json()['user']['id']
elif resp.status_code == 400 and "already registered" in resp.text:
    print("User already exists, continuing...")
    # Get user id to leverage existing
    resp = requests.get(f'{BASE_URL}/admin/users', headers={'Authorization': f'Bearer {admin_token}'})
    for u in resp.json():
        if u['student_id'] == new_student_id:
            user_id = u['id']
            break
    # Reset it to be sure
    requests.post(f'{BASE_URL}/admin/reset_password', json={'user_id': user_id}, headers={'Authorization': f'Bearer {admin_token}'})
else:
    print(f"Registration failed: {resp.text}")
    exit(1)

# 3. Login as New Student (Initial)
print("\n--- 3. Login as New Student (Initial) ---")
resp = requests.post(f'{BASE_URL}/login', json={'student_id': new_student_id, 'password': new_student_id})
if resp.status_code != 200:
    print(f"Student login failed: {resp.text}")
    exit(1)

data = resp.json()
is_changed = data['user']['is_password_changed']
student_token = data['token']
print(f"Logged in. is_password_changed: {is_changed}")

if is_changed is not False:
    print("ERROR: is_password_changed should be False initially.")
    exit(1)
else:
    print("SUCCESS: is_password_changed is False.")

# 4. Change Password
print("\n--- 4. Change Password ---")
new_pass = "newpassword123"
resp = requests.post(f'{BASE_URL}/change_password', json={'current_password': new_student_id, 'new_password': new_pass}, headers={'Authorization': f'Bearer {student_token}'})
if resp.status_code == 200:
    print("Password changed successfully.")
else:
    print(f"Password change failed: {resp.text}")
    exit(1)

# 5. Login with New Password
print("\n--- 5. Login with New Password ---")
resp = requests.post(f'{BASE_URL}/login', json={'student_id': new_student_id, 'password': new_pass})
if resp.status_code != 200:
    print(f"Student login with new pass failed: {resp.text}")
    exit(1)

data = resp.json()
is_changed = data['user']['is_password_changed']
print(f"Logged in. is_password_changed: {is_changed}")

if is_changed is not True:
    print("ERROR: is_password_changed should be True after change.")
    exit(1)
else:
    print("SUCCESS: is_password_changed is True.")

# 6. Admin Reset Password
print("\n--- 6. Admin Reset Password ---")
resp = requests.post(f'{BASE_URL}/admin/reset_password', json={'user_id': user_id}, headers={'Authorization': f'Bearer {admin_token}'})
if resp.status_code == 200:
    print("Password reset by admin successful.")
else:
    print(f"Admin reset failed: {resp.text}")
    exit(1)

# 7. Login with Initial Password (After Reset)
print("\n--- 7. Login with Initial Password (After Reset) ---")
resp = requests.post(f'{BASE_URL}/login', json={'student_id': new_student_id, 'password': new_student_id})
if resp.status_code != 200:
    print(f"Student login with initial pass failed: {resp.text}")
    exit(1)

data = resp.json()
is_changed = data['user']['is_password_changed']
print(f"Logged in. is_password_changed: {is_changed}")

if is_changed is not False:
    print("ERROR: is_password_changed should be False after reset.")
    exit(1)
else:
    print("SUCCESS: is_password_changed is False (Reset confirmed).")

print("\n--- ALL TESTS PASSED ---")
