import sqlite3
import json

db_path = r'C:\Users\ertug\.gemini\antigravity\scratch\08-Oyunlar-Simulasyonlar-ve-Trainer\ErtugrulYZ-Spor-ve-Iddaa-Analiz-Motoru\data\autonomous_agent.db'
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
c = conn.cursor()

c.execute("SELECT * FROM bets ORDER BY id ASC")
bets = [dict(r) for r in c.fetchall()]

print(f"=== TOPLAM BAHİS/KUPON SAYISI: {len(bets)} ===")
for b in bets:
    print(f"ID #{b['id']} | {b['match_name']} | Oran: {b['odds']:.2f} | Tutar: {b['stake']:.2f} TL | Durum: {b['status']}")

print("\n=== AKTİF (BEKLEYEN) KUPONLAR ===")
pending = [b for b in bets if b['status'] == 'PENDING']
for p in pending:
    potential = p['stake'] * p['odds']
    print(f"-> Kupon #{p['id']}: {p['match_name']}")
    print(f"   Yatırılan: {p['stake']:.2f} TL | Oran: {p['odds']:.2f} | Olası Kazanç: {potential:.2f} TL | Net Kâr Beklentisi: +{potential - p['stake']:.2f} TL")

c.execute("SELECT balance FROM bankroll ORDER BY id DESC LIMIT 1")
bal = c.fetchone()['balance']
print(f"\nKasadaki Serbest Nakit: {bal:.2f} TL")
total_pending_stake = sum(p['stake'] for p in pending)
total_potential_win = sum(p['stake'] * p['odds'] for p in pending)
print(f"Sahadaki Toplam Tutar: {total_pending_stake:.2f} TL")
print(f"Kazanırsa Toplam Gelecek: {total_potential_win:.2f} TL")
print(f"Toplam Portföy (Nakit + Sahadaki): {bal + total_pending_stake:.2f} TL")

conn.close()

# Also inspect data/kasa_ve_bahisler.json if exists
try:
    with open(r'C:\Users\ertug\.gemini\antigravity\scratch\08-Oyunlar-Simulasyonlar-ve-Trainer\ErtugrulYZ-Spor-ve-Iddaa-Analiz-Motoru\data\kasa_ve_bahisler.json', 'r', encoding='utf-8') as f:
        kb = json.load(f)
        print("\n=== KASA VE BAHİSLER JSON ÖZETİ ===")
        print(f"Toplam Bahis: {kb.get('toplam_bahis')}, Kazanan: {kb.get('kazanan_bahis')}, Kaybeden: {kb.get('kaybeden_bahis')}")
        print(f"Win Rate: %{kb.get('basari_orani', 0):.2f}, Bakiye: {kb.get('bakiye', 0):.2f} TL, Net Kâr: {kb.get('net_kar', 0):.2f} TL")
except Exception as e:
    print("kasa_ve_bahisler.json okunamadı:", e)
