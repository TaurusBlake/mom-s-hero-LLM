#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試配額錯誤處理
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app_llm import generate_recommendations_with_llm, conversation_state

def test_quota_error_handling():
    """測試配額錯誤處理"""
    print("=== 測試配額錯誤處理 ===")
    
    # 模擬用戶ID
    test_user_id = "test_user_123"
    
    # 測試食材
    test_ingredients = ["白菜", "小黃瓜"]
    
    print(f"測試食材: {test_ingredients}")
    
    # 重置用戶狀態
    conversation_state.reset_user_state(test_user_id)
    
    # 測試推薦生成
    result = generate_recommendations_with_llm(test_user_id, test_ingredients)
    
    print(f"結果: {result}")
    
    # 檢查用戶狀態
    state = conversation_state.get_user_state(test_user_id)
    print(f"用戶狀態: {state}")

if __name__ == "__main__":
    test_quota_error_handling() 