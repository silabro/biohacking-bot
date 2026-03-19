# ──────────────────────────────────────────────
# Silabro Biohacking Bot — Production Dockerfile
# ──────────────────────────────────────────────
FROM python:3.12-slim AS base

# Prevent Python from writing .pyc and enable unbuffered logs
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# ── System dependencies for WeasyPrint PDF rendering ──
# WeasyPrint requires Pango, Cairo, GDK-Pixbuf and GLib.
# Cyrillic fonts are mandatory for correct Russian text in PDFs.
RUN apt-get update && apt-get install -y --no-install-recommends \
    # WeasyPrint core C-libraries
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libpangoft2-1.0-0 \
    libgdk-pixbuf-2.0-0 \
    libcairo2 \
    libglib2.0-0 \
    libffi-dev \
    libxml2 \
    libxslt1.1 \
    shared-mime-info \
    # Fonts — Cyrillic rendering (кириллица)
    fonts-freefont-ttf \
    fonts-dejavu-core \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /opt/app

# ── Install Python dependencies (cached layer) ──
COPY pyproject.toml ./
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir .

# ── Copy application code ──
COPY app/ ./app/
COPY prompts/ ./prompts/

# ── Run as non-root for security ──
RUN useradd --create-home botuser
USER botuser

CMD ["python", "-m", "app"]
