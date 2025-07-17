# 1. 以 Python 3.10 slim 為基底
FROM python:3.10-slim

# 2. 安裝 FFmpeg
RUN apt-get update \
 && apt-get install -y ffmpeg \
 && ffmpeg -version \ # 添加這行來驗證
 && rm -rf /var/lib/apt/lists/*

# 3. 設定工作目錄並複製專案程式碼
WORKDIR /app
COPY . /app

# 4. 安裝 Python 相依套件
RUN pip install --no-cache-dir -r requirements.txt

# 5. 啟動 Flask 應用
CMD ["python", "app_llm_ui_integrated.py"]