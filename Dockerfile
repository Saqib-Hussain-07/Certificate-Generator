# Certificate Generation System - Docker Image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies for PDF/Image processing
RUN apt-get update && apt-get install -y \
    build-essential \
    libffi-dev \
    libjpeg-dev \
    libpng-dev \
    libfreetype6-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better Docker layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p certificates qr_codes templates static

# Set environment variables
ENV PYTHONPATH=/app
ENV FLASK_APP=wsgi.py
ENV FLASK_ENV=production

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
  CMD curl -f http://localhost:8000/ || exit 1

# Run the application with gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "--timeout", "300", "wsgi:app"]