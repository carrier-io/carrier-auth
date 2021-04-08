FROM python:3.8

ENV PYTHONUNBUFFERED 1
RUN pip install --upgrade pip
RUN pip install --upgrade setuptools

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY plugins ./plugins
COPY config/pylon.yml ./config/pylon.yml
COPY config/auth_settings.yaml ./config/auth_settings.yaml
COPY setup.py .
RUN set -x && pip install --no-cache-dir /app

ENTRYPOINT ["app"]