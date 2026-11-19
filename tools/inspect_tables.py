import urllib.request
from bs4 import BeautifulSoup

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept-Language': 'tr-TR,tr;q=0.9'
}

url = 'https://arsiv.mackolik.com/Iddaa-Programi'
req = urllib.request.Request(url, headers=headers)
with urllib.request.urlopen(req, timeout=10) as resp:
    html = resp.read().decode('utf-8', errors='ignore')

soup = BeautifulSoup(html, 'html.parser')
tables = soup.find_all('table')
print(f"Total tables: {len(tables)}")
for i, t in enumerate(tables[:5]):
    print(f"Table {i}: id={t.get('id')}, class={t.get('class')}, rows={len(t.find_all('tr'))}")
    first_tr = t.find('tr')
    if first_tr:
        print(f"  First tr text: {first_tr.get_text(separator=' | ', strip=True)[:120]}")
