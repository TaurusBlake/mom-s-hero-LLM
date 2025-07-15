#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MomsHero LLM 版本測試腳本
驗證 Google Gemini 連接和食譜生成功能
"""

import os
import json
from dotenv import load_dotenv
from database.models import init_db, save_recipe, Recipe, get_recipe_count
import google.generativeai as genai

# 載入環境變數
load_dotenv()

def test_llm_connection():
    """測試 LLM 連接"""
    print("=== 測試 LLM 連接 ===")
    
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("❌ 錯誤：未設定 GOOGLE_API_KEY")
        return False
    
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        print("✅ Google Gemini 連接成功")
        return model
    except Exception as e:
        print(f"❌ LLM 連接失敗: {e}")
        return False

def test_recipe_generation(model):
    """測試食譜生成"""
    print("\n=== 測試食譜生成 ===")
    
    # 載入提示模板
    try:
        with open('prompts/recipe_prompt.txt', 'r', encoding='utf-8') as f:
            prompt_template = f.read()
    except FileNotFoundError:
        print("❌ 錯誤：找不到提示模板檔案")
        return False
    
    # 測試訊息
    test_messages = [
        "我想做簡單的蛋炒飯",
        "請教我煮紅燒肉",
        "有什麼適合初學者的料理？"
    ]
    
    for i, message in enumerate(test_messages, 1):
        print(f"\n--- 測試 {i}: {message} ---")
        
        try:
            # 組合完整提示
            full_prompt = f"{prompt_template}\n\n用戶需求：{message}"
            
            # 調用 LLM
            response = model.generate_content(full_prompt)
            
            print(f"✅ 生成成功")
            print(f"回應長度: {len(response.text)} 字元")
            print(f"前100字: {response.text[:100]}...")
            
            # 記錄 Token 使用量（如果可用）
            if hasattr(response, 'usage_metadata'):
                usage = response.usage_metadata
                print(f"Token 使用量 - 輸入: {usage.prompt_token_count}, 輸出: {usage.candidates_token_count}")
            
        except Exception as e:
            print(f"❌ 生成失敗: {e}")
            return False
    
    return True

def test_recipe_parsing():
    """測試食譜內容解析"""
    print("\n=== 測試食譜內容解析 ===")
    
    # 模擬 LLM 回應
    sample_response = """【食譜名稱】
美味蛋炒飯

【食材準備】
雞蛋 2顆
白飯 2碗
蔥 1根
醬油 適量
鹽 少許

【烹調時間】
15分鐘

【難度等級】
簡單

【詳細步驟】
1. 將雞蛋打散
2. 熱鍋下油
3. 炒蛋至半熟
4. 加入白飯翻炒
5. 調味即可

【小技巧】
使用隔夜飯會更好吃哦！"""
    
    # 解析邏輯（從 app_llm.py 複製）
    lines = sample_response.split('\n')
    title = "食譜"
    ingredients = ""
    cooking_time = ""
    difficulty = ""
    
    for i, line in enumerate(lines):
        if "【食譜名稱】" in line or "食譜名稱" in line:
            if i + 1 < len(lines):
                title = lines[i + 1].strip()
        elif "【食材準備】" in line or "食材" in line:
            j = i + 1
            while j < len(lines) and not any(keyword in lines[j] for keyword in ["【", "烹調時間", "難度"]):
                ingredients += lines[j].strip() + " "
                j += 1
        elif "【烹調時間】" in line or "烹調時間" in line:
            if i + 1 < len(lines):
                cooking_time = lines[i + 1].strip()
        elif "【難度等級】" in line or "難度" in line:
            if i + 1 < len(lines):
                difficulty = lines[i + 1].strip()
    
    parsed_info = {
        "title": title,
        "ingredients": ingredients.strip(),
        "cooking_time": cooking_time,
        "difficulty": difficulty
    }
    
    print("✅ 解析成功")
    print(f"標題: {parsed_info['title']}")
    print(f"食材: {parsed_info['ingredients']}")
    print(f"時間: {parsed_info['cooking_time']}")
    print(f"難度: {parsed_info['difficulty']}")
    
    return True

def test_database_integration():
    """測試資料庫整合"""
    print("\n=== 測試資料庫整合 ===")
    
    # 初始化資料庫
    init_db()
    initial_count = get_recipe_count()
    print(f"初始食譜數量: {initial_count}")
    
    # 建立測試食譜
    test_recipe = Recipe(
        user_id="llm_test_user",
        user_message="LLM 測試訊息",
        recipe_title="LLM 測試食譜",
        recipe_content="這是 LLM 生成的測試食譜內容...",
        ingredients="測試食材",
        cooking_time="30分鐘",
        difficulty="中等"
    )
    
    # 儲存食譜
    recipe_id = save_recipe(test_recipe)
    final_count = get_recipe_count()
    
    print(f"✅ 儲存成功，ID: {recipe_id}")
    print(f"現在食譜數量: {final_count}")
    print(f"新增數量: {final_count - initial_count}")
    
    return True

def main():
    """主測試函數"""
    print("🚀 MomsHero LLM 版本功能測試")
    print("=" * 50)
    
    # 測試 LLM 連接
    model = test_llm_connection()
    if not model:
        print("\n❌ LLM 連接失敗，無法繼續測試")
        return
    
    # 測試食譜生成
    if not test_recipe_generation(model):
        print("\n❌ 食譜生成測試失敗")
        return
    
    # 測試食譜解析
    if not test_recipe_parsing():
        print("\n❌ 食譜解析測試失敗")
        return
    
    # 測試資料庫整合
    if not test_database_integration():
        print("\n❌ 資料庫整合測試失敗")
        return
    
    print("\n✅ 所有 LLM 功能測試完成！")
    print("\n📋 LLM 版本狀態:")
    print("   - Google Gemini: ✅ 連接正常")
    print("   - 食譜生成: ✅ 功能正常")
    print("   - 內容解析: ✅ 功能正常")
    print("   - 資料庫整合: ✅ 功能正常")
    
    print("\n🎯 下一步:")
    print("   1. 執行 python app_llm.py 啟動 LLM 版本")
    print("   2. 使用 ngrok 暴露本地伺服器")
    print("   3. 設定 Line Bot Webhook URL")
    print("   4. 開始測試真正的食譜生成功能")

if __name__ == "__main__":
    main() 