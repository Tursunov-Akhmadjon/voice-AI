import requests
import json
import sys

# Set encoding to utf-8 for console output
sys.stdout.reconfigure(encoding='utf-8')

BASE_URL = "http://127.0.0.1:8000/chat"

def run_test(name, payload):
    print(f"\n--- Running Test: {name} ---")
    print(f"Payload: {json.dumps(payload)}")
    try:
        response = requests.post(BASE_URL, json=payload)
        if response.status_code == 200:
            data = response.json()
            print("Status: SUCCESS")
            print(f"Response (Latin): {data.get('response')[:100]}...")
            if 'cyrillic' in data and data['cyrillic']:
                print(f"Cyrillic: {data['cyrillic'][:100]}...")
            else:
                print("Cyrillic: None")
            print(f"Cached: {data.get('cached')}")
        else:
            print(f"Status: FAILED ({response.status_code})")
            print(response.text)
    except Exception as e:
        print(f"Error: {e}")

# Test 1: Version 1 (Default)
run_test("Version 1 (Default)", {"message": "Salom, universitet qayerda joylashgan?", "session_id": "test_report_v1", "version": 1})

# Test 2: Version 2 (Cyrillic)
run_test("Version 2 (Cyrillic)", {"message": "Salom, universitet qayerda joylashgan?", "session_id": "test_report_v2", "version": 2})

# Test 3: Version 2 (Cache Hit)
run_test("Version 2 (Cache Hit)", {"message": "Salom, universitet qayerda joylashgan?", "session_id": "test_report_v2", "version": 2})
