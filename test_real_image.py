#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
真實圖片測試腳本
測試實際的圖片處理流程
"""

import os
import logging
from dotenv import load_dotenv

# 設定詳細日誌
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 載入環境變數
load_dotenv()

def test_with_real_image():
    """使用真實圖片測試"""
    print("=== 使用真實圖片測試 ===")
    
    # 檢查是否有測試圖片
    test_images = [
        "test_real_fridge.jpg",
        "fridge_test.jpg", 
        "ingredients_test.jpg",
        "test_image.jpg"
    ]
    
    found_images = []
    for img in test_images:
        if os.path.exists(img):
            found_images.append(img)
    
    if not found_images:
        print("❌ 未找到測試圖片")
        print("💡 請將您的冰箱照片放在專案目錄中，命名為以下任一檔案：")
        for img in test_images:
            print(f"  - {img}")
        return False
    
    print(f"✅ 找到測試圖片: {found_images}")
    
    # 測試每張圖片
    for img_path in found_images:
        print(f"\n📷 測試圖片: {img_path}")
        
        try:
            from image_processor import ImageProcessor
            import google.generativeai as genai
            
            # 初始化 LLM
            google_api_key = os.getenv("GOOGLE_API_KEY")
            if not google_api_key:
                print("❌ 未設定 GOOGLE_API_KEY")
                return False
            
            genai.configure(api_key=google_api_key)
            llm_model = genai.GenerativeModel('gemini-1.5-flash')
            
            # 建立圖片處理器
            processor = ImageProcessor(llm_model)
            
            # 檢查圖片檔案
            file_size = os.path.getsize(img_path)
            print(f"📏 圖片大小: {file_size} bytes")
            
            if file_size == 0:
                print("❌ 圖片檔案為空")
                continue
            
            # 分析圖片
            print("🤖 開始分析圖片...")
            result = processor.analyze_fridge_image(img_path)
            
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
                
        except Exception as e:
            print(f"❌ 圖片分析異常: {e}")
            logger.exception("詳細錯誤資訊:")
    
    return False

def test_image_formats():
    """測試不同圖片格式"""
    print("\n=== 測試圖片格式支援 ===")
    
    try:
        from image_processor import ImageProcessor
        import google.generativeai as genai
        
        # 初始化
        google_api_key = os.getenv("GOOGLE_API_KEY")
        genai.configure(api_key=google_api_key)
        llm_model = genai.GenerativeModel('gemini-1.5-flash')
        processor = ImageProcessor(llm_model)
        
        # 檢查支援的格式
        formats = processor.get_supported_formats()
        print(f"📋 支援的格式: {formats}")
        
        # 建立測試圖片
        from PIL import Image, ImageDraw
        
        for format_name in ['jpg', 'png', 'webp']:
            print(f"\n🖼️ 測試 {format_name.upper()} 格式...")
            
            # 建立測試圖片
            img = Image.new('RGB', (400, 300), color='lightblue')
            draw = ImageDraw.Draw(img)
            draw.text((50, 50), f"測試圖片 - {format_name}", fill='black')
            
            test_file = f"test_format.{format_name}"
            img.save(test_file, format=format_name.upper())
            
            # 測試分析
            try:
                result = processor.analyze_fridge_image(test_file)
                if result:
                    print(f"✅ {format_name.upper()} 格式支援正常")
                else:
                    print(f"⚠️ {format_name.upper()} 格式分析失敗")
            except Exception as e:
                print(f"❌ {format_name.upper()} 格式異常: {e}")
            
            # 清理
            try:
                os.remove(test_file)
            except:
                pass
        
        return True
        
    except Exception as e:
        print(f"❌ 格式測試失敗: {e}")
        return False

def test_prompt_effectiveness():
    """測試提示詞效果"""
    print("\n=== 測試提示詞效果 ===")
    
    try:
        from image_processor import ImageProcessor
        import google.generativeai as genai
        
        # 初始化
        google_api_key = os.getenv("GOOGLE_API_KEY")
        genai.configure(api_key=google_api_key)
        llm_model = genai.GenerativeModel('gemini-1.5-flash')
        
        # 建立測試圖片
        from PIL import Image, ImageDraw
        
        # 建立一個看起來像食材的圖片
        img = Image.new('RGB', (600, 400), color='white')
        draw = ImageDraw.Draw(img)
        
        # 繪製一些食材
        draw.ellipse([50, 50, 150, 100], fill='orange', outline='black', width=2)
        draw.text((70, 110), "胡蘿蔔", fill='black')
        
        draw.ellipse([200, 50, 300, 100], fill='lightgreen', outline='black', width=2)
        draw.text((220, 110), "青菜", fill='black')
        
        draw.rectangle([350, 50, 450, 100], fill='pink', outline='black', width=2)
        draw.text((370, 110), "豬肉", fill='black')
        
        test_file = "test_ingredients.jpg"
        img.save(test_file, "JPEG", quality=95)
        
        # 測試不同提示詞
        prompts = [
            "請分析這張圖片中的食材",
            "這是冰箱裡的食材，請識別並提供食譜建議",
            "請分析這張冰箱食材圖片，並提供實用的食譜建議：\n\n【食材識別】\n- 列出所有可見的食材\n- 估計食材的數量和狀態\n\n【食譜建議】\n- 根據識別到的食材，提供 3 個料理建議\n- 每個建議包含：料理名稱、主要食材、預估烹飪時間、難度等級\n\n請用繁體中文回答，格式要清楚易讀。"
        ]
        
        for i, prompt in enumerate(prompts, 1):
            print(f"\n🧪 測試提示詞 {i}:")
            print(f"📝 提示詞: {prompt[:50]}...")
            
            try:
                # 直接使用 LLM 測試
                response = llm_model.generate_content([prompt, img])
                if response and response.text:
                    print(f"✅ 回應長度: {len(response.text)} 字元")
                    print(f"📋 回應預覽: {response.text[:100]}...")
                else:
                    print("❌ 無回應")
            except Exception as e:
                print(f"❌ 提示詞測試失敗: {e}")
        
        # 清理
        try:
            os.remove(test_file)
        except:
            pass
        
        return True
        
    except Exception as e:
        print(f"❌ 提示詞測試失敗: {e}")
        return False

def main():
    """主測試函數"""
    print("🔍 開始真實圖片功能測試")
    print("=" * 50)
    
    # 執行測試
    tests = [
        ("真實圖片測試", test_with_real_image),
        ("圖片格式測試", test_image_formats),
        ("提示詞效果測試", test_prompt_effectiveness)
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
        print("\n💡 如果 Line Bot 圖片功能仍有問題，可能是：")
        print("1. Line Bot 配置問題")
        print("2. 網路連接問題")
        print("3. 圖片下載問題")
        print("4. 暫存檔案權限問題")
    else:
        print("⚠️ 部分測試失敗，請檢查設定")
    
    print("\n🔧 測試完成！")

if __name__ == "__main__":
    main() 