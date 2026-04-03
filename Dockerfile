FROM python:3.13-slim

# Cài đặt các thư viện GIS hệ thống (bản chuẩn cho Linux)
RUN apt-get update && apt-get install -y \
    binutils \
    libproj-dev \
    gdal-bin \
    libgdal-dev \
    python3-gdal \
    && rm -rf /var/lib/apt/lists/*

# Set environment variables so Django can locate the geospatial libraries
ENV GDAL_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu/libgdal.so.30
ENV GEOS_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu/libgeos_c.so.1
ENV LD_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu:$LD_LIBRARY_PATH

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Chạy server (config.wsgi là tên folder chứa file wsgi của bạn)
CMD gunicorn config.wsgi:application --bind 0.0.0.0:$PORT