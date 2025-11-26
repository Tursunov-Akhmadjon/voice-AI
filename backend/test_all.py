import time, json, requests

BASE_URL = 'http://127.0.0.1:8001/chat'

def post(message, session_id, version):
    payload = {'message': message, 'session_id': session_id, 'version': version}
    return requests.post(BASE_URL, json=payload, timeout=30)

def test_assistant1():
    resp = post('Salom, universitet qayerda joylashgan?', 'test1', 1)
    data = resp.json()
    assert resp.status_code == 200, f'Assistant1 HTTP {resp.status_code}'
    assert 'response' in data, 'No response field'
    # Ensure no markdown symbols
    for sym in ['*', '-', '#']:
        assert sym not in data['response'], f'Markdown symbol {sym} found'
    # Ensure no follow‑up phrase at end
    follow_ups = [
        "Boshqa savolingiz bormi?",
        "Yana qanday ma'lumot kerak?",
        "Qo'shimcha savollaringiz bormi?",
        "Yana biror narsa bilmoqchimisiz?",
        "Boshqa biror narsa haqida so'ramoqchimisiz?",
        "Yana qanday yordam bera olaman?",
        "Qo'shimcha ma'lumot kerakmi?",
        "Boshqa biror savolingiz bo'lsa ayting."
    ]
    for fu in follow_ups:
        assert not data['response'].strip().endswith(fu), 'Repeated follow‑up found'
    print('Assistant1 test passed')

def test_assistant2_audio():
    resp = post('Salom, universitet qayerda joylashgan?', 'test2', 2)
    data = resp.json()
    assert resp.status_code == 200, f'Assistant2 HTTP {resp.status_code}'
    assert 'audio' in data and data['audio'], 'Audio missing for Assistant2'
    print('Assistant2 audio generation test passed')

def test_caching():
    # First request (cold)
    resp1 = post('Qanday yordam bera olaman?', 'test3', 2)
    data1 = resp1.json()
    # Second request same message (should be cache hit)
    resp2 = post('Qanday yordam bera olaman?', 'test3', 2)
    data2 = resp2.json()
    assert data2.get('cached') is True, 'Cache flag not true on second request'
    assert 'audio' in data2 and data2['audio'], 'Audio missing on cached response'
    print('Caching test passed')

if __name__ == '__main__':
    # Give server a moment to start if needed
    time.sleep(2)
    test_assistant1()
    test_assistant2_audio()
    test_caching()
    print('All tests passed')
