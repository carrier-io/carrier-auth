FROM python:3.7-alpine

RUN apk add --update --no-cache \
  build-base \
  coreutils \
  gcc \
  libffi-dev \
  libressl \
  libressl-dev

ENV CRYPTOGRAPHY_DONT_BUILD_RUST=1
ENV PYTHONUNBUFFERED 1
RUN pip3 install --upgrade pip
RUN pip3 install --upgrade setuptools

WORKDIR /auth
COPY requirements.txt .
COPY auth /auth/auth
COPY setup.py .
RUN set -x && pip3 install --no-cache-dir /auth

ENTRYPOINT ["app"]