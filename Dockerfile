# Temel imaj
FROM python:3.9-slim

# Çalışma dizinini ayarla
WORKDIR /app

# Bağımlılıkları yükle
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Uygulama dosyalarını kopyala
COPY . .

# Gerekli portları aç
EXPOSE 8000

# Uygulamayı çalıştır
CMD ["python", "app.py"]