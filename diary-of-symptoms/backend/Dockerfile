FROM python:3.11-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /build

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        gcc \
        libffi-dev \
        libpq-dev && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

FROM python:3.11-slim

ENV APP_DEBUG=False \
    PORT=8000 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH=/home/appuser/.local/bin:$PATH \
    PYTHONPATH=/app/backend

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        fontconfig \
        fonts-dejavu-core \
        libcairo2 \
        libffi8 \
        libgdk-pixbuf-2.0-0 \
        libglib2.0-0 \
        libpango-1.0-0 \
        libpangocairo-1.0-0 \
        libpangoft2-1.0-0 \
        shared-mime-info && \
    rm -rf /var/lib/apt/lists/*

RUN useradd --create-home --shell /usr/sbin/nologin appuser

COPY --from=builder --chown=appuser:appuser /root/.local /home/appuser/.local
COPY --chown=appuser:appuser diary-of-symptoms/backend ./backend

WORKDIR /app/backend
USER appuser

EXPOSE 8000

CMD ["uvicorn", "app.services.main:app", "--host", "0.0.0.0", "--port", "8000"]
