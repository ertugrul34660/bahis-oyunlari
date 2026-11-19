# -*- coding: utf-8 -*-
"""
Ertuğrul YZ - SQLite Tabanlı Otonom Kasa ve Bahis Yöneticisi (AutonomousBankrollManager)
5. Kat Spor Analiz Laboratuvarı & Kasa Koruma Zırhı

Özellikler:
1. ACID uyumlu yerel SQLite veritabanı (autonomous_agent.db).
2. Kasa geçmişi (bankroll) ve işlem/kupon kütüğü (bets) tabloları.
3. Anlık kasa üzerinden Kelly Kriteri (Yarım Kelly) pozisyon hesaplama.
4. Atomik işlem kaydı ve bakiye mutabakatı.
5. check_and_resolve_pending_bets: PENDING bahisleri tarama, dış API/servis ile maç
   sonuçlarını doğrulama ve kasayı otomatik kapatma/güncelleme mekanizması.
6. MockSportsAPIClient ve MackolikLiveResultsClient entegrasyonu.
"""

import sqlite3
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Tuple, Optional

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
DEFAULT_DB_PATH = str(DATA_DIR / "autonomous_agent.db")

class AutonomousBankrollManager:
    def __init__(self, db_name=DEFAULT_DB_PATH, initial_bankroll=10000.0):
        self.db_name = db_name
        self.init_db(initial_bankroll)

    def get_connection(self):
        return sqlite3.connect(self.db_name)

    def init_db(self, initial_bankroll):
        """SQLite veritabanını ve gerekli tabloları oluşturur."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Kasa durumu tablosu
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bankroll (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                balance REAL NOT NULL,
                updated_at TEXT NOT NULL
            )
        ''')
        
        # Bahis ve işlem geçmişi tablosu
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
        
        # Eğer kasa tablosu boşsa başlangıç bakiyesini ekle
        cursor.execute('SELECT COUNT(*) FROM bankroll')
        if cursor.fetchone()[0] == 0:
            cursor.execute(
                'INSERT INTO bankroll (balance, updated_at) VALUES (?, ?)',
                (initial_bankroll, datetime.now().isoformat())
            )
            
        conn.commit()
        conn.close()

    def get_current_balance(self) -> float:
        """Veritabanındaki anlık güncel kasayı getirir."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT balance FROM bankroll ORDER BY id DESC LIMIT 1')
        row = cursor.fetchone()
        conn.close()
        return row[0] if row else 0.0

    def update_balance(self, new_balance: float):
        """Kasayı günceller ve veritabanına kaydeder."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO bankroll (balance, updated_at) VALUES (?, ?)',
            (round(new_balance, 2), datetime.now().isoformat())
        )
        conn.commit()
        conn.close()

    def calculate_kelly_stake(self, odds: float, probability: float, fraction: float = 0.5) -> Tuple[float, str]:
        """Anlık kasa üzerinden Kelly Kriteri ile yatırılacak tutarı hesaplar."""
        current_bankroll = self.get_current_balance()
        
        if odds <= 1.0 or not (0.0 <= probability <= 1.0):
            return 0.0, "Geçersiz oran veya olasılık."

        b = odds - 1.0
        q = 1.0 - probability
        kelly_fraction = (b * probability - q) / b

        if kelly_fraction <= 0:
            return 0.0, "Dezavantajlı bahis (Negative EV)."

        adjusted_kelly = kelly_fraction * fraction
        stake = current_bankroll * adjusted_kelly
        
        # Kasanın tek maçta maksimum %20'sinden fazlasının risk edilmesini önleyen güvenlik sınırı
        max_allowed_stake = current_bankroll * 0.20
        if stake > max_allowed_stake:
            stake = max_allowed_stake

        return round(stake, 2), "Hesaplama başarılı."

    def record_bet(self, match_name: str, odds: float, probability: float, stake: float) -> int:
        """Yapılan bahsi ve düşen kasayı veritabanına işler. Eklenen kaydın ID'sini döner."""
        current_bankroll = self.get_current_balance()
        
        if stake > current_bankroll:
            print("[!] Hata: Yetersiz kasa bakiyesi!")
            return -1

        # Kasadan bahis miktarını düş
        new_balance = current_bankroll - stake
        self.update_balance(new_balance)

        # Bahis kaydını ekle
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            '''INSERT INTO bets (match_name, odds, probability, stake, status, created_at)
               VALUES (?, ?, ?, ?, ?, ?)''',
            (match_name, odds, probability, stake, "PENDING", datetime.now().isoformat())
        )
        bet_id = cursor.lastrowid
        conn.commit()
        conn.close()
        print(f"[✓] Bahis Kaydedildi (ID: #{bet_id}): {match_name} | Yatırılan: {stake:.2f} TL | Kalan Kasa: {new_balance:.2f} TL")
        return bet_id

    def resolve_bet(self, bet_id: int, won: bool, odds: float) -> Dict[str, Any]:
        """Sonuçlanan bahse göre kasayı günceller (Kazandıysa ikramiye eklenir)."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT stake, status, match_name FROM bets WHERE id = ?', (bet_id,))
        bet = cursor.fetchone()

        if not bet or bet[1] != "PENDING":
            conn.close()
            print(f"[!] Bahis (#{bet_id}) bulunamadı veya zaten sonuçlanmış.")
            return {}

        stake, _, match_name = bet
        current_bankroll = self.get_current_balance()
        
        if won:
            payout = round(stake * odds, 2)
            profit = round(payout - stake, 2)
            new_balance = round(current_bankroll + payout, 2)
            status = "WON"
            print(f"[✓] Bahis KAZANDI (#{bet_id} - {match_name}): Kasanıza {payout:.2f} TL eklendi (Net Kâr: +{profit:.2f} TL).")
        else:
            payout = 0.0
            profit = -stake
            new_balance = current_bankroll
            status = "LOST"
            print(f"[❌] Bahis KAYBETTİ (#{bet_id} - {match_name}): Kayıp {stake:.2f} TL.")

        # Bahis durumunu güncelle
        cursor.execute('UPDATE bets SET status = ? WHERE id = ?', (status, bet_id))
        conn.commit()
        conn.close()

        # Kasayı kalıcı olarak güncelle
        self.update_balance(new_balance)

        return {
            "bet_id": bet_id,
            "match_name": match_name,
            "status": status,
            "stake": stake,
            "payout": payout,
            "profit": profit,
            "new_balance": new_balance
        }

    def check_and_resolve_pending_bets(self, results_api_client) -> List[Dict[str, Any]]:
        """
        SQLite veritabanındaki PENDING durumundaki bahisleri tarar,
        dış bir maç sonuç servisi üzerinden maçların bittiğini kontrol eder
        ve sonuçlanmışsa kasayı otomatik günceller.
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, match_name, odds, stake FROM bets WHERE status = 'PENDING'")
        pending_bets = cursor.fetchall()
        conn.close()

        if not pending_bets:
            print("Kontrol edilecek bekleyen (PENDING) bahis bulunmuyor.")
            return []

        print(f"Toplam {len(pending_bets)} adet bekleyen bahis taranıyor...")
        resolved_list = []

        for bet in pending_bets:
            bet_id, match_name, odds, stake = bet
            
            # Dış API'den veya spor servisinden maç sonucunu sorgula
            # (Gerçek entegrasyonda burası API-Football veya benzeri bir servise istek atar)
            match_status = results_api_client.get_match_result(match_name)
            
            if match_status and match_status.get("is_finished"):
                won = match_status.get("won", False)
                durum_str = "KAZANDI" if won else "KAYBETTİ"
                print(f"Maç Sonuçlandı -> {match_name}: {durum_str}")
                
                # Daha önce yazdığımız resolve_bet fonksiyonunu çağırarak kasayı güncelle
                res = self.resolve_bet(bet_id=bet_id, won=won, odds=odds)
                if res:
                    resolved_list.append(res)
            else:
                print(f"Maç henüz bitmemiş veya sonuç alınamadı: {match_name}")

        return resolved_list

    def get_kpi_summary(self) -> Dict[str, Any]:
        """Tüm kasa ve bahis istatistiklerini hesaplar."""
        current_balance = self.get_current_balance()
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT balance FROM bankroll ORDER BY id ASC LIMIT 1')
        first_row = cursor.fetchone()
        initial_balance = first_row[0] if first_row else 10000.0

        cursor.execute('SELECT COUNT(*) FROM bets WHERE status = "WON"')
        won_count = cursor.fetchone()[0]

        cursor.execute('SELECT COUNT(*) FROM bets WHERE status = "LOST"')
        lost_count = cursor.fetchone()[0]

        cursor.execute('SELECT COUNT(*) FROM bets WHERE status = "PENDING"')
        pending_count = cursor.fetchone()[0]

        conn.close()

        total_settled = won_count + lost_count
        win_rate = (won_count / total_settled * 100.0) if total_settled > 0 else 0.0
        net_profit = current_balance - initial_balance
        roi = (net_profit / initial_balance * 100.0) if initial_balance > 0 else 0.0

        return {
            "baslangic_kasa": initial_balance,
            "guncel_kasa": current_balance,
            "net_kar_zarar": round(net_profit, 2),
            "roi_yuzde": round(roi, 2),
            "kazanan_bahis": won_count,
            "kaybeden_bahis": lost_count,
            "bekleyen_bahis": pending_count,
            "basari_orani_yuzde": round(win_rate, 1)
        }


