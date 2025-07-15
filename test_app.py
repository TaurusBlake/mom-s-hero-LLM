# test_app.py - 測試版本，不依賴環境變數
import logging
from flask import Flask, request, abort

# --- 資料庫模組 ---
from database.models import init_db, save_recipe, Recipe, get_recipe_count

# --- 初始化 Flask 應用 ---
app = Flask(__name__)

# --- 設定日誌 ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='momshero_test.log',
    filemode='a'
)

# --- 初始化資料庫 ---
print("正在初始化資料庫...")
init_db()

# --- 載入提示模板 ---
def load_prompt_template():
    """載入食譜生成提示模板"""
    try:
        with open('prompts/recipe_prompt.txt', 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return "你是一位溫暖的資深煮婦，請提供實用的食譜建議。"

PROMPT_TEMPLATE = load_prompt_template()
print(f"提示模板載入成功，長度: {len(PROMPT_TEMPLATE)} 字元")

# --- 模擬 Line Bot 訊息處理 ---
def simulate_line_message(user_id: str, user_message: str) -> str:
    """模擬 Line Bot 訊息處理"""
    print(f"模擬收到來自用戶 {user_id} 的訊息: {user_message}")
    
    # 生成回應
    ai_response = f"""親愛的朋友，我收到您的訊息：「{user_message}」

目前系統正在測試階段，我暫時無法為您生成食譜。
當您準備好測試 LLM 功能時，請告訴我，我會為您提供美味的食譜建議！

目前資料庫中已儲存了 {get_recipe_count()} 個食譜記錄。
"""
    
    # 儲存到資料庫
    try:
        recipe = Recipe(
            user_id=user_id,
            user_message=user_message,
            recipe_title="測試回應",
            recipe_content=ai_response,
            ingredients="測試食材",
            cooking_time="測試時間",
            difficulty="簡單"
        )
        save_recipe(recipe)
        print(f"食譜已儲存到資料庫")
    except Exception as e:
        print(f"儲存食譜時發生錯誤: {e}")
    
    return ai_response

# --- 測試路由 ---
@app.route("/test", methods=['POST'])
def test_message():
    """測試訊息處理"""
    data = request.get_json()
    user_id = data.get('user_id', 'test_user')
    user_message = data.get('message', '測試訊息')
    
    response = simulate_line_message(user_id, user_message)
    return {"response": response, "user_id": user_id}

@app.route("/test", methods=['GET'])
def test_form():
    """測試表單"""
    return '''
    <h1>MomsHero 測試頁面</h1>
    <form method="POST">
        <p>用戶 ID: <input type="text" name="user_id" value="test_user"></p>
        <p>訊息: <input type="text" name="message" value="我想做紅燒肉"></p>
        <input type="submit" value="發送測試訊息">
    </form>
    <p><a href="/health">健康檢查</a></p>
    <p><a href="/stats">統計資訊</a></p>
    '''

# --- 健康檢查路由 ---
@app.route("/health", methods=['GET'])
def health_check():
    recipe_count = get_recipe_count()
    return {
        "status": "healthy",
        "recipe_count": recipe_count,
        "message": f"資料庫中有 {recipe_count} 個食譜記錄"
    }

# --- 統計資訊路由 ---
@app.route("/stats", methods=['GET'])
def stats():
    """顯示統計資訊"""
    recipe_count = get_recipe_count()
    return f'''
    <h1>MomsHero 統計資訊</h1>
    <p>資料庫中食譜數量: {recipe_count}</p>
    <p>提示模板長度: {len(PROMPT_TEMPLATE)} 字元</p>
    <p><a href="/test">返回測試頁面</a></p>
    '''

# --- 主程式 ---
if __name__ == "__main__":
    print("=== MomsHero 測試版啟動 ===")
    print(f"資料庫中現有食譜數量: {get_recipe_count()}")
    print("測試頁面: http://localhost:5000/test")
    print("健康檢查: http://localhost:5000/health")
    print("統計資訊: http://localhost:5000/stats")
    print("=" * 50)
    
    app.run(debug=True, host='0.0.0.0', port=5000) 