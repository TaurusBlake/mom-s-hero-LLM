<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" class="logo" width="120"/>

# MomsHero 簡化版專案計畫書

## 一、專案概述與願景

**願景**：打造一個溫暖、有同理心的 AI 料理家教，透過 Line Bot 即時互動，為使用者提供個人化、口語化且具關懷的食譜推薦與料理問答服務。

**核心目標**：
- 使用 Line Bot 連接 Google Gemini LLM 直接生成食譜
- 以「資深煮婦／暖男主廚」作為 AI 角色設定
- 儲存每次生成的食譜，累積食譜資料庫
- 未來可擴展為多輪問答與 RAG 功能

## 二、技術架構與工具選型

| 層級 | 工具／技術 | 說明 |
| :-- | :-- | :-- |
| 後端框架 | Flask (Python) | 輕量、易上手，適合快速開發 |
| 即時通訊平台 | Line Bot SDK | 使用 Line Bot API 實現用戶互動 |
| AI 核心 | Google Gemini (1.5-flash) | 直接生成食譜內容 |
| 資料儲存 | SQLite | 輕量級資料庫，儲存生成的食譜 |
| 開發環境 | Windows | 本地開發，未來可部署至 Render/Heroku 雲端平台 |

## 三、專案資料結構

```
MomsHero-Simple/
├── app.py                       # 主程式（Flask + LineBot + Gemini）
├── database/
│   ├── __init__.py
│   ├── models.py                # 資料庫模型定義
│   └── recipes.db               # SQLite 資料庫檔案
├── prompts/
│   └── recipe_prompt.txt        # 食譜生成提示模板
├── templates/                   # HTML 模板（若需網頁展示）
├── .env                         # 密鑰設定（LINE, Google API）
└── requirements.txt             # Python 套件依賴
```

## 四、開發執行藍圖

### 階段一：環境設定與基礎架構

1. 建置 Python 虛擬環境並安裝套件

```bash
pip install flask line-bot-sdk python-dotenv langchain-google-genai sqlite3
```

2. 設定環境變數（LINE Bot Token、Google API Key）
3. 建立 SQLite 資料庫結構，定義食譜儲存模型

### 階段二：核心功能整合

1. 在 `app.py` 初始化：
    - 載入 `.env` 密鑰
    - 連接 SQLite 資料庫
    - 設定 Google Gemini LLM
    - 載入角色提示模板
2. Webhook 路由 `/callback` 處理：
    - 接收用戶訊息 → LLM 生成食譜 → 儲存到資料庫 → 回傳給用戶

### 階段三：測試與優化

1. 本地測試：
    - 使用 ngrok 暴露本地伺服器
    - 測試食譜生成、資料儲存功能
2. 基本優化：
    - 調整提示模板，優化食譜品質
    - 確保資料庫儲存正常運作

### 階段四：未來擴展規劃

1. **多輪問答功能** - 支援上下文對話
2. **LINE Bot 美化** - 改善用戶介面與體驗
3. **RAG 功能整合** - 基於累積的食譜資料建立檢索系統
4. **雲端部署** - 部署至生產環境

## 五、資料庫設計

### 食譜表結構 (recipes)
```sql
CREATE TABLE recipes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,           -- Line 用戶 ID
    user_message TEXT NOT NULL,      -- 用戶原始訊息
    recipe_title TEXT NOT NULL,      -- 食譜標題
    recipe_content TEXT NOT NULL,    -- 完整食譜內容
    ingredients TEXT,                -- 食材清單
    cooking_time TEXT,               -- 烹調時間
    difficulty TEXT,                 -- 難度等級
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 六、開發任務分解

### 立即執行任務
- [ ] 環境設定與套件安裝
- [ ] 資料庫模型建立
- [ ] Line Bot 基礎設定
- [ ] Gemini LLM 整合
- [ ] 食譜生成與儲存功能
- [ ] 本地測試

### 未來優化任務
- [ ] 多輪對話支援
- [ ] LINE Bot 介面美化
- [ ] 食譜檢索功能
- [ ] 用戶偏好學習
- [ ] 雲端部署

## 七、風險與因應

| 風險 | 因應策略 |
|------|----------|
| Gemini API 限制 | 設定合理的請求頻率限制 |
| 資料庫效能 | 定期清理舊資料，建立索引 |
| 提示工程效果 | 持續優化提示模板 |
| 部署複雜度 | 先本地測試，再逐步部署 |

這個簡化版本專注於核心功能，開發速度快，未來可以根據需求逐步擴展功能。

