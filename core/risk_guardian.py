# -*- coding: utf-8 -*-
"""
Ertuğrul YZ - Risk Yönetimi, Devre Kesici ve Telemetri Muhafızı (Risk Guardian)
5. Kat Spor Analiz Laboratuvarı & Kasa Koruma Zırhı

Temel Görevler:
1. Maksimum Günlük Kayıp Sınırı (%10) aşıldığında sistemi otomatik kilitler (Circuit Breaker).
2. Oran ve risk dengesi bozuk (düşük oran - yüksek risk) maçları eler.
3. Her kararı, gerekçeyi ve risk metriğini atomik telemetri günlüğüne kaydeder.
4. Veri akışı bozulmalarında acil durum Güvenli Kurtarma Modu'nu (Safe Mode) tetikler.
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Tuple, List

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
TELEMETRY_FILE = DATA_DIR / "telemetri_gunlugu.jsonl"
SAFE_MODE_FILE = DATA_DIR / "guvenli_kurtarma_durumu.json"

class RiskGuardian:
    def __init__(self, max_daily_loss_pct: float = 0.10):
        self.max_daily_loss_pct = max_daily_loss_pct  # %10 Maksimum Günlük Kayıp Sınırı
        self.state = self._load_state()

    def _load_state(self) -> Dict[str, Any]:
        if SAFE_MODE_FILE.exists():
            try:
                with open(SAFE_MODE_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {
            "devre_kesici_kilitli": False,
            "guvenli_mod_aktif": False,
            "gunluk_baslangic_kasa": 10000.0,
            "gunluk_en_yuksek_kasa": 10000.0,
            "tarih": datetime.now().strftime("%Y-%m-%d"),
            "kilit_nedeni": "Yok (Sistem Aktif ve Güvenli)"
        }

    def _save_state(self):
        with open(SAFE_MODE_FILE, "w", encoding="utf-8") as f:
            json.dump(self.state, f, ensure_ascii=False, indent=2)

    def check_circuit_breaker(self, current_bankroll: float) -> Tuple[bool, str]:
        """
        Kasa Koruma Kuralı 1: Maksimum Günlük Kayıp Sınırı.
        Kayıp %10'a ulaştığında sistemi kilitler ve yeni bahisleri durdurur.
        """
        today_str = datetime.now().strftime("%Y-%m-%d")
        if self.state.get("tarih") != today_str:
            # Yeni güne geçildiğinde kilit sıfırlanır
            self.state["tarih"] = today_str
            self.state["gunluk_baslangic_kasa"] = current_bankroll
            self.state["gunluk_en_yuksek_kasa"] = current_bankroll
            self.state["devre_kesici_kilitli"] = False
            self.state["kilit_nedeni"] = "Yeni gün başlangıcı - Kasa sıfırlandı"
            self._save_state()

        start_bank = self.state["gunluk_baslangic_kasa"]
        drawdown = (start_bank - current_bankroll) / start_bank if start_bank > 0 else 0

        if drawdown >= self.max_daily_loss_pct:
            self.state["devre_kesici_kilitli"] = True
            msg = f"DEVRE KESİCİ KİLİTLENDİ: Günlük kayıp limiti (%{drawdown*100:.1f} >= %{self.max_daily_loss_pct*100:.1f}) aşıldı! Günün geri kalanında tüm bahisler durduruldu."
            self.state["kilit_nedeni"] = msg
            self._save_state()
            self.log_telemetry("CIRCUIT_BREAKER_TRIGGERED", {"drawdown": drawdown, "kasa": current_bankroll}, msg)
            return True, msg

        return False, "Kasa güvenli limitler dahilinde."

    def validate_odds_risk_balance(self, odds: float, calculated_prob_pct: float, pick_name: str) -> Tuple[bool, str]:
        """
        Kasa Koruma Kuralı 2: Oran ve Risk Dengesi.
        Düşük oranlı ama yüksek riskli tuzak maçlara asla bütçe verilmez.
        """
        # Tuzak Kuralı: Oran < 1.30 ama model olasılığı %75'in altındaysa REDDET!
        if odds < 1.30 and calculated_prob_pct < 75.0:
            return False, f"TUZAK ORAN REDDİ: Oran çok düşük ({odds:.2f}) fakat risk yüksek (Olasılık %{calculated_prob_pct:.1f} < %75). Kasa riske atılamaz."

        # Tuzak Kuralı: Oran > 4.50 ama olasılık %15'in altındaysa hayali kazanç peşinde koşulmaz
        if odds > 4.50 and calculated_prob_pct < 15.0:
            return False, f"HAYALİ ORAN REDDİ: Yüksek oran ({odds:.2f}) ancak istatistiksel zemin yetersiz (%{calculated_prob_pct:.1f})."

        return True, "Oran ve risk dengesi onaylandı."

    def trigger_safe_mode(self, reason: str):
        """Veri akışı bozulduğunda güvenli moda geçer."""
        self.state["guvenli_mod_aktif"] = True
        self.state["kilit_nedeni"] = f"GÜVENLİ KURTARMA MODU: {reason}"
        self._save_state()
        self.log_telemetry("SAFE_MODE_ACTIVATED", {}, reason)

    def recover_safe_mode(self):
        """Veri bağlantısı düzeldiğinde sistemi normale döndürür."""
        self.state["guvenli_mod_aktif"] = False
        self.state["kilit_nedeni"] = "Sistem normal operasyonel modda"
        self._save_state()
        self.log_telemetry("SAFE_MODE_RECOVERED", {}, "Veri akışı doğrulandı, normal çalışma sürdürülüyor.")

    def log_telemetry(self, event_type: str, metrics: Dict[str, Any], rationale: str):
        """Atomik Doğrulama ve Durum Kalıcılığı: Tüm kararları anında diske kaydeder."""
        record = {
            "zaman": datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3],
            "olay": event_type,
            "metrikler": metrics,
            "karar_gerekcesi": rationale
        }
        with open(TELEMETRY_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
