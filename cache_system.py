#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快取系統
減少LLM API調用，提升回應速度和降低成本
"""

import json
import hashlib
import time
import os
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import logging

class CacheSystem:
    def __init__(self, cache_dir="cache", ttl_hours=24):
        """
        初始化快取系統
        
        Args:
            cache_dir: 快取檔案目錄
            ttl_hours: 快取存活時間（小時）
        """
        self.cache_dir = cache_dir
        self.ttl_seconds = ttl_hours * 3600
        self.memory_cache = {}  # 記憶體快取
        self.memory_cache_ttl = {}  # 記憶體快取TTL
        
        # 建立快取目錄
        os.makedirs(cache_dir, exist_ok=True)
        
        # 快取統計
        self.stats = {
            "hits": 0,
            "misses": 0,
            "saves": 0,
            "expired": 0
        }
    
    def _generate_key(self, prompt: str, function_type: str) -> str:
        """生成快取鍵值"""
        content = f"{function_type}:{prompt}"
        return hashlib.md5(content.encode('utf-8')).hexdigest()
    
    def _get_cache_file_path(self, key: str) -> str:
        """獲取快取檔案路徑"""
        return os.path.join(self.cache_dir, f"{key}.json")
    
    def _is_expired(self, timestamp: float) -> bool:
        """檢查是否過期"""
        return time.time() - timestamp > self.ttl_seconds
    
    def get(self, prompt: str, function_type: str) -> Optional[str]:
        """
        從快取獲取資料
        
        Args:
            prompt: LLM提示詞
            function_type: 函數類型 (recommendations, details, alternatives, etc.)
        
        Returns:
            快取的結果，如果不存在或過期則返回None
        """
        key = self._generate_key(prompt, function_type)
        
        # 先檢查記憶體快取
        if key in self.memory_cache:
            if not self._is_expired(self.memory_cache_ttl[key]):
                self.stats["hits"] += 1
                logging.info(f"記憶體快取命中: {function_type}")
                return self.memory_cache[key]
            else:
                # 清理過期的記憶體快取
                del self.memory_cache[key]
                del self.memory_cache_ttl[key]
                self.stats["expired"] += 1
        
        # 檢查檔案快取
        cache_file = self._get_cache_file_path(key)
        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    cache_data = json.load(f)
                
                if not self._is_expired(cache_data['timestamp']):
                    # 載入到記憶體快取
                    self.memory_cache[key] = cache_data['result']
                    self.memory_cache_ttl[key] = cache_data['timestamp']
                    
                    self.stats["hits"] += 1
                    logging.info(f"檔案快取命中: {function_type}")
                    return cache_data['result']
                else:
                    # 清理過期檔案
                    os.remove(cache_file)
                    self.stats["expired"] += 1
                    logging.info(f"快取過期: {function_type}")
            except Exception as e:
                logging.error(f"讀取快取檔案失敗: {e}")
        
        self.stats["misses"] += 1
        logging.info(f"快取未命中: {function_type}")
        return None
    
    def set(self, prompt: str, function_type: str, result: str) -> None:
        """
        儲存資料到快取
        
        Args:
            prompt: LLM提示詞
            function_type: 函數類型
            result: LLM回應結果
        """
        key = self._generate_key(prompt, function_type)
        timestamp = time.time()
        
        # 儲存到記憶體快取
        self.memory_cache[key] = result
        self.memory_cache_ttl[key] = timestamp
        
        # 儲存到檔案快取
        cache_data = {
            'timestamp': timestamp,
            'function_type': function_type,
            'prompt': prompt,
            'result': result
        }
        
        cache_file = self._get_cache_file_path(key)
        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)
            
            self.stats["saves"] += 1
            logging.info(f"快取儲存成功: {function_type}")
        except Exception as e:
            logging.error(f"儲存快取檔案失敗: {e}")
    
    def clear_expired(self) -> int:
        """清理過期快取，返回清理數量"""
        cleared_count = 0
        
        # 清理記憶體快取
        expired_keys = []
        for key, timestamp in self.memory_cache_ttl.items():
            if self._is_expired(timestamp):
                expired_keys.append(key)
        
        for key in expired_keys:
            del self.memory_cache[key]
            del self.memory_cache_ttl[key]
            cleared_count += 1
        
        # 清理檔案快取
        for filename in os.listdir(self.cache_dir):
            if filename.endswith('.json'):
                file_path = os.path.join(self.cache_dir, filename)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        cache_data = json.load(f)
                    
                    if self._is_expired(cache_data['timestamp']):
                        os.remove(file_path)
                        cleared_count += 1
                except Exception as e:
                    logging.error(f"清理快取檔案失敗: {e}")
        
        logging.info(f"清理了 {cleared_count} 個過期快取")
        return cleared_count
    
    def get_stats(self) -> Dict[str, Any]:
        """獲取快取統計"""
        hit_rate = 0
        if self.stats["hits"] + self.stats["misses"] > 0:
            hit_rate = (self.stats["hits"] / (self.stats["hits"] + self.stats["misses"])) * 100
        
        return {
            **self.stats,
            "hit_rate": round(hit_rate, 2),
            "memory_cache_size": len(self.memory_cache),
            "cache_dir_size": len([f for f in os.listdir(self.cache_dir) if f.endswith('.json')])
        }
    
    def clear_all(self) -> None:
        """清理所有快取"""
        self.memory_cache.clear()
        self.memory_cache_ttl.clear()
        
        for filename in os.listdir(self.cache_dir):
            if filename.endswith('.json'):
                os.remove(os.path.join(self.cache_dir, filename))
        
        logging.info("所有快取已清理")

# 全域快取實例
cache_system = CacheSystem()

# 快取裝飾器
def cache_result(function_type: str, ttl_hours: int = 24):
    """快取裝飾器"""
    def decorator(func):
        def wrapper(prompt, *args, **kwargs):
            # 嘗試從快取獲取
            cached_result = cache_system.get(prompt, function_type)
            if cached_result:
                return cached_result
            
            # 調用原始函數
            result = func(prompt, *args, **kwargs)
            
            # 儲存到快取
            if result and not result.startswith("抱歉"):
                cache_system.set(prompt, function_type, result)
            
            return result
        return wrapper
    return decorator 