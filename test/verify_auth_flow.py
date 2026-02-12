import requests
import sys

def verify_auth():
    base_url = "http://localhost:8000/auth"
    username = "verifyuser_final"
    password = "password123"
    
    print(f"--- Verifying Auth at {base_url} ---")
    
    # 1. Register
    reg_payload = {
        "username": username,
        "email": f"{username}@example.com",
        "password": password
    }
    print(f"Attempting registration for {username}...")
    try:
        resp = requests.post(f"{base_url}/register", json=reg_payload, timeout=5)
        print(f"Register Status: {resp.status_code}")
        if resp.status_code not in [200, 400]: # 400 if already exists
            print(f"Success/Exists: {resp.text}")
        else:
            print(f"Registration Result: {resp.text}")
    except Exception as e:
        print(f"Registration Failed: {e}")
        return

    # 2. Login
    print(f"\nAttempting login for {username}...")
    login_payload = {
        "username": username,
        "password": password
    }
    try:
        resp = requests.post(f"{base_url}/login", data=login_payload, timeout=5)
        print(f"Login Status: {resp.status_code}")
        if resp.status_code == 200:
            print("Login Successful!")
            print(f"Token: {resp.json().get('access_token')[:20]}...")
        else:
            print(f"Login Failed: {resp.text}")
    except Exception as e:
        print(f"Login Request Failed: {e}")

if __name__ == "__main__":
    verify_auth()
