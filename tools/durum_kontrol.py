import sqlite3

db_path = r'C:\Users\ertug\.gemini\antigravity\scratch\08-Oyunlar-Simulasyonlar-ve-Trainer\ErtugrulYZ-Spor-ve-Iddaa-Analiz-Motoru\data\autonomous_agent.db'
conn = sqlite3.connect(db_path)
c = conn.cursor()
c.execute("PRAGMA table_info(bets)")
print("Cols:", c.fetchall())

c.execute("SELECT * FROM bets ORDER BY id DESC LIMIT 5")
rows = c.fetchall()
for r in rows:
    print(r)
conn.close()
