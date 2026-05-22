# Sử dụng Python base image
FROM python:3.11-slim

# Thiết lập các biến môi trường
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Cài đặt các thư viện hệ thống cần thiết cho GeoDjango (GDAL, GEOS, PROJ)
RUN apt-get update && apt-get install -y \
    binutils \
    libproj-dev \
    gdal-bin \
    libgdal-dev \
    python3-gdal \
    && rm -rf /var/lib/apt/lists/*

# Thiết lập thư mục làm việc
WORKDIR /app

# Sao chép requirements.txt và cài đặt các thư viện Python
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

# Sao chép toàn bộ source code vào container
COPY . /app/

# Thu thập các file tĩnh (CSS, JS, Images)
RUN python manage.py collectstatic --noinput

# Expose port (Render sẽ tự động cấu hình qua biến môi trường PORT)
EXPOSE 8000

# Khởi chạy server bằng Gunicorn
CMD ["sh", "-c", "python manage.py migrate && gunicorn config.wsgi:application --bind 0.0.0.0:${PORT:-8000}"]
