FROM python:3.13-bookworm

WORKDIR /app

COPY requirements.txt .

RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    python3-dev \
    openjdk-17-jdk \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "-m", "main"]
