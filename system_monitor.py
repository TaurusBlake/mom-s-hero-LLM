#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
系統監控工具
監控LLM狀態、API配額、用戶使用情況等
"""

import os
import time
import json
from datetime import datetime, timedelta
import logging

class SystemMonitor:
    def __init__(self):
        self.stats_file = "system_stats.json"
        self.load_stats()
    
    def load_stats(self):
        """載入統計資料"""
        try:
            with open(self.stats_file, 'r', encoding='utf-8') as f:
                self.stats = json.load(f)
        except FileNotFoundError:
            self.stats = {
                "llm_quota_errors": 0,
                "total_requests": 0,
                "successful_requests": 0,
                "last_quota_error": None,
                "daily_usage": {},
                "user_activity": {}
            }
    
    def save_stats(self):
        """儲存統計資料"""
        with open(self.stats_file, 'w', encoding='utf-8') as f:
            json.dump(self.stats, f, ensure_ascii=False, indent=2)
    
    def record_quota_error(self):
        """記錄配額錯誤"""
        self.stats["llm_quota_errors"] += 1
        self.stats["last_quota_error"] = datetime.now().isoformat()
        self.save_stats()
    
    def record_request(self, user_id, success=True):
        """記錄請求"""
        self.stats["total_requests"] += 1
        if success:
            self.stats["successful_requests"] += 1
        
        # 記錄每日使用量
        today = datetime.now().strftime("%Y-%m-%d")
        if today not in self.stats["daily_usage"]:
            self.stats["daily_usage"][today] = {
                "total": 0,
                "successful": 0,
                "quota_errors": 0
            }
        
        self.stats["daily_usage"][today]["total"] += 1
        if success:
            self.stats["daily_usage"][today]["successful"] += 1
        
        # 記錄用戶活動
        if user_id not in self.stats["user_activity"]:
            self.stats["user_activity"][user_id] = {
                "first_seen": datetime.now().isoformat(),
                "last_seen": datetime.now().isoformat(),
                "total_requests": 0
            }
        
        self.stats["user_activity"][user_id]["last_seen"] = datetime.now().isoformat()
        self.stats["user_activity"][user_id]["total_requests"] += 1
        
        self.save_stats()
    
    def get_system_status(self):
        """獲取系統狀態"""
        success_rate = 0
        if self.stats["total_requests"] > 0:
            success_rate = (self.stats["successful_requests"] / self.stats["total_requests"]) * 100
        
        return {
            "total_requests": self.stats["total_requests"],
            "successful_requests": self.stats["successful_requests"],
            "quota_errors": self.stats["llm_quota_errors"],
            "success_rate": round(success_rate, 2),
            "last_quota_error": self.stats["last_quota_error"],
            "active_users": len(self.stats["user_activity"]),
            "today_usage": self.get_today_usage()
        }
    
    def get_today_usage(self):
        """獲取今日使用量"""
        today = datetime.now().strftime("%Y-%m-%d")
        return self.stats["daily_usage"].get(today, {
            "total": 0,
            "successful": 0,
            "quota_errors": 0
        })
    
    def get_quota_status(self):
        """獲取配額狀態"""
        if not self.stats["last_quota_error"]:
            return "正常"
        
        last_error = datetime.fromisoformat(self.stats["last_quota_error"])
        hours_since_error = (datetime.now() - last_error).total_seconds() / 3600
        
        if hours_since_error < 24:
            return f"配額已用完 ({hours_since_error:.1f}小時前)"
        else:
            return "可能已重置"
    
    def generate_report(self):
        """生成系統報告"""
        status = self.get_system_status()
        
        report = f"""
=== MomsHero 系統狀態報告 ===
生成時間: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

📊 使用統計:
- 總請求數: {status['total_requests']}
- 成功請求: {status['successful_requests']}
- 配額錯誤: {status['quota_errors']}
- 成功率: {status['success_rate']}%

👥 用戶統計:
- 活躍用戶: {status['active_users']}

📅 今日使用:
- 總請求: {status['today_usage']['total']}
- 成功: {status['today_usage']['successful']}
- 配額錯誤: {status['today_usage']['quota_errors']}

🔧 配額狀態: {self.get_quota_status()}

💡 建議:
"""
        
        if status['quota_errors'] > 0:
            report += "- 考慮升級到付費版本\n"
            report += "- 監控每日使用量\n"
        
        if status['success_rate'] < 80:
            report += "- 檢查API連接穩定性\n"
        
        return report

# 全域監控實例
system_monitor = SystemMonitor() 