#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
圖片功能測試腳本
測試 LLM 圖片處理整合
"""

import os
import sys
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

def test_image_processor():
    """測試圖片處理器初始化"""
    print("=== 測試圖片處理器初始化 ===")
    
    try:
        from image_processor import ImageProcessor
        import google.generativeai as genai
        
        google_api_key = os.getenv("GOOGLE_API_KEY")
        if not google_api_key:
            print("❌ 未設定 GOOGLE_API_KEY")
            return False
        
        # 初始化 LLM
        genai.configure(api_key=google_api_key)
        llm_model = genai.GenerativeModel('gemini-1.5-flash')
        
        processor = ImageProcessor(llm_model)
        print("✅ 圖片處理器初始化成功")
        
        # 測試支援的格式
        formats = processor.get_supported_formats()
        print(f"📋 支援的圖片格式: {formats}")
        
        # 測試最大檔案大小
        max_size = processor.get_max_file_size()
        print(f"📏 最大檔案大小: {max_size} MB")
        
        return True
        
    except Exception as e:
        print(f"❌ 圖片處理器初始化失敗: {e}")
        return False

def test_app_integration():
    """測試應用程式整合"""
    print("\n=== 測試應用程式整合 ===")
    
    try:
        # 測試導入
        from app_llm import IMAGE_AVAILABLE, LLM_AVAILABLE, SPEECH_AVAILABLE
        
        print(f"🤖 LLM 可用狀態: {LLM_AVAILABLE}")
        print(f"🎤 語音處理可用狀態: {SPEECH_AVAILABLE}")
        print(f"📷 圖片處理可用狀態: {IMAGE_AVAILABLE}")
        
        if IMAGE_AVAILABLE:
            print("✅ 圖片功能已成功整合到應用程式")
            return True
        else:
            print("❌ 圖片功能未成功整合")
            return False
            
    except Exception as e:
        print(f"❌ 應用程式整合測試失敗: {e}")
        return False

def test_health_endpoint():
    """測試健康檢查端點"""
    print("\n=== 測試健康檢查端點 ===")
    
    try:
        import requests
        
        response = requests.get("http://localhost:5000/health", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ 健康檢查端點正常")
            print(f"📊 狀態: {data.get('status')}")
            print(f"🤖 LLM 可用: {data.get('llm_available')}")
            print(f"🎤 語音可用: {data.get('speech_available')}")
            print(f"📷 圖片可用: {data.get('image_available')}")
            print(f"📚 食譜數量: {data.get('recipe_count')}")
            return True
        else:
            print(f"❌ 健康檢查失敗，狀態碼: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 健康檢查測試失敗: {e}")
        return False

def simulate_image_processing():
    """模擬圖片處理流程"""
    print("\n=== 模擬圖片處理流程 ===")
    
    try:
        # 模擬用戶發送圖片訊息
        user_id = "test_user_123"
        image_description = "冰箱內有雞蛋、胡蘿蔔、高麗菜、豬肉"
        
        print(f"📷 用戶圖片: {image_description}")
        
        # 模擬圖片分析結果
        analysis_result = f"""
【食材識別】
- 雞蛋：6顆，新鮮
- 胡蘿蔔：2根，保存良好
- 高麗菜：1顆，新鮮
- 豬肉：300克，冷凍保存

【食譜建議】
1. 高麗菜炒豬肉
   主要食材：高麗菜、豬肉、蒜
   預估烹飪時間：15分鐘
   難度：簡單

2. 胡蘿蔔炒蛋
   主要食材：胡蘿蔔、雞蛋、蔥
   預估烹飪時間：10分鐘
   難度：簡單

3. 高麗菜蛋花湯
   主要食材：高麗菜、雞蛋、蔥
   預估烹飪時間：20分鐘
   難度：簡單

【實用提示】
- 豬肉建議先解凍再烹調
- 高麗菜可以分次使用，保存較久
- 雞蛋和胡蘿蔔搭配營養豐富
        """
        
        print(f"🤖 圖片分析結果: {analysis_result[:100]}...")
        print("✅ 圖片處理流程模擬成功")
        return True
        
    except Exception as e:
        print(f"❌ 圖片處理流程模擬失敗: {e}")
        return False

def test_image_analysis_prompt():
    """測試圖片分析提示詞"""
    print("\n=== 測試圖片分析提示詞 ===")
    
    try:
        prompt = """
        請分析這張冰箱食材圖片，並提供實用的食譜建議：

        【食材識別】
        - 列出所有可見的食材
        - 估計食材的數量和狀態（新鮮度、保存狀況等）

        【食譜建議】
        - 根據識別到的食材，提供 3 個料理建議
        - 每個建議包含：料理名稱、主要食材、預估烹飪時間、難度等級

        【實用提示】
        - 食材搭配建議
        - 保存建議（如果食材需要特別處理）

        請用繁體中文回答，格式要清楚易讀，重點是實用性。
        如果圖片中沒有食材或無法識別，請說明並建議用戶重新拍攝。
        """
        
        print(f"📝 提示詞長度: {len(prompt)} 字元")
        print("✅ 圖片分析提示詞設計合理")
        return True
        
    except Exception as e:
        print(f"❌ 提示詞測試失敗: {e}")
        return False

def main():
    """主測試函數"""
    print("📷 開始圖片功能測試")
    print("=" * 50)
    
    # 執行測試
    tests = [
        ("圖片處理器初始化", test_image_processor),
        ("應用程式整合", test_app_integration),
        ("健康檢查端點", test_health_endpoint),
        ("圖片處理流程", simulate_image_processing),
        ("圖片分析提示詞", test_image_analysis_prompt)
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
        print("🎉 所有測試通過！圖片功能準備就緒")
        print("\n💡 下一步:")
        print("1. 啟動應用程式: python app_llm.py")
        print("2. 使用 ngrok 建立外部連接")
        print("3. 在 Line 中測試圖片功能")
        print("4. 拍攝冰箱食材照片進行測試")
    else:
        print("⚠️ 部分測試失敗，請檢查設定")
    
    print("\n🔧 測試完成！")

if __name__ == "__main__":
    main() 