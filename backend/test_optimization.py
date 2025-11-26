import requests
import json
import sys
import time

# Set encoding to utf-8 for console output
sys.stdout.reconfigure(encoding='utf-8')

BASE_URL = "http://127.0.0.1:8000/chat"

def run_test(name, payload):
    print(f"\n--- Running Test: {name} ---")
    start_time = time.time()
    try:
        response = requests.post(BASE_URL, json=payload)
        duration = time.time() - start_time
        if response.status_code == 200:
            data = response.json()
            print(f"Status: SUCCESS (Time: {duration:.2f}s)")
            print(f"Response: {data.get('response')[:100]}...")
            
            # Check for markdown symbols
            text = data.get('response')
            if '*' in text or '#' in text or '- ' in text:
                print("WARNING: Markdown symbols found!")
            else:
                print("Text Cleaning: PASS")
                
            audio = data.get('audio')
            if audio:
                print(f"Audio: Received ({len(audio)} chars)")
            else:
                print("Audio: None")
                
            print(f"Cached: {data.get('cached')}")
        else:
            print(f"Status: FAILED ({response.status_code})")
            print(response.text)
    except Exception as e:
        print(f"Error: {e}")

# Test 1: Text Cleaning (Assistant 1)
run_test("Text Cleaning (Assistant 1)", {"message": "Universitet haqida ma'lumot bering", "session_id": "test_clean_v1", "version": 1})

# Test 2: Audio Generation (Assistant 2) - First run (slow)
run_test("Audio Generation (Assistant 2 - Cold)", {"message": "Salom", "session_id": "test_audio_v2", "version": 2})

# Test 3: Audio Caching (Assistant 2) - Second run (fast)
run_test("Audio Caching (Assistant 2 - Warm)", {"message": "Salom", "session_id": "test_audio_v2", "version": 2})
