# -*- coding: utf-8 -*-
import sys
from pathlib import Path
from datetime import datetime

project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

from core.mackolik_harvester import MackolikHarvester

harvester = MackolikHarvester()
matches = harvester.fetch_live_program()

print(f"Toplam Bültendeki Maç Sayısı: {len(matches)}")
print(f"Şu Anki Saat: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 70)

# Saat ve lig bilgisine göre sırala / filtrele
for idx, m in enumerate(matches[:15], 1):
    saat = m.get('saat', 'Bilinmiyor')
    lig = m.get('lig', 'Genel Lig')
    ev = m.get('ev_sahibi', '')
    dep = m.get('deplasman', '')
    oranlar = m.get('oranlar', {})
    ms1 = oranlar.get('ms_1', 0.0)
    msx = oranlar.get('ms_x', 0.0)
    ms2 = oranlar.get('ms_2', 0.0)
    
    print(f"#{idx:<2} | Saat: {saat:<5} | Lig: {lig:<20} | {ev} vs {dep}")
    print(f"     Oranlar -> MS 1: {ms1} | X: {msx} | MS 2: {ms2}")
    print("-" * 70)
