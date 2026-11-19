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
table = soup.find('table', class_='iddaa-oyna-table')
if table:
    rows = table.find_all('tr')
    print(f"iddaa-oyna-table rows: {len(rows)}")
    for idx, r in enumerate(rows[:20]):
        tds = [td.get_text(strip=True) for td in r.find_all('td')]
        if tds:
            print(f"Row {idx} ({len(tds)} cols): {' | '.join(tds[:8])}")
        else:
            th = r.find('th')
            if th:
                print(f"Row {idx} (Header): {th.get_text(strip=True)}")
