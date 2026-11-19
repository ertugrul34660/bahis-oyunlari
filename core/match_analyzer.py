# -*- coding: utf-8 -*-
"""
Ertuğrul YZ - Spor ve İddaa Analiz Motoru (Gelişmiş Çekirdek Modül)
5. Kat: AR-GE, 3D Simülasyon, Oyun & Spor Analiz Laboratuvarı
Zorunlu Standart: Puan + Oran + Kadro + Oyuncular + Fiziki Durum + Teknik Eşleşme
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional

@dataclass
class TeamStats:
    name: str
    league: str
    rank: int
    points: int
    played: int
    wins: int
    draws: int
    losses: int
    goals_for: int
    goals_against: int
    form: List[str]  # e.g. ["G", "G", "B", "M", "G"]

    @property
    def goal_difference(self) -> int:
        return self.goals_for - self.goals_against


@dataclass
class SquadDetails:
    probable_11: List[str]
    formation: str
    manager: str
    missing_players: List[str]  # Sakat / Cezalı
    rotation_risk: str  # Düşük / Orta / Yüksek (Kupa rotasyonu)


@dataclass
class PhysicalDetails:
    rest_days: int
    travel_km: int  # Deplasman seyahat mesafesi
    fatigue_level: str  # Dinç / Normal / Yorgun
    stamina_risk_min: int  # Kondisyonun düşeceği tahmin edilen dakika (örn: 65)


@dataclass
class MatchOdds:
    ms_1: float
    ms_x: float
    ms_2: float
    alt_25: float
    ust_25: float
    kg_var: float
    kg_yok: float
    cifte_1x: Optional[float] = None
    cifte_12: Optional[float] = None
    cifte_x2: Optional[float] = None

    def calculate_implied_probabilities(self) -> Dict[str, float]:
        inv_1 = 1.0 / self.ms_1 if self.ms_1 > 0 else 0
        inv_x = 1.0 / self.ms_x if self.ms_x > 0 else 0
        inv_2 = 1.0 / self.ms_2 if self.ms_2 > 0 else 0
        total_inv = inv_1 + inv_x + inv_2

        if total_inv == 0:
            return {"ev_sahibi_yuzde": 33.3, "beraberlik_yuzde": 33.3, "deplasman_yuzde": 33.3, "iddaa_kar_marji": 0.0}

        margin = (total_inv - 1.0) * 100.0
        return {
            "ev_sahibi_yuzde": round((inv_1 / total_inv) * 100.0, 1),
            "beraberlik_yuzde": round((inv_x / total_inv) * 100.0, 1),
            "deplasman_yuzde": round((inv_2 / total_inv) * 100.0, 1),
            "iddaa_kar_marji": round(margin, 2)
        }


def format_deep_analysis(home: TeamStats, away: TeamStats,
                         home_squad: SquadDetails, away_squad: SquadDetails,
                         home_phy: PhysicalDetails, away_phy: PhysicalDetails,
                         odds: MatchOdds, match_date: str) -> str:
    """Yönetim Kurulu standardında eksiksiz 5 sütunlu derin analiz metni."""
    probs = odds.calculate_implied_probabilities()
    lines = []
    lines.append("=" * 70)
    lines.append(f"⚽ ERTUĞRUL YZ - TAM KAPSAMLI MAÇ, KADRO, FİZİKİ VE TEKNİK ANALİZ")
    lines.append(f"📅 {match_date} | Lig/Kupa: {home.league}")
    lines.append(f"🏟️ Karşılaşma: {home.name} vs {away.name}")
    lines.append("=" * 70)

    # 1. Puan & Durum
    lines.append("\n📊 1) LİG VE PUAN DURUMU")
    lines.append("-" * 70)
    lines.append(f"• {home.name}: Sıra #{home.rank} | {home.points} Puan ({home.league})")
    lines.append(f"• {away.name}: Sıra #{away.rank} | {away.points} Puan ({away.league})")

    # 2. Kadro & Oyuncular
    lines.append("\n👥 2) KADRO, OYUNCULAR VE EKSİKLER")
    lines.append("-" * 70)
    lines.append(f"• {home.name} (T.D: {home_squad.manager} | Diziliş: {home_squad.formation}):")
    lines.append(f"  - Muhtemel 11: {', '.join(home_squad.probable_11)}")
    lines.append(f"  - Eksikler: {', '.join(home_squad.missing_players) if home_squad.missing_players else 'Yok (Tam Kadro)'}")
    lines.append(f"  - Rotasyon Durumu: {home_squad.rotation_risk}")
    lines.append(f"• {away.name} (T.D: {away_squad.manager} | Diziliş: {away_squad.formation}):")
    lines.append(f"  - Muhtemel 11: {', '.join(away_squad.probable_11)}")
    lines.append(f"  - Eksikler: {', '.join(away_squad.missing_players) if away_squad.missing_players else 'Yok / Dinlendirilenler'}")
    lines.append(f"  - Rotasyon Durumu: {away_squad.rotation_risk}")

    # 3. Fiziki Durum
    lines.append("\n⚡ 3) FİZİKİ DURUM, DİNLENME VE SEYAHAT YORGUNLUĞU")
    lines.append("-" * 70)
    lines.append(f"• {home.name}: {home_phy.rest_days} gün dinlendi | {home_phy.travel_km} km seyahat | Durum: {home_phy.fatigue_level} | Kondisyon Eşiği: ~{home_phy.stamina_risk_min}. dk")
    lines.append(f"• {away.name}: {away_phy.rest_days} gün dinlendi | {away_phy.travel_km} km seyahat | Durum: {away_phy.fatigue_level} | Kondisyon Eşiği: 90+ dk")

    # 4. Oranlar & Olasılık
    lines.append("\n🎯 4) RESMİ İDDAA ORANLARI & YAPAY ZEKA OLASILIKLARI")
    lines.append("-" * 70)
    lines.append(f"• MS: 1 ({odds.ms_1:.2f}) | X ({odds.ms_x:.2f}) | 2 ({odds.ms_2:.2f})")
    lines.append(f"• Alt/Üst: 2.5 Alt ({odds.alt_25:.2f}) | 2.5 Üst ({odds.ust_25:.2f})")
    lines.append(f"• Karşılıklı Gol: KG Var ({odds.kg_var:.2f}) | KG Yok ({odds.kg_yok:.2f})")
    lines.append(f"• Olasılık: %{probs['ev_sahibi_yuzde']} Ev | %{probs['beraberlik_yuzde']} X | %{probs['deplasman_yuzde']} Dep")

    lines.append("=" * 70)
    return "\n".join(lines)


def format_quick_summary(home: TeamStats, away: TeamStats, odds: MatchOdds, match_date: str) -> str:
    """Hızlı maç ve oran özet metni."""
    probs = odds.calculate_implied_probabilities()
    lines = [
        "=" * 65,
        f"⚽ {home.name} vs {away.name} ({home.league})",
        f"📅 Maç Saati: {match_date}",
        "-" * 65,
        f"📊 Puan: {home.name} #{home.rank} ({home.points} P) | {away.name} #{away.rank} ({away.points} P)",
        f"🎯 Oranlar: MS 1 ({odds.ms_1:.2f}) | X ({odds.ms_x:.2f}) | MS 2 ({odds.ms_2:.2f})",
        f"🎲 Olasılık: %{probs['ev_sahibi_yuzde']} Ev | %{probs['beraberlik_yuzde']} X | %{probs['deplasman_yuzde']} Dep",
        f"🥅 2.5 Alt ({odds.alt_25:.2f}) | 2.5 Üst ({odds.ust_25:.2f})",
        "=" * 65
    ]
    return "\n".join(lines)

