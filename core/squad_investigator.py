# -*- coding: utf-8 -*-
"""
Ertuğrul YZ - Kadro, Sakat/Cezalı ve Rotasyon İstihbarat Ajanı (Squad Investigator)
Maç analizi öncesinde takımların ilk 11'lerini, kilit eksiklerini ve rotasyon riskini denetler.
Kadro istihbaratı doğrulanmayan maçlara kupon açılmasını engeller.
"""

from dataclasses import dataclass
from typing import List, Dict, Any, Tuple

@dataclass
class KadroRaporu:
    takim: str
    eksikler: List[str]
    as_kadro_orani: float  # 0.0 - 1.0 (1.0 = Tam As Kadro)
    rotasyon_var_mi: bool
    kilit_oyuncu_yok_mu: bool
    aciklama: str

class SquadInvestigator:
    def __init__(self):
        pass

    def evaluate_squad_risk(self, home_squad: KadroRaporu, away_squad: KadroRaporu) -> Tuple[bool, str]:
        """
        Kadro ve rotasyon riskini değerlendirir.
        Eğer bir takımda kontrolsüz kupa rotasyonu veya kilit oyuncu eksikliği varsa uyarır/engeller.
        """
        # 1. Kupa Rotasyon Riski (Zvolen & Tenerife dersi)
        if home_squad.rotasyon_var_mi and home_squad.as_kadro_orani < 0.60:
            return False, f"YÜKSEK ROTASYON ALARMI: {home_squad.takim} as kadrosunun %40+'ını dinlendiriyor. Savunma kurgusu çöker, riskli maç!"

        if away_squad.rotasyon_var_mi and away_squad.as_kadro_orani < 0.60:
            return False, f"YÜKSEK ROTASYON ALARMI: {away_squad.takim} as kadrosunun %40+'ını dinlendiriyor. Deplasman güvenilirliği sıfır!"

        # 2. Kilit Forvet / Kaleci Eksikliği
        if home_squad.kilit_oyuncu_yok_mu and len(home_squad.eksikler) >= 3:
            return True, f"DİKKAT: {home_squad.takim} takımında 3+ kilit eksik var ({', '.join(home_squad.eksikler[:3])}). Gol beklentisi düşürülmeli."

        return True, "Kadro derinliği ve eksik kontrolü onaylandı."
