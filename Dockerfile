# Stage 1: Base Python environment
FROM python:3.10-slim AS base

# Prevent Python from writing .pyc and enable unbuffered logging
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Install system dependencies for OpenCV, TFLite, and OpenGL support
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libglib2.0-0 \
    libsm6 \
    libxrender1 \
    libgl1-mesa-glx \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY app/requirements.txt .
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Stage 2: Copy application code
FROM base AS final
COPY app/ .

# Expose FASTAPI port (60000)
EXPOSE 60000

# Launch Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "60000"]
