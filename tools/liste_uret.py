import sqlite3
import json

db_path = r'C:\Users\ertug\.gemini\antigravity\scratch\08-Oyunlar-Simulasyonlar-ve-Trainer\ErtugrulYZ-Spor-ve-Iddaa-Analiz-Motoru\data\autonomous_agent.db'
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
c = conn.cursor()
c.execute("SELECT * FROM bets ORDER BY id ASC")
bets = [dict(r) for r in c.fetchall()]
conn.close()

won_bets = [b for b in bets if b['status'] == 'WON']
lost_bets = [b for b in bets if b['status'] == 'LOST']

print("=== KAZANAN (BİLDİĞİMİZ) KASA BAHİSLERİ ===")
total_won_profit = 0
for b in won_bets:
    profit = (b['stake'] * b['odds']) - b['stake']
    total_won_profit += profit
    print(f"ID #{b['id']:02d}: {b['match_name']} -> Oran: {b['odds']:.2f} | Tutar: {b['stake']:.2f} TL | Kâr: +{profit:.2f} TL")

print("\n=== KAYBEDEN (BİLEMEDİĞİMİZ) KASA BAHİSLERİ ===")
total_lost_stake = 0
for b in lost_bets:
    total_lost_stake += b['stake']
    print(f"ID #{b['id']:02d}: {b['match_name']} -> Oran: {b['odds']:.2f} | Kayıp: -{b['stake']:.2f} TL")

print(f"\nNet Kasa Kârı: +{total_won_profit - total_lost_stake:.2f} TL")