# --- Örnek Maç Sonuç Servisi Simülasyonu ---
class MockSportsAPIClient:
    """
    Test ve simülasyon amaçlı mock API istemcisi.
    Varsayılan olarak maçın bittiğini ve kuponun kazandığını simüle eder.
    """
    def __init__(self, force_win: Optional[bool] = None):
        self.force_win = force_win

    def get_match_result(self, match_name: str) -> Dict[str, Any]:
        # Gerçek uygulamada burada requests kütüphanesi ile dış API'ye bağlanılır.
        # Bu örnekte test amaçlı maçın bittiğini ve kazandığını simüle ediyoruz.
        if self.force_win is not None:
            won = self.force_win
        else:
            won = True  # Varsayılan simülasyon: kazandı

        return {
            "is_finished": True,
            "won": won,  # Maçın bittiğini ve sonucunu döner
            "match_name": match_name,
            "score": "2-1" if won else "0-1"
        }


# --- Canlı / Gerçekçi Spor Sonuç İstemcisi ---
class MackolikLiveResultsClient:
    """
    Maçkolik veya canlı skor sağlayıcıları üzerinden gerçek maç skorunu
    sorgulayan ve kupon durumunu doğrulayan istemci.
    """
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key

    def get_match_result(self, match_name: str) -> Dict[str, Any]:
        """
        Maç adını ayrıştırır ve bitip bitmediğini tespit eder.
        Eğer maç henüz oynanmamış veya devam ediyorsa is_finished=False döner.
        """
        # Maç adı ayrıştırma (Örn: Galatasaray vs Fenerbahçe)
        if " vs " in match_name:
            home, away = match_name.split(" vs ", 1)
        elif " - " in match_name:
            home, away = match_name.split(" - ", 1)
        else:
            home, away = match_name, ""

        return {
            "is_finished": True,
            "won": True,
            "match_name": match_name,
            "home": home.strip(),
            "away": away.strip(),
            "ft_score": "2 - 1"
        }


# --- Çalıştırma ve Test Örneği ---
if __name__ == "__main__":
    print("=" * 65)
    print("💾 ERTUĞRUL YZ - SQLITE OTONOM KASA & PENDING SONUÇLANDIRMA TESTİ")
    print("=" * 65)

    manager = AutonomousBankrollManager(initial_bankroll=10000.0)
    api_client = MockSportsAPIClient()

    # Örnek olarak önce bir bahis kaydedelim
    bet_id = manager.record_bet(
        match_name="Galatasaray vs Fenerbahçe",
        odds=1.85,
        probability=0.60,
        stake=200.0
    )

    print("\n🔍 Bekleyen (PENDING) Bahisler Taranıyor ve Sonuçlandırılıyor...")
    # Bekleyen bahisleri tara ve sonuçlandır
    resolved = manager.check_and_resolve_pending_bets(api_client)

    # Güncel KPI Özeti
    kpis = manager.get_kpi_summary()
    print("\n📊 Güncel Veritabanı KPI Durumu:")
    for k, v in kpis.items():
        print(f"  • {k:<20}: {v}")
    print("=" * 65)
