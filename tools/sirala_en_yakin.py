# -*- coding: utf-8 -*-
import sys
from pathlib import Path
from datetime import datetime

project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

from core.mackolik_harvester import MackolikHarvester

harvester = MackolikHarvester()
matches = harvester.fetch_live_program()

now = datetime.now()
current_time_str = now.strftime('%H:%M')

def parse_match_time(m):
    s = m.get('saat', '99:99')
    try:
        parts = s.split(':')
        return int(parts[0]) * 60 + int(parts[1])
    except:
        return 9999

current_minutes = now.hour * 60 + now.minute

# Bugünden kalan maçlar (current_minutes'ten sonraki maçlar)
upcoming_today = []
tomorrow_matches = []

for m in matches:
    t_min = parse_match_time(m)
    if t_min >= current_minutes:
        upcoming_today.append((t_min, m))
    else:
        # Gece yarısından sonrakiler (00:00 - 05:00 vb.)
        tomorrow_matches.append((t_min, m))

upcoming_today.sort(key=lambda x: x[0])
tomorrow_matches.sort(key=lambda x: x[0])

print(f"Şu Anki Saat: {current_time_str}")
print("=" * 75)
print("📌 BUGÜN SAATİNE EN YAKIN İLK 10 MAÇ:")
print("=" * 75)

for idx, (t_min, m) in enumerate(upcoming_today[:10], 1):
    saat = m.get('saat')
    diff_min = t_min - current_minutes
    hours_left = diff_min // 60
    mins_left = diff_min % 60
    
    print(f"#{idx:<2} | Saat: {saat} (Kalan: {hours_left} saat {mins_left} dk) | Lig: {m.get('lig')}")
    print(f"     👉 {m.get('ev_sahibi')} vs {m.get('deplasman')}")
    print(f"     Oranlar: MS 1: {m['oranlar']['ms_1']} | X: {m['oranlar']['ms_x']} | MS 2: {m['oranlar']['ms_2']}")
    print("-" * 75)

if not upcoming_today:
    print("Bugün için daha geç saatte maç kalmadı, gece maçları:")
    for idx, (t_min, m) in enumerate(tomorrow_matches[:5], 1):
        print(f"#{idx} | Saat: {m.get('saat')} | {m.get('ev_sahibi')} vs {m.get('deplasman')}")
