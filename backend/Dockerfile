# ==============================================================================
# DocuAgent AI — Production Backend Dockerfile
# Optimized build for FastAPI ASGI server
# ==============================================================================

FROM python:3.11-slim-bookworm AS runtime

# System environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000

WORKDIR /app

# Configure apt retries and install runtime utilities and WeasyPrint libraries
RUN echo 'Acquire::Retries "3";' > /etc/apt/apt.conf.d/80-retries && \
    apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    shared-mime-info \
    libpango-1.0-0 \
    libpangoft2-1.0-0 \
    libharfbuzz-subset0 \
    libcairo2 \
    && rm -rf /var/lib/apt/lists/*

# Install Python production dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Create storage volume directories
RUN mkdir -p /app/assets /app/exports

# Create non-root application user for secure execution
RUN groupadd -g 1001 docuagent && \
    useradd -u 1001 -g docuagent -s /bin/bash -m docuagent

# Copy application source tree
COPY . /app

# Configure ownership and permissions
RUN chown -R docuagent:docuagent /app && \
    chmod -R 755 /app/assets /app/exports

USER docuagent

EXPOSE 8000

# Run high-performance ASGI server with Gunicorn process manager and Uvicorn workers
CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "-w", "2", "-b", "0.0.0.0:8000", "--timeout", "120", "--access-logfile", "-", "--error-logfile", "-", "app.main:app"]
