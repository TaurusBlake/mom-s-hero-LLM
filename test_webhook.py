#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Line Bot Webhook 測試腳本
模擬 Line Bot 發送的 webhook 請求
"""

import requests
import json
import time

def test_webhook_local():
    """測試本地 webhook"""
    print("=== 測試本地 Webhook ===")
    
    # 模擬 Line Bot 的 webhook 資料
    webhook_data = {
        "events": [
            {
                "type": "message",
                "message": {
                    "type": "text",
                    "text": "我想做蛋炒飯"
                },
                "replyToken": "test_reply_token",
                "source": {
                    "userId": "test_user_123",
                    "type": "user"
                }
            }
        ]
    }
    
    # 發送測試請求
    try:
        response = requests.post(
            "http://localhost:5000/callback",
            json=webhook_data,
            headers={
                "Content-Type": "application/json",
                "X-Line-Signature": "test_signature"
            }
        )
        
        print(f"狀態碼: {response.status_code}")
        print(f"回應: {response.text}")
        
        if response.status_code == 200:
            print("✅ Webhook 測試成功！")
        else:
            print("❌ Webhook 測試失敗")
            
    except Exception as e:
        print(f"❌ 連接錯誤: {e}")

def test_health_endpoint():
    """測試健康檢查端點"""
    print("\n=== 測試健康檢查端點 ===")
    
    try:
        response = requests.get("http://localhost:5000/health")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ 健康檢查成功！")
            print(f"狀態: {data.get('status')}")
            print(f"食譜數量: {data.get('recipe_count')}")
            print(f"LLM 狀態: {data.get('llm_available')}")
        else:
            print(f"❌ 健康檢查失敗: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 連接錯誤: {e}")

def main():
    """主測試函數"""
    print("🚀 Line Bot Webhook 測試")
    print("=" * 40)
    
    # 檢查應用程式是否運行
    print("請確保應用程式正在運行：")
    print("  python app_simple.py 或 python app_llm.py")
    print()
    
    # 測試健康檢查
    test_health_endpoint()
    
    # 測試 webhook
    test_webhook_local()
    
    print("\n📋 下一步：")
    print("1. 安裝 ngrok: https://ngrok.com/download")
    print("2. 執行: ngrok http 5000")
    print("3. 複製 ngrok URL")
    print("4. 在 Line Developers Console 設定 Webhook URL")
    print("5. 測試 Line Bot 對話")

if __name__ == "__main__":
    main() 