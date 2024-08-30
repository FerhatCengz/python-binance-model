# Python 3.12.4 imajını kullan
FROM python:3.12.4-slim

# Gerekli sistem bağımlılıklarını yükle
RUN apt-get update && apt-get install -y \
    build-essential \
    pkg-config \
    libhdf5-dev \
    && apt-get clean

# Çalışma dizinini oluştur ve ayarla
WORKDIR /app

# Gereken bağımlılıkları yüklemek için gerekli dosyaları kopyala
COPY requirements.txt .

# Gerekli Python paketlerini yükle
RUN pip install --no-cache-dir -r requirements.txt

# Uygulama kodlarını kopyala
COPY . .

# Flask uygulamasını 0.0.0.0 host ve 8080 portu üzerinden çalıştır
CMD ["python", "app.py"]
