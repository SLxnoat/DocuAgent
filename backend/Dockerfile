# ==============================================================================
# DocuAgent AI — Production Backend Dockerfile
# Multi-stage optimized build for FastAPI API server with Playwright & WeasyPrint
# ==============================================================================

FROM python:3.11-slim AS runtime

# System environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PLAYWRIGHT_BROWSERS_PATH=/ms-playwright \
    PORT=8000

WORKDIR /app

# Install native compilation and PDF/document rendering libraries
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    curl \
    ca-certificates \
    libffi-dev \
    shared-mime-info \
    libpango-1.0-0 \
    libpangoft2-1.0-0 \
    libharfbuzz-subset0 \
    libcairo2 \
    pandoc \
    && rm -rf /var/lib/apt/lists/*

# Install Python production dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Install Playwright browser engine & required system dependencies
RUN mkdir -p /ms-playwright && \
    playwright install --with-deps chromium

# Create storage volume directories
RUN mkdir -p /app/assets /app/exports

# Create non-root application user for secure execution
RUN groupadd -g 1001 docuagent && \
    useradd -u 1001 -g docuagent -s /bin/bash -m docuagent

# Copy application source tree
COPY . /app

# Configure ownership and permissions
RUN chown -R docuagent:docuagent /app /ms-playwright && \
    chmod -R 755 /app/assets /app/exports

USER docuagent

EXPOSE 8000

# Run high-performance ASGI server with Gunicorn process manager and Uvicorn workers
CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "-w", "4", "-b", "0.0.0.0:8000", "--timeout", "120", "--access-logfile", "-", "--error-logfile", "-", "app.main:app"]
