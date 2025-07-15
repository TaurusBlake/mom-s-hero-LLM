#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
用戶體驗改進工具
智能提示、錯誤恢復、用戶引導等
"""

import random
from datetime import datetime

class UserExperience:
    def __init__(self):
        self.welcome_messages = [
            "歡迎來到 MomsHero！👩‍🍳 我是您的專屬料理助手，請告訴我您有哪些食材，我會為您推薦適合的料理！",
            "嗨！我是 MomsHero 料理助手 🍳 讓我幫您把食材變成美味料理吧！請分享您的食材～",
            "歡迎使用 MomsHero！🥘 我是您的料理小幫手，請告訴我您手邊有什麼食材，我來為您規劃料理！"
        ]
        
        self.ingredient_examples = [
            "例如：雞蛋、白飯、蔥",
            "例如：豬肉、青菜、豆腐", 
            "例如：雞胸肉、胡蘿蔔、洋蔥",
            "例如：鮭魚、秋葵、松露"
        ]
        
        self.quota_error_messages = [
            "抱歉，AI 服務的免費額度已用完。請稍後再試，或考慮升級到付費版本。",
            "目前 AI 服務暫時無法使用（配額已用完）。請稍後再試！",
            "AI 服務暫時休息中（免費額度用完）。請稍後再來找我聊天吧！"
        ]
        
        self.help_messages = [
            "💡 使用提示：\n• 告訴我您的食材，我會推薦料理\n• 選擇料理編號查看詳細食譜\n• 輸入「重新開始」重置對話\n• 輸入「幫助」查看此訊息",
            "📖 使用說明：\n• 分享食材 → 獲得推薦\n• 選擇料理 → 查看食譜\n• 詢問替代 → 獲得建議\n• 重新開始 → 重置對話",
            "🎯 快速開始：\n1. 告訴我您的食材\n2. 從推薦中選擇料理\n3. 查看詳細食譜\n4. 詢問替代方案"
        ]
    
    def get_welcome_message(self):
        """獲取歡迎訊息"""
        message = random.choice(self.welcome_messages)
        examples = random.sample(self.ingredient_examples, 2)
        
        return f"{message}\n\n{examples[0]}\n{examples[1]}"
    
    def get_quota_error_message(self):
        """獲取配額錯誤訊息"""
        return random.choice(self.quota_error_messages)
    
    def get_help_message(self):
        """獲取幫助訊息"""
        return random.choice(self.help_messages)
    
    def get_smart_prompt(self, user_message, conversation_history=None):
        """根據用戶訊息和對話歷史提供智能提示"""
        # 檢測用戶可能的意圖
        if any(word in user_message for word in ['不會', '不懂', '怎麼', '如何']):
            return "需要我為您詳細說明嗎？請告訴我您想了解什麼！"
        
        if any(word in user_message for word in ['謝謝', '感謝', '謝謝你']):
            return "不客氣！很高興能幫到您。如果還有其他問題，隨時告訴我！"
        
        if any(word in user_message for word in ['再見', '掰掰', '拜拜']):
            return "再見！希望今天的料理建議對您有幫助。下次見！👋"
        
        if any(word in user_message for word in ['好吃', '美味', '讚']):
            return "太好了！很高興您喜歡。如果還需要其他料理建議，隨時告訴我！"
        
        return None
    
    def get_retry_suggestion(self, error_type):
        """根據錯誤類型提供重試建議"""
        suggestions = {
            "quota": "建議：\n• 稍後再試（配額可能已重置）\n• 考慮升級到付費版本\n• 使用其他時間測試",
            "network": "建議：\n• 檢查網路連接\n• 稍後再試\n• 如果問題持續，請聯繫支援",
            "general": "建議：\n• 稍後再試\n• 重新輸入您的需求\n• 如果問題持續，請聯繫支援"
        }
        
        return suggestions.get(error_type, suggestions["general"])
    
    def get_conversation_flow_hint(self, stage):
        """根據對話階段提供流程提示"""
        hints = {
            "idle": "💡 提示：告訴我您有哪些食材，我會為您推薦料理！",
            "waiting_for_ingredients": "💡 提示：您可以選擇推薦的料理編號，或提供更多食材",
            "waiting_for_choice": "💡 提示：您可以詢問替代方案，或選擇其他料理",
            "waiting_for_feedback": "💡 提示：您可以詢問更多細節，或開始新的對話"
        }
        
        return hints.get(stage, "")
    
    def format_ingredient_suggestion(self, ingredients):
        """格式化食材建議"""
        if not ingredients:
            return "請告訴我您有哪些食材，我會為您推薦適合的料理！"
        
        suggestion = f"根據您提供的食材：{', '.join(ingredients)}\n\n"
        suggestion += "我為您推薦以下料理：\n"
        
        return suggestion
    
    def get_encouragement_message(self):
        """獲取鼓勵訊息"""
        encouragements = [
            "💪 您做得很棒！繼續探索更多美味料理吧！",
            "🌟 每個大廚都是從簡單的料理開始的，您已經很棒了！",
            "🎉 料理的樂趣就在於嘗試，您正在做很棒的事情！",
            "👏 您的料理熱情讓我印象深刻，繼續加油！"
        ]
        
        return random.choice(encouragements)

# 全域用戶體驗實例
user_experience = UserExperience() 