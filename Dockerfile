FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

# Install system dependencies including GDAL and all required libraries
RUN apt-get update && apt-get install -y \
    curl \
    gnupg \
    lsb-release \
    software-properties-common \
    && add-apt-repository ppa:deadsnakes/ppa \
    && apt-get update && apt-get install -y \
    python3.13 \
    python3.13-venv \
    python3.13-dev \
    python3-pip \
    build-essential \
    gdal-bin \
    libgdal-dev \
    libgdal32 \
    libgeos-dev \
    libgeos-c1v5 \
    libproj-dev \
    libproj25 \
    binutils \
    git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements and install Python dependencies in a virtualenv
COPY requirements.txt .
RUN python3.13 -m venv /app/.venv && \
    /app/.venv/bin/pip install --upgrade pip setuptools wheel && \
    /app/.venv/bin/pip install -r requirements.txt

# Copy application code
COPY . .

# Set environment variables for GDAL - use the actual installed library names
ENV GDAL_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu/libgdal.so.32
ENV GEOS_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu/libgeos_c.so.1
ENV PROJ_LIB=/usr/share/proj
ENV LD_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu:$LD_LIBRARY_PATH

# Collect static files (ignore errors if not applicable)
RUN /app/.venv/bin/python manage.py collectstatic --noinput 2>/dev/null || true

# Run migrations and start gunicorn
CMD /app/.venv/bin/python manage.py migrate && \
    /app/.venv/bin/gunicorn --bind 0.0.0.0:${PORT:-8000} config.wsgi:application