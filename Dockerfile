FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
RUN apt-get update && apt-get install -y --no-install-recommends gcc g++ libc6-dev curl unzip ca-certificates \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
# Data is fetched at build time so the running service never calls out.
RUN ./scripts/fetch_ephemeris.sh ephe && ./scripts/fetch_geonames.sh data/geonames
ENV SR11_EPHE_PATH=/app/ephe SR11_GEONAMES_DIR=/app/data/geonames
# SR11_API_KEY must be supplied by the host's secret settings, never baked in.
EXPOSE 8080
CMD ["gunicorn", "-c", "gunicorn.conf.py", "app:app"]
