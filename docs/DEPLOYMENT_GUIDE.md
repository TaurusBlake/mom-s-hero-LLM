# MomsHero LLM UI 部署與維護指南

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
AZURE_SPEECH_KEY=your_azure_speech_key
AZURE_SPEECH_REGION=your_azure_speech_region
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
python app_llm_ui_integrated.py

# 使用 ngrok 進行外部連接
ngrok http 5000
```

### 2. 生產環境部署
```bash
# 使用 Gunicorn (Linux/Mac)
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app_llm_ui_integrated:app

# 使用 Waitress (Windows)
pip install waitress
waitress-serve --host=0.0.0.0 --port=5000 app_llm_ui_integrated:app
```

### 3. Docker 部署
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 5000

CMD ["python", "app_llm_ui_integrated.py"]
```

## 📊 監控與維護

### 系統監控
```bash
# 檢查系統狀態
curl http://localhost:5000/health

# 查看日誌
tail -f momshero_llm_ui.log

# 檢查Python進程
ps aux | grep python
```

### 定期維護任務
1. **每日檢查**
   - 查看系統日誌
   - 檢查 API 配額狀態
   - 監控用戶活動

2. **每週檢查**
   - 清理舊日誌文件
   - 備份資料庫
   - 檢查磁碟空間

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

#### 2. LINE Bot Webhook 錯誤
**症狀**: 無法接收用戶訊息
**解決方案**:
- 檢查 Webhook URL 設定
- 確認 ngrok 連接正常
- 驗證 Channel Secret

#### 3. 語音處理錯誤
**症狀**: 語音訊息無法轉換
**解決方案**:
- 檢查 Azure Speech Service 金鑰
- 確認網路連接正常
- 檢查暫存檔案權限

#### 4. 圖片處理錯誤
**症狀**: 圖片無法識別
**解決方案**:
- 檢查 Google Vision API 配額
- 確認圖片格式支援
- 檢查暫存目錄權限

#### 5. 資料庫錯誤
**症狀**: 無法儲存對話記錄
**解決方案**:
- 檢查資料庫文件權限
- 確認 SQLite 版本
- 重建資料庫（如需要）

### 錯誤代碼說明
- `429`: API 配額用完
- `401`: API 金鑰無效
- `403`: 權限不足
- `503`: 服務暫時不可用
- `500`: 內部伺服器錯誤

## 📈 效能優化

### 1. LLM 調用優化
- 使用重試機制（已內建）
- 簡化提示詞長度
- 監控 API 回應時間

### 2. 資料庫優化
- 定期清理舊記錄
- 建立索引
- 備份重要資料

### 3. 記憶體管理
- 監控記憶體使用
- 定期清理暫存檔案
- 重啟服務釋放記憶體

### 4. 系統資源
```bash
# 監控系統資源
htop  # 或 top
df -h  # 磁碟空間
free -m  # 記憶體使用
```

## 🔄 升級指南

### 1. 備份重要資料
```bash
# 備份資料庫
cp database/recipes.db database/recipes_backup_$(date +%Y%m%d).db

# 備份設定
cp .env .env_backup_$(date +%Y%m%d)

# 備份日誌
cp *.log logs_backup_$(date +%Y%m%d)/
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
# 檢查語法錯誤
python -m py_compile app_llm_ui_integrated.py

# 檢查健康狀態
curl http://localhost:5000/health
```

### 4. 重啟服務
```bash
# 停止現有服務
pkill -f app_llm_ui_integrated.py

# 啟動新版本
python app_llm_ui_integrated.py
```

## 📱 LINE Bot 設定

### Webhook 設定
1. 登入 [LINE Developers Console](https://developers.line.biz/)
2. 選擇你的 Bot
3. 在 "Messaging API" 分頁設定：
   - Webhook URL: `https://your-domain.com/callback`
   - Use webhook: 啟用
   - Auto-reply messages: 停用
   - Greeting messages: 可選

### 測試 Webhook
```bash
# 測試連接
curl -X POST https://your-domain.com/callback
```

## 🔐 安全性檢查

### 1. 環境變數保護
- 絕不將 `.env` 檔案提交到 Git
- 定期更換 API 金鑰
- 使用強密碼

### 2. 系統安全
- 定期更新系統套件
- 設定防火牆規則
- 監控異常訪問

### 3. 日誌安全
- 避免記錄敏感資訊
- 定期清理舊日誌
- 設定日誌輪轉

## 📞 支援與聯絡

### 緊急聯絡
- **系統管理員**: [管理員聯絡方式]
- **技術支援**: [技術支援信箱]

### 監控資源
- **健康檢查**: `/health` 端點
- **系統日誌**: `momshero_llm_ui.log`
- **錯誤日誌**: 查看 Python traceback

### 外部資源
- [LINE Bot 文檔](https://developers.line.biz/en/docs/messaging-api/)
- [Google Gemini API](https://ai.google.dev/gemini)
- [Azure Speech Service](https://docs.microsoft.com/azure/cognitive-services/speech-service/)

## 📝 更新日誌

### v2.0.0 (2025-01-17)
- ✅ 整合 UI 功能（輪播卡片、快速回覆）
- ✅ 新增語音處理功能
- ✅ 新增圖片識別功能
- ✅ 優化 LLM 重試機制
- ✅ 精簡架構，提升穩定性

### 維護計畫
- [ ] 自動化部署腳本
- [ ] 監控儀表板
- [ ] 自動備份機制
- [ ] 效能分析工具 