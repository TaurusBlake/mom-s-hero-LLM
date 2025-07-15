#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MomsHero 多輪對話測試腳本
模擬完整的對話流程
"""

import requests
import json
import time

def test_conversation_flow():
    """測試完整的對話流程"""
    print("🚀 MomsHero 多輪對話測試")
    print("=" * 50)
    
    # 測試用戶 ID
    user_id = "test_user_001"
    
    # 測試對話流程
    test_scenarios = [
        {
            "message": "我有雞蛋和白飯",
            "description": "1. 用戶提供食材"
        },
        {
            "message": "1",
            "description": "2. 用戶選擇第一個推薦"
        },
        {
            "message": "我沒有醬油",
            "description": "3. 用戶詢問替代方案"
        },
        {
            "message": "謝謝",
            "description": "4. 用戶結束對話"
        },
        {
            "message": "重新開始",
            "description": "5. 用戶重新開始"
        },
        {
            "message": "我有豬肉和青菜",
            "description": "6. 新的對話開始"
        }
    ]
    
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\n--- 測試 {i}: {scenario['description']} ---")
        print(f"用戶訊息: {scenario['message']}")
        
        # 發送測試請求
        try:
            response = requests.post(
                "http://localhost:5000/test_conversation",
                json={
                    "user_id": user_id,
                    "message": scenario['message']
                },
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ 回應成功")
                print(f"當前階段: {data['current_stage']}")
                print(f"食材: {data['ingredients']}")
                print(f"推薦數量: {data['recommendations_count']}")
                print(f"回應長度: {len(data['response'])} 字元")
                print(f"回應前100字: {data['response'][:100]}...")
            else:
                print(f"❌ 請求失敗: {response.status_code}")
                
        except Exception as e:
            print(f"❌ 連接錯誤: {e}")
        
        # 等待一下再進行下一個測試
        time.sleep(1)
    
    print("\n✅ 多輪對話測試完成！")

def test_edge_cases():
    """測試邊界情況"""
    print("\n🔍 測試邊界情況")
    print("=" * 30)
    
    edge_cases = [
        {
            "user_id": "edge_user_001",
            "message": "你好",
            "description": "空閒狀態的問候"
        },
        {
            "user_id": "edge_user_002", 
            "message": "我有一些奇怪的食材",
            "description": "未知食材"
        },
        {
            "user_id": "edge_user_003",
            "message": "4",
            "description": "選擇不存在的選項"
        },
        {
            "user_id": "edge_user_004",
            "message": "我想做滿漢全席",
            "description": "複雜需求"
        }
    ]
    
    for case in edge_cases:
        print(f"\n--- {case['description']} ---")
        print(f"用戶訊息: {case['message']}")
        
        try:
            response = requests.post(
                "http://localhost:5000/test_conversation",
                json={
                    "user_id": case['user_id'],
                    "message": case['message']
                },
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ 回應成功")
                print(f"階段: {data['current_stage']}")
                print(f"回應: {data['response'][:80]}...")
            else:
                print(f"❌ 請求失敗: {response.status_code}")
                
        except Exception as e:
            print(f"❌ 連接錯誤: {e}")

def test_health_check():
    """測試健康檢查"""
    print("\n🏥 測試健康檢查")
    print("=" * 20)
    
    try:
        response = requests.get("http://localhost:5000/health")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ 健康檢查成功")
            print(f"狀態: {data['status']}")
            print(f"食譜數量: {data['recipe_count']}")
            print(f"對話用戶數: {data['conversation_users']}")
        else:
            print(f"❌ 健康檢查失敗: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 連接錯誤: {e}")

def main():
    """主測試函數"""
    print("請確保應用程式正在運行：")
    print("  python app_simple.py")
    print()
    
    # 測試健康檢查
    test_health_check()
    
    # 測試完整對話流程
    test_conversation_flow()
    
    # 測試邊界情況
    test_edge_cases()
    
    print("\n🎯 測試完成！")
    print("如果所有測試都通過，多輪對話功能應該可以正常運作。")
    print("您現在可以：")
    print("1. 使用 ngrok 暴露本地伺服器")
    print("2. 設定 Line Bot Webhook")
    print("3. 開始真正的 Line Bot 對話測試")

if __name__ == "__main__":
    main() 