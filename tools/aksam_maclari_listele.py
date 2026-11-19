# -*- coding: utf-8 -*-
import sys
from pathlib import Path
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

from tools.sirala_kalan_program import analyzed_program

print("\n🌙 AKŞAM KUŞAĞI MAÇLARI VE TAHMİNLER:")
print("=" * 75)
for p in analyzed_program:
    if any(t in p['saat'] for t in ['20:45', '21:00', '22:45', '23:00']):
        print(f"[{p['saat']}] {p['mac']:<35} | {p['lig'][:20]}")
        print(f"     👉 Tahmin: {p['secim']:<8} | Oran: {p['oran']:.2f} | Güven: %{p['guven']} | {p['not']}")
        print("-" * 75)
