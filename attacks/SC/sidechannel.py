from bs4 import BeautifulSoup
import requests
import random
import string
import time

BASE_URL = "http://localhost:3000"
REGISTER_URL = f"{BASE_URL}/signup"
LOGIN_URL = f"{BASE_URL}/login"
PARK_URL = f"{BASE_URL}/park"

# test acc
VALID_USERNAME = "testuser"
VALID_PASSWORD = "test1234"
VALID_PLATE = "ABC123"

# test acc 2
SECOND_USERNAME = "testuser2"
SECOND_PASSWORD = "test1234"

# list of some location IDs from DB for demo
# need to be replaced with valid IDs of locations from mongoDB
LOCATION_IDS = [
    "681070a8d9e334005e11a843",
    "681070a8d9e334005e11a844",
    "681070a8d9e334005e11a845"
]


def generate_license_plate():
    letters = "ABCDE"
    digits = "0123456789"
    return ''.join(random.choices(letters, k=3)) + ''.join(random.choices(digits, k=3))


def register_user(session, username, plate, password):
    data = {
        "username": username,
        "plate": plate,
        "password": password,
        "password2": password
    }
    response = session.post(REGISTER_URL, data=data)
    return response


def login_user(session, username, password):
    data = {
        "username": username,
        "password": password
    }
    response = session.post(LOGIN_URL, data=data, allow_redirects=False)
    return response.status_code in [200, 302]


def try_park(session, plate, location_id):
    data = {
        "licensePlate": plate,
        "location": location_id,
        "mintime": 10
    }

    response = session.post(PARK_URL, data=data)
    soup = BeautifulSoup(response.text, 'html.parser')

    alert = soup.find("div", class_="alert")
    if alert:
        alert_text = alert.get_text(strip=True)
        if "already" in alert_text.lower() or "error" in alert_text.lower() or "fail" in alert_text.lower():
            return "fail", alert_text
        elif "success" in alert_text.lower() or "parked" in alert_text.lower():
            return "success", alert_text
        else:
            return "unknown", alert_text
    else:
        return "unknown", "No alert message found"


def main():
    # create sessions for both users
    session1 = requests.Session()
    session2 = requests.Session()

    print("[*] Registering test user (testuser)...")
    res1 = register_user(session1, VALID_USERNAME, VALID_PLATE, VALID_PASSWORD)
    print(
        f"→ Status: {res1.status_code} | Already exists: {'License plate already registered' in res1.text}")

    # generate 99 other plates + the one we expect to already exist
    plates = [VALID_PLATE]
    while len(plates) < 100:
        new_plate = generate_license_plate()
        if new_plate not in plates:
            plates.append(new_plate)

    print("\n[*] Trying to register all plates...")
    for plate in plates:
        resp = register_user(session1, "bot_" + plate, plate, "test1234")
        if "License plate already registered" in resp.text:
            print(f"[+] Detected registered plate: {plate}")

    print("\n[*] Logging in as testuser...")
    if login_user(session1, VALID_USERNAME, VALID_PASSWORD):
        print("[+] Logged in.")
    else:
        print("[-] Login failed for testuser.")
        return

    location_id = LOCATION_IDS[0]
    print(f"[*] Parking {VALID_PLATE} at location {location_id}...")
    park_response_1 = try_park(session1, VALID_PLATE, location_id)
    print(f"[+] Park response: {park_response_1[:100]}")

    print("\n[*] Registering second user (testuser2)...")
    res2 = register_user(session2, SECOND_USERNAME, "CDE456", SECOND_PASSWORD)
    print(
        f"→ Status: {res2.status_code} | Message: {'License plate already registered' in res2.text}")

    print("[*] Logging in as testuser2...")
    if login_user(session2, SECOND_USERNAME, SECOND_PASSWORD):
        print("[+] Logged in.")
    else:
        print("[-] Login failed for testuser2.")
        return

    print(f"[*] Attempting to park {VALID_PLATE} again...")
    status, message = try_park(session2, VALID_PLATE, LOCATION_IDS[1])

    if status == "fail":
        print(f"Failed to park again: {message}")
    elif status == "success":
        print(f"Duplicate parking succeeded {message}")
    else:
        print(f"Unknown outcome. Message: {message}")


print("\nAttack Done")


if __name__ == "__main__":
    main()
