#!/bin/bash

# Start script for DPDP Compliance Checker
# This script can be used locally or on Render

# Default values
PORT="${PORT:-5000}"
WORKERS="${WORKERS:-1}"
THREADS="${THREADS:-4}"

echo "Starting DPDP Compliance Checker..."
echo "Port: $PORT"
echo "Workers: $WORKERS"
echo "Threads: $THREADS"

# Check if FAISS index exists, if not build it
if [ ! -f "utils/vector_store/index/policy_index.faiss" ]; then
    echo "FAISS index not found. Building index..."
    python -m utils.vector_store.build_index
fi

# Start gunicorn with configuration
exec gunicorn --config gunicorn.conf.py app:app
