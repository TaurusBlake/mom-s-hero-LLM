# 📱 MomsHero LLM UI 技術指南

本文檔包含系統的技術架構、多媒體功能使用指南和實現原理。

## 📋 目錄
- [系統架構流程](#系統架構流程)
- [圖片識別功能](#圖片識別功能)
- [語音轉文字功能](#語音轉文字功能)
- [技術實現細節](#技術實現細節)

---

## 🔄 系統架構流程

### 完整使用流程圖

```mermaid
graph TD
    A[1. 使用者在 Line Bot 輸入] --> B{判斷輸入類型};
    B -->|圖片| C[使用 Gemini API 判斷食材];
    B -->|語音| D[呼叫 Azure Speech Service 將語音轉文字];
    B -->|文字| E[直接使用文字];

    C --> F[2. 傳入 Gemini API 生成三個食譜];
    D --> E;
    E --> F;

    F --> G["以卡片形式呈現三個食譜<br>顯示按鈕"];
    G --> H{"使用者點擊按鈕"};
    H -->|查看詳細食譜| I[3. 顯示詳細食譜 (暫存為 Recipe_X)];
    H -->|重新開始| A;

    I --> J{"使用者點擊按鈕"};
    J -->|我有缺少食材| K[4. 使用者輸入缺少的食材];
    J -->|重新開始| A;

    K --> L{判斷輸入類型};
    L -->|語音| M[呼叫 Azure Speech Service 將語音轉文字];
    L -->|文字| N[直接使用文字];

    M --> N;
    N --> O[5. 傳入 Gemini API 尋找替代方案 (暫存為 Substitute_Y)];
    O --> P["顯示替代方案<br>詢問是否還有缺少"];
    P --> Q{"使用者操作"};
    Q -->|繼續輸入缺少內容| K;
    Q -->|完成替代方案| R[6. 整合 Recipe_X 與 Substitute_Y];
    Q -->|重新開始| A;

    R --> S[7. 儲存完整食譜到資料庫];
    S --> T[8. 回傳最終建議給使用者];
    T --> A;
```

### 🎯 主要處理階段

1. **輸入處理**：支援文字、語音、圖片三種輸入方式
2. **內容分析**：使用 AI 技術解析用戶需求
3. **智能推薦**：基於 LLM 生成 3 道料理建議
4. **互動回應**：輪播卡片 + 快速回覆按鈕
5. **深度服務**：詳細食譜、替代方案、資料儲存

---

## 📷 圖片識別功能

### 功能概述

MomsHero 支援圖片識別功能！用戶可以直接拍攝冰箱食材照片，系統會自動識別食材並提供食譜建議。

### 🎯 功能特色

#### 智能食材識別
- 自動識別冰箱中的各種食材
- 評估食材的新鮮度和保存狀況
- 支援常見的蔬菜、肉類、蛋類等食材

#### 🍳 實用食譜建議
- 根據識別到的食材提供 3 個料理建議
- 每個建議包含：料理名稱、主要食材、烹飪時間、難度等級
- 提供食材搭配和保存建議

#### 📱 簡單易用
- 直接在 LINE 中拍照上傳
- 支援多種圖片格式（JPG、PNG、GIF、BMP、WebP）
- 最大支援 10MB 圖片檔案

### 🔧 使用方法

#### 1. 拍攝食材照片
- 打開冰箱，拍攝食材照片
- 確保光線充足，食材清晰可見
- 建議拍攝角度能清楚看到所有食材

#### 2. 上傳到 LINE Bot
- 在 LINE 中選擇「圖片」功能
- 選擇剛才拍攝的照片
- 發送給 MomsHero Bot

#### 3. 獲得食譜建議
- 系統會自動分析圖片中的食材
- 提供詳細的食材識別結果
- 推薦適合的料理方案

### ⚙️ 技術架構

#### 核心元件
- **圖片處理器** (`image_processor.py`)
  - 使用 Google Gemini Vision 進行圖片分析
  - 智能食材識別和食譜生成
  - 支援多種圖片格式

#### 處理流程
1. 用戶上傳圖片到 LINE Bot
2. 系統下載圖片到暫存目錄
3. 使用 Gemini Vision 分析圖片內容
4. 生成食材識別和食譜建議
5. 回傳結果給用戶
6. 清理暫存檔案

#### 提示詞設計
```
請分析這張冰箱食材圖片，並提供實用的食譜建議：

【食材識別】
- 列出所有可見的食材
- 估計食材的數量和狀態（新鮮度、保存狀況等）

【食譜建議】
- 根據識別到的食材，提供 3 個料理建議
- 每個建議包含：料理名稱、主要食材、預估烹飪時間、難度等級

【實用提示】
- 食材搭配建議
- 保存建議
```

### 📊 效果展示

#### 輸入示例
- 用戶上傳冰箱照片：包含雞蛋、番茄、洋蔥

#### 輸出示例
```
🔍 圖片分析結果：

【識別食材】
✅ 雞蛋 - 6顆，新鮮
✅ 番茄 - 3顆，成熟
✅ 洋蔥 - 1顆，良好

【推薦料理】
[輪播卡片展示]
1. 番茄炒蛋 (15分鐘/簡單)
2. 洋蔥煎蛋 (10分鐘/簡單)  
3. 番茄蛋花湯 (20分鐘/簡單)
```

---

## 🎤 語音轉文字功能

### 功能概述

支援語音訊息處理，用戶可以直接說話描述食材或需求，系統自動轉換為文字並處理。

### 🚀 可行性結論

根據技術研究結果，**語音轉文字功能完全可行**：

- ✅ **高可行性** - LINE Bot 完全支援語音訊息接收
- ✅ **技術成熟** - Azure Speech Service 具備強大轉換能力
- ✅ **整合完善** - 已有大量開發者成功實現類似功能

### 🔄 技術流程

#### 1. 語音訊息接收階段
- **LINE Bot Webhook** 接收語音訊息事件
- 語音訊息類型為 `audio`，包含訊息ID和時長
- 使用 `line_bot_api.get_message_content()` 下載語音檔

#### 2. 音檔處理階段
- **格式轉換**：LINE傳送的語音檔為 **AAC格式** (Android) 或 **M4A格式** (iOS)
- **Azure要求**：支援多種格式，包括 WAV、MP3、M4A
- **無需轉檔**：直接支援 LINE 的 M4A 格式

#### 3. 語音轉文字階段
- 調用 **Azure Speech Service** 進行語音轉文字
- 支援繁體中文識別
- 返回轉換後的文字內容

#### 4. 後續處理階段
- 將轉換的文字當作普通文字訊息處理
- 進入標準的食譜推薦流程
- 儲存對話記錄到資料庫

### ⚙️ 技術實現

#### 核心元件
- **語音處理器** (`speech_processor.py`)
  - Azure Speech Service 整合
  - 音訊格式支援
  - 暫存檔案管理

#### 程式碼範例
```python
# 處理語音訊息
def handle_audio_message(event):
    # 1. 下載語音檔案
    content = blob_api.get_message_content(message_id)
    
    # 2. 儲存到暫存檔案
    temp_file = f"temp_files/{user_id}_audio_{message_id}.m4a"
    with open(temp_file, 'wb') as f:
        f.write(content)
    
    # 3. 語音轉文字
    text = speech_processor.process_line_audio(temp_file)
    
    # 4. 清理暫存檔案
    os.remove(temp_file)
    
    # 5. 當作文字訊息處理
    response = handle_conversation(user_id, text)
    return response
```

#### 設定需求
```bash
# Azure Speech Service 設定
AZURE_SPEECH_KEY=your_azure_speech_key
AZURE_SPEECH_REGION=your_azure_speech_region
```

### 📱 使用體驗

#### 使用流程
1. **用戶**：發送語音訊息「我有雞蛋和番茄，想做什麼菜？」
2. **系統**：自動轉換為文字「我有雞蛋和番茄，想做什麼菜？」
3. **系統**：進入標準推薦流程，提供料理建議
4. **用戶**：收到輪播卡片形式的料理推薦

#### 優勢特色
- **免打字**：直接語音描述需求
- **多輪對話**：支援語音 + 文字混合對話
- **準確識別**：Azure Speech Service 高準確率
- **自然互動**：更符合日常對話習慣

---

## 🛠️ 技術實現細節

### 系統架構
```
app_llm_ui_integrated.py (主程式)
├── speech_processor.py (語音處理)
├── image_processor.py (圖片處理)
├── database/ (資料儲存)
└── prompts/ (AI提示詞)
```

### API 整合
- **Google Gemini 1.5-flash**: 文字生成、圖片分析
- **Azure Speech Service**: 語音轉文字
- **LINE Bot API**: 訊息收發、UI渲染

### 錯誤處理
- **重試機制**: LLM API 失敗時自動重試 3 次
- **降級處理**: API 失敗時提供友好錯誤訊息
- **資源清理**: 自動清理暫存檔案

### 效能優化
- **精簡Prompt**: 減少 LLM 處理時間
- **並發處理**: 支援多用戶同時使用
- **暫存管理**: 定期清理暫存檔案

### 安全性
- **環境變數**: 敏感資訊安全儲存
- **輸入驗證**: 防止惡意輸入
- **檔案清理**: 防止暫存檔案累積

---

## 📞 技術支援

### 相關文檔
- **部署指南**: `docs/DEPLOYMENT_GUIDE.md`
- **專案說明**: `README.md`

### API 文檔
- [Google Gemini API](https://ai.google.dev/gemini)
- [Azure Speech Service](https://docs.microsoft.com/azure/cognitive-services/speech-service/)
- [LINE Bot API](https://developers.line.biz/en/docs/messaging-api/)

### 故障排除
如遇到技術問題，請查看部署指南的故障排除章節，或檢查系統健康狀態：
```bash
curl http://localhost:5000/health
```

---

**MomsHero LLM UI** - 智能多媒體料理助手 🤖✨ 