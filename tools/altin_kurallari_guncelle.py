import json
from datetime import datetime

file_path = r'C:\Users\ertug\.gemini\antigravity\scratch\08-Oyunlar-Simulasyonlar-ve-Trainer\ErtugrulYZ-Spor-ve-Iddaa-Analiz-Motoru\data\ogrenilen_altin_kurallar.json'

with open(file_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

new_rules = [
    {
        "id": "RULE-11",
        "mac_referansi": "Malavan 1-1 Gol Gohar (Skor 1-1 ve İY X BİLİNDİ)",
        "tur": "TAM_İSABET_SKOR_ZAFERİ",
        "kural": "Savunma odaklı liglerde Poisson skor gücü: İran ve benzeri kısır liglerde hücum lambda parametresi 1.1-1.2 bandındayken '1-1' skor tahmini (%13.2) ve 'İY X' (%46.8) matematiksel olarak en yüksek isabeti sağlar.",
        "etki_alani": ["poisson_skor_matrisi", "ilk_yari_beraberlik_katsayisi"]
    },
    {
        "id": "RULE-12",
        "mac_referansi": "Svay Rieng 4-1 Port FC (Poisson 4-6 Gol ve KG VAR BİLİNDİ)",
        "tur": "POISSON_TG_ZAFERİ",
        "kural": "Asya Şampiyonlar ve Kupa dinamikleri: Asya kulüpler şampiyonalarında takımların geçiş savunması zayıf olduğundan Poisson '4-6 Gol' ve 'KG VAR' modelleri tekil 2.5 Alt bahislerine kıyasla çok daha yüksek başarı üretir.",
        "etki_alani": ["toplam_gol_bandi", "kg_var_olasiligi"]
    },
    {
        "id": "RULE-13",
        "mac_referansi": "Dob 1-1 Bistrica (2.5 Alt KAZANDI - Oran: 1.65)",
        "tur": "KAZANÇ_PEKİŞTİRMESİ",
        "kural": "Slovenya Kupa kontrollü oyun disiplini: Denk Slovenya kupa eşleşmelerinde takımlar uzatmaya gitme riskini göze alarak düşük tempolu oynar; 2.5 Alt tercihi ve İY X kilitlenmesi kasayı büyütür (+97.50 TL kâr).",
        "etki_alani": ["kasa_yonetimi", "oran_deger_farki"]
    }
]

# Ensure no duplicate
existing_ids = {r['id'] for r in data['kurallar']}
for nr in new_rules:
    if nr['id'] not in existing_ids:
        data['kurallar'].append(nr)

data['guncelleme'] = datetime.now().isoformat()

with open(file_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"Toplam Kural Sayisi: {len(data['kurallar'])}")
