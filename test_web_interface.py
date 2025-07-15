#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試 MomsHero 網頁介面功能
"""

import requests
import json
import time

def test_web_interface():
    """測試網頁介面功能"""
    base_url = "http://localhost:5000"
    
    print("=== 測試 MomsHero 網頁介面 ===")
    
    # 測試健康檢查
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 健康檢查通過: {data}")
        else:
            print(f"❌ 健康檢查失敗: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ 無法連接到伺服器: {e}")
        return
    
    # 測試多輪對話
    test_cases = [
        {
            "user_id": "test_user_1",
            "message": "我有雞蛋、白飯、蔥",
            "description": "提供食材"
        },
        {
            "user_id": "test_user_1", 
            "message": "1",
            "description": "選擇第一個推薦"
        },
        {
            "user_id": "test_user_1",
            "message": "我沒有醬油",
            "description": "詢問替代方案"
        },
        {
            "user_id": "test_user_2",
            "message": "家裡有豬肉、青菜、豆腐",
            "description": "另一個用戶提供食材"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n--- 測試 {i}: {test_case['description']} ---")
        
        try:
            response = requests.post(
                f"{base_url}/test_conversation",
                json={
                    "user_id": test_case["user_id"],
                    "message": test_case["message"]
                },
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ 回應: {data['response'][:100]}...")
                print(f"   狀態: {data['current_stage']}")
                print(f"   食材: {data['ingredients']}")
                print(f"   推薦數量: {data['recommendations_count']}")
            else:
                print(f"❌ 請求失敗: {response.status_code}")
                print(f"   錯誤: {response.text}")
                
        except Exception as e:
            print(f"❌ 測試失敗: {e}")
        
        time.sleep(1)  # 避免請求過快
    
    print("\n=== 測試完成 ===")
    print("💡 提示：")
    print("1. 用瀏覽器打開 http://localhost:5000/test_conversation 可以看到互動式測試介面")
    print("2. 在網頁中可以直接輸入訊息測試多輪對話")
    print("3. 點擊範例訊息可以快速測試不同功能")

if __name__ == "__main__":
    test_web_interface() 