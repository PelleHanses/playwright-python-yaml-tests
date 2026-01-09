# Python-basimage
FROM python:3.12-slim
 
# Undvik interaktiva apt-frågor
ENV DEBIAN_FRONTEND=noninteractive
 
# Installera systemberoenden som Playwright behöver
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    ca-certificates \
    fonts-liberation \
    libnss3 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxrandr2 \
    libxdamage1 \
    libgbm1 \
    libasound2 \
    libxshmfence1 \
    libgtk-3-0 \
    libx11-xcb1 \
    libxcb1 \
    libxext6 \
    libxfixes3 \
    libxrender1 \
    libxss1 \
    libxtst6 \
    && rm -rf /var/lib/apt/lists/*
 
# Uppgradera pip
RUN python -m pip install --upgrade pip
 
# Installera Python Playwright + deps
RUN pip install playwright pyyaml
 
# Installera browsers (Chromium räcker oftast)
RUN playwright install chromium
 
# Arbetskatalog
WORKDIR /work
 
# Kopiera tester
COPY ./app/ /work

ENTRYPOINT ["python", "runner.py"]
CMD ["--help"]
 
# Standardkommando (kan overridas)
#CMD ["python", "runner.py", "--help"]
