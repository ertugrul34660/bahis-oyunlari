# -*- coding: utf-8 -*-
"""
Ertuğrul YZ - Otonom Bahis ve Öğrenme Botu Dashboard Üreteci (Borsa & Quant Entegrasyonlu)
Sanal Kasa + Hata Otopsisi + Borsa Teknik İndikatörleri (RSI, Volatilite, +EV, Kelly)
"""

import json
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
BANKROLL_FILE = DATA_DIR / "kasa_ve_bahisler.json"
WEIGHTS_FILE = DATA_DIR / "agirliklar_model.json"
LEARNING_LOG_FILE = DATA_DIR / "ogrenme_gunlugu.json"

def generate_bot_dashboard_html() -> str:
    # 1. Kasa verileri
    bankroll = {"guncel_kasa": 10000.0, "net_kar_zarar": 0.0, "basari_orani_yuzde": 0.0, "toplam_bahis_sayisi": 0, "bahis_gecmisi": []}
    if BANKROLL_FILE.exists():
        try:
            with open(BANKROLL_FILE, "r", encoding="utf-8") as f:
                bankroll = json.load(f)
        except Exception:
            pass

    # 2. Ağırlıklar
    weights = {"agirliklar": {}, "ogrenilen_kurallar": []}
    if WEIGHTS_FILE.exists():
        try:
            with open(WEIGHTS_FILE, "r", encoding="utf-8") as f:
                weights = json.load(f)
        except Exception:
            pass

    # 3. Öğrenme Günlüğü
    logs = []
    if LEARNING_LOG_FILE.exists():
        try:
            with open(LEARNING_LOG_FILE, "r", encoding="utf-8") as f:
                logs = json.load(f)
        except Exception:
            pass

    # Bahis tablosu HTML
    bets_html = ""
    for b in reversed(bankroll.get("bahis_gecmisi", [])[-8:]):
        durum_color = "#10B981" if b.get("durum") == "KAZANDI" else ("#EF4444" if b.get("durum") == "KAYBETTİ" else "#F59E0B")
        kazanc_str = f"+{b.get('kazanc', 0):.2f} TL" if b.get('kazanc', 0) > 0 else f"{b.get('kazanc', 0):.2f} TL"
        bets_html += f"""
        <tr>
            <td style="padding: 10px; border-bottom: 1px solid rgba(255,255,255,0.05);">{b.get('mac')}</td>
            <td style="padding: 10px; border-bottom: 1px solid rgba(255,255,255,0.05); font-weight: 700; color: #38BDF8;">{b.get('secim')}</td>
            <td style="padding: 10px; border-bottom: 1px solid rgba(255,255,255,0.05);">{b.get('oran'):.2f}</td>
            <td style="padding: 10px; border-bottom: 1px solid rgba(255,255,255,0.05);">{b.get('yatirilan_tutar'):.2f} TL</td>
            <td style="padding: 10px; border-bottom: 1px solid rgba(255,255,255,0.05); font-weight: 700; color: {durum_color};">{b.get('durum')} ({kazanc_str})</td>
        </tr>
        """

    # Ağırlık barları HTML
    agirlik_html = ""
    for k, v in weights.get("agirliklar", {}).items():
        pct = round(v * 100, 1)
        k_clean = k.replace("_", " ").title()
        agirlik_html += f"""
        <div style="margin-bottom: 12px;">
            <div style="display:flex; justify-content:space-between; font-size:12px; margin-bottom:4px;">
                <span>{k_clean}</span>
                <span style="color: #00E5FF; font-weight:700;">%{pct}</span>
            </div>
            <div style="height: 6px; background: #334155; border-radius: 3px; overflow: hidden;">
                <div style="width: {pct*2}%; max-width:100%; height:100%; background: linear-gradient(90deg, #0077B6, #00E5FF);"></div>
            </div>
        </div>
        """

    # Öğrenme ve Otopsi Kartları HTML
    otopsi_html = ""
    for log in reversed(logs[-4:]):
        if log.get("sonuc") == "KAYBETTİ":
            otopsi_html += f"""
            <div style="background: rgba(239, 68, 68, 0.08); border-left: 3px solid #EF4444; border-radius: 8px; padding: 12px; margin-bottom: 10px; font-size: 13px;">
                <div style="font-weight: 700; color: #FCA5A5;">❌ {log.get('mac')} (Tahmin: {log.get('tahmin')} / Sonuç: {log.get('gerceklesen')})</div>
                <div style="color: #E2E8F0; margin-top: 4px;"><strong>🔍 Hatanın Kökü:</strong> {log.get('hata_koku')}</div>
                <div style="color: #00E5FF; margin-top: 2px;"><strong>💡 Alınan Ders:</strong> {log.get('alinan_ders')}</div>
            </div>
            """
        elif log.get("sonuc") == "KAZANDI":
            otopsi_html += f"""
            <div style="background: rgba(16, 185, 129, 0.08); border-left: 3px solid #10B981; border-radius: 8px; padding: 12px; margin-bottom: 10px; font-size: 13px;">
                <div style="font-weight: 700; color: #6EE7B7;">✓ {log.get('mac')} (Tahmin: {log.get('tahmin')})</div>
                <div style="color: #CBD5E1; margin-top: 4px;">Tahmin başarılı. Model parametreleri doğrulandı ve pekiştirildi.</div>
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
    <title>Ertuğrul YZ - Borsa & Kantitatif Futbol Ticaret Terminali</title>
    <style>
        :root {{
            --bg: #0B0F19;
            --card-bg: #131B2E;
            --accent-cyan: #00E5FF;
            --accent-blue: #0077B6;
            --text-pri: #FFFFFF;
            --text-sec: #94A3B8;
            --green: #10B981;
            --red: #EF4444;
        }}
        * {{ margin:0; padding:0; box-sizing:border-box; font-family:'Segoe UI', system-ui, sans-serif; }}
        body {{ background: var(--bg); color: var(--text-pri); padding: 24px; min-height: 100vh; }}
        .container {{ max-width: 1100px; margin: 0 auto; }}
        .header {{ display: flex; align-items: center; justify-content: space-between; border-bottom: 2px solid var(--accent-blue); padding-bottom: 16px; margin-bottom: 24px; }}
        .logo-area {{ display: flex; align-items: center; gap: 12px; }}
        .logo-title {{ font-size: 22px; font-weight: 800; color: var(--accent-cyan); letter-spacing: 1px; }}
        .badge {{ background: rgba(0, 229, 255, 0.15); color: var(--accent-cyan); border: 1px solid var(--accent-cyan); padding: 4px 12px; border-radius: 20px; font-size: 13px; font-weight: 600; }}
        
        .kpi-row {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 24px; }}
        .kpi-card {{ background: var(--card-bg); border-radius: 12px; padding: 18px; border: 1px solid rgba(255,255,255,0.06); }}
        .kpi-title {{ font-size: 11px; color: var(--text-sec); text-transform: uppercase; margin-bottom: 6px; letter-spacing: 0.5px; }}
        .kpi-val {{ font-size: 24px; font-weight: 800; color: #FFFFFF; }}
        
        .quant-banner {{ background: linear-gradient(135deg, #0F172A, #1E293B); border: 1px solid rgba(0, 229, 255, 0.3); border-radius: 12px; padding: 16px 20px; margin-bottom: 24px; display: flex; justify-content: space-between; align-items: center; }}
        .quant-pill {{ background: rgba(0, 229, 255, 0.1); border: 1px solid var(--accent-cyan); color: var(--accent-cyan); padding: 6px 14px; border-radius: 8px; font-size: 13px; font-weight: 700; }}

        .grid-2 {{ display: grid; grid-template-columns: 1.15fr 0.85fr; gap: 20px; margin-bottom: 24px; }}
        .card {{ background: var(--card-bg); border-radius: 14px; padding: 20px; border: 1px solid rgba(255,255,255,0.06); }}
        .card-header {{ font-size: 15px; font-weight: 700; color: var(--accent-cyan); margin-bottom: 14px; display:flex; align-items:center; gap:8px; }}
        
        table {{ width: 100%; border-collapse: collapse; font-size: 13px; text-align: left; }}
        th {{ padding: 10px; color: var(--text-sec); border-bottom: 1px solid rgba(255,255,255,0.1); font-size: 11px; text-transform: uppercase; }}
        
        .footer {{ text-align: center; color: var(--text-sec); font-size: 12px; margin-top: 24px; padding-top: 16px; border-top: 1px solid rgba(255,255,255,0.08); }}
    </style>
</head>
<body>
    <div class="container">
        <header class="header">
            <div class="logo-area">
                <span class="logo-title">Ertuğrul YZ</span>
            </div>
            <span class="badge">📈 Borsa & Kantitatif Finans Destekli Spor Terminali</span>
        </header>

        <!-- KANTİTATİF BORSA VURGUSU -->
        <div class="quant-banner">
            <div>
                <div style="font-size: 16px; font-weight: 800; color: #FFFFFF;">🏛️ Wall Street & Jane Street Kantitatif Modeli Devrede</div>
                <div style="font-size: 13px; color: var(--text-sec); margin-top: 2px;">Takım Form RSI • Bollinger Gol Volatilitesi • Beklenen Değer (+EV Alpha) • Kelly Criterion Sizing</div>
            </div>
            <div class="quant-pill">⚡ %25 Fractional Kelly Aktif</div>
        </div>

        <!-- KPI METRİKLER -->
        <div class="kpi-row">
            <div class="kpi-card">
                <div class="kpi-title">Portföy / Sanal Kasa</div>
                <div class="kpi-val" style="color: #38BDF8;">{kasa_val:,.2f} TL</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-title">Net Kâr / Getiri</div>
                <div class="kpi-val" style="color: {kar_color};">{kar_prefix}{kar_val:,.2f} TL</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-title">Başarı Oranı (Win Rate)</div>
                <div class="kpi-val" style="color: var(--accent-cyan);">%{bankroll.get('basari_orani_yuzde', 0.0)}</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-title">Gerçekleştirilen Emirler</div>
                <div class="kpi-val">{bankroll.get('toplam_bahis_sayisi', 0)} İşlem</div>
            </div>
        </div>

        <div class="grid-2">
            <!-- SON BAHİSLER / POZİSYONLAR -->
            <div class="card">
                <div class="card-header">📊 Açılan Pozisyonlar ve Sonuçlar</div>
                <table>
                    <thead>
                        <tr>
                            <th>Karşılaşma</th>
                            <th>Emir / Seçim</th>
                            <th>Fiyat (Oran)</th>
                            <th>Pozisyon Boyutu</th>
                            <th>Durum</th>
                        </tr>
                    </thead>
                    <tbody>
                        {bets_html if bets_html else '<tr><td colspan="5" style="text-align:center; padding:20px; color:#64748B;">Henüz pozisyon kaydı yok.</td></tr>'}
                    </tbody>
                </table>
            </div>

            <!-- ÖĞRENME VE MODEL AĞIRLIKLARI -->
            <div class="card">
                <div class="card-header">🧠 Kantitatif Karar Ağırlıkları (Öz-Öğrenme)</div>
                <div style="margin-bottom: 20px;">
                    {agirlik_html}
                </div>

                <div class="card-header" style="font-size: 14px; margin-top: 16px;">🔍 Kök Neden Otopsisi ("Nerede Yanıldık?")</div>
                <div>
                    {otopsi_html if otopsi_html else '<div style="color:#64748B; font-size:13px;">Henüz hata veya öğrenme kaydı oluşmadı.</div>'}
                </div>
            </div>
        </div>

        <footer class="footer">
            Ertuğrul YZ Holding • 2. Kat Finans & Borsa ⨉ 5. Kat Spor Analiz Laboratuvarı Entegrasyonu
        </footer>
    </div>
</body>
</html>
"""
    return html
