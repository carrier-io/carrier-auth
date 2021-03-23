FROM python:3.8

#RUN apk add --update --no-cache \
#  build-base \
#  coreutils \
#  gcc \
#  libffi-dev \
#  libressl \
#  libressl-dev

#RUN apk add --update git gcc libffi-dev libressl libressl-dev build-base coreutils

ENV PYTHONUNBUFFERED 1
RUN pip install --upgrade pip
RUN pip install --upgrade setuptools

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

#COPY config ./config
#COPY plugins ./plugins
#COPY app.py .

#COPY setup.py .
#RUN set -x && pip3 install --no-cache-dir /auth
#
#ENTRYPOINT ["app"]