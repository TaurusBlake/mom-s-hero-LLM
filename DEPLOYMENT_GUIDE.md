# MomsHero LineBot 部署與維護指南

## 📋 目錄
- [環境設定](#環境設定)
- [部署步驟](#部署步驟)
- [監控與維護](#監控與維護)
- [故障排除](#故障排除)
- [升級指南](#升級指南)

## 🔧 環境設定

### 必要環境變數
```bash
# .env 文件
GOOGLE_API_KEY=your_google_api_key
LINE_CHANNEL_ACCESS_TOKEN=your_line_channel_access_token
LINE_CHANNEL_SECRET=your_line_channel_secret
```

### Python 環境
```bash
# 建立虛擬環境
python -m venv .venv

# 啟動虛擬環境
# Windows
.venv\Scripts\activate
# Linux/Mac
source .venv/bin/activate

# 安裝依賴
pip install -r requirements.txt
```

## 🚀 部署步驟

### 1. 本地開發環境
```bash
# 啟動應用
python app_llm.py

# 使用 ngrok 進行外部連接
ngrok http 5000
```

### 2. 生產環境部署
```bash
# 使用 Gunicorn (Linux/Mac)
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app_llm:app

# 使用 Waitress (Windows)
pip install waitress
waitress-serve --host=0.0.0.0 --port=5000 app_llm:app
```

### 3. Docker 部署
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 5000

CMD ["python", "app_llm.py"]
```

## 📊 監控與維護

### 系統監控
```bash
# 檢查系統狀態
python -c "from system_monitor import system_monitor; print(system_monitor.generate_report())"

# 查看日誌
tail -f momshero_llm.log

# 檢查健康狀態
curl http://localhost:5000/health
```

### 定期維護任務
1. **每日檢查**
   - 查看系統日誌
   - 檢查 API 配額狀態
   - 監控用戶活動

2. **每週檢查**
   - 清理舊日誌文件
   - 備份資料庫
   - 更新系統統計

3. **每月檢查**
   - 檢查 API 使用量
   - 評估系統效能
   - 更新依賴套件

## 🔍 故障排除

### 常見問題

#### 1. LLM API 配額用完
**症狀**: 出現 429 錯誤
**解決方案**:
- 等待配額重置（通常24小時）
- 升級到付費版本
- 檢查 API 金鑰設定

#### 2. LineBot Webhook 錯誤
**症狀**: 無法接收用戶訊息
**解決方案**:
- 檢查 Webhook URL 設定
- 確認 ngrok 連接正常
- 驗證 Channel Secret

#### 3. 資料庫錯誤
**症狀**: 無法儲存食譜記錄
**解決方案**:
- 檢查資料庫文件權限
- 確認 SQLite 版本
- 重建資料庫（如需要）

### 錯誤代碼說明
- `429`: API 配額用完
- `401`: API 金鑰無效
- `403`: 權限不足
- `500`: 內部伺服器錯誤

## 📈 效能優化

### 1. LLM 調用優化
- 使用快取機制
- 批量處理請求
- 優化提示詞長度

### 2. 資料庫優化
- 定期清理舊記錄
- 建立索引
- 使用連接池

### 3. 記憶體管理
- 監控記憶體使用
- 定期重啟服務
- 清理暫存文件

## 🔄 升級指南

### 1. 備份重要資料
```bash
# 備份資料庫
cp database/recipes.db database/recipes_backup_$(date +%Y%m%d).db

# 備份設定
cp .env .env_backup_$(date +%Y%m%d)
```

### 2. 更新程式碼
```bash
# 拉取最新程式碼
git pull origin main

# 更新依賴
pip install -r requirements.txt --upgrade
```

### 3. 測試新功能
```bash
# 運行測試
python test_llm.py

# 檢查健康狀態
curl http://localhost:5000/health
```

## 📞 支援與聯絡

### 技術支援
- 查看日誌文件: `momshero_llm.log`
- 系統狀態: `system_stats.json`
- 健康檢查: `/health` 端點

### 聯絡資訊
- 專案維護者: [您的聯絡方式]
- 技術文件: [專案 Wiki]
- 問題回報: [GitHub Issues]

## 📝 更新日誌

### v1.0.0 (2024-01-XX)
- 初始版本發布
- 支援多輪對話
- LLM 整合
- 基本食譜推薦功能

### 未來規劃
- [ ] 離線食譜資料庫
- [ ] 用戶偏好學習
- [ ] 多語言支援
- [ ] 進階分析功能 