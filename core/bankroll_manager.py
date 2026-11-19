# -*- coding: utf-8 -*-
"""
Ertuğrul YZ - Sanal Kasa ve Bahis Yönetimi (Bankroll Manager - Kelly Standartlı)
5. Kat: AR-GE, 3D Simülasyon, Oyun & Spor Analiz Laboratuvarı
"""

import json
from pathlib import Path
from typing import Dict, Any, List
from core.kelly_calculator import kelly_criterion_stake

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
BANKROLL_FILE = DATA_DIR / "kasa_ve_bahisler.json"

class BankrollManager:
    def __init__(self, kelly_fraction: float = 0.5):
        self.kelly_fraction = kelly_fraction  # Varsayılan Yarım Kelly (0.5) sermaye koruma modu
        self.data = self._load()

    def _load(self) -> Dict[str, Any]:
        if not BANKROLL_FILE.exists():
            return {
                "baslangic_kasa": 10000.0,
                "guncel_kasa": 10000.0,
                "toplam_bahis_sayisi": 0,
                "kazanan_bahis_sayisi": 0,
                "kaybeden_bahis_sayisi": 0,
                "basari_orani_yuzde": 0.0,
                "net_kar_zarar": 0.0,
                "roi_yuzde": 0.0,
                "bahis_gecmisi": []
            }
        with open(BANKROLL_FILE, "r", encoding="utf-8") as f:
            return json.load(f)

    def _save(self):
        with open(BANKROLL_FILE, "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)

    def calculate_stake(self, odds: float, confidence_score: int, calculated_prob: float = None) -> float:
        """
        Yönetim Kurulu onaylı standart Kelly Kriteri pozisyon hesaplaması.
        """
        kasa = self.data["guncel_kasa"]
        prob = calculated_prob if calculated_prob is not None else min(0.95, max(0.20, confidence_score / 100.0))

        # Standart Kelly hesaplayıcısını çağır
        res = kelly_criterion_stake(
            bankroll=kasa,
            odds=odds,
            probability=prob,
            fraction=self.kelly_fraction
        )

        stake = res["recommended_stake"]
        if stake <= 0.0:
            return 0.0

        # Maksimum tek bahis koruma tavanı (Kasanın maksimum %5'i)
        max_cap = kasa * 0.05
        final_stake = min(max_cap, stake)
        return max(50.0, round(final_stake, 2))

    def place_bet(self, match_name: str, pick: str, odds: float, confidence: int, calculated_prob: float = None) -> Dict[str, Any]:
        stake = self.calculate_stake(odds, confidence, calculated_prob)
        bet_record = {
            "bet_id": f"BET-{self.data['toplam_bahis_sayisi'] + 1:04d}",
            "mac": match_name,
            "secim": pick,
            "oran": odds,
            "guven": confidence,
            "yatirilan_tutar": stake,
            "durum": "BEKLIYOR",
            "kazanc": 0.0
        }
        self.data["bahis_gecmisi"].append(bet_record)
        self.data["toplam_bahis_sayisi"] += 1
        self._save()
        return bet_record

    def settle_bet(self, bet_id: str, is_won: bool) -> Dict[str, Any]:
        for bet in self.data["bahis_gecmisi"]:
            if bet["bet_id"] == bet_id and bet["durum"] == "BEKLIYOR":
                stake = bet["yatirilan_tutar"]
                odds = bet["oran"]
                if is_won:
                    profit = round(stake * (odds - 1.0), 2)
                    self.data["guncel_kasa"] = round(self.data["guncel_kasa"] + profit, 2)
                    bet["durum"] = "KAZANDI"
                    bet["kazanc"] = profit
                    self.data["kazanan_bahis_sayisi"] += 1
                else:
                    self.data["guncel_kasa"] = round(self.data["guncel_kasa"] - stake, 2)
                    bet["durum"] = "KAYBETTİ"
                    bet["kazanc"] = -stake
                    self.data["kaybeden_bahis_sayisi"] += 1

                self.data["net_kar_zarar"] = round(self.data["guncel_kasa"] - self.data["baslangic_kasa"], 2)
                tot = self.data["kazanan_bahis_sayisi"] + self.data["kaybeden_bahis_sayisi"]
                if tot > 0:
                    self.data["basari_orani_yuzde"] = round((self.data["kazanan_bahis_sayisi"] / tot) * 100, 1)
                    self.data["roi_yuzde"] = round((self.data["net_kar_zarar"] / self.data["baslangic_kasa"]) * 100, 1)

                self._save()
                return bet

        return {}
