# -*- coding: utf-8 -*-
"""
Ertuğrul YZ - Öz-Öğrenen Bahis Zekası (Gelişmiş Adaptive Learner Engine)
5. Kat: AR-GE, 3D Simülasyon, Oyun & Spor Analiz Laboratuvarı

Akıllı Bahis Kriterleri:
1. Yüksek Olasılık Filtresi: Olasılığı %40'ın altındaki sürprizlere doğrudan girmez.
2. Ağır Favori Koruması: Ev sahibi kadro ve formda ezici üstünse (%65+ olasılık) MS 1 önceliklenir.
3. Kök Neden Otopsisi: Kaybedilen bahiste hangi etkenin yanılttığı tespit edilip parametreler eğitilir.
"""

import json
from pathlib import Path
from typing import Dict, Any, Tuple

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
WEIGHTS_FILE = DATA_DIR / "agirliklar_model.json"
LEARNING_LOG_FILE = DATA_DIR / "ogrenme_gunlugu.json"

class AdaptiveLearner:
    def __init__(self):
        self.weights = self._load_weights()

    def _load_weights(self) -> Dict[str, Any]:
        if not WEIGHTS_FILE.exists():
            return {
                "versiyon": "1.1.0",
                "toplam_ogrenme_adimi": 0,
                "ogrenme_katsayisi_lr": 0.05,
                "agirliklar": {
                    "kadro_kalitesi": 0.35,
                    "form_ve_puan": 0.25,
                    "fiziki_kondisyon_dinlenme": 0.15,
                    "seyahat_ve_yol_cezasi": 0.10,
                    "ev_sahibi_avantaji": 0.10,
                    "oran_deger_farki": 0.05
                },
                "ogrenilen_kurallar": []
            }
        with open(WEIGHTS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)

    def _save_weights(self):
        with open(WEIGHTS_FILE, "w", encoding="utf-8") as f:
            json.dump(self.weights, f, ensure_ascii=False, indent=2)

    def predict_match(self, home_feat: Dict[str, float], away_feat: Dict[str, float], odds: Dict[str, float]) -> Dict[str, Any]:
        w = self.weights["agirliklar"]

        # Ev Sahibi ve Deplasman Güç Skorları
        h_kadro = home_feat.get("kadro", 0.5)
        h_form = home_feat.get("form", 0.5)
        h_dinlenme = home_feat.get("dinlenme", 0.7)

        a_kadro = away_feat.get("kadro", 0.5)
        a_form = away_feat.get("form", 0.5)
        a_dinlenme = away_feat.get("dinlenme", 0.7)
        a_seyahat = away_feat.get("seyahat", 0.0)

        home_power = (
            h_kadro * w["kadro_kalitesi"] +
            h_form * w["form_ve_puan"] +
            h_dinlenme * w["fiziki_kondisyon_dinlenme"] +
            1.0 * w["ev_sahibi_avantaji"]
        )

        away_power = (
            a_kadro * w["kadro_kalitesi"] +
            a_form * w["form_ve_puan"] +
            a_dinlenme * w["fiziki_kondisyon_dinlenme"] -
            (a_seyahat * w["seyahat_ve_yol_cezasi"])
        )

        diff = home_power - away_power

        # Olasılık modellemesi (Sigmoid benzeri)
        if diff > 0.35:
            p_1 = 70.0 + min(20.0, diff * 25)
            p_2 = max(5.0, 15.0 - diff * 15)
            p_x = 100.0 - (p_1 + p_2)
        elif diff < -0.35:
            p_2 = 65.0 + min(25.0, abs(diff) * 25)
            p_1 = max(5.0, 15.0 - abs(diff) * 15)
            p_x = 100.0 - (p_1 + p_2)
        else:
            p_x = 35.0 + (0.35 - abs(diff)) * 20
            rem = (100.0 - p_x) / 2
            p_1 = rem + diff * 30
            p_2 = rem - diff * 30

        p_1 = round(max(5.0, min(90.0, p_1)), 1)
        p_x = round(max(10.0, min(50.0, p_x)), 1)
        p_2 = round(max(5.0, min(90.0, 100.0 - (p_1 + p_x))), 1)

        # Değerli ve mantıklı bahsi seç (Value + Absolute Probability Guard)
        candidates = {}
        if p_1 >= 50.0:
            candidates["MS 1"] = p_1
        if p_2 >= 45.0:
            candidates["MS 2"] = p_2
        if p_x >= 32.0 and abs(p_1 - p_2) < 15.0:
            candidates["MS X"] = p_x

        # Alt / Üst Kontrolü
        if odds.get("alt_25", 1.8) >= 1.50 and (a_seyahat > 0.6 or h_kadro < 0.4 or abs(p_1 - p_2) < 12.0):
            candidates["2.5 Alt"] = 55.0

        if not candidates:
            candidates["MS 1" if p_1 >= p_2 else "MS 2"] = max(p_1, p_2)

        best_pick = max(candidates, key=candidates.get)

        # Seçilen bahsin oranını al
        if best_pick == "MS 1":
            odd_val = odds.get("ms_1", 1.80)
        elif best_pick == "MS 2":
            odd_val = odds.get("ms_2", 1.80)
        elif best_pick == "MS X":
            odd_val = odds.get("ms_x", 3.20)
        else:
            odd_val = odds.get("alt_25", 1.65)

        return {
            "p_1": p_1,
            "p_x": p_x,
            "p_2": p_2,
            "secilen_bahis": best_pick,
            "oran": odd_val,
            "guven_skoru": int(min(95, max(55, candidates[best_pick] * 1.1)))
        }

    def learn_from_result(self, match_name: str, predicted_pick: str, actual_result: str,
                          home_feat: Dict[str, float], away_feat: Dict[str, float]) -> Dict[str, Any]:
        is_won = (predicted_pick == actual_result)
        lr = self.weights.get("ogrenme_katsayisi_lr", 0.05)
        w = self.weights["agirliklar"]

        if is_won:
            hata_koku = "Yok (Başarılı Tahmin)"
            alinan_ders = f"'{predicted_pick}' tercihi başarıyla sonuçlandı. Karar parametreleri doğrulandı."
        else:
            hata_koku, alinan_ders, adjustments = self._diagnose_mistake(
                predicted_pick, actual_result, home_feat, away_feat
            )
            for k, delta in adjustments.items():
                if k in w:
                    w[k] = max(0.05, min(0.45, round(w[k] + delta * lr, 3)))

            # Normalize
            tot = sum(w.values())
            for k in w:
                w[k] = round(w[k] / tot, 3)

        log_entry = {
            "mac": match_name,
            "tahmin": predicted_pick,
            "gerceklesen": actual_result,
            "sonuc": "KAZANDI" if is_won else "KAYBETTİ",
            "hata_koku": hata_koku,
            "alinan_ders": alinan_ders
        }
        self._append_learning_log(log_entry)
        self.weights["toplam_ogrenme_adimi"] = self.weights.get("toplam_ogrenme_adimi", 0) + 1
        self._save_weights()

        return {
            "sonuc": "KAZANDI" if is_won else "KAYBETTİ",
            "hata_koku": hata_koku,
            "alinan_ders": alinan_ders,
            "guncel_agirliklar": self.weights["agirliklar"]
        }

    def _diagnose_mistake(self, predicted: str, actual: str, home_feat: Dict[str, float], away_feat: Dict[str, float]) -> Tuple[str, str, Dict[str, float]]:
        adjustments = {}

        if predicted == "MS 2" and actual in ["MS X", "MS 1"]:
            if away_feat.get("seyahat", 0) > 0.5:
                kök = "Seyahat ve Uçuş Yorgunluğu Azımsandı"
                ders = "Deplasman takımının uzun yol yorgunluğu (1000+ km) cezası artırıldı, deplasman galibiyet eşiği yükseltildi."
                adjustments["seyahat_ve_yol_cezasi"] = +1.0
                adjustments["kadro_kalitesi"] = -0.5
            elif home_feat.get("dinlenme", 0) > 0.8:
                kök = "Ev Sahibi Dinlenmişliği ve Savunma Direnci Hafife Alındı"
                ders = "7 gün dinlenen ev sahiplerinin direnci yükseltildi."
                adjustments["fiziki_kondisyon_dinlenme"] = +1.0
                adjustments["ev_sahibi_avantaji"] = +0.5
            else:
                kök = "Kadro Kalitesi Farkı Abartıldı (Rotasyon Zafiyeti)"
                ders = "Kupa maçlarında üst lig ekiplerinin rotasyon zafiyeti hesaba katıldı."
                adjustments["kadro_kalitesi"] = -1.0
                adjustments["ev_sahibi_avantaji"] = +0.5

        elif predicted == "MS 1" and actual == "MS 2":
            kök = "Ev Sahibi Avantajı Abartıldı"
            ders = "Ev sahibi kredisinden kısılarak kadro kalitesi ağırlığına aktarıldı."
            adjustments["ev_sahibi_avantaji"] = -1.0
            adjustments["kadro_kalitesi"] = +1.0

        elif predicted == "MS X" and actual == "MS 1":
            kök = "Ev Sahibi Erken Gol ve İç Saha Baskısı Hafife Alındı"
            ders = "İç sahada erken gol bulan takımların skoru koruma direnci yükseltildi, ev sahibi avantajı artırıldı."
            adjustments["ev_sahibi_avantaji"] = +1.0
            adjustments["fiziki_kondisyon_dinlenme"] = +0.5

        elif predicted == "MS X" and actual == "MS 2":
            kök = "Deplasman Takımının Geçiş Hücumu ve Kadro Kalitesi Hafife Alındı"
            ders = "Deplasman ekiplerinin geçiş hücumu ve bireysel kalite farkı ağırlığı artırıldı."
            adjustments["kadro_kalitesi"] = +1.0
            adjustments["ev_sahibi_avantaji"] = -0.5

        elif predicted == "2.5 Alt" and actual in ["MS 1", "MS 2", "2.5 Üst"]:
            kök = "Hücum Gücü ve Erken Gol Riski Düşük Hesaplandı"
            ders = "Takımların hücum üretkenliği ve erken gol ihtimali form katsayısına bağlandı."
            adjustments["form_ve_puan"] = +0.5
            adjustments["oran_deger_farki"] = -0.5

        else:
            kök = "Genel Güç Dengesi ve Beklenmeyen Oyun Akışı"
            ders = "Form ve dinlenme parametreleri dengelendi."
            adjustments["form_ve_puan"] = -0.5
            adjustments["fiziki_kondisyon_dinlenme"] = +0.5

        return kök, ders, adjustments


    def _append_learning_log(self, entry: Dict[str, Any]):
        logs = []
        if LEARNING_LOG_FILE.exists():
            try:
                with open(LEARNING_LOG_FILE, "r", encoding="utf-8") as f:
                    logs = json.load(f)
            except Exception:
                logs = []
        logs.append(entry)
        logs = logs[-100:]
        with open(LEARNING_LOG_FILE, "w", encoding="utf-8") as f:
            json.dump(logs, f, ensure_ascii=False, indent=2)
