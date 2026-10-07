FROM python:3.12-slim-bookworm
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
RUN apt-get update && apt-get install -y --no-install-recommends gcc g++ libc6-dev curl unzip ca-certificates \
    wkhtmltopdf fonts-inter fontconfig \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
# Fonts for the Your 2027 PDF (Lora is OFL, see fonts/Lora-OFL.txt; Inter comes from fonts-inter).
RUN mkdir -p /usr/local/share/fonts/sr11 && cp fonts/*.ttf /usr/local/share/fonts/sr11/ && fc-cache -f
ENV QT_QPA_PLATFORM=offscreen
# Data is fetched at build time so the running service never calls out.
RUN ./scripts/fetch_ephemeris.sh ephe && ./scripts/fetch_geonames.sh data/geonames
ENV SR11_EPHE_PATH=/app/ephe SR11_GEONAMES_DIR=/app/data/geonames
# SR11_API_KEY must be supplied by the host's secret settings, never baked in.
EXPOSE 8080
CMD ["gunicorn", "-c", "gunicorn.conf.py", "app:app"]
