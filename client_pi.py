import requests
import json
import datetime
import os

# Configuration
SERVER_URL = "http://localhost:5000/api/record_attendance"  # Change localhost to server IP if running on actual RasPi
API_KEY = "default-insecure-api-key" # Make sure this matches backend config

def send_attendance(student_id, status='present'):
    """
    Send attendance data to the server using API Key authentication.
    """
    headers = {
        'Content-Type': 'application/json',
        'X-API-KEY': API_KEY
    }
    
    payload = {
        'student_id': student_id,
        'status': status,
        'recorded_by': 'raspi_client_01',
        'timestamp': datetime.datetime.now().isoformat()
    }
    
    print(f"Sending data to {SERVER_URL}...")
    try:
        response = requests.post(SERVER_URL, json=payload, headers=headers)
        
        if response.status_code == 201:
            print("SUCCESS: Attendance recorded.")
            print(f"Response: {response.json()}")
            return True
        elif response.status_code == 401:
            print("ERROR: Unauthorized (Invalid API Key).")
            return False
        else:
            print(f"ERROR: Failed to record attendance. Status code: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("ERROR: Could not connect to server. Is it running?")
        return False
    except Exception as e:
        print(f"ERROR: An unexpected error occurred: {e}")
        return False

if __name__ == "__main__":
    print("--- Raspberry Pi Attendance Client (Simulated) ---")
    
    # Simple interactive loop for testing
    while True:
        sid = input("\nEnter student ID (or 'q' to quit): ").strip()
        if sid.lower() == 'q':
            break
            
        if not sid:
            continue
            
        send_attendance(sid)
