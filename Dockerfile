# ===============================
# ISP Analyzer – Streamlit + Speedtest + Wi-Fi Diagnostics
# Maintainer: CTLALTDELETE
# ===============================

# 1️⃣ Base lightweight Python image (arm64/amd64 compatible)
FROM python:3.12-slim

# 2️⃣ Set working directory
WORKDIR /app

# 3️⃣ Copy project files into container
COPY . /app

# 4️⃣ Install system dependencies (for network + Wi-Fi tools)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    net-tools \
    iproute2 \
    wireless-tools \
    jq \
    && rm -rf /var/lib/apt/lists/*

# 5️⃣ Install Python dependencies for ISP Analyzer
# Removed the specific speedtest-cli version that no longer exists
RUN pip install --no-cache-dir \
    streamlit==1.39.0 \
    pandas==2.2.2 \
    speedtest-cli \
    matplotlib==3.9.2 \
    plotly==5.24.1 \
    requests==2.32.3

# 6️⃣ Optional: Set UTF-8 locale and environment
ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8
ENV TZ=Europe/London

# 7️⃣ Expose Streamlit port
EXPOSE 8501

# 8️⃣ Streamlit configuration (disable CORS for internal LAN access)
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_HEADLESS=true
ENV STREAMLIT_SERVER_ENABLECORS=false
ENV STREAMLIT_SERVER_ENABLEXSRSFPROTECTION=false

# 9️⃣ Run the Streamlit ISP Analyzer app
CMD ["streamlit", "run", "isp_speed_analyzer_alerts.py", "--server.port=8501", "--server.address=0.0.0.0"]