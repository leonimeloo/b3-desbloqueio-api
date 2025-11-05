FROM python:3.11-slim

LABEL maintainer="leonimeloo"

WORKDIR /app

RUN apt-get update \
    && apt-get -y install sudo poppler-utils tesseract-ocr tesseract-ocr-por \
    && sudo groupadd docker

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8080

CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]