FROM python:3.9-slim


RUN apt-get update && \
    apt-get install -y \
    build-essential \
    python3-dev \
    python3-setuptools \
    chromium-driver \
    gcc \
    make









COPY ./job_scrape /app
COPY ./requirements.txt /app/requirements.txt

COPY ./entrypoint.sh /app/entrypoint.sh