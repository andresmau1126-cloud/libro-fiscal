import urllib.request
import urllib.error

paths = ['/api/auth/login/', '/api/auth/register/', '/api/auth/me/']
for path in paths:
    url = 'http://127.0.0.1:8000' + path
    try:
        req = urllib.request.Request(url, method='GET')
        with urllib.request.urlopen(req, timeout=5) as resp:
            print(path, resp.status)
    except urllib.error.HTTPError as e:
        print(path, 'HTTP', e.code)
    except Exception as e:
        print(path, 'ERR', type(e).__name__, e)
