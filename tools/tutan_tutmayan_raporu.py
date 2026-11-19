import sqlite3

db_path = r'C:\Users\ertug\.gemini\antigravity\scratch\08-Oyunlar-Simulasyonlar-ve-Trainer\ErtugrulYZ-Spor-ve-Iddaa-Analiz-Motoru\data\autonomous_agent.db'
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
c = conn.cursor()

c.execute("SELECT * FROM bets ORDER BY id ASC")
rows = [dict(r) for r in c.fetchall()]

won = [r for r in rows if r['status'] == 'WON']
lost = [r for r in rows if r['status'] == 'LOST']

print(f"=== KAZANAN (TUTAN) BAHİSLER ({len(won)} Adet) ===")
total_won_profit = 0
for r in won:
    profit = (r['stake'] * r['odds']) - r['stake']
    total_won_profit += profit
    print(f"✅ ID #{r['id']:02d} | {r['match_name']:<48} | Oran: {r['odds']:.2f} | Tutar: {r['stake']:>6.2f} TL | Kâr: +{profit:>7.2f} TL")

print(f"\n=== KAYBEDEN (TUTMAYAN) BAHİSLER ({len(lost)} Adet) ===")
total_lost_stake = 0
for r in lost:
    total_lost_stake += r['stake']
    print(f"❌ ID #{r['id']:02d} | {r['match_name']:<48} | Oran: {r['odds']:.2f} | Kayıp: -{r['stake']:>6.2f} TL")

c.execute("SELECT balance FROM bankroll ORDER BY id DESC LIMIT 1")
bal = c.fetchone()['balance']

print("\n" + "="*70)
print(f"ÖZET BİLANÇO: Başlangıç: 10.000 TL | Güncel Kasa: {bal:.2f} TL | Net Kâr: +{bal - 10000:.2f} TL")
print(f"Kazanılan Brüt Kâr: +{total_won_profit:.2f} TL | Kaybedilen Tutar: -{total_lost_stake:.2f} TL")
print("="*70)
conn.close()
