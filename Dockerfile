FROM python:3.10-slim

RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y git

WORKDIR /tmp
COPY requirements.txt .

ENV PYTHONUNBUFFERED=True \
    PORT=9090 \
    WORKERS=2 \
    THREADS=4

RUN pip install -r requirements.txt


WORKDIR /app

COPY *.py /app/

CMD exec gunicorn --preload --bind :$PORT --workers $WORKERS --threads $THREADS --timeout 0 _wsgi:app