#!/usr/bin/env bash
# build.sh - Script Render chạy để build ứng dụng

# Dừng ngay nếu có lỗi
set -o errexit

# 1. Cài thư viện hệ thống cho GeoDjango (GDAL, GEOS, PostGIS client)
apt-get update -y
apt-get install -y \
    binutils \
    libproj-dev \
    gdal-bin \
    libgdal-dev \
    python3-gdal

# 2. Cài các Python packages
pip install --upgrade pip
pip install -r requirements.txt

# 3. Thu thập static files
python manage.py collectstatic --noinput

# 4. Chạy migration tự động
python manage.py migrate
