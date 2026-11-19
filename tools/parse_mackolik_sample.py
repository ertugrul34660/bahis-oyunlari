import urllib.request
from bs4 import BeautifulSoup
import re

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept-Language': 'tr-TR,tr;q=0.9'
}

def parse_program():
    url = 'https://arsiv.mackolik.com/Iddaa-Programi'
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=10) as resp:
        html = resp.read().decode('utf-8', errors='ignore')
    
    soup = BeautifulSoup(html, 'html.parser')
    rows = soup.find_all('tr', id=re.compile(r'^tr_\d+'))
    print(f"Total match rows found: {len(rows)}")

    matches = []
    for r in rows[:15]:
        tds = r.find_all('td')
        # Print basic columns
        text_cols = [td.get_text(strip=True) for td in tds]
        if len(text_cols) >= 8:
            matches.append(text_cols[:10])
    
    for idx, m in enumerate(matches[:5], 1):
        print(f"Match {idx}: {m}")

if __name__ == '__main__':
    parse_program()
