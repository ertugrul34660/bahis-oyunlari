# Ertuğrul YZ - Borsa ve Kantitatif Finans Destekli Futbol & İddaa Ticaret Sistemi

**Yetki & Onay:** Yönetim Kurulu Başkanı (Ertuğrul YZ)  
**Kategori:** 2. Kat (Finans, Borsa ve Ticaret) ile 5. Kat (Spor Analiz & AR-GE Laboratuvarı) Entegrasyonu  
**Amaç:** Wall Street, Borsa İstanbul ve Jane Street kantitatif ticaret stratejilerini (Kelly Criterion, RSI, Volatilite Bantları, Beklenen Değer +EV, Hedging, Drawdown Stop-Loss) futbol ve İddaa bültenine eksiksiz uyarlamak.

---

## 🏛️ Borsa ve Futbol Dönüşüm Matrisi (The Quant Matrix)

| Borsa & Finans Kavramı | Futbol & İddaa Karşılığı | Matematiksel Formül / Mantık |
| :--- | :--- | :--- |
| **Piyasa Fiyatı (Market Price)** | **İddaa Bülten Oranı** | $Piyasa\_Olasılığı = 1 / Oran$ |
| **İçsel Değer (Fair Value)** | **Yapay Zeka Gerçek Olasılığı ($P_{model}$)** | Kadro, form, fiziki yorgunluk ve xG bazlı gerçek ihtimal |
| **Alfa & Iskontolu Alım (+EV)** | **Değerli Bahis (Value Bet)** | $EV = (P_{model} \times Oran) - 1.0 > +0.05$ (Net Kâr Marjı) |
| **RSI (Göreceli Güç Endeksi)** | **Takım Form & Tükenmişlik RSI (0-100)** | Son 5 maçlık skor ivmesi (RSI > 80: Aşırı Şişirilmiş / RSI < 25: Kelepir/Tepki) |
| **Bollinger Bantları & Volatilite** | **Gol Volatilitesi & Skor Oynaklığı** | Standart sapma düşükse = 2.5 Alt, Yüksekse = KG Var & 2.5 Üst |
| **Kelly Criterion (Pozisyon Boyutu)** | **Optimal Kasa Stake Hesaplaması** | $f^* = \frac{bp - q}{b}$ (Fractional %25 Kelly ile sıfır batma riski) |
| **Hedging (Korunma / Put Opsiyonu)** | **Çifte Şans & Beraberlikte İade (DNB)** | Ana pozisyon riske girdiğinde sigorta kuponu |
| **Stop-Loss / Risk Yönetimi** | **Maksimum Drawdown Koruması** | Günlük %5 kasa erimesinde otomatik işlem durdurma ve savunma modu |

---

## 📊 1. Kantitatif Göstergeler

### 1) Futbol RSI (Relative Strength Index)
- **Aşırı Alım Bölgesi (RSI > 75):** Takım peş peşe kazanmış, medya ve bülten aşırı şişirmiş, İddaa oranı çok düşmüş (1.15 - 1.25 bandı). **Tuzak / Short Adayı!**
- **Aşırı Satım Bölgesi (RSI < 25):** Takım şanssız puanlar kaybetmiş ama kadro kalitesi yüksek. Oranı bültende şişirilmiş (2.50+ bandı). **Kelepir Değer / Long Adayı!**

### 2) Beklenen Değer ($+EV$ Alpha Filter)
Model bir maça sadece tahmin tutacak diye girmez; borsada hisse seçer gibi matematiksel getiri beklentisi $+EV \ge \%5$ olan seçeneklere yatırım yapar.

### 3) Kelly Kriteri ile Dinamik Kasa Yönetimi
Kasa asla rasgele bölünmez. Modelin bulduğu getiri avantajı (edge) ne kadar büyükse pozisyon büyüklüğü Kelly formülüyle dinamik olarak artırılır.
