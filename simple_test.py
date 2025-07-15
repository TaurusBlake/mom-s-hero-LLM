#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
簡單測試
"""

import requests
import time

def test_server():
    print("測試伺服器連接...")
    
    try:
        # 等待伺服器啟動
        time.sleep(2)
        
        # 測試健康檢查
        response = requests.get("http://localhost:5000/health", timeout=5)
        print(f"健康檢查: {response.status_code}")
        if response.status_code == 200:
            print(f"回應: {response.json()}")
        
        # 測試主頁
        response = requests.get("http://localhost:5000/", timeout=5)
        print(f"主頁: {response.status_code}")
        if response.status_code == 200:
            print(f"內容: {response.text[:100]}")
            
    except requests.exceptions.ConnectionError:
        print("❌ 無法連接到伺服器")
    except Exception as e:
        print(f"❌ 錯誤: {e}")

if __name__ == "__main__":
    test_server() 