FROM python:3.8

ENV PYTHONUNBUFFERED 1
RUN pip install --upgrade pip
RUN pip install --upgrade setuptools

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt --no-cache

COPY plugins ./plugins
COPY config/pylon.yml ./config/pylon.yml
#COPY config/auth_settings.yaml ./config/auth_settings.yaml
COPY config/*.yml ./config/
COPY app.py .

ENTRYPOINT ["python", "app.py"]