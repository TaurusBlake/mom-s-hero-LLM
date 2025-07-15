#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
提交準備腳本
檢查專案完整性並生成提交訊息
"""

import os
import sys
import json
from datetime import datetime

def check_project_structure():
    """檢查專案結構完整性"""
    required_files = [
        "app_llm.py",
        "app_simple.py", 
        "cache_system.py",
        "recipe_features.py",
        "system_monitor.py",
        "user_experience.py",
        "test_suite.py",
        "requirements.txt",
        "README.md",
        "DEPLOYMENT_GUIDE.md",
        ".gitignore",
        "database/models.py",
        "prompts/recipe_prompt.txt"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    return missing_files

def check_imports():
    """檢查模組導入是否正常"""
    modules_to_test = [
        "app_llm",
        "cache_system", 
        "recipe_features",
        "system_monitor",
        "user_experience"
    ]
    
    import_errors = []
    for module in modules_to_test:
        try:
            __import__(module)
        except ImportError as e:
            import_errors.append(f"{module}: {e}")
    
    return import_errors

def generate_commit_message():
    """生成提交訊息"""
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    commit_message = f"""feat: 完成 MomsHero LLM 初始版本

🎉 主要功能
- 多輪對話系統：支援連續對話和狀態管理
- LLM 整合：Google Gemini API 整合
- 快取機制：記憶體和檔案快取，減少 API 調用
- 系統監控：詳細的使用統計和錯誤追蹤
- 用戶體驗：智能提示和個性化回應

🔧 核心模組
- app_llm.py: 主應用程式 (LLM 版本)
- cache_system.py: 快取系統
- recipe_features.py: 食譜擴展功能
- system_monitor.py: 系統監控
- user_experience.py: 用戶體驗工具
- test_suite.py: 完整測試套件

📊 系統特色
- 配額錯誤處理：智能處理 API 限制
- 錯誤恢復：完善的錯誤處理機制
- 效能優化：快取和批量處理
- 安全性：環境變數和輸入驗證

📚 文件
- README.md: 完整的專案說明
- DEPLOYMENT_GUIDE.md: 部署和維護指南
- 測試套件：單元測試、整合測試、效能測試

🚀 技術棧
- Flask + LineBot SDK
- Google Gemini LLM
- SQLite 資料庫
- 快取系統

版本: v1.0.0
時間: {current_time}
"""
    
    return commit_message

def check_environment():
    """檢查環境設定"""
    env_file = ".env"
    env_example = "env_example.txt"
    
    issues = []
    
    if not os.path.exists(env_example):
        issues.append("缺少 env_example.txt 檔案")
    
    if os.path.exists(env_file):
        issues.append("警告: .env 檔案存在，請確認已加入 .gitignore")
    
    return issues

def main():
    """主函數"""
    print("=== MomsHero LLM 提交準備檢查 ===\n")
    
    # 檢查專案結構
    print("1. 檢查專案結構...")
    missing_files = check_project_structure()
    if missing_files:
        print(f"❌ 缺少檔案: {missing_files}")
    else:
        print("✅ 專案結構完整")
    
    # 檢查導入
    print("\n2. 檢查模組導入...")
    import_errors = check_imports()
    if import_errors:
        print(f"❌ 導入錯誤: {import_errors}")
    else:
        print("✅ 模組導入正常")
    
    # 檢查環境
    print("\n3. 檢查環境設定...")
    env_issues = check_environment()
    if env_issues:
        for issue in env_issues:
            print(f"⚠️  {issue}")
    else:
        print("✅ 環境設定正常")
    
    # 生成提交訊息
    print("\n4. 生成提交訊息...")
    commit_message = generate_commit_message()
    
    # 儲存提交訊息到檔案
    with open("commit_message.txt", "w", encoding="utf-8") as f:
        f.write(commit_message)
    
    print("✅ 提交訊息已儲存到 commit_message.txt")
    
    # 總結
    print("\n=== 檢查總結 ===")
    if not missing_files and not import_errors:
        print("🎉 專案準備完成，可以提交到 GitHub！")
        print("\n下一步:")
        print("1. git add .")
        print("2. git commit -F commit_message.txt")
        print("3. git push origin main")
    else:
        print("⚠️  請先解決上述問題再提交")
    
    return len(missing_files) + len(import_errors) == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 