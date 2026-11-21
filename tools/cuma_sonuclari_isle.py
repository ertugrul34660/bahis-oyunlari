# -*- coding: utf-8 -*-
"""20 Kasım 2026 Cuma akşamı sonuçlarını öğrenme günlüğüne işler."""
import json
from pathlib import Path

LOG = Path(__file__).resolve().parent.parent / "data" / "ogrenme_gunlugu.json"

kayitlar = [
    {"mac": "Nancy 1-0 Dijon (İY 0-0)", "tahmin": "2.5 Alt / İY X / İY-MS X/1 / Skor 1-1 (alt. 1-0)",
     "gerceklesen": "1-0", "sonuc": "TUTTU (2.5 Alt, İY X, X/1, alternatif skor 1-0); ana skor 1-1 tutmadı",
     "hata_koku": "Yok", "alinan_ders": "Düşük gollü Ligue 2 eşleşmelerinde İY X + 2.5 Alt güçlü."},
    {"mac": "Bayern 1-1 Köln (İY 1-1)", "tahmin": "İY 1 / Handikap 1 / Skor 2-0 / KG YOK",
     "gerceklesen": "1-1", "sonuc": "TUTMADI (tüm tahminler)",
     "hata_koku": "Ağır favoriye (kadroda Neuer, Davies, Gnabry, Díaz eksik) aşırı güven; Köln 12'de erken gol buldu.",
     "alinan_ders": "Çok eksikli favoride handikap/İY 1 de oynanmaz; 1.20 MS'yi pas geçmek doğruydu ama türev bahisler de pas geçilmeli."},
    {"mac": "Athletic Bilbao 0-1 Espanyol", "tahmin": "MS 1 / İY 1 / Skor 2-0 / KG YOK",
     "gerceklesen": "0-1", "sonuc": "TUTMADI (KG YOK hariç)",
     "hata_koku": "Yeni teknik direktör etkisi (Espanyol, Sarabia'nın ilk maçı) hesaba katılmadı.",
     "alinan_ders": "Yeni hoca ilk maçı = motivasyon sıçraması; deplasman takımına karşı MS 1 oynanmaz."},
    {"mac": "Clermont vs Metz", "tahmin": "İY X / 1-1",
     "gerceklesen": "MAÇ OYNANMADI (fikstür hatası: gerçekte Annecy 4-2 Clermont, Metz 1-1 Boulogne)",
     "sonuc": "GEÇERSİZ", "hata_koku": "Doğrulanmamış fikstür kaynağı kullanıldı.",
     "alinan_ders": "Her maç en az 2 bağımsız kaynaktan fikstür teyidi almadan bültene girmez."},
]

data = json.loads(LOG.read_text(encoding="utf-8")) if LOG.exists() else []
data.extend(kayitlar)
LOG.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"[OK] {len(kayitlar)} kayıt eklendi. Toplam: {len(data)}")
