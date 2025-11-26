import requests
import json
import sys
import base64

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
            
            audio = data.get('audio')
            if audio:
                print(f"Audio: Received base64 string (Length: {len(audio)})")
                # Verify it's valid base64
                try:
                    base64.b64decode(audio)
                    print("Audio: Valid Base64")
                except:
                    print("Audio: Invalid Base64")
            else:
                print("Audio: None")
                
            print(f"Cached: {data.get('cached')}")
        else:
            print(f"Status: FAILED ({response.status_code})")
            print(response.text)
    except Exception as e:
        print(f"Error: {e}")

# Test 1: Assistant 1 (Browser TTS) - Expect no audio
run_test("Assistant 1 (Browser TTS)", {"message": "Salom", "session_id": "test_audio_v1", "version": 1})

# Test 2: Assistant 2 (Backend TTS) - Expect audio
run_test("Assistant 2 (Backend TTS)", {"message": "Salom", "session_id": "test_audio_v2", "version": 2})
