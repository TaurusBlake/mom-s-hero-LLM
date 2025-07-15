#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
離線食譜資料庫
當LLM不可用時提供基本建議
"""

# 基本食譜資料庫
OFFLINE_RECIPES = {
    "白菜": [
        {
            "name": "清炒白菜",
            "ingredients": ["白菜", "蒜", "鹽", "油"],
            "time": "10分鐘",
            "difficulty": "簡單",
            "steps": [
                "白菜洗淨切段",
                "蒜切碎",
                "熱油爆香蒜末",
                "加入白菜翻炒",
                "加鹽調味即可"
            ]
        },
        {
            "name": "白菜豆腐湯",
            "ingredients": ["白菜", "豆腐", "蔥", "鹽"],
            "time": "15分鐘", 
            "difficulty": "簡單",
            "steps": [
                "白菜洗淨切段",
                "豆腐切塊",
                "水煮開後加入白菜",
                "加入豆腐煮5分鐘",
                "加鹽調味，撒蔥花"
            ]
        }
    ],
    "小黃瓜": [
        {
            "name": "涼拌小黃瓜",
            "ingredients": ["小黃瓜", "蒜", "醋", "糖", "鹽"],
            "time": "5分鐘",
            "difficulty": "簡單", 
            "steps": [
                "小黃瓜切片",
                "蒜切碎",
                "加入醋、糖、鹽調味",
                "拌勻即可食用"
            ]
        },
        {
            "name": "小黃瓜炒蛋",
            "ingredients": ["小黃瓜", "雞蛋", "鹽", "油"],
            "time": "8分鐘",
            "difficulty": "簡單",
            "steps": [
                "小黃瓜切片",
                "雞蛋打散",
                "熱油炒蛋",
                "加入小黃瓜翻炒",
                "加鹽調味"
            ]
        }
    ],
    "高麗菜": [
        {
            "name": "高麗菜炒肉絲",
            "ingredients": ["高麗菜", "豬肉絲", "蒜", "醬油", "鹽"],
            "time": "12分鐘",
            "difficulty": "中等",
            "steps": [
                "高麗菜洗淨切絲",
                "豬肉絲醃製",
                "熱油爆香蒜末",
                "炒肉絲至變色",
                "加入高麗菜翻炒",
                "加醬油、鹽調味"
            ]
        }
    ],
    "玉米": [
        {
            "name": "玉米濃湯",
            "ingredients": ["玉米", "牛奶", "奶油", "鹽"],
            "time": "20分鐘",
            "difficulty": "中等",
            "steps": [
                "玉米剝粒",
                "煮玉米粒至軟",
                "加入牛奶煮開",
                "加入奶油調味",
                "加鹽調味即可"
            ]
        }
    ]
}

def get_offline_recommendations(ingredients):
    """根據食材獲取離線推薦"""
    recommendations = []
    
    for ingredient in ingredients:
        if ingredient in OFFLINE_RECIPES:
            for recipe in OFFLINE_RECIPES[ingredient]:
                recommendations.append(recipe)
    
    # 去重並限制數量
    unique_recipes = []
    seen_names = set()
    
    for recipe in recommendations:
        if recipe["name"] not in seen_names:
            unique_recipes.append(recipe)
            seen_names.add(recipe["name"])
    
    return unique_recipes[:3]  # 最多返回3個

def get_offline_recipe_details(recipe_name):
    """獲取離線食譜詳情"""
    for category in OFFLINE_RECIPES.values():
        for recipe in category:
            if recipe["name"] == recipe_name:
                return recipe
    return None

def format_offline_recommendations(recommendations):
    """格式化離線推薦"""
    if not recommendations:
        return "抱歉，沒有找到適合的離線食譜。"
    
    result = "根據您的食材，我推薦以下料理：\n\n"
    
    for i, recipe in enumerate(recommendations, 1):
        result += f"{i}. {recipe['name']}\n"
        result += f"   主要食材：{', '.join(recipe['ingredients'])}\n"
        result += f"   預估烹飪時間：{recipe['time']}\n"
        result += f"   難度：{recipe['difficulty']}\n\n"
    
    result += "請選擇 1、2 或 3 來查看詳細食譜！"
    return result

def format_offline_recipe_details(recipe):
    """格式化離線食譜詳情"""
    if not recipe:
        return "抱歉，找不到該食譜的詳細資訊。"
    
    result = f"【{recipe['name']}】詳細食譜\n\n"
    result += "【食材準備】\n"
    for ingredient in recipe['ingredients']:
        result += f"- {ingredient}\n"
    
    result += f"\n【烹調時間】\n- {recipe['time']}\n"
    result += f"\n【難度等級】\n- {recipe['difficulty']}\n"
    
    result += "\n【詳細步驟】\n"
    for i, step in enumerate(recipe['steps'], 1):
        result += f"{i}. {step}\n"
    
    result += "\n【小技巧】\n- 注意火候控制，避免過度烹調\n- 調味時可依個人口味調整"
    
    return result 