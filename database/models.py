import sqlite3
import os
from datetime import datetime
from typing import Optional, List, Dict, Any

class Recipe:
    def __init__(self, user_id: str, user_message: str, recipe_title: str, 
                 recipe_content: str, ingredients: Optional[str] = None,
                 cooking_time: Optional[str] = None, difficulty: Optional[str] = None):
        self.user_id = user_id
        self.user_message = user_message
        self.recipe_title = recipe_title
        self.recipe_content = recipe_content
        self.ingredients = ingredients
        self.cooking_time = cooking_time
        self.difficulty = difficulty
        self.created_at = datetime.now()

def get_db_connection():
    """建立資料庫連接"""
    db_path = os.path.join(os.path.dirname(__file__), 'recipes.db')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row  # 讓查詢結果可以像字典一樣存取
    return conn

def init_db():
    """初始化資料庫，建立食譜表"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 建立食譜表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS recipes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            user_message TEXT NOT NULL,
            recipe_title TEXT NOT NULL,
            recipe_content TEXT NOT NULL,
            ingredients TEXT,
            cooking_time TEXT,
            difficulty TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()
    print("資料庫初始化完成！")

def save_recipe(recipe: Recipe) -> int:
    """儲存食譜到資料庫"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO recipes (user_id, user_message, recipe_title, recipe_content, 
                           ingredients, cooking_time, difficulty, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        recipe.user_id,
        recipe.user_message,
        recipe.recipe_title,
        recipe.recipe_content,
        recipe.ingredients,
        recipe.cooking_time,
        recipe.difficulty,
        recipe.created_at
    ))
    
    recipe_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    print(f"食譜已儲存，ID: {recipe_id}")
    return recipe_id

def get_recipes_by_user(user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
    """根據用戶 ID 取得最近的食譜"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT * FROM recipes 
        WHERE user_id = ? 
        ORDER BY created_at DESC 
        LIMIT ?
    ''', (user_id, limit))
    
    recipes = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return recipes

def get_all_recipes(limit: int = 50) -> List[Dict[str, Any]]:
    """取得所有食譜（用於未來 RAG 功能）"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT * FROM recipes 
        ORDER BY created_at DESC 
        LIMIT ?
    ''', (limit,))
    
    recipes = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return recipes

def get_recipe_count() -> int:
    """取得食譜總數"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*) FROM recipes')
    count = cursor.fetchone()[0]
    conn.close()
    
    return count 