#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
圖片上傳測試腳本
模擬 Line Bot 圖片上傳功能
"""

import os
import requests
import json
from PIL import Image, ImageDraw, ImageFont
import io

def create_test_image():
    """建立測試圖片"""
    print("🎨 建立測試圖片...")
    
    # 建立一個簡單的測試圖片
    width, height = 400, 300
    image = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(image)
    
    # 添加一些文字來模擬食材
    try:
        # 嘗試使用系統字體
        font = ImageFont.truetype("arial.ttf", 20)
    except:
        # 如果沒有找到字體，使用預設字體
        font = ImageFont.load_default()
    
    # 繪製食材文字
    ingredients = [
        "🥚 雞蛋 x6",
        "🥕 胡蘿蔔 x2", 
        "🥬 高麗菜 x1",
        "🥩 豬肉 300g"
    ]
    
    y_position = 50
    for ingredient in ingredients:
        draw.text((50, y_position), ingredient, fill='black', font=font)
        y_position += 40
    
    # 添加標題
    draw.text((50, 20), "冰箱食材測試圖片", fill='blue', font=font)
    
    # 保存圖片
    test_image_path = "test_fridge_image.jpg"
    image.save(test_image_path, "JPEG")
    
    print(f"✅ 測試圖片已建立: {test_image_path}")
    return test_image_path

def test_image_analysis():
    """測試圖片分析功能"""
    print("\n🔍 測試圖片分析功能...")
    
    try:
        from image_processor import ImageProcessor
        import google.generativeai as genai
        
        # 載入環境變數
        from dotenv import load_dotenv
        load_dotenv()
        
        google_api_key = os.getenv("GOOGLE_API_KEY")
        if not google_api_key:
            print("❌ 未設定 GOOGLE_API_KEY")
            return False
        
        # 初始化 LLM
        genai.configure(api_key=google_api_key)
        llm_model = genai.GenerativeModel('gemini-1.5-flash')
        
        # 建立圖片處理器
        processor = ImageProcessor(llm_model)
        
        # 建立測試圖片
        test_image_path = create_test_image()
        
        # 分析圖片
        print("🤖 開始分析圖片...")
        result = processor.analyze_fridge_image(test_image_path)
        
        if result:
            print("✅ 圖片分析成功！")
            print("\n📋 分析結果:")
            print("-" * 50)
            print(result)
            print("-" * 50)
            
            # 提取食材
            ingredients = processor.extract_ingredients_from_analysis(result)
            print(f"\n🥬 識別到的食材: {ingredients}")
            
            return True
        else:
            print("❌ 圖片分析失敗")
            return False
            
    except Exception as e:
        print(f"❌ 圖片分析測試失敗: {e}")
        return False

def test_webhook_simulation():
    """模擬 Webhook 圖片上傳"""
    print("\n🌐 模擬 Webhook 圖片上傳...")
    
    try:
        # 建立測試圖片
        test_image_path = create_test_image()
        
        # 模擬 Line Bot Webhook 事件
        webhook_event = {
            "destination": "test_destination",
            "events": [
                {
                    "type": "message",
                    "message": {
                        "id": "test_message_id",
                        "type": "image",
                        "contentProvider": {
                            "type": "line"
                        }
                    },
                    "timestamp": 1234567890,
                    "source": {
                        "type": "user",
                        "userId": "test_user_123"
                    },
                    "replyToken": "test_reply_token",
                    "mode": "active"
                }
            ]
        }
        
        print("📤 模擬發送 Webhook 事件...")
        print(f"📋 事件內容: {json.dumps(webhook_event, indent=2, ensure_ascii=False)}")
        
        # 這裡可以實際發送 POST 請求到 webhook 端點
        # 但需要先啟動應用程式
        print("💡 注意：實際測試需要啟動應用程式 (python app_llm.py)")
        
        return True
        
    except Exception as e:
        print(f"❌ Webhook 模擬失敗: {e}")
        return False

def main():
    """主測試函數"""
    print("📷 開始圖片上傳測試")
    print("=" * 50)
    
    # 執行測試
    tests = [
        ("圖片分析功能", test_image_analysis),
        ("Webhook 模擬", test_webhook_simulation)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} 測試通過")
            else:
                print(f"❌ {test_name} 測試失敗")
        except Exception as e:
            print(f"❌ {test_name} 測試異常: {e}")
        
        print("-" * 30)
    
    print("\n" + "=" * 50)
    print(f"📊 測試結果: {passed}/{total} 通過")
    
    if passed == total:
        print("🎉 圖片上傳功能測試完成！")
        print("\n💡 下一步:")
        print("1. 啟動應用程式: python app_llm.py")
        print("2. 使用 ngrok 建立外部連接")
        print("3. 在 Line 中實際測試圖片功能")
    else:
        print("⚠️ 部分測試失敗，請檢查設定")
    
    # 清理測試檔案
    try:
        if os.path.exists("test_fridge_image.jpg"):
            os.remove("test_fridge_image.jpg")
            print("🧹 已清理測試圖片")
    except:
        pass
    
    print("\n🔧 測試完成！")

if __name__ == "__main__":
    main() 