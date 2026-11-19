# -*- coding: utf-8 -*-
"""
Ertuğrul YZ - Maçkolik Tarayan ve Öğrenen Robot Dashboard Üreteci
"""

import json
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
BULLETIN_FILE = DATA_DIR / "mackolik_bulteni.json"
BANKROLL_FILE = DATA_DIR / "kasa_ve_bahisler.json"
WEIGHTS_FILE = DATA_DIR / "agirliklar_model.json"
LEARNING_LOG_FILE = DATA_DIR / "ogrenme_gunlugu.json"

def generate_mackolik_dashboard_html() -> str:
    # 1. Bülten Verisi
    bulletin = []
    if BULLETIN_FILE.exists():
        try:
            with open(BULLETIN_FILE, "r", encoding="utf-8") as f:
                bulletin = json.load(f)
        except Exception:
            pass

    # 2. Kasa Verisi
    bankroll = {"guncel_kasa": 10000.0, "net_kar_zarar": 0.0, "basari_orani_yuzde": 0.0, "toplam_bahis_sayisi": 0, "bahis_gecmisi": []}
    if BANKROLL_FILE.exists():
        try:
            with open(BANKROLL_FILE, "r", encoding="utf-8") as f:
                bankroll = json.load(f)
        except Exception:
            pass

    # 3. Model Ağırlıkları
    weights = {"agirliklar": {}}
    if WEIGHTS_FILE.exists():
        try:
            with open(WEIGHTS_FILE, "r", encoding="utf-8") as f:
                weights = json.load(f)
        except Exception:
            pass

    # 4. Hata ve Öğrenme Günlüğü
    logs = []
    if LEARNING_LOG_FILE.exists():
        try:
            with open(LEARNING_LOG_FILE, "r", encoding="utf-8") as f:
                logs = json.load(f)
        except Exception:
            pass

    # Maçkolik Canlı Bülten Tablosu
    bulten_html = ""
    for m in bulletin[:8]:
        o = m.get("oranlar", {})
        bulten_html += f"""
        <tr>
            <td style="padding:8px; border-bottom:1px solid rgba(255,255,255,0.05); color:#94A3B8;">{m.get('saat')}</td>
            <td style="padding:8px; border-bottom:1px solid rgba(255,255,255,0.05); font-size:11px; color:#38BDF8;">{m.get('lig')}</td>
            <td style="padding:8px; border-bottom:1px solid rgba(255,255,255,0.05); font-weight:700;">{m.get('ev_sahibi')} vs {m.get('deplasman')}</td>
            <td style="padding:8px; border-bottom:1px solid rgba(255,255,255,0.05); text-align:center;">{o.get('ms_1'):.2f}</td>
            <td style="padding:8px; border-bottom:1px solid rgba(255,255,255,0.05); text-align:center;">{o.get('ms_x'):.2f}</td>
            <td style="padding:8px; border-bottom:1px solid rgba(255,255,255,0.05); text-align:center;">{o.get('ms_2'):.2f}</td>
            <td style="padding:8px; border-bottom:1px solid rgba(255,255,255,0.05); text-align:center; color:#00E5FF;">{o.get('alt_25'):.2f}</td>
        </tr>
        """

    # Oynanan Bahisler Tablosu
    bets_html = ""
    for b in reversed(bankroll.get("bahis_gecmisi", [])[-6:]):
        durum_color = "#10B981" if b.get("durum") == "KAZANDI" else ("#EF4444" if b.get("durum") == "KAYBETTİ" else "#F59E0B")
        kazanc = b.get("kazanc", 0.0)
        kazanc_str = f"{kazanc:+,.2f} TL" if kazanc != 0 else "-"
        bets_html += f"""
        <tr>
            <td style="padding:8px; border-bottom:1px solid rgba(255,255,255,0.05);">{b.get('mac')}</td>
            <td style="padding:8px; border-bottom:1px solid rgba(255,255,255,0.05); color:#38BDF8; font-weight:700;">{b.get('secim')} ({b.get('oran'):.2f})</td>
            <td style="padding:8px; border-bottom:1px solid rgba(255,255,255,0.05);">{b.get('yatirilan_tutar', 0):.2f} TL</td>
            <td style="padding:8px; border-bottom:1px solid rgba(255,255,255,0.05); font-weight:700; color:{durum_color};">{b.get('durum')} ({kazanc_str})</td>
        </tr>
        """

    # Model Ağırlık Barları
    agirlik_html = ""
    for k, v in weights.get("agirliklar", {}).items():
        pct = round(v * 100, 1)
        k_clean = k.replace("_", " ").title()
        agirlik_html += f"""
        <div style="margin-bottom: 10px;">
            <div style="display:flex; justify-content:space-between; font-size:11px; margin-bottom:3px;">
                <span>{k_clean}</span>
                <span style="color: #00E5FF; font-weight:700;">%{pct}</span>
            </div>
            <div style="height: 5px; background: #334155; border-radius: 3px; overflow: hidden;">
                <div style="width: {pct*2}%; max-width:100%; height:100%; background: linear-gradient(90deg, #0077B6, #00E5FF);"></div>
            </div>
        </div>
        """

    # Hata Otopsisi Kartları
    otopsi_html = ""
    for log in reversed(logs[-4:]):
        if log.get("sonuc") == "KAYBETTİ":
            otopsi_html += f"""
            <div style="background: rgba(239, 68, 68, 0.08); border-left: 3px solid #EF4444; border-radius: 8px; padding: 10px; margin-bottom: 8px; font-size: 12px;">
                <div style="font-weight: 700; color: #FCA5A5;">❌ {log.get('mac')} (Tahmin: {log.get('tahmin')} / Sonuç: {log.get('gerceklesen')})</div>
                <div style="color: #E2E8F0; margin-top: 3px;"><strong>🔍 Hata Kökü:</strong> {log.get('hata_koku')}</div>
                <div style="color: #00E5FF; margin-top: 2px;"><strong>💡 Alınan Ders:</strong> {log.get('alinan_ders')}</div>
            </div>
            """
        elif log.get("sonuc") == "KAZANDI":
            otopsi_html += f"""
            <div style="background: rgba(16, 185, 129, 0.08); border-left: 3px solid #10B981; border-radius: 8px; padding: 10px; margin-bottom: 8px; font-size: 12px;">
                <div style="font-weight: 700; color: #6EE7B7;">✓ {log.get('mac')} (Tahmin: {log.get('tahmin')})</div>
                <div style="color: #CBD5E1; margin-top: 2px;">Tahmin isabetli. Model parametreleri pekiştirildi.</div>
            </div>
            """

    kasa_val = bankroll.get("guncel_kasa", 10000.0)
    kar_val = bankroll.get("net_kar_zarar", 0.0)
    kar_color = "#10B981" if kar_val >= 0 else "#EF4444"
    kar_prefix = "+" if kar_val > 0 else ""

    html = f"""<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Ertuğrul YZ - Maçkolik Canlı Tarayıcı ve Öz-Öğrenen Robot Paneli</title>
    <style>
        :root {{
            --bg: #0B0F19;
            --card: #131B2E;
            --cyan: #00E5FF;
            --blue: #0077B6;
            --text: #FFFFFF;
            --muted: #94A3B8;
        }}
        * {{ margin:0; padding:0; box-sizing:border-box; font-family:'Segoe UI', system-ui, sans-serif; }}
        body {{ background: var(--bg); color: var(--text); padding: 20px; min-height: 100vh; }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        .header {{ display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid var(--blue); padding-bottom: 14px; margin-bottom: 20px; }}
        .title {{ font-size: 22px; font-weight: 800; color: var(--cyan); letter-spacing: 1px; }}
        .badge {{ background: rgba(0,229,255,0.15); color: var(--cyan); border: 1px solid var(--cyan); padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: 600; }}
        
        .kpi-row {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 14px; margin-bottom: 20px; }}
        .kpi {{ background: var(--card); padding: 16px; border-radius: 12px; border: 1px solid rgba(255,255,255,0.06); }}
        .kpi-title {{ font-size: 11px; color: var(--muted); text-transform: uppercase; margin-bottom: 4px; }}
        .kpi-val {{ font-size: 22px; font-weight: 800; color: #FFF; }}
        
        .grid-2 {{ display: grid; grid-template-columns: 1.2fr 0.8fr; gap: 20px; margin-bottom: 20px; }}
        .card {{ background: var(--card); border-radius: 14px; padding: 18px; border: 1px solid rgba(255,255,255,0.06); }}
        .card-header {{ font-size: 15px; font-weight: 700; color: var(--cyan); margin-bottom: 12px; display:flex; align-items:center; gap:8px; }}
        
        table {{ width: 100%; border-collapse: collapse; font-size: 12px; text-align: left; }}
        th {{ padding: 8px; color: var(--muted); border-bottom: 1px solid rgba(255,255,255,0.1); font-size: 11px; text-transform: uppercase; }}
        
        .footer {{ text-align: center; color: var(--muted); font-size: 12px; margin-top: 24px; padding-top: 14px; border-top: 1px solid rgba(255,255,255,0.08); }}
    </style>
</head>
<body>
    <div class="container">
        <header class="header">
            <div>
                <span class="title">Ertuğrul YZ</span>
                <span style="margin-left: 10px; color: var(--muted); font-size: 13px;">Maçkolik Canlı İddaa Tarayıcı & Öz-Öğrenen Robot</span>
            </div>
            <span class="badge">🤖 Otomatik Tarama & Öğrenme Modülü</span>
        </header>

        <!-- KPI METRİKLERİ -->
        <div class="kpi-row">
            <div class="kpi">
                <div class="kpi-title">Sanal Kasa</div>
                <div class="kpi-val" style="color: #38BDF8;">{kasa_val:,.2f} TL</div>
            </div>
            <div class="kpi">
                <div class="kpi-title">Net Kâr / Zarar</div>
                <div class="kpi-val" style="color: {kar_color};">{kar_prefix}{kar_val:,.2f} TL</div>
            </div>
            <div class="kpi">
                <div class="kpi-title">Model Başarı Oranı</div>
                <div class="kpi-val" style="color: var(--cyan);">%{bankroll.get('basari_orani_yuzde', 0.0)}</div>
            </div>
            <div class="kpi">
                <div class="kpi-title">Canlı Taranan Maç</div>
                <div class="kpi-val">{len(bulletin)} Maçkolik Maçı</div>
            </div>
        </div>

        <div class="grid-2">
            <!-- MAÇKOLİK CANLI BÜLTENİ -->
            <div class="card">
                <div class="card-header">📡 Maçkolik Canlı İddaa Bülteni (Son Tarananlar)</div>
                <table>
                    <thead>
                        <tr>
                            <th>Saat</th>
                            <th>Lig</th>
                            <th>Karşılaşma</th>
                            <th style="text-align:center;">MS 1</th>
                            <th style="text-align:center;">MS X</th>
                            <th style="text-align:center;">MS 2</th>
                            <th style="text-align:center;">2.5 Alt</th>
                        </tr>
                    </thead>
                    <tbody>
                        {bulten_html if bulten_html else '<tr><td colspan="7" style="text-align:center; padding:15px; color:#64748B;">Bülten henüz taranmadı.</td></tr>'}
                    </tbody>
                </table>

                <div class="card-header" style="margin-top:20px;">🎯 Robotun Oynadığı Kuponlar & Bahisler</div>
                <table>
                    <thead>
                        <tr>
                            <th>Karşılaşma</th>
                            <th>Bahis</th>
                            <th>Yatırılan</th>
                            <th>Sonuç</th>
                        </tr>
                    </thead>
                    <tbody>
                        {bets_html if bets_html else '<tr><td colspan="4" style="text-align:center; padding:15px; color:#64748B;">Henüz bahis kaydı yok.</td></tr>'}
                    </tbody>
                </table>
            </div>

            <!-- ÖĞRENME VE HATA OTOPSİSİ -->
            <div class="card">
                <div class="card-header">🧠 Güncel Öğrenme Parametreleri (Ağırlıklar)</div>
                {agirlik_html}

                <div class="card-header" style="margin-top:18px;">🔍 "Nerede Yanıldık & Ne Öğrendik?" Günlüğü</div>
                {otopsi_html if otopsi_html else '<div style="color:#64748B; font-size:12px;">Henüz hata veya ders kaydı yok.</div>'}
            </div>
        </div>

        <footer class="footer">
            Ertuğrul YZ Holding • 5. Kat Spor Analiz Laboratuvarı • Maçkolik Canlı Öğrenme Robotu
        </footer>
    </div>
</body>
</html>
"""
    return html
