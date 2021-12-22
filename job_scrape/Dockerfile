FROM python:3.9-slim


LABEL maintainer="Pongpun364"

# set work directory
WORKDIR /usr/src/app


# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

EXPOSE 8000

COPY ./requirements.txt .


# install dependencies
RUN apt-get update && \
    apt-get install -y \
    build-essential \
    python3-dev \
    python3-setuptools \
    unzip \
    chromium-driver \
    gcc \
    make &&\
    pip install --upgrade pip &&\
    pip install --no-cache-dir -r requirements.txt &&\
    apt-get remove -y --purge make gcc build-essential python3-dev python3-setuptools &&\
    apt-get autoremove -y &&\
    rm -rf /var/lib/apt/lists/*


COPY . .

COPY ./entrypoint.sh .

RUN chmod +x /usr/src/app/entrypoint.sh &&\
    chmod 775 /usr/src/app/database/ &&\
    chmod 774 /usr/src/app/database/db.sqlite3 &&\
    chmod -R 777 /usr/src/app/uploads/


CMD [ "/usr/src/app/entrypoint.sh" ]
