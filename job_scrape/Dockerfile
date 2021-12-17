FROM python:3.9-slim


LABEL maintainer="Pongpun364"

# set work directory
WORKDIR /usr/src/app


# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

EXPOSE 8000

# install dependencies
RUN apt-get update && \
    apt-get install -y \
    build-essential \
    python3-dev \
    python3-setuptools \
    unzip \
    chromium-driver \
    gcc \
    make 

COPY ./requirements.txt .

RUN pip install --upgrade pip &&\
    pip install -r requirements.txt &&\
    apt-get remove -y --purge make gcc build-essential &&\
    apt-get autoremove -y

COPY . .

COPY ./entrypoint.sh .

RUN chmod +x /usr/src/app/entrypoint.sh



CMD [ "/usr/src/app/entrypoint.sh" ]
