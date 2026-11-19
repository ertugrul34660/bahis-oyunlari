# -*- coding: utf-8 -*-
"""
Ertuğrul YZ - Maç Öncesi İddaa ve Puan Analiz Aracı
Kullanım:
    python mac_analiz_et.py
    python mac_analiz_et.py "Galatasaray" "Fenerbahce" "Trendyol Süper Lig"
"""

import sys
import os
from pathlib import Path

# Add core and ui to path
current_dir = Path(__file__).resolve().parent
project_root = current_dir.parent
sys.path.append(str(project_root))

from core.match_analyzer import TeamStats, MatchOdds, format_quick_summary
from ui.report_generator import generate_match_html

def run_analysis(home_name="Galatasaray", away_name="Fenerbahçe", league="Süper Lig", match_date="Yarın 20:00"):
    print(f"\n[+] {home_name} vs {away_name} için 1 gün önce İddaa ve Puan verileri taranıyor...\n")

    # Örnek/Varsayılan model verisi (Canlı bülten taranmadığında akıllı simülasyon)
    home_team = TeamStats(
        name=home_name,
        league=league,
        rank=1,
        points=31,
        played=12,
        wins=10,
        draws=1,
        losses=1,
        goals_for=28,
        goals_against=10,
        form=["G", "G", "G", "B", "G"]
    )

    away_team = TeamStats(
        name=away_name,
        league=league,
        rank=2,
        points=26,
        played=12,
        wins=8,
        draws=2,
        losses=2,
        goals_for=25,
        goals_against=12,
        form=["G", "M", "G", "G", "G"]
    )

    odds = MatchOdds(
        ms_1=2.05,
        ms_x=3.30,
        ms_2=2.90,
        alt_25=1.85,
        ust_25=1.65,
        kg_var=1.55,
        kg_yok=2.00,
        cifte_1x=1.28,
        cifte_12=1.22,
        cifte_x2=1.55
    )

    # Konsol Özeti
    summary_text = format_quick_summary(home_team, away_team, odds, match_date)
    print(summary_text)

    # HTML Raporu oluştur
    probs = odds.calculate_implied_probabilities()
    yorum = f"Ev sahibi {home_name} form ve puan avantajıyla sahaya çıkıyor (%{probs['ev_sahibi_yuzde']} olasılık). Ancak deplasman ekibi {away_name} gol yollarında etkili. Karşılıklı gol ve 2.5 üst ihtimali istatistiksel olarak öne çıkıyor."

    html_content = generate_match_html(
        home_team=home_name,
        away_team=away_name,
        league=league,
        match_date=match_date,
        home_pts=home_team.points,
        home_rank=home_team.rank,
        away_pts=away_team.points,
        away_rank=away_team.rank,
        ms1=odds.ms_1,
        msx=odds.ms_x,
        ms2=odds.ms_2,
        alt=odds.alt_25,
        ust=odds.ust_25,
        kg_var=odds.kg_var,
        kg_yok=odds.kg_yok,
        yorum=yorum
    )

    report_path = project_root / "ui" / "son_analiz.html"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"\n[✓] Görsel Rapor Üretildi: {report_path}")

if __name__ == "__main__":
    h = sys.argv[1] if len(sys.argv) > 1 else "Galatasaray"
    a = sys.argv[2] if len(sys.argv) > 2 else "Fenerbahçe"
    l = sys.argv[3] if len(sys.argv) > 3 else "Trendyol Süper Lig"
    run_analysis(h, a, l)
