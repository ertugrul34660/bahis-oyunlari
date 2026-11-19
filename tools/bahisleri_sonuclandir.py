import sqlite3
from datetime import datetime

db_path = r'C:\Users\ertug\.gemini\antigravity\scratch\08-Oyunlar-Simulasyonlar-ve-Trainer\ErtugrulYZ-Spor-ve-Iddaa-Analiz-Motoru\data\autonomous_agent.db'
conn = sqlite3.connect(db_path)
c = conn.cursor()

new_balance = 10929.22 + 247.50
now_str = datetime.now().isoformat()
c.execute("INSERT INTO bankroll (balance, updated_at) VALUES (?, ?)", (new_balance, now_str))
conn.commit()

c.execute("SELECT * FROM bankroll ORDER BY id DESC LIMIT 1")
print(f"Yeni Kasa Bakiyesi: {c.fetchone()}")

# Check all bets status
c.execute("SELECT id, match_name, odds, stake, status FROM bets ORDER BY id ASC")
for row in c.fetchall():
    print(row)

conn.close()
