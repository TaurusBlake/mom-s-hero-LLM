#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Line 圖片下載測試腳本
模擬 Line Bot 的圖片下載流程
"""

import os
import logging
from dotenv import load_dotenv

# 設定日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 載入環境變數
load_dotenv()

def test_line_api_connection():
    """測試 Line API 連接"""
    print("=== 測試 Line API 連接 ===")
    
    try:
        from linebot.v3.messaging import Configuration, ApiClient, MessagingApi
        
        # 檢查環境變數
        line_channel_access_token = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
        line_channel_secret = os.getenv("LINE_CHANNEL_SECRET")
        
        if not line_channel_access_token:
            print("❌ 未設定 LINE_CHANNEL_ACCESS_TOKEN")
            return False
        
        if not line_channel_secret:
            print("❌ 未設定 LINE_CHANNEL_SECRET")
            return False
        
        print(f"✅ LINE_CHANNEL_ACCESS_TOKEN 已設定: {line_channel_access_token[:10]}...")
        print(f"✅ LINE_CHANNEL_SECRET 已設定: {line_channel_secret[:10]}...")
        
        # 測試 API 連接
        configuration = Configuration(access_token=line_channel_access_token)
        
        with ApiClient(configuration) as api_client:
            line_bot_api = MessagingApi(api_client)
            print("✅ Line Bot API 連接成功")
        
        return True
        
    except Exception as e:
        print(f"❌ Line API 連接失敗: {e}")
        return False

def test_image_download_simulation():
    """模擬圖片下載流程"""
    print("\n=== 模擬圖片下載流程 ===")
    
    try:
        # 建立測試圖片
        from PIL import Image, ImageDraw
        
        # 建立一個看起來像食材的圖片
        img = Image.new('RGB', (800, 600), color='lightblue')
        draw = ImageDraw.Draw(img)
        
        # 繪製一些食材
        draw.ellipse([100, 100, 200, 150], fill='orange', outline='black', width=2)
        draw.text((120, 160), "胡蘿蔔", fill='black')
        
        draw.ellipse([250, 100, 350, 180], fill='lightgreen', outline='black', width=2)
        draw.text((270, 190), "青菜", fill='black')
        
        draw.rectangle([400, 100, 500, 150], fill='pink', outline='black', width=2)
        draw.text((420, 160), "豬肉", fill='black')
        
        # 保存測試圖片
        test_image_path = "simulated_line_image.jpg"
        img.save(test_image_path, "JPEG", quality=95)
        
        print(f"✅ 測試圖片已建立: {test_image_path}")
        print(f"📏 圖片大小: {os.path.getsize(test_image_path)} bytes")
        
        # 模擬 Line 下載流程
        temp_dir = "temp_files"
        os.makedirs(temp_dir, exist_ok=True)
        
        # 模擬用戶 ID 和訊息 ID
        user_id = "test_user_123"
        message_id = "test_message_456"
        
        # 模擬下載到暫存檔案
        temp_file = os.path.join(temp_dir, f"{user_id}_image_{message_id}.jpg")
        
        # 複製圖片到暫存位置
        import shutil
        shutil.copy2(test_image_path, temp_file)
        
        print(f"✅ 圖片已下載到暫存位置: {temp_file}")
        print(f"📏 暫存檔案大小: {os.path.getsize(temp_file)} bytes")
        
        # 測試圖片處理
        from image_processor import ImageProcessor
        import google.generativeai as genai
        
        google_api_key = os.getenv("GOOGLE_API_KEY")
        genai.configure(api_key=google_api_key)
        llm_model = genai.GenerativeModel('gemini-1.5-flash')
        
        processor = ImageProcessor(llm_model)
        
        print("🤖 開始分析暫存圖片...")
        result = processor.analyze_fridge_image(temp_file)
        
        if result:
            print("✅ 暫存圖片分析成功！")
            print("\n📋 分析結果:")
            print("-" * 50)
            print(result)
            print("-" * 50)
        else:
            print("❌ 暫存圖片分析失敗")
        
        # 清理檔案
        try:
            os.remove(test_image_path)
            os.remove(temp_file)
            print("🧹 測試檔案已清理")
        except:
            pass
        
        return True
        
    except Exception as e:
        print(f"❌ 圖片下載模擬失敗: {e}")
        logger.exception("詳細錯誤資訊:")
        return False

def test_app_image_handler():
    """測試應用程式的圖片處理函數"""
    print("\n=== 測試應用程式圖片處理函數 ===")
    
    try:
        # 檢查應用程式是否正在運行
        import requests
        
        response = requests.get("http://localhost:5000/health", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ 應用程式正在運行")
            print(f"📷 圖片功能可用: {data.get('image_available')}")
            
            if data.get('image_available'):
                print("✅ 圖片處理功能已啟用")
                return True
            else:
                print("❌ 圖片處理功能未啟用")
                return False
        else:
            print(f"❌ 應用程式健康檢查失敗: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 應用程式測試失敗: {e}")
        return False

def check_logs():
    """檢查應用程式日誌"""
    print("\n=== 檢查應用程式日誌 ===")
    
    log_file = "momshero_llm.log"
    
    if os.path.exists(log_file):
        print(f"✅ 日誌檔案存在: {log_file}")
        
        # 讀取最後幾行日誌
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                
            if lines:
                print("📋 最近的日誌記錄:")
                for line in lines[-10:]:  # 最後 10 行
                    print(f"  {line.strip()}")
            else:
                print("📋 日誌檔案為空")
                
        except Exception as e:
            print(f"❌ 讀取日誌失敗: {e}")
    else:
        print(f"❌ 日誌檔案不存在: {log_file}")
    
    return True

def main():
    """主測試函數"""
    print("🔍 開始 Line 圖片下載測試")
    print("=" * 50)
    
    # 執行測試
    tests = [
        ("Line API 連接", test_line_api_connection),
        ("圖片下載模擬", test_image_download_simulation),
        ("應用程式圖片處理", test_app_image_handler),
        ("日誌檢查", check_logs)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} 通過")
            else:
                print(f"❌ {test_name} 失敗")
        except Exception as e:
            print(f"❌ {test_name} 異常: {e}")
        
        print("-" * 30)
    
    print("\n" + "=" * 50)
    print(f"📊 測試結果: {passed}/{total} 通過")
    
    if passed == total:
        print("🎉 所有測試通過！")
        print("\n💡 如果 Line Bot 圖片功能仍有問題，請檢查：")
        print("1. Line Bot 的 Webhook URL 設定")
        print("2. 網路連接和防火牆設定")
        print("3. 實際在 Line 中測試圖片功能")
    else:
        print("⚠️ 部分測試失敗，請檢查設定")
    
    print("\n🔧 測試完成！")

if __name__ == "__main__":
    main() 