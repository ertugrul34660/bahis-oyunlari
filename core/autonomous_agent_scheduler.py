# -*- coding: utf-8 -*-
"""
Ertuğrul YZ - Otonom Ajan Zamanlayıcısı (AutonomousAgentScheduler)
5. Kat: Spor Analiz Laboratuvarı & Kasa Koruma Zırhı

Özellikler:
1. SQLite veritabanı (autonomous_agent.db) entegrasyonu.
2. PENDING bahisleri tarama ve sonuçlandırma.
3. Python `schedule` kütüphanesi ile periyodik (ör. her 15 dakikada bir) otomatik çalışma.
4. Hem tek seferlik kontrol (--once) hem de 7/24 sonsuz arka plan döngüsü desteği.
"""

import sys
import time
import sqlite3
from pathlib import Path
from datetime import datetime
import schedule

# Proje dizinleri ve varsayılan veritabanı
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
DEFAULT_DB_PATH = str(DATA_DIR / "autonomous_agent.db")


class AutonomousAgentScheduler:
    def __init__(self, db_name=None, initial_bankroll=10000.0):
        # Varsayılan olarak projenin merkezi data/autonomous_agent.db veritabanını kullan
        if db_name is None or db_name == "autonomous_agent.db":
            self.db_name = DEFAULT_DB_PATH
        else:
            self.db_name = db_name
            
        self.init_db(initial_bankroll)

    def get_connection(self):
        return sqlite3.connect(self.db_name)

    def init_db(self, initial_bankroll):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bankroll (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                balance REAL NOT NULL,
                updated_at TEXT NOT NULL
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                match_name TEXT NOT NULL,
                odds REAL NOT NULL,
                probability REAL NOT NULL,
                stake REAL NOT NULL,
                status TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        ''')
        cursor.execute('SELECT COUNT(*) FROM bankroll')
        if cursor.fetchone()[0] == 0:
            cursor.execute(
                'INSERT INTO bankroll (balance, updated_at) VALUES (?, ?)',
                (initial_bankroll, datetime.now().isoformat())
            )
        conn.commit()
        conn.close()

    def get_current_balance(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT balance FROM bankroll ORDER BY id DESC LIMIT 1')
        row = cursor.fetchone()
        conn.close()
        return row[0] if row else 0.0

    def update_balance(self, new_balance):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO bankroll (balance, updated_at) VALUES (?, ?)',
            (round(new_balance, 2), datetime.now().isoformat())
        )
        conn.commit()
        conn.close()

    def resolve_bet(self, bet_id, won, odds):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT stake, status, match_name FROM bets WHERE id = ?', (bet_id,))
        bet = cursor.fetchone()

        if not bet or bet[1] != "PENDING":
            conn.close()
            return

        stake, _, match_name = bet
        current_bankroll = self.get_current_balance()
        
        if won:
            payout = round(stake * odds, 2)
            new_balance = round(current_bankroll + payout, 2)
            status = "WON"
            print(f"[BAŞARILI] Bahis Kazandı! ({match_name}) İkramiye eklendi: {payout} TL | Yeni Kasa: {new_balance:.2f} TL")
        else:
            new_balance = current_bankroll
            status = "LOST"
            print(f"[BİLGİ] Bahis Kaybetti. ({match_name}) | Kayıp: {stake:.2f} TL | Kasa: {new_balance:.2f} TL")

        cursor.execute('UPDATE bets SET status = ? WHERE id = ?', (status, bet_id))
        conn.commit()
        conn.close()
        self.update_balance(new_balance)

    def check_and_resolve_pending_bets(self, results_api_client):
        """Zamanlanmış görev tarafından periyodik olarak çalıştırılacak fonksiyondur."""
        print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] PENDING bahisler taranıyor...")
        
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, match_name, odds, stake FROM bets WHERE status = 'PENDING'")
        pending_bets = cursor.fetchall()
        conn.close()

        if not pending_bets:
            print("Bekleyen bahis bulunmuyor.")
            return

        print(f"Toplam {len(pending_bets)} adet bekleyen bahis bulundu, sonuçlar sorgulanıyor...")
        for bet in pending_bets:
            bet_id, match_name, odds, stake = bet
            match_status = results_api_client.get_match_result(match_name)
            
            if match_status and match_status.get("is_finished"):
                won = match_status.get("won", False)
                print(f"Maç Sonuçlandı -> {match_name}: {'KAZANDI' if won else 'KAYBETTİ'}")
                self.resolve_bet(bet_id=bet_id, won=won, odds=odds)
            else:
                print(f"Maç devam ediyor: {match_name}")


class MockSportsAPIClient:
    def __init__(self, force_win=True):
        self.force_win = force_win

    def get_match_result(self, match_name):
        # Gerçek ortamda API sorgusu veya web scraper çalışır
        return {"is_finished": True, "won": self.force_win, "match_name": match_name}


if __name__ == "__main__":
    agent = AutonomousAgentScheduler(initial_bankroll=10000.0)
    api_client = MockSportsAPIClient()

    print("=" * 65)
    print("⏰ ERTUĞRUL YZ - OTONOM AJAN ZAMANLAYICISI (SCHEDULE)")
    print("=" * 65)
    print(f"Otonom Ajan Başlatıldı. Güncel Kasa: {agent.get_current_balance():,.2f} TL")
    print(f"Veritabanı Dosyası: {agent.db_name}")

    # Eğer komut satırından --once veya --single parametresi verilmişse hemen tek sefer çalıştır ve çık
    if len(sys.argv) > 1 and sys.argv[1] in ["--once", "--single", "-1"]:
        print("[*] Tek seferlik anlık tarama modu aktif...")
        agent.check_and_resolve_pending_bets(results_api_client=api_client)
        print(f"[*] İşlem tamamlandı. Son Kasa: {agent.get_current_balance():,.2f} TL")
        sys.exit(0)

    print("Scheduler aktif: Her 15 dakikada bir maç sonuçları kontrol edilecek...")

    # Her 15 dakikada bir kontrol etmesi için zamanlayıcıyı tanımla
    schedule.every(15).minutes.do(agent.check_and_resolve_pending_bets, results_api_client=api_client)
    
    # Başlangıçta hemen bir kez kontrol etmek için:
    agent.check_and_resolve_pending_bets(results_api_client=api_client)

    # 7/24 Sonsuz Arka Plan Döngüsü
    print("[*] 7/24 Zamanlayıcı döngüsüne girildi (Çıkmak için Ctrl+C)...")
    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[!] Zamanlayıcı kullanıcı tarafından durduruldu.")
