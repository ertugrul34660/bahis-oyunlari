import sys
from pathlib import Path
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

from core.mackolik_harvester import MackolikHarvester

def main():
    h = MackolikHarvester()
    matches = h.fetch_live_program()
    print("=" * 70)
    print(f"📡 MAÇKOLİK İDDAA BÜLTENİ TARANDI (Toplam Maç: {len(matches)})")
    print("=" * 70)
    for idx, m in enumerate(matches[:10], 1):
        o = m["oranlar"]
        print(f"{idx:02d}. [{m['saat']}] {m['ev_sahibi']} vs {m['deplasman']}")
        print(f"    Lig: {m['lig']} | MS 1: {o['ms_1']} | MS X: {o['ms_x']} | MS 2: {o['ms_2']} | 2.5 Alt: {o['alt_25']}")
    print("=" * 70)

if __name__ == "__main__":
    main()
