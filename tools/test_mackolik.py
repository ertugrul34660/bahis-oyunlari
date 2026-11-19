import urllib.request
import re
import json

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept-Language': 'tr-TR,tr;q=0.9'
}

def test():
    urls = [
        'https://arsiv.mackolik.com/Iddaa-Programi',
        'https://www.mackolik.com/tr',
        'https://api.mackolik.com/op/matches'
    ]
    for url in urls:
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = resp.read()
                print(f"{url} -> Success! Status: {resp.status}, Bytes: {len(data)}")
        except Exception as e:
            print(f"{url} -> Error: {e}")

if __name__ == '__main__':
    test()
