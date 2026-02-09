FROM python:3.10

WORKDIR /app

RUN apt-get update && apt-get install -y \
    poppler-utils \
    tesseract-ocr \
    antiword \
    libxml2-dev \
    libxslt1-dev \
    libjpeg-dev \
    zlib1g-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY . /app

RUN pip install "pip<24.1"
RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "app.py"]