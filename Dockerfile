FROM python:3.11-slim

LABEL maintainer="leonimeloo"

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    sudo \
    poppler-utils \
    tesseract-ocr \
    tesseract-ocr-por \
    build-essential \
    libglib2.0-0 \
    libsm6 \
    libxrender1 \
    libfontconfig1 \
    libgl1 \
    && rm -rf /var/lib/apt/lists/* \
    && sudo groupadd docker

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8080

CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]