# Use Python 3.12 slim image for smaller size
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Build FAISS vector index (required for semantic search)
RUN python -m utils.vector_store.build_index

# Create directory for shared memory (for gunicorn)
RUN mkdir -p /dev/shm && chmod 777 /dev/shm

# Expose port (Render will set PORT env variable)
EXPOSE 5000

# Run with gunicorn using our config file
CMD gunicorn --config gunicorn.conf.py app:app
