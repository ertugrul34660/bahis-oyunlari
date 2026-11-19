# -*- coding: utf-8 -*-
"""
Ertuğrul YZ - Maçkolik Canlı İddaa Programı Tarayıcı (Mackolik Harvester)
5. Kat Spor Analiz Laboratuvarı

Canlı Maçkolik bültenini çeker, maçları, ligleri, başlama saatlerini ve
resmi İddaa oranlarını (MS 1, X, 2, 2.5 Alt, 2.5 Üst) parse eder.
"""

import urllib.request
import json
import re
from pathlib import Path
from typing import List, Dict, Any
from bs4 import BeautifulSoup

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
BULLETIN_FILE = DATA_DIR / "mackolik_bulteni.json"

class MackolikHarvester:
    URL = "https://arsiv.mackolik.com/Iddaa-Programi"
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "tr-TR,tr;q=0.9,en-US;q=0.8"
    }

    def fetch_live_program(self) -> List[Dict[str, Any]]:
        """Maçkolik İddaa programını canlı çeker ve yapılandırılmış liste döner."""
        try:
            req = urllib.request.Request(self.URL, headers=self.HEADERS)
            with urllib.request.urlopen(req, timeout=12) as resp:
                html = resp.read().decode("utf-8", errors="ignore")
        except Exception as e:
            print(f"[!] Maçkolik bülteni çekilemedi ({e}), yerel önbellek kullanılıyor.")
            return self._load_cache()

        soup = BeautifulSoup(html, "html.parser")
        table = soup.find("table", class_="iddaa-oyna-table")
        if not table:
            return self._load_cache()

        matches = []
        current_league = "Bilinmeyen Lig"

        for row in table.find_all("tr"):
            # Lig başlığı kontrolü
            th = row.find("th")
            if th:
                current_league = th.get_text(strip=True)
                continue

            tds = row.find_all("td")
            # 1 col olan satır da lig başlığı olabilir
            if len(tds) == 1:
                t_text = tds[0].get_text(strip=True)
                if t_text and not t_text.startswith("Tarih"):
                    current_league = t_text
                continue

            # Maç satırı en az 16 sütun içerir
            if len(tds) >= 16:
                time_str = tds[0].get_text(strip=True)
                match_name = tds[7].get_text(strip=True)
                
                # Başlık satırlarını atla
                if not match_name or "Maç" in match_name or "-" not in match_name:
                    continue

                parts = match_name.split("-", 1)
                home_team = parts[0].strip()
                away_team = parts[1].strip() if len(parts) > 1 else ""

                code = tds[9].get_text(strip=True)
                ms_1 = self._parse_float(tds[10].get_text(strip=True))
                ms_x = self._parse_float(tds[11].get_text(strip=True))
                ms_2 = self._parse_float(tds[12].get_text(strip=True))
                
                alt_25 = self._parse_float(tds[14].get_text(strip=True))
                ust_25 = self._parse_float(tds[15].get_text(strip=True))

                # Geçerli oran varsa listeye ekle
                if ms_1 > 1.0 and ms_2 > 1.0:
                    item = {
                        "mac_id": f"MK-{code}" if code else f"MK-{len(matches)+1:03d}",
                        "lig": current_league,
                        "saat": time_str,
                        "ev_sahibi": home_team,
                        "deplasman": away_team,
                        "oranlar": {
                            "ms_1": ms_1,
                            "ms_x": ms_x,
                            "ms_2": ms_2,
                            "alt_25": alt_25 if alt_25 > 1.0 else 1.65,
                            "ust_25": ust_25 if ust_25 > 1.0 else 1.75
                        }
                    }
                    matches.append(item)

        # Önbelleğe kaydet
        self._save_cache(matches)
        return matches

    def _parse_float(self, val_str: str) -> float:
        try:
            return float(val_str.replace(",", "."))
        except Exception:
            return 0.0

    def _save_cache(self, matches: List[Dict[str, Any]]):
        try:
            with open(BULLETIN_FILE, "w", encoding="utf-8") as f:
                json.dump(matches, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[!] Bülten önbelleğe yazılamadı: {e}")

    def _load_cache(self) -> List[Dict[str, Any]]:
        if BULLETIN_FILE.exists():
            try:
                with open(BULLETIN_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return []
