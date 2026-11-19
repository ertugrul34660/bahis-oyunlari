# -*- coding: utf-8 -*-
"""
Ertuğrul YZ - Kelly Kriteri Kasa ve Pozisyon Boyutlandırma Motoru (Kelly Calculator)
5. Kat Spor Analiz Laboratuvarı & 2. Kat Finans Entegrasyonu

Yönetim Kurulu Başkanı Tarafından Tescillenen Standart Kelly Fonksiyonu.
"""

def kelly_criterion_stake(bankroll, odds, probability, fraction=1.0):
    """
    Kelly Kriteri ile ideal bahis miktarını hesaplar.
    
    Parametreler:
    - bankroll (float): Toplam mevcut kasanız (örneğin 10000 TL)
    - odds (float): Bahis oranı (Ondalık / Decimal format, örn. 2.10)
    - probability (float): Kazanma olasılığınız (0 ile 1 arasında, örn. %55 için 0.55)
    - fraction (float): Kesirli Kelly katsayısı (Güvenlik için genelde 0.5 yani Yarım Kelly kullanılır)
    
    Dönüş:
    - dict: Yatırılacak ideal tutar ve kasanın yüzde kaçı olduğu
    """
    if odds <= 1.0:
        raise ValueError("Bahis oranı 1.0'dan büyük olmalıdır.")
    if not (0.0 <= probability <= 1.0):
        probability = max(0.0, min(1.0, probability))
        
    # Net ondalık oran (b = odds - 1)
    b = odds - 1.0
    
    # Kelly Formülü: f* = (bp - q) / b  (q = 1 - p)
    q = 1.0 - probability
    kelly_fraction = (b * probability - q) / b
    
    # Eğer sonuç negatifse, bu bahis matematiksel olarak dezavantajlıdır (value yok)
    if kelly_fraction <= 0:
        return {
            "recommended_stake": 0.0,
            "stake_percentage": 0.0,
            "message": "Bahis dezavantajlı (Negative Expected Value). Oynanmamalı."
        }
    
    # Güvenlik için Kesirli Kelly (Fractional Kelly) uygulama
    adjusted_kelly = kelly_fraction * fraction
    
    # Yatırılacak miktar ve yüzde
    recommended_stake = bankroll * adjusted_kelly
    stake_percentage = adjusted_kelly * 100.0
    
    return {
        "recommended_stake": round(recommended_stake, 2),
        "stake_percentage": round(stake_percentage, 2),
        "message": "Hesaplama başarılı."
    }

# --- Örnek Kullanım ---
if __name__ == "__main__":
    toplam_kasa = 10000.0   # 10.000 TL Kasa
    bahis_orani = 2.10      # Verilen oran
    tahmini_olasilik = 0.52 # Kazanma ihtimaliniz %52
    
    # Risk yönetimi için Yarım Kelly (fraction=0.5) kullanarak hesaplama
    sonuc = kelly_criterion_stake(
        bankroll=toplam_kasa, 
        odds=bahis_orani, 
        probability=tahmini_olasilik, 
        fraction=0.5
    )
    
    print("=" * 60)
    print("🎯 ERTUĞRUL YZ - KELLY KRİTERİ HESAPLAMA SONUCU")
    print("=" * 60)
    print(f"Toplam Kasa: {toplam_kasa:,.2f} TL")
    print(f"Bahis Oranı: {bahis_orani:.2f} | Model Olasılığı: %{tahmini_olasilik*100:.1f}")
    print(f"Yatırılacak Önerilen Tutar: {sonuc['recommended_stake']} TL")
    print(f"Kasanın Yüzdesi: %{sonuc['stake_percentage']}")
    print(f"Durum: {sonuc['message']}")
    print("=" * 60)
