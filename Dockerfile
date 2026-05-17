# ============================
# 1. Base image
# ============================
FROM python:3.10-slim

# Prevent Python from writing .pyc files
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# ============================
# 2. System dependencies
# ============================
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    unzip \
    git \
    libnss3 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libgbm1 \
    libasound2 \
    libpangocairo-1.0-0 \
    libpango-1.0-0 \
    libgtk-3-0 \
    libx11-xcb1 \
    && rm -rf /var/lib/apt/lists/*

# ============================
# 3. Install Python dependencies
# ============================
COPY requirements.txt /app/requirements.txt
WORKDIR /app

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# ============================
# 4. Install Playwright browsers
# ============================
RUN playwright install --with-deps chromium

# ============================
# 5. Copy app code
# ============================
COPY . /app

# ============================
# 6. Expose Streamlit port
# ============================
EXPOSE 8501

# ============================
# 7. Streamlit config
# ============================
ENV STREAMLIT_SERVER_HEADLESS=true
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

# ============================
# 8. Run the app
# ============================
CMD ["streamlit", "run", "app.py"]

