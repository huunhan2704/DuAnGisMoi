FROM python:3.13-slim

# Cài đặt các thư viện GIS hệ thống (bản chuẩn cho Linux)
RUN apt-get update && apt-get install -y \
    binutils \
    libproj-dev \
    gdal-bin \
    libgdal-dev \
    python3-gdal \
    && rm -rf /var/lib/apt/lists/*

# Thiết lập đường dẫn thư viện cho Django
ENV GDAL_LIBRARY_PATH=/usr/lib/libgdal.so
ENV GEOS_LIBRARY_PATH=/usr/lib/libgeos_c.so

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Chạy server (config.wsgi là tên folder chứa file wsgi của bạn)
CMD gunicorn config.wsgi:application --bind 0.0.0.0:$PORT