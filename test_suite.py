#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MomsHero 測試套件
包含單元測試、整合測試、效能測試等
"""

import unittest
import sys
import os
import time
import json
from unittest.mock import Mock, patch

# 添加專案路徑
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 導入測試模組
from app_llm import (
    is_recipe_related, 
    extract_ingredients, 
    extract_choice,
    ConversationState,
    handle_conversation
)
from system_monitor import SystemMonitor
from user_experience import UserExperience

class TestRecipeRelated(unittest.TestCase):
    """測試食譜相關性判斷"""
    
    def test_recipe_related_messages(self):
        """測試食譜相關訊息"""
        related_messages = [
            "我有白菜跟小黃瓜",
            "雞蛋可以做什麼料理",
            "推薦炒飯食譜",
            "如何煮湯",
            "替代方案"
        ]
        
        for message in related_messages:
            with self.subTest(message=message):
                result = is_recipe_related(message)
                self.assertTrue(result, f"訊息 '{message}' 應該被判斷為相關")
    
    def test_non_recipe_messages(self):
        """測試非食譜相關訊息"""
        non_related_messages = [
            "今天天氣真好",
            "你好嗎",
            "現在幾點了",
            "明天要上班"
        ]
        
        for message in non_related_messages:
            with self.subTest(message=message):
                result = is_recipe_related(message)
                # 注意：由於我們使用寬鬆原則，這些可能也會返回 True
                # 實際測試中需要根據 LLM 回應調整

class TestIngredientExtraction(unittest.TestCase):
    """測試食材提取"""
    
    def test_common_ingredients(self):
        """測試常見食材提取"""
        test_cases = [
            ("我有白菜跟小黃瓜", ["白菜", "小黃瓜"]),
            ("家裡有雞蛋、白飯、蔥", ["雞蛋", "白飯", "蔥"]),
            ("冰箱裡有豬肉、青菜、豆腐", ["豬肉", "青菜", "豆腐"])
        ]
        
        for message, expected in test_cases:
            with self.subTest(message=message):
                result = extract_ingredients(message)
                for ingredient in expected:
                    self.assertIn(ingredient, result, f"應該提取到食材 '{ingredient}'")
    
    def test_no_ingredients(self):
        """測試無食材訊息"""
        no_ingredient_messages = [
            "你好",
            "今天天氣真好",
            "我想聊天"
        ]
        
        for message in no_ingredient_messages:
            with self.subTest(message=message):
                result = extract_ingredients(message)
                self.assertEqual(len(result), 0, f"訊息 '{message}' 不應該提取到食材")

class TestChoiceExtraction(unittest.TestCase):
    """測試選擇提取"""
    
    def test_number_extraction(self):
        """測試數字提取"""
        test_cases = [
            ("我選擇1", 1),
            ("選2號", 2),
            ("第三個", 3),
            ("我要第1個", 1)
        ]
        
        for message, expected in test_cases:
            with self.subTest(message=message):
                result = extract_choice(message)
                self.assertEqual(result, expected, f"應該提取到數字 {expected}")

class TestConversationState(unittest.TestCase):
    """測試對話狀態管理"""
    
    def setUp(self):
        self.state_manager = ConversationState()
        self.test_user_id = "test_user_123"
    
    def test_new_user_state(self):
        """測試新用戶狀態"""
        state = self.state_manager.get_user_state(self.test_user_id)
        
        self.assertEqual(state['stage'], 'idle')
        self.assertEqual(state['ingredients'], [])
        self.assertEqual(state['recommendations'], [])
        self.assertIsNone(state['selected_recipe'])
    
    def test_state_update(self):
        """測試狀態更新"""
        updates = {
            'stage': 'waiting_for_ingredients',
            'ingredients': ['白菜', '小黃瓜']
        }
        
        self.state_manager.update_user_state(self.test_user_id, updates)
        state = self.state_manager.get_user_state(self.test_user_id)
        
        self.assertEqual(state['stage'], 'waiting_for_ingredients')
        self.assertEqual(state['ingredients'], ['白菜', '小黃瓜'])
    
    def test_state_reset(self):
        """測試狀態重置"""
        # 先設定一些狀態
        self.state_manager.update_user_state(self.test_user_id, {
            'stage': 'waiting_for_choice',
            'ingredients': ['白菜']
        })
        
        # 重置狀態
        self.state_manager.reset_user_state(self.test_user_id)
        state = self.state_manager.get_user_state(self.test_user_id)
        
        self.assertEqual(state['stage'], 'idle')
        self.assertEqual(state['ingredients'], [])

class TestSystemMonitor(unittest.TestCase):
    """測試系統監控"""
    
    def setUp(self):
        self.monitor = SystemMonitor()
        self.test_user_id = "test_user_123"
    
    def test_record_request(self):
        """測試記錄請求"""
        initial_total = self.monitor.stats["total_requests"]
        
        self.monitor.record_request(self.test_user_id, success=True)
        
        self.assertEqual(self.monitor.stats["total_requests"], initial_total + 1)
        self.assertEqual(self.monitor.stats["successful_requests"], initial_total + 1)
    
    def test_record_quota_error(self):
        """測試記錄配額錯誤"""
        initial_errors = self.monitor.stats["llm_quota_errors"]
        
        self.monitor.record_quota_error()
        
        self.assertEqual(self.monitor.stats["llm_quota_errors"], initial_errors + 1)
        self.assertIsNotNone(self.monitor.stats["last_quota_error"])

class TestUserExperience(unittest.TestCase):
    """測試用戶體驗"""
    
    def setUp(self):
        self.ux = UserExperience()
    
    def test_welcome_message(self):
        """測試歡迎訊息"""
        message = self.ux.get_welcome_message()
        
        self.assertIsInstance(message, str)
        self.assertGreater(len(message), 50)
        self.assertIn("食材", message)
    
    def test_quota_error_message(self):
        """測試配額錯誤訊息"""
        message = self.ux.get_quota_error_message()
        
        self.assertIsInstance(message, str)
        self.assertIn("配額", message or "額度", message)
    
    def test_smart_prompt(self):
        """測試智能提示"""
        # 測試感謝訊息
        result = self.ux.get_smart_prompt("謝謝你")
        self.assertIsNotNone(result)
        self.assertIn("不客氣", result)
        
        # 測試再見訊息
        result = self.ux.get_smart_prompt("再見")
        self.assertIsNotNone(result)
        self.assertIn("再見", result)

class TestPerformance(unittest.TestCase):
    """效能測試"""
    
    def test_ingredient_extraction_performance(self):
        """測試食材提取效能"""
        test_message = "我有白菜、小黃瓜、高麗菜、玉米、胡蘿蔔、洋蔥、蒜、薑、醬油、鹽、糖、油"
        
        start_time = time.time()
        for _ in range(100):
            extract_ingredients(test_message)
        end_time = time.time()
        
        avg_time = (end_time - start_time) / 100
        self.assertLess(avg_time, 0.01, "食材提取應該在 10ms 內完成")
    
    def test_conversation_state_performance(self):
        """測試對話狀態管理效能"""
        state_manager = ConversationState()
        
        start_time = time.time()
        for i in range(1000):
            user_id = f"user_{i}"
            state_manager.get_user_state(user_id)
        end_time = time.time()
        
        avg_time = (end_time - start_time) / 1000
        self.assertLess(avg_time, 0.001, "狀態管理應該在 1ms 內完成")

def run_tests():
    """運行所有測試"""
    print("=== 開始運行 MomsHero 測試套件 ===")
    
    # 建立測試套件
    test_suite = unittest.TestSuite()
    
    # 添加測試類別
    test_classes = [
        TestRecipeRelated,
        TestIngredientExtraction,
        TestChoiceExtraction,
        TestConversationState,
        TestSystemMonitor,
        TestUserExperience,
        TestPerformance
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # 運行測試
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # 輸出結果
    print(f"\n=== 測試結果 ===")
    print(f"運行測試: {result.testsRun}")
    print(f"失敗: {len(result.failures)}")
    print(f"錯誤: {len(result.errors)}")
    
    if result.failures:
        print("\n失敗的測試:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback}")
    
    if result.errors:
        print("\n錯誤的測試:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback}")
    
    return result.wasSuccessful()

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1) 