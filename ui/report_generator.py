# -*- coding: utf-8 -*-
"""
Ertuğrul YZ - Spor ve İddaa Analiz Motoru (Gelişmiş Görsel Rapor Üreteci)
Kadro, Oyuncular, Fiziki Durum, Taktik ve Oran Kartları
"""

def generate_deep_match_html(home_team: str, away_team: str, league: str, match_date: str,
                             home_pts: int, home_rank: int, away_pts: int, away_rank: int,
                             home_11: list, away_11: list,
                             home_mgr: str, away_mgr: str,
                             home_rest: int, away_rest: int,
                             home_travel: int, away_travel: int,
                             home_missing: list, away_missing: list,
                             ms1: float, msx: float, ms2: float,
                             alt: float, ust: float, kg_var: float, kg_yok: float,
                             taktik_yorum: str, logo_path: str = "../assets/Ertugrul_YZ_Logo.svg") -> str:

    inv_1 = 1.0 / ms1 if ms1 > 0 else 0
    inv_x = 1.0 / msx if msx > 0 else 0
    inv_2 = 1.0 / ms2 if ms2 > 0 else 0
    tot = inv_1 + inv_x + inv_2 or 1
    p1 = round((inv_1 / tot) * 100, 1)
    px = round((inv_x / tot) * 100, 1)
    p2 = round((inv_2 / tot) * 100, 1)

    h_11_str = " • ".join(home_11)
    a_11_str = " • ".join(away_11)
    h_miss_str = ", ".join(home_missing) if home_missing else "Eksik Yok (Tam Kadro)"
    a_miss_str = ", ".join(away_missing) if away_missing else "Kupa Dinlendirmesi / Rotasyon"

    html = f"""<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Ertuğrul YZ - {home_team} vs {away_team} Derin Analiz</title>
    <style>
        :root {{
            --bg-color: #0B0F19;
            --card-bg: #131B2E;
            --accent-cyan: #00E5FF;
            --accent-blue: #0077B6;
            --text-primary: #FFFFFF;
            --text-secondary: #94A3B8;
            --green: #10B981;
            --yellow: #F59E0B;
            --red: #EF4444;
        }}
        * {{ margin: 0; padding: 0; box-sizing: border-box; font-family: 'Segoe UI', system-ui, sans-serif; }}
        body {{ background-color: var(--bg-color); color: var(--text-primary); padding: 24px; min-height: 100vh; }}
        .container {{ max-width: 1000px; margin: 0 auto; }}
        .header {{ display: flex; align-items: center; justify-content: space-between; border-bottom: 2px solid var(--accent-blue); padding-bottom: 16px; margin-bottom: 24px; }}
        .logo-area {{ display: flex; align-items: center; gap: 12px; }}
        .logo-area img {{ width: 44px; height: 44px; }}
        .logo-title {{ font-size: 22px; font-weight: 800; letter-spacing: 1px; color: var(--accent-cyan); text-transform: uppercase; }}
        .badge {{ background: rgba(0, 229, 255, 0.15); color: var(--accent-cyan); border: 1px solid var(--accent-cyan); padding: 4px 12px; border-radius: 20px; font-size: 13px; font-weight: 600; }}
        
        .match-banner {{ background: linear-gradient(135deg, #131B2E, #1E293B); border: 1px solid rgba(0, 229, 255, 0.3); border-radius: 16px; padding: 24px; text-align: center; margin-bottom: 24px; box-shadow: 0 8px 24px rgba(0,0,0,0.5); }}
        .league-title {{ color: var(--accent-cyan); font-size: 14px; text-transform: uppercase; letter-spacing: 1.5px; margin-bottom: 8px; font-weight: 600; }}
        .teams {{ display: flex; justify-content: space-around; align-items: center; margin: 16px 0; }}
        .team-box {{ flex: 1; }}
        .team-name {{ font-size: 28px; font-weight: 800; }}
        .team-rank {{ color: var(--text-secondary); font-size: 14px; margin-top: 4px; }}
        .vs {{ font-size: 22px; font-weight: 900; color: var(--accent-cyan); padding: 0 16px; }}
        
        .grid-2 {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 20px; }}
        .card {{ background: var(--card-bg); border-radius: 14px; padding: 20px; border: 1px solid rgba(255,255,255,0.06); }}
        .card-header {{ font-size: 16px; font-weight: 700; color: var(--accent-cyan); margin-bottom: 14px; display: flex; align-items: center; gap: 8px; }}
        
        .lineup-box {{ background: #0F172A; border-radius: 8px; padding: 12px; margin-top: 8px; font-size: 13px; line-height: 1.6; border-left: 3px solid var(--accent-cyan); }}
        .stat-badge {{ display: inline-block; background: rgba(255,255,255,0.06); padding: 4px 8px; border-radius: 6px; font-size: 12px; margin: 4px 4px 4px 0; color: #CBD5E1; }}
        
        .odds-row {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; margin-bottom: 12px; }}
        .odd-btn {{ background: #0F172A; border: 1px solid rgba(0, 229, 255, 0.2); border-radius: 10px; padding: 10px 6px; text-align: center; }}
        .odd-label {{ font-size: 11px; color: var(--text-secondary); display: block; margin-bottom: 4px; }}
        .odd-value {{ font-size: 17px; font-weight: 800; color: #38BDF8; }}
        
        .prob-bar {{ height: 10px; border-radius: 5px; background: #334155; margin-top: 10px; overflow: hidden; display: flex; }}
        .prob-fill-1 {{ background: var(--accent-cyan); height: 100%; }}
        .prob-fill-x {{ background: var(--yellow); height: 100%; }}
        .prob-fill-2 {{ background: var(--red); height: 100%; }}
        
        .summary-box {{ background: rgba(0, 229, 255, 0.05); border-left: 4px solid var(--accent-cyan); padding: 16px; border-radius: 8px; line-height: 1.6; font-size: 14px; color: #E2E8F0; margin-top: 12px; }}
        .footer {{ text-align: center; color: var(--text-secondary); font-size: 12px; margin-top: 24px; padding-top: 16px; border-top: 1px solid rgba(255,255,255,0.08); }}
    </style>
</head>
<body>
    <div class="container">
        <header class="header">
            <div class="logo-area">
                <img src="{logo_path}" alt="Ertuğrul YZ Logo">
                <span class="logo-title">Ertuğrul YZ</span>
            </div>
            <span class="badge">Derin Kadro, Fiziki & Teknik Analiz Motoru</span>
        </header>

        <section class="match-banner">
            <div class="league-title">🏆 {league}</div>
            <div class="teams">
                <div class="team-box">
                    <div class="team-name">{home_team}</div>
                    <div class="team-rank">Sıra: #{home_rank} • {home_pts} Puan • T.D: {home_mgr}</div>
                </div>
                <div class="vs">VS</div>
                <div class="team-box">
                    <div class="team-name">{away_team}</div>
                    <div class="team-rank">Sıra: #{away_rank} • {away_pts} Puan • T.D: {away_mgr}</div>
                </div>
            </div>
            <div style="color: var(--text-secondary); font-size: 13px;">📅 {match_date}</div>
        </section>

        <!-- KADRO VE OYUNCULAR -->
        <div class="grid-2">
            <div class="card">
                <div class="card-header">👥 {home_team} Kadro & Oyuncular</div>
                <div><span class="stat-badge">🏟️ Saha: Ev Sahibi</span> <span class="stat-badge">💤 Dinlenme: {home_rest} Gün</span> <span class="stat-badge">✈️ Ulaşım: 0 KM</span></div>
                <div class="lineup-box">
                    <strong>📋 Muhtemel 11:</strong><br>{h_11_str}
                </div>
                <div style="margin-top: 10px; font-size: 13px;">
                    <strong>🏥 Eksikler:</strong> {h_miss_str}
                </div>
            </div>

            <div class="card">
                <div class="card-header">👥 {away_team} Kadro & Oyuncular</div>
                <div><span class="stat-badge">✈️ Deplasman: {away_travel} KM Seyahat</span> <span class="stat-badge">💤 Dinlenme: {away_rest} Gün</span> <span class="stat-badge">🔄 Rotasyon: Yüksek</span></div>
                <div class="lineup-box">
                    <strong>📋 Muhtemel 11:</strong><br>{a_11_str}
                </div>
                <div style="margin-top: 10px; font-size: 13px;">
                    <strong>🏥 Eksikler:</strong> {a_miss_str}
                </div>
            </div>
        </div>

        <!-- FİZİKİ VE TEKNİK ÇARPIŞMA + ORANLAR -->
        <div class="grid-2">
            <div class="card">
                <div class="card-header">⚡ Fiziki Kondisyon & Taktiksel Çarpışma</div>
                <div style="font-size: 13px; line-height: 1.6; color: #CBD5E1;">
                    <p>• <strong>Kondisyon & Eşik:</strong> Badajoz evinde tam hafta dinlenmiş halde çıksa da 65-70. dakikadan sonra fiziksel temposu düşebilir. Tenerife ise profesyonel lig temposuna sahip ancak Kanarya Adaları'ndan İspanya içlerine 1.500+ km uçuş/yol yorgunluğu taşımaktadır.</p>
                    <p style="margin-top: 8px;">• <strong>Taktiksel Düzen:</strong> Badajoz derin savunma bloğu kurup Aquiles ve Cerro ile kontra arayacak; Tenerife ise kanatlardan (Gerard Valentín) açılan ortalarla Ranos ve Gomis'i topla buluşturmaya odaklanacaktır.</p>
                </div>
                <div class="summary-box">
                    <strong>💡 Ertuğrul YZ İbre Yorumu:</strong><br>{taktik_yorum}
                </div>
            </div>

            <div class="card">
                <div class="card-header">🎯 Resmi Oranlar & Yapay Zeka Olasılığı</div>
                <div class="odds-row">
                    <div class="odd-btn">
                        <span class="odd-label">MS 1</span>
                        <span class="odd-value">{ms1:.2f}</span>
                    </div>
                    <div class="odd-btn">
                        <span class="odd-label">MS X</span>
                        <span class="odd-value">{msx:.2f}</span>
                    </div>
                    <div class="odd-btn">
                        <span class="odd-label">MS 2</span>
                        <span class="odd-value">{ms2:.2f}</span>
                    </div>
                </div>
                <div class="odds-row" style="grid-template-columns: 1fr 1fr;">
                    <div class="odd-btn">
                        <span class="odd-label">2.5 Alt</span>
                        <span class="odd-value">{alt:.2f}</span>
                    </div>
                    <div class="odd-btn">
                        <span class="odd-label">2.5 Üst</span>
                        <span class="odd-value">{ust:.2f}</span>
                    </div>
                </div>
                <div style="margin-top: 14px;">
                    <div style="display:flex; justify-content:space-between; font-size:12px;">
                        <span>Badajoz (%{p1})</span>
                        <span>Beraberlik (%{px})</span>
                        <span>Tenerife (%{p2})</span>
                    </div>
                    <div class="prob-bar">
                        <div class="prob-fill-1" style="width: {p1}%;"></div>
                        <div class="prob-fill-x" style="width: {px}%;"></div>
                        <div class="prob-fill-2" style="width: {p2}%;"></div>
                    </div>
                </div>
            </div>
        </div>

        <footer class="footer">
            Ertuğrul YZ Holding Otonom Ajan Yönetimi • 5. Kat Spor Analiz Laboratuvarı • Her hakkı saklıdır.
        </footer>
    </div>
</body>
</html>
"""
    return html


def generate_match_html(home_team: str, away_team: str, league: str, match_date: str,
                        home_pts: int, home_rank: int, away_pts: int, away_rank: int,
                        ms1: float, msx: float, ms2: float,
                        alt: float, ust: float, kg_var: float, kg_yok: float,
                        yorum: str, **kwargs) -> str:
    """Temel parametrelerle hızlı HTML raporu üreten sarmalayıcı fonksiyon."""
    return generate_deep_match_html(
        home_team=home_team, away_team=away_team, league=league, match_date=match_date,
        home_pts=home_pts, home_rank=home_rank, away_pts=away_pts, away_rank=away_rank,
        home_11=["Muhtemel Kadro"], away_11=["Muhtemel Kadro"],
        home_mgr="Teknik Heyet", away_mgr="Teknik Heyet",
        home_rest=4, away_rest=3, home_travel=0, away_travel=1800,
        home_missing=[], away_missing=[],
        ms1=ms1, msx=msx, ms2=ms2, alt=alt, ust=ust, kg_var=kg_var, kg_yok=kg_yok,
        taktik_yorum=yorum
    )

