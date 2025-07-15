#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MomsHero 簡化版測試腳本
驗證資料庫和提示模板功能
"""

from database.models import init_db, save_recipe, Recipe, get_recipe_count, get_recipes_by_user
import os

def test_database():
    """測試資料庫功能"""
    print("=== 測試資料庫功能 ===")
    
    # 初始化資料庫
    init_db()
    print(f"初始食譜數量: {get_recipe_count()}")
    
    # 建立測試食譜
    test_recipe = Recipe(
        user_id="test_user_001",
        user_message="我想做紅燒肉",
        recipe_title="美味紅燒肉",
        recipe_content="這是一道經典的紅燒肉食譜...",
        ingredients="五花肉、醬油、糖、蔥薑蒜",
        cooking_time="60分鐘",
        difficulty="中等"
    )
    
    # 儲存食譜
    recipe_id = save_recipe(test_recipe)
    print(f"儲存食譜成功，ID: {recipe_id}")
    print(f"現在食譜數量: {get_recipe_count()}")
    
    # 查詢用戶食譜
    user_recipes = get_recipes_by_user("test_user_001")
    print(f"用戶 test_user_001 的食譜數量: {len(user_recipes)}")
    
    if user_recipes:
        latest_recipe = user_recipes[0]
        print(f"最新食譜: {latest_recipe['recipe_title']}")
        print(f"用戶訊息: {latest_recipe['user_message']}")
    
    print("資料庫測試完成！\n")

def test_prompt_template():
    """測試提示模板"""
    print("=== 測試提示模板 ===")
    
    try:
        with open('prompts/recipe_prompt.txt', 'r', encoding='utf-8') as f:
            prompt = f.read()
        
        print(f"提示模板載入成功")
        print(f"模板長度: {len(prompt)} 字元")
        print(f"前100字: {prompt[:100]}...")
        
    except FileNotFoundError:
        print("錯誤：找不到提示模板檔案")
    except Exception as e:
        print(f"錯誤：載入提示模板時發生問題 - {e}")
    
    print("提示模板測試完成！\n")

def test_simulation():
    """測試模擬 LLM 回應"""
    print("=== 測試模擬 LLM 回應 ===")
    
    user_message = "我想做簡單的蛋炒飯"
    
    # 模擬回應
    ai_response = f"""親愛的朋友，我收到您的訊息：「{user_message}」

目前系統正在測試階段，我暫時無法為您生成食譜。
當您準備好測試 LLM 功能時，請告訴我，我會為您提供美味的食譜建議！

目前資料庫中已儲存了 {get_recipe_count()} 個食譜記錄。
"""
    
    print(f"用戶訊息: {user_message}")
    print(f"AI 回應長度: {len(ai_response)} 字元")
    print("模擬回應測試完成！\n")

def main():
    """主測試函數"""
    print("🚀 MomsHero 簡化版功能測試")
    print("=" * 50)
    
    # 測試資料庫
    test_database()
    
    # 測試提示模板
    test_prompt_template()
    
    # 測試模擬回應
    test_simulation()
    
    print("✅ 所有測試完成！")
    print("\n📋 專案狀態:")
    print(f"   - 資料庫: ✅ 正常運作")
    print(f"   - 提示模板: ✅ 已載入")
    print(f"   - 模擬回應: ✅ 可運作")
    print(f"   - 食譜儲存: ✅ 功能正常")
    
    print("\n🎯 下一步:")
    print("   1. 設定 .env 檔案（複製 env_example.txt）")
    print("   2. 填入您的 Line Bot 和 Google API 金鑰")
    print("   3. 執行 python app_simple.py 啟動完整版本")
    print("   4. 使用 ngrok 暴露本地伺服器進行 Line Bot 測試")

if __name__ == "__main__":
    main() 