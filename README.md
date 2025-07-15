# MomsHero LLM - 智能料理助手

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/Flask-2.0+-green.svg)](https://flask.palletsprojects.com/)
[![LineBot](https://img.shields.io/badge/LineBot-v3-orange.svg)](https://developers.line.biz/)
[![Gemini](https://img.shields.io/badge/Gemini-LLM-purple.svg)](https://ai.google.dev/gemini)

一個基於 LineBot 和 Google Gemini LLM 的智能料理助手，支援多輪對話、食材推薦、食譜生成等功能。

## 🌟 功能特色

### 核心功能
- **多輪對話**：支援連續對話，記住用戶狀態和偏好
- **智能推薦**：根據食材自動推薦適合的料理
- **詳細食譜**：提供完整的烹調步驟和技巧
- **替代方案**：當缺少某些食材時提供替代建議

### 進階功能
- **營養分析**：分析食材營養價值和健康程度
- **季節推薦**：根據當季食材提供建議
- **難度評估**：評估料理難度並提供相應建議
- **烹調技巧**：提供各種烹調方法的專業技巧

### 系統特色
- **快取機制**：減少 API 調用，提升回應速度
- **錯誤處理**：完善的錯誤處理和用戶引導
- **系統監控**：詳細的使用統計和系統狀態監控
- **用戶體驗**：智能提示和個性化回應

## 🚀 快速開始

### 環境需求
- Python 3.8+
- LineBot 開發者帳號
- Google Gemini API 金鑰

### 安裝步驟

1. **克隆專案**
```bash
git clone https://github.com/your-username/mom-s-hero-llm.git
cd mom-s-hero-llm
```

2. **建立虛擬環境**
```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux/Mac
source .venv/bin/activate
```

3. **安裝依賴**
```bash
pip install -r requirements.txt
```

4. **設定環境變數**
```bash
# 複製範例檔案
cp env_example.txt .env

# 編輯 .env 檔案，填入您的 API 金鑰
GOOGLE_API_KEY=your_google_api_key
LINE_CHANNEL_ACCESS_TOKEN=your_line_channel_access_token
LINE_CHANNEL_SECRET=your_line_channel_secret
```

5. **啟動應用**
```bash
python app_llm.py
```

6. **設定 LineBot Webhook**
   - 使用 ngrok 建立外部連接：`ngrok http 5000`
   - 在 LineBot 開發者控制台設定 Webhook URL：`https://your-ngrok-url/callback`

## 📁 專案結構

```
mom-s-hero-llm/
├── app_llm.py              # 主應用程式 (LLM 版本)
├── app_simple.py           # 簡化版本 (測試用)
├── cache_system.py         # 快取系統
├── recipe_features.py      # 食譜擴展功能
├── system_monitor.py       # 系統監控
├── user_experience.py      # 用戶體驗工具
├── test_suite.py           # 測試套件
├── database/               # 資料庫模組
│   ├── models.py
│   └── recipes.db
├── prompts/                # 提示詞模板
│   └── recipe_prompt.txt
├── templates/              # 網頁模板
├── requirements.txt        # Python 依賴
├── README.md              # 專案說明
├── DEPLOYMENT_GUIDE.md    # 部署指南
└── .gitignore             # Git 忽略檔案
```

## 🔧 核心模組說明

### 1. 多輪對話系統 (`app_llm.py`)
- 狀態管理：追蹤用戶對話階段
- LLM 整合：使用 Google Gemini 生成回應
- 錯誤處理：配額限制和網路錯誤處理

### 2. 快取系統 (`cache_system.py`)
- 記憶體快取：快速存取常用回應
- 檔案快取：持久化儲存
- TTL 機制：自動清理過期快取

### 3. 食譜功能 (`recipe_features.py`)
- 營養分析：計算營養價值
- 季節推薦：當季食材建議
- 難度評估：料理難度分析

### 4. 系統監控 (`system_monitor.py`)
- 使用統計：API 調用次數、成功率
- 配額監控：追蹤 API 使用量
- 用戶活動：分析用戶行為

## 📊 使用統計

系統提供詳細的使用統計和監控功能：

```bash
# 查看系統狀態
curl http://localhost:5000/health

# 生成系統報告
python -c "from system_monitor import system_monitor; print(system_monitor.generate_report())"
```

## 🧪 測試

運行完整的測試套件：

```bash
python test_suite.py
```

測試包含：
- 單元測試：核心功能驗證
- 整合測試：模組間互動
- 效能測試：回應時間和資源使用

## 📈 效能優化

### 快取策略
- **記憶體快取**：常用回應快速存取
- **檔案快取**：持久化儲存，減少 API 調用
- **智能清理**：自動清理過期快取

### API 優化
- **批量處理**：減少 API 調用次數
- **錯誤重試**：網路錯誤自動重試
- **配額管理**：監控和預警機制

## 🔒 安全性

- **環境變數**：敏感資訊使用環境變數
- **輸入驗證**：用戶輸入安全檢查
- **錯誤處理**：避免敏感資訊洩露
- **日誌管理**：安全的日誌記錄

## 🤝 貢獻指南

1. Fork 專案
2. 建立功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交變更 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 開啟 Pull Request

## 📝 更新日誌

### v1.0.0 (2024-01-XX)
- ✅ 初始版本發布
- ✅ 多輪對話系統
- ✅ LLM 整合
- ✅ 快取機制
- ✅ 系統監控
- ✅ 用戶體驗優化

### 未來規劃
- [ ] 離線食譜資料庫
- [ ] 用戶偏好學習
- [ ] 多語言支援
- [ ] 進階分析功能
- [ ] 社群功能

## 📞 支援與聯絡

- **技術支援**：查看 `DEPLOYMENT_GUIDE.md`
- **問題回報**：[GitHub Issues](https://github.com/your-username/mom-s-hero-llm/issues)
- **功能建議**：[GitHub Discussions](https://github.com/your-username/mom-s-hero-llm/discussions)

## 📄 授權

本專案採用 MIT 授權條款 - 詳見 [LICENSE](LICENSE) 檔案

## 🙏 致謝

- [LineBot SDK](https://github.com/line/line-bot-sdk-python)
- [Google Gemini API](https://ai.google.dev/gemini)
- [Flask Framework](https://flask.palletsprojects.com/)

---

**MomsHero LLM** - 讓料理變得簡單有趣！👩‍🍳 