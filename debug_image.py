#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
圖片功能除錯腳本
診斷圖片處理問題
"""

import os
import logging
import tempfile
from dotenv import load_dotenv

# 設定詳細日誌
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 載入環境變數
load_dotenv()

def test_llm_initialization():
    """測試 LLM 初始化"""
    print("=== 測試 LLM 初始化 ===")
    
    try:
        import google.generativeai as genai
        
        google_api_key = os.getenv("GOOGLE_API_KEY")
        if not google_api_key:
            print("❌ 未設定 GOOGLE_API_KEY")
            return False
        
        print(f"✅ GOOGLE_API_KEY 已設定: {google_api_key[:10]}...")
        
        # 初始化 LLM
        genai.configure(api_key=google_api_key)
        llm_model = genai.GenerativeModel('gemini-1.5-flash')
        
        # 測試簡單文字回應
        response = llm_model.generate_content("請說你好")
        if response and response.text:
            print("✅ LLM 文字回應測試成功")
            return llm_model
        else:
            print("❌ LLM 文字回應測試失敗")
            return False
            
    except Exception as e:
        print(f"❌ LLM 初始化失敗: {e}")
        return False

def test_image_processor():
    """測試圖片處理器"""
    print("\n=== 測試圖片處理器 ===")
    
    try:
        from image_processor import ImageProcessor
        
        llm_model = test_llm_initialization()
        if not llm_model:
            return False
        
        processor = ImageProcessor(llm_model)
        print("✅ 圖片處理器初始化成功")
        
        # 測試支援的格式
        formats = processor.get_supported_formats()
        print(f"📋 支援的圖片格式: {formats}")
        
        return processor
        
    except Exception as e:
        print(f"❌ 圖片處理器測試失敗: {e}")
        return False

def test_real_image_analysis():
    """測試真實圖片分析"""
    print("\n=== 測試真實圖片分析 ===")
    
    try:
        processor = test_image_processor()
        if not processor:
            return False
        
        # 建立一個更真實的測試圖片
        from PIL import Image, ImageDraw, ImageFont
        import io
        
        # 建立一個看起來像食材的圖片
        width, height = 800, 600
        image = Image.new('RGB', (width, height), color='lightblue')
        draw = ImageDraw.Draw(image)
        
        # 繪製一些圓形代表食材
        # 雞蛋
        draw.ellipse([100, 100, 200, 150], fill='white', outline='black', width=2)
        draw.text((120, 160), "雞蛋", fill='black')
        
        # 胡蘿蔔
        draw.ellipse([250, 100, 350, 180], fill='orange', outline='black', width=2)
        draw.text((270, 190), "胡蘿蔔", fill='black')
        
        # 高麗菜
        draw.ellipse([400, 100, 500, 160], fill='lightgreen', outline='black', width=2)
        draw.text((420, 170), "高麗菜", fill='black')
        
        # 豬肉
        draw.rectangle([100, 250, 200, 300], fill='pink', outline='black', width=2)
        draw.text((120, 310), "豬肉", fill='black')
        
        # 保存圖片
        test_image_path = "debug_test_image.jpg"
        image.save(test_image_path, "JPEG", quality=95)
        
        print(f"✅ 測試圖片已建立: {test_image_path}")
        print(f"📏 圖片大小: {os.path.getsize(test_image_path)} bytes")
        
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
        print(f"❌ 真實圖片分析失敗: {e}")
        logger.exception("詳細錯誤資訊:")
        return False

def test_app_integration():
    """測試應用程式整合"""
    print("\n=== 測試應用程式整合 ===")
    
    try:
        # 檢查應用程式是否正在運行
        import requests
        
        response = requests.get("http://localhost:5000/health", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ 應用程式正在運行")
            print(f"📊 狀態: {data.get('status')}")
            print(f"🤖 LLM 可用: {data.get('llm_available')}")
            print(f"🎤 語音可用: {data.get('speech_available')}")
            print(f"📷 圖片可用: {data.get('image_available')}")
            
            if not data.get('image_available'):
                print("❌ 圖片功能在應用程式中不可用")
                return False
            
            return True
        else:
            print(f"❌ 應用程式健康檢查失敗: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 應用程式整合測試失敗: {e}")
        return False

def test_webhook_endpoint():
    """測試 Webhook 端點"""
    print("\n=== 測試 Webhook 端點 ===")
    
    try:
        import requests
        import json
        
        # 模擬圖片訊息事件
        webhook_data = {
            "destination": "test_destination",
            "events": [
                {
                    "type": "message",
                    "message": {
                        "id": "test_message_id",
                        "type": "image"
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
        
        # 發送測試請求（不包含 Line 簽名，預期會失敗）
        response = requests.post(
            "http://localhost:5000/callback",
            json=webhook_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"📤 Webhook 回應狀態碼: {response.status_code}")
        
        # 預期會因為缺少簽名而失敗，這是正常的
        if response.status_code in [400, 500]:
            print("✅ Webhook 端點正常（預期的簽名驗證失敗）")
            print("💡 這是正常的，因為測試請求沒有包含 Line 簽名")
            return True
        else:
            print("❌ Webhook 端點異常")
            return False
            
    except Exception as e:
        print(f"❌ Webhook 測試失敗: {e}")
        return False

def check_temp_directory():
    """檢查暫存目錄"""
    print("\n=== 檢查暫存目錄 ===")
    
    temp_dir = "temp_files"
    
    if os.path.exists(temp_dir):
        print(f"✅ 暫存目錄存在: {temp_dir}")
        
        # 列出暫存檔案
        files = os.listdir(temp_dir)
        print(f"📁 暫存檔案數量: {len(files)}")
        
        if files:
            print("📋 暫存檔案列表:")
            for file in files:
                file_path = os.path.join(temp_dir, file)
                size = os.path.getsize(file_path)
                print(f"  - {file} ({size} bytes)")
        
        return True
    else:
        print(f"❌ 暫存目錄不存在: {temp_dir}")
        print("💡 嘗試建立暫存目錄...")
        
        try:
            os.makedirs(temp_dir, exist_ok=True)
            print("✅ 暫存目錄建立成功")
            return True
        except Exception as e:
            print(f"❌ 建立暫存目錄失敗: {e}")
            return False

def main():
    """主除錯函數"""
    print("🔍 開始圖片功能除錯")
    print("=" * 50)
    
    # 執行測試
    tests = [
        ("LLM 初始化", test_llm_initialization),
        ("圖片處理器", test_image_processor),
        ("真實圖片分析", test_real_image_analysis),
        ("應用程式整合", test_app_integration),
        ("Webhook 端點", test_webhook_endpoint),
        ("暫存目錄檢查", check_temp_directory)
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
    print(f"📊 除錯結果: {passed}/{total} 通過")
    
    if passed == total:
        print("🎉 所有測試通過！圖片功能應該正常")
    else:
        print("⚠️ 發現問題，請檢查上述錯誤訊息")
    
    # 清理測試檔案
    try:
        if os.path.exists("debug_test_image.jpg"):
            os.remove("debug_test_image.jpg")
            print("🧹 已清理測試圖片")
    except:
        pass
    
    print("\n🔧 除錯完成！")

if __name__ == "__main__":
    main() 