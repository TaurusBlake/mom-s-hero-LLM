#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
圖片處理模組
使用現有 LLM 處理 Line Bot 圖片訊息
"""

import os
import logging
import tempfile
from typing import Optional
from PIL import Image
import io

class ImageProcessor:
    """圖片處理器"""
    
    def __init__(self, llm_model):
        """
        初始化圖片處理器
        
        Args:
            llm_model: 現有的 LLM 模型實例
        """
        self.llm_model = llm_model
        self.logger = logging.getLogger(__name__)
    
    def analyze_fridge_image(self, image_file: str) -> Optional[str]:
        """
        分析冰箱食材圖片
        
        Args:
            image_file: 圖片檔案路徑
            
        Returns:
            分析結果文字，失敗則返回 None
        """
        try:
            # 載入圖片
            with open(image_file, 'rb') as f:
                image_data = f.read()
            
            # 建立分析提示詞
            prompt = """
            請分析這張冰箱食材圖片，只列出可見的食材名稱，用逗號分隔。

            例如：
            - 雞蛋,白飯,蔥,蒜,薑
            - 豬肉,青菜,豆腐,胡蘿蔔
            - 雞胸肉,甜椒,洋蔥,馬鈴薯

            如果圖片中沒有食材或無法識別，請回傳「無食材」。

            請只回傳食材名稱，不要其他說明文字。
            """
            
            # 使用 LLM 分析圖片
            self.logger.info(f"開始分析圖片: {image_file}")
            
            # 建立圖片物件
            image = Image.open(io.BytesIO(image_data))
            
            # 發送給 LLM 分析
            response = self.llm_model.generate_content([prompt, image])
            
            if response and response.text:
                self.logger.info(f"圖片分析成功，回應長度: {len(response.text)}")
                return response.text
            else:
                self.logger.warning("LLM 圖片分析回應為空")
                return None
                
        except Exception as e:
            self.logger.error(f"圖片分析失敗: {e}")
            return None
    
    def extract_ingredients_from_analysis(self, analysis_text: str) -> list:
        """
        從分析結果中提取食材列表
        
        Args:
            analysis_text: LLM 分析結果
            
        Returns:
            食材列表
        """
        try:
            # 簡單的食材提取邏輯
            ingredients = []
            
            # 常見食材關鍵字
            common_ingredients = [
                "雞蛋", "豬肉", "牛肉", "雞肉", "魚", "蝦", "豆腐", "青菜", "白菜", "高麗菜",
                "胡蘿蔔", "洋蔥", "蒜", "薑", "蔥", "辣椒", "馬鈴薯", "地瓜", "玉米",
                "番茄", "青椒", "茄子", "南瓜", "冬瓜", "絲瓜", "苦瓜", "小黃瓜",
                "香菇", "金針菇", "杏鮑菇", "木耳", "海帶", "紫菜", "豆芽", "韭菜",
                "芹菜", "菠菜", "空心菜", "莧菜", "芥菜", "油菜", "青江菜", "小白菜",
                "蘿蔔", "白蘿蔔", "紅蘿蔔", "牛蒡", "蓮藕", "竹筍", "茭白筍", "蘆筍",
                "花椰菜", "青花菜", "白花菜", "芥藍", "芥菜", "油菜", "青江菜", "小白菜"
            ]
            
            # 在分析文字中尋找食材
            for ingredient in common_ingredients:
                if ingredient in analysis_text:
                    ingredients.append(ingredient)
            
            return list(set(ingredients))  # 去重
            
        except Exception as e:
            self.logger.error(f"食材提取失敗: {e}")
            return []
    
    def get_supported_formats(self) -> list:
        """獲取支援的圖片格式"""
        return ["jpg", "jpeg", "png", "gif", "bmp", "webp"]
    
    def get_max_file_size(self) -> int:
        """獲取最大支援的檔案大小（MB）"""
        return 10  # 10MB

# 全域圖片處理器實例
image_processor = None

def init_image_processor(llm_model):
    """初始化全域圖片處理器"""
    global image_processor
    try:
        image_processor = ImageProcessor(llm_model)
        logging.info("圖片處理器初始化成功")
    except Exception as e:
        logging.error(f"圖片處理器初始化失敗: {e}")
        image_processor = None

def get_image_processor() -> Optional[ImageProcessor]:
    """獲取全域圖片處理器實例"""
    return image_processor 