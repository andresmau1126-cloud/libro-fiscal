import urllib.request
import urllib.error
import json

url = 'http://127.0.0.1:8000/api/auth/login/'
data = json.dumps({}).encode('utf-8')
req = urllib.request.Request(url, data=data, method='POST', headers={'Content-Type': 'application/json'})
try:
    with urllib.request.urlopen(req, timeout=5) as resp:
        print(resp.status)
        print(resp.read().decode('utf-8'))
except urllib.error.HTTPError as e:
    print('HTTP', e.code)
    print(e.read().decode('utf-8'))
except Exception as e:
    print('ERR', type(e).__name__, e)
