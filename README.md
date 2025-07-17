# MomsHero LLM UI - 智能料理助手

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/Flask-2.0+-green.svg)](https://flask.palletsprojects.com/)
[![LineBot](https://img.shields.io/badge/LineBot-v3-orange.svg)](https://developers.line.biz/)
[![Gemini](https://img.shields.io/badge/Gemini-LLM-purple.svg)](https://ai.google.dev/gemini)

一個基於 LINE Bot 和 Google Gemini LLM 的智能料理助手，支援**多輪對話**、**語音處理**、**圖片識別**和**智能食譜推薦**。

## 🌟 功能特色

### 🤖 核心 AI 功能
- **智能推薦**：根據食材自動推薦 3 道適合料理（輪播UI）
- **詳細食譜**：提供完整烹調步驟、食材份量和小技巧
- **替代方案**：當缺少食材時提供替代建議
- **多輪對話**：支援連續對話，記住對話狀態

### 🎤 多媒體支援
- **語音轉文字**：支援語音訊息，自動轉換為文字處理
- **圖片識別**：拍攝冰箱照片，自動識別食材並推薦料理
- **UI 互動**：輪播卡片、快速回覆按鈕等豐富互動體驗

### ⚡ 系統特色
- **智能重試**：LLM API 失敗時自動重試（3次+指數退避）
- **優化提示**：精簡 Prompt 設計，提升回應速度
- **資料持久化**：SQLite 資料庫儲存對話記錄

## 🚀 快速開始

### 環境需求
- Python 3.8+
- LINE Bot 開發者帳號
- Google Gemini API 金鑰
- Azure Speech Service 金鑰（語音功能）

### 安裝步驟

1. **克隆專案**
```bash
git clone https://github.com/your-username/recipes_LLM.git
cd recipes_LLM
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
創建 `.env` 檔案並填入你的 API 金鑰：
```bash
GOOGLE_API_KEY=your_google_api_key
LINE_CHANNEL_ACCESS_TOKEN=your_line_channel_access_token
LINE_CHANNEL_SECRET=your_line_channel_secret
AZURE_SPEECH_KEY=your_azure_speech_key
AZURE_SPEECH_REGION=your_azure_speech_region
```

5. **啟動應用**
```bash
python app_llm_ui_integrated.py
```

6. **設定 LINE Bot Webhook**
   - 使用 ngrok 建立外部連接：`ngrok http 5000`
   - 在 LINE Bot 開發者控制台設定 Webhook URL：`https://your-ngrok-url/callback`

## 📁 專案結構

```
recipes_LLM/
├── 🚀 app_llm_ui_integrated.py    # 主程式 (42KB)
│
├── 🛠️ 核心模組
│   ├── speech_processor.py       # 語音處理 (Azure Speech Service)
│   └── image_processor.py        # 圖片處理 (Gemini Vision)
│
├── 📂 資料與配置
│   ├── database/                 # 資料庫模組
│   │   ├── models.py             # 資料模型
│   │   ├── recipes.db            # SQLite 資料庫
│   │   └── __init__.py
│   ├── prompts/                  # 提示範本
│   │   └── recipe_prompt.txt     # LLM 提示詞
│   └── docs/                     # 完整文檔
│
├── ⚙️ 設定檔案
│   ├── requirements.txt          # Python 依賴
│   ├── .gitignore               # Git 忽略清單
│   └── README.md                # 本檔案
│
└── 🔧 開發環境
    ├── .git/                     # Git 版本控制
    └── .venv/                    # 虛擬環境
```

## 🔧 核心模組說明

### 1. 主程式 (`app_llm_ui_integrated.py`)
- **對話管理**：多輪對話狀態追蹤
- **LLM 整合**：Google Gemini 1.5-flash 智能生成
- **UI 渲染**：LINE 輪播卡片、快速回覆按鈕
- **錯誤處理**：重試機制和完善的異常處理

### 2. 語音處理 (`speech_processor.py`)
- **語音轉文字**：Azure Speech Service 整合
- **音訊格式**：支援 LINE 的 m4a 格式
- **暫存管理**：自動清理暫存音訊檔案

### 3. 圖片處理 (`image_processor.py`)
- **視覺識別**：Google Gemini Vision 分析圖片
- **食材識別**：自動識別冰箱內食材
- **智能推薦**：基於識別結果生成料理建議

## 📊 功能展示

### 🎯 使用流程
1. 用戶發送**文字**、**語音**或**圖片**
2. 系統自動識別內容並提取食材
3. LLM 生成 3 個料理推薦（輪播展示）
4. 用戶點選料理獲得詳細食譜
5. 支援替代方案查詢

### 💬 對話範例
```
用戶：「我有雞蛋和番茄」
系統：[輪播卡片] 番茄炒蛋 | 蛋花湯 | 西式煎蛋

用戶：點擊「番茄炒蛋」
系統：詳細食譜 + [快速回覆] 我食材有缺 | 重新開始

用戶：點擊「我食材有缺」
系統：替代方案建議...
```

## 🧪 健康檢查

檢查系統狀態：
```bash
curl http://localhost:5000/health
```

回應示例：
```json
{
    "status": "healthy",
    "message": "MomsHero LLM UI 整合版運行中",
    "features": {
        "llm_available": true,
        "speech_available": true,
        "image_available": true
    }
}
```

## 📈 效能優化

### ⚡ 速度優化
- **簡化 Prompt**：減少 75% 提示詞長度
- **移除冗餘日誌**：減少磁碟 I/O 操作
- **智能重試**：3次重試 + 指數退避策略

### 🔄 穩定性優化
- **API 重試機制**：處理 Google Gemini 503 錯誤
- **完善錯誤處理**：用戶友好的錯誤訊息
- **資源清理**：自動清理暫存檔案

## 🔒 安全性

- **環境變數**：敏感資訊使用環境變數保護
- **輸入驗證**：用戶輸入安全檢查
- **暫存清理**：自動清理音訊和圖片暫存檔
- **日誌安全**：避免記錄敏感資訊

## 🤝 貢獻指南

1. Fork 專案
2. 建立功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交變更 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 開啟 Pull Request

## 📝 更新日誌

### v2.0.0 (2025-01-17) - 🎉 LLM UI 整合版
- ✅ **統一架構**：單一主程式，極度精簡
- ✅ **UI 整合**：輪播卡片 + 快速回覆按鈕
- ✅ **多媒體支援**：語音 + 圖片處理
- ✅ **效能優化**：重試機制 + 速度提升
- ✅ **架構精簡**：從 50+ 檔案精簡到 8 個核心檔案

### 未來規劃
- [ ] 用戶偏好學習
- [ ] 食譜評分系統
- [ ] 多語言支援
- [ ] 進階營養分析

## 📞 支援與聯絡

- **技術文檔**：查看 `docs/` 目錄
- **部署指南**：`docs/DEPLOYMENT_GUIDE.md`
- **圖片功能**：`docs/IMAGE_GUIDE.md`
- **問題回報**：[GitHub Issues](https://github.com/your-username/recipes_LLM/issues)

## 📄 授權

本專案採用 MIT 授權條款 - 詳見 [LICENSE](LICENSE) 檔案

## 🙏 致謝

- [LINE Bot SDK](https://github.com/line/line-bot-sdk-python)
- [Google Gemini API](https://ai.google.dev/gemini)
- [Azure Speech Service](https://azure.microsoft.com/services/cognitive-services/speech-to-text/)
- [Flask Framework](https://flask.palletsprojects.com/)

---

**MomsHero LLM UI** - 用 AI 讓料理變得簡單有趣！👩‍🍳✨ 