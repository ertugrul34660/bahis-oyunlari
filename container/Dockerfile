# Ertuğrul YZ - 7/24 Kesintisiz VPS Spor & İddaa Robotu Dockerfile
FROM python:3.11-slim

LABEL maintainer="Ertuğrul YZ Holding <ertugrul-yz>"
LABEL description="7/24 Maçkolik Canlı İddaa Tarayıcı ve Öz-Öğrenen Robot"

ENV PYTHONUNBUFFERED=1
ENV TZ=Europe/Istanbul

WORKDIR /app

# Gerekli sistem paketleri
RUN apt-get update && apt-get install -y --no-install-recommends \
    tzdata curl ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Bağımlılıklar
RUN pip install --no-cache-dir beautifulsoup4 requests

# Proje dosyalarını kopyala
COPY core/ /app/core/
COPY ui/ /app/ui/
COPY data/ /app/data/
COPY docs/ /app/docs/

# Çalıştırma komutu
CMD ["python", "core/vps_spor_daemon.py"]
