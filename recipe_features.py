#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
食譜擴展功能
營養分析、烹調技巧、季節推薦、難度評估等
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging

class RecipeFeatures:
    def __init__(self):
        self.nutrition_data = self._load_nutrition_data()
        self.seasonal_ingredients = self._load_seasonal_data()
        self.cooking_tips = self._load_cooking_tips()
        self.difficulty_factors = self._load_difficulty_factors()
    
    def _load_nutrition_data(self) -> Dict[str, Dict]:
        """載入營養資料"""
        return {
            "白菜": {"calories": 12, "protein": 1.2, "carbs": 2.2, "fiber": 1.0, "vitamin_c": 27},
            "小黃瓜": {"calories": 16, "protein": 0.7, "carbs": 3.6, "fiber": 0.5, "vitamin_c": 2.8},
            "雞蛋": {"calories": 155, "protein": 12.6, "carbs": 1.1, "fiber": 0, "vitamin_d": 87},
            "豬肉": {"calories": 242, "protein": 27, "carbs": 0, "fiber": 0, "iron": 1.0},
            "豆腐": {"calories": 76, "protein": 8.1, "carbs": 1.9, "fiber": 0.3, "calcium": 350},
            "高麗菜": {"calories": 25, "protein": 1.3, "carbs": 5.8, "fiber": 2.5, "vitamin_c": 36},
            "玉米": {"calories": 86, "protein": 3.2, "carbs": 19, "fiber": 2.7, "vitamin_b6": 0.1}
        }
    
    def _load_seasonal_data(self) -> Dict[str, List[str]]:
        """載入季節性食材資料"""
        return {
            "春季": ["春筍", "韭菜", "菠菜", "豌豆", "草莓"],
            "夏季": ["小黃瓜", "茄子", "苦瓜", "冬瓜", "西瓜"],
            "秋季": ["南瓜", "芋頭", "栗子", "柿子", "柚子"],
            "冬季": ["白菜", "高麗菜", "蘿蔔", "茼蒿", "橘子"]
        }
    
    def _load_cooking_tips(self) -> Dict[str, List[str]]:
        """載入烹調技巧"""
        return {
            "炒": [
                "火候要快，避免食材出水",
                "先爆香蒜末薑絲增加香氣",
                "調味料最後加入避免過鹹"
            ],
            "煮": [
                "水量要適中，避免營養流失",
                "大火煮開後轉小火慢燉",
                "加入薑片去腥提鮮"
            ],
            "蒸": [
                "蒸籠要預熱，避免食材黏底",
                "蒸的時間要控制好，避免過熟",
                "可以加入枸杞增加營養"
            ],
            "炸": [
                "油溫要控制好，避免外焦內生",
                "食材要瀝乾水分，避免油爆",
                "炸完後用廚房紙巾吸油"
            ]
        }
    
    def _load_difficulty_factors(self) -> Dict[str, int]:
        """載入難度評估因素"""
        return {
            "食材準備": {"簡單": 1, "中等": 2, "困難": 3},
            "烹調時間": {"10分鐘內": 1, "10-30分鐘": 2, "30分鐘以上": 3},
            "技巧要求": {"基本": 1, "中等": 2, "進階": 3},
            "調味複雜度": {"簡單": 1, "中等": 2, "複雜": 3}
        }
    
    def analyze_nutrition(self, ingredients: List[str]) -> Dict[str, Any]:
        """分析食材營養價值"""
        total_nutrition = {
            "calories": 0,
            "protein": 0,
            "carbs": 0,
            "fiber": 0,
            "vitamin_c": 0,
            "vitamin_d": 0,
            "iron": 0,
            "calcium": 0
        }
        
        found_ingredients = []
        
        for ingredient in ingredients:
            if ingredient in self.nutrition_data:
                found_ingredients.append(ingredient)
                nutrition = self.nutrition_data[ingredient]
                for key, value in nutrition.items():
                    if key in total_nutrition:
                        total_nutrition[key] += value
        
        # 計算營養評分
        nutrition_score = 0
        if total_nutrition["protein"] > 0:
            nutrition_score += 1
        if total_nutrition["fiber"] > 2:
            nutrition_score += 1
        if total_nutrition["vitamin_c"] > 20:
            nutrition_score += 1
        if total_nutrition["calcium"] > 200:
            nutrition_score += 1
        
        return {
            "ingredients": found_ingredients,
            "nutrition": total_nutrition,
            "score": nutrition_score,
            "health_level": self._get_health_level(nutrition_score)
        }
    
    def _get_health_level(self, score: int) -> str:
        """獲取健康等級"""
        if score >= 4:
            return "非常健康"
        elif score >= 3:
            return "健康"
        elif score >= 2:
            return "一般"
        else:
            return "基礎"
    
    def get_seasonal_recommendations(self, current_month: Optional[int] = None) -> Dict[str, Any]:
        """獲取季節性推薦"""
        if current_month is None:
            current_month = datetime.now().month
        
        season_map = {
            (3, 4, 5): "春季",
            (6, 7, 8): "夏季", 
            (9, 10, 11): "秋季",
            (12, 1, 2): "冬季"
        }
        
        current_season = None
        for months, season in season_map.items():
            if current_month in months:
                current_season = season
                break
        
        if not current_season:
            current_season = "冬季"
        
        seasonal_ingredients = self.seasonal_ingredients.get(current_season, [])
        
        return {
            "current_season": current_season,
            "seasonal_ingredients": seasonal_ingredients,
            "recommendation": f"現在是{current_season}，建議使用當季食材：{', '.join(seasonal_ingredients[:5])}"
        }
    
    def get_cooking_tips(self, cooking_method: str) -> List[str]:
        """獲取烹調技巧"""
        return self.cooking_tips.get(cooking_method, [
            "注意火候控制",
            "調味要適中",
            "食材要新鮮"
        ])
    
    def assess_difficulty(self, recipe_info: Dict[str, Any]) -> Dict[str, Any]:
        """評估料理難度"""
        difficulty_score = 0
        factors = {}
        
        # 評估食材準備難度
        ingredients_count = len(recipe_info.get("ingredients", []))
        if ingredients_count <= 3:
            factors["食材準備"] = "簡單"
            difficulty_score += 1
        elif ingredients_count <= 6:
            factors["食材準備"] = "中等"
            difficulty_score += 2
        else:
            factors["食材準備"] = "困難"
            difficulty_score += 3
        
        # 評估烹調時間
        cooking_time = recipe_info.get("cooking_time", "")
        if "10分鐘" in cooking_time or "5分鐘" in cooking_time:
            factors["烹調時間"] = "10分鐘內"
            difficulty_score += 1
        elif "30分鐘" in cooking_time or "20分鐘" in cooking_time:
            factors["烹調時間"] = "10-30分鐘"
            difficulty_score += 2
        else:
            factors["烹調時間"] = "30分鐘以上"
            difficulty_score += 3
        
        # 評估技巧要求
        if "簡單" in recipe_info.get("difficulty", ""):
            factors["技巧要求"] = "基本"
            difficulty_score += 1
        elif "中等" in recipe_info.get("difficulty", ""):
            factors["技巧要求"] = "中等"
            difficulty_score += 2
        else:
            factors["技巧要求"] = "進階"
            difficulty_score += 3
        
        # 評估調味複雜度
        if "鹽" in str(recipe_info) and "醬油" not in str(recipe_info):
            factors["調味複雜度"] = "簡單"
            difficulty_score += 1
        elif "醬油" in str(recipe_info) and "糖" in str(recipe_info):
            factors["調味複雜度"] = "中等"
            difficulty_score += 2
        else:
            factors["調味複雜度"] = "複雜"
            difficulty_score += 3
        
        # 計算總體難度
        if difficulty_score <= 6:
            overall_difficulty = "簡單"
        elif difficulty_score <= 9:
            overall_difficulty = "中等"
        else:
            overall_difficulty = "困難"
        
        return {
            "difficulty_score": difficulty_score,
            "overall_difficulty": overall_difficulty,
            "factors": factors,
            "suggestions": self._get_difficulty_suggestions(difficulty_score)
        }
    
    def _get_difficulty_suggestions(self, score: int) -> List[str]:
        """獲取難度建議"""
        if score <= 6:
            return [
                "適合初學者",
                "可以輕鬆完成",
                "建議先準備好所有食材"
            ]
        elif score <= 9:
            return [
                "需要一些烹調經驗",
                "建議按照步驟進行",
                "注意火候控制"
            ]
        else:
            return [
                "適合有經驗的廚師",
                "建議先練習基本技巧",
                "可以尋求協助"
            ]
    
    def get_ingredient_substitutions(self, ingredient: str) -> List[str]:
        """獲取食材替代建議"""
        substitutions = {
            "雞蛋": ["豆腐", "亞麻籽", "奇亞籽"],
            "牛奶": ["豆漿", "杏仁奶", "椰奶"],
            "豬肉": ["雞肉", "牛肉", "豆腐"],
            "蒜": ["薑", "洋蔥", "韭菜"],
            "醬油": ["鹽", "味噌", "魚露"],
            "糖": ["蜂蜜", "楓糖漿", "椰糖"]
        }
        
        return substitutions.get(ingredient, [])
    
    def get_recipe_variations(self, base_recipe: str) -> List[str]:
        """獲取料理變化版本"""
        variations = {
            "炒飯": ["蛋炒飯", "蝦仁炒飯", "蔬菜炒飯", "咖哩炒飯"],
            "湯": ["清湯", "濃湯", "酸辣湯", "蔬菜湯"],
            "炒菜": ["清炒", "蒜炒", "薑炒", "辣炒"],
            "蒸蛋": ["原味蒸蛋", "蝦仁蒸蛋", "蔬菜蒸蛋", "香菇蒸蛋"]
        }
        
        for base, vars in variations.items():
            if base in base_recipe:
                return vars
        
        return []
    
    def get_meal_planning_tips(self, ingredients: List[str]) -> Dict[str, Any]:
        """獲取餐點規劃建議"""
        nutrition_analysis = self.analyze_nutrition(ingredients)
        seasonal_info = self.get_seasonal_recommendations()
        
        tips = []
        
        # 營養建議
        if nutrition_analysis["nutrition"]["protein"] < 10:
            tips.append("建議搭配蛋白質豐富的食材")
        
        if nutrition_analysis["nutrition"]["fiber"] < 3:
            tips.append("建議增加蔬菜攝取")
        
        # 季節建議
        seasonal_ingredients = seasonal_info["seasonal_ingredients"]
        missing_seasonal = [ing for ing in seasonal_ingredients if ing not in ingredients]
        if missing_seasonal:
            tips.append(f"可以考慮加入當季食材：{', '.join(missing_seasonal[:3])}")
        
        return {
            "tips": tips,
            "nutrition_analysis": nutrition_analysis,
            "seasonal_info": seasonal_info,
            "meal_suggestions": self._get_meal_suggestions(ingredients)
        }
    
    def _get_meal_suggestions(self, ingredients: List[str]) -> List[str]:
        """獲取餐點建議"""
        suggestions = []
        
        if "雞蛋" in ingredients:
            suggestions.append("早餐：蛋料理 + 蔬菜")
        
        if "豬肉" in ingredients or "雞肉" in ingredients:
            suggestions.append("午餐：肉類主菜 + 湯品")
        
        if "豆腐" in ingredients:
            suggestions.append("晚餐：豆腐料理 + 青菜")
        
        if "高麗菜" in ingredients or "白菜" in ingredients:
            suggestions.append("湯品：蔬菜湯")
        
        return suggestions

# 全域食譜功能實例
recipe_features = RecipeFeatures() 