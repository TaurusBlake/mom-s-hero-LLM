# app_simple.py - 簡化版 MomsHero Line Bot (加入多輪對話)
import logging
import os
import json
from flask import Flask, request, abort, render_template
from dotenv import load_dotenv

# --- LineBot 核心元件 ---
from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import (
    Configuration, ApiClient, MessagingApi,
    ReplyMessageRequest, TextMessage
)
from linebot.v3.webhooks import MessageEvent, TextMessageContent

# --- 資料庫模組 ---
from database.models import init_db, save_recipe, Recipe, get_recipe_count

# --- 載入環境變數 ---
load_dotenv()

# --- 初始化 Flask 應用 ---
app = Flask(__name__)

# --- 設定金鑰（請從 .env 檔案載入） ---
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")

# --- 設定日誌 ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='momshero.log',
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

# --- 用戶對話狀態管理 ---
class ConversationState:
    def __init__(self):
        self.user_states = {}  # 儲存每個用戶的對話狀態
    
    def get_user_state(self, user_id):
        """取得用戶的對話狀態"""
        if user_id not in self.user_states:
            self.user_states[user_id] = {
                'stage': 'idle',  # idle, waiting_for_ingredients, waiting_for_choice, waiting_for_feedback
                'ingredients': [],
                'recommendations': [],
                'selected_recipe': None,
                'recipe_details': None
            }
        return self.user_states[user_id]
    
    def update_user_state(self, user_id, updates):
        """更新用戶的對話狀態"""
        state = self.get_user_state(user_id)
        state.update(updates)
        self.user_states[user_id] = state
    
    def reset_user_state(self, user_id):
        """重置用戶的對話狀態"""
        self.user_states[user_id] = {
            'stage': 'idle',
            'ingredients': [],
            'recommendations': [],
            'selected_recipe': None,
            'recipe_details': None
        }

# 全域對話狀態管理器
conversation_state = ConversationState()

# --- 多輪對話處理函數 ---
def handle_conversation(user_id, user_message):
    """處理多輪對話邏輯"""
    state = conversation_state.get_user_state(user_id)
    
    # 檢查是否要重置對話
    if any(keyword in user_message for keyword in ['重新開始', '重置', '重新', '開始']):
        conversation_state.reset_user_state(user_id)
        return "好的！讓我們重新開始。請告訴我您有哪些食材，我會為您推薦適合的料理！"
    
    # 根據當前階段處理訊息
    if state['stage'] == 'idle':
        return handle_idle_stage(user_id, user_message)
    elif state['stage'] == 'waiting_for_ingredients':
        return handle_ingredients_stage(user_id, user_message)
    elif state['stage'] == 'waiting_for_choice':
        return handle_choice_stage(user_id, user_message)
    elif state['stage'] == 'waiting_for_feedback':
        return handle_feedback_stage(user_id, user_message)
    else:
        return handle_idle_stage(user_id, user_message)

def handle_idle_stage(user_id, user_message):
    """處理閒置階段的訊息"""
    # 檢查是否包含食材資訊
    ingredients = extract_ingredients(user_message)
    
    if ingredients:
        # 用戶提供了食材，進入推薦階段
        conversation_state.update_user_state(user_id, {
            'stage': 'waiting_for_ingredients',
            'ingredients': ingredients
        })
        return generate_recommendations(user_id, ingredients)
    else:
        # 引導用戶提供食材
        return """歡迎來到 MomsHero！👩‍🍳

我是您的專屬料理助手，請告訴我您有哪些食材，我會為您推薦適合的料理！

例如：
- 「我有雞蛋、白飯、蔥」
- 「家裡有豬肉、青菜、豆腐」
- 「冰箱裡有雞胸肉、胡蘿蔔」

請分享您的食材吧！"""

def handle_ingredients_stage(user_id, user_message):
    """處理食材收集階段的訊息"""
    # 檢查是否要重新提供食材
    if any(keyword in user_message for keyword in ['重新', '換', '其他']):
        ingredients = extract_ingredients(user_message)
        if ingredients:
            conversation_state.update_user_state(user_id, {
                'ingredients': ingredients
            })
            return generate_recommendations(user_id, ingredients)
    
    # 檢查是否選擇了推薦料理
    choice = extract_choice(user_message)
    if choice and 1 <= choice <= 3:
        state = conversation_state.get_user_state(user_id)
        if state['recommendations'] and choice <= len(state['recommendations']):
            selected_recipe = state['recommendations'][choice - 1]
            conversation_state.update_user_state(user_id, {
                'stage': 'waiting_for_choice',
                'selected_recipe': selected_recipe
            })
            return generate_recipe_details(selected_recipe)
    
    # 如果都不是，重新生成推薦
    ingredients = extract_ingredients(user_message)
    if ingredients:
        conversation_state.update_user_state(user_id, {
            'ingredients': ingredients
        })
        return generate_recommendations(user_id, ingredients)
    
    return "請選擇 1、2 或 3 來選擇您想要的料理，或者告訴我您有其他食材！"

def handle_choice_stage(user_id, user_message):
    """處理選擇階段的訊息"""
    # 檢查是否詢問替代方案
    if any(keyword in user_message for keyword in ['沒有', '缺少', '替代', '換', '其他']):
        conversation_state.update_user_state(user_id, {
            'stage': 'waiting_for_feedback'
        })
        return generate_alternatives(user_message)
    
    # 檢查是否要重新選擇
    if any(keyword in user_message for keyword in ['重新選擇', '換一個', '其他選項']):
        state = conversation_state.get_user_state(user_id)
        return generate_recommendations(user_id, state['ingredients'])
    
    # 預設回應
    return """如果您需要替代方案，請告訴我缺少什麼食材！
例如：「我沒有醬油」、「家裡沒有蔥」等。

或者您可以說「重新選擇」來看看其他推薦料理。"""

def handle_feedback_stage(user_id, user_message):
    """處理反饋階段的訊息"""
    # 提供替代方案後，可以重新開始或繼續
    if any(keyword in user_message for keyword in ['謝謝', '好的', '了解']):
        conversation_state.update_user_state(user_id, {
            'stage': 'idle'
        })
        return "不客氣！如果還有其他問題，隨時告訴我。您也可以說「重新開始」來尋找新的料理靈感！"
    
    # 如果還有其他問題，繼續提供幫助
    return "還有其他需要協助的地方嗎？我可以幫您調整食譜或推薦其他料理！"

def extract_ingredients(message):
    """從訊息中提取食材"""
    # 簡單的食材識別邏輯（實際使用時可以用更複雜的 NLP）
    common_ingredients = [
        '雞蛋', '白飯', '蔥', '蒜', '薑', '醬油', '鹽', '糖', '油',
        '豬肉', '牛肉', '雞肉', '魚', '蝦', '豆腐', '青菜', '白菜',
        '胡蘿蔔', '馬鈴薯', '洋蔥', '番茄', '青椒', '紅蘿蔔', '高麗菜',
        '香菇', '金針菇', '木耳', '粉絲', '麵條', '麵粉', '蛋', '牛奶'
    ]
    
    found_ingredients = []
    for ingredient in common_ingredients:
        if ingredient in message:
            found_ingredients.append(ingredient)
    
    return found_ingredients

def extract_choice(message):
    """從訊息中提取選擇數字"""
    import re
    numbers = re.findall(r'\d+', message)
    if numbers:
        return int(numbers[0])
    return None

def generate_recommendations(user_id, ingredients):
    """生成料理推薦（模擬版本）"""
    if not ingredients:
        return "請告訴我您有哪些食材，我會為您推薦適合的料理！"
    
    # 根據食材生成推薦（實際使用時會調用 LLM）
    recommendations = []
    
    if '雞蛋' in ingredients and '白飯' in ingredients:
        recommendations.append({
            'name': '黃金蛋炒飯',
            'main_ingredients': '雞蛋、白飯、蔥',
            'cooking_time': '15分鐘',
            'difficulty': '簡單'
        })
    
    if '豬肉' in ingredients:
        recommendations.append({
            'name': '蒜香炒豬肉',
            'main_ingredients': '豬肉、蒜、青菜',
            'cooking_time': '20分鐘',
            'difficulty': '中等'
        })
    
    if '豆腐' in ingredients:
        recommendations.append({
            'name': '麻婆豆腐',
            'main_ingredients': '豆腐、豬肉末、豆瓣醬',
            'cooking_time': '25分鐘',
            'difficulty': '中等'
        })
    
    # 如果沒有特定組合，提供通用推薦
    if not recommendations:
        recommendations = [
            {
                'name': '簡單炒青菜',
                'main_ingredients': '青菜、蒜、鹽',
                'cooking_time': '10分鐘',
                'difficulty': '簡單'
            },
            {
                'name': '蛋花湯',
                'main_ingredients': '雞蛋、蔥、鹽',
                'cooking_time': '15分鐘',
                'difficulty': '簡單'
            },
            {
                'name': '蒜香炒肉絲',
                'main_ingredients': '豬肉、蒜、醬油',
                'cooking_time': '20分鐘',
                'difficulty': '中等'
            }
        ]
    
    # 儲存推薦到用戶狀態
    conversation_state.update_user_state(user_id, {
        'recommendations': recommendations
    })
    
    # 格式化推薦回應
    response = f"根據您提供的食材：{', '.join(ingredients)}\n\n我為您推薦以下料理：\n\n"
    
    for i, recipe in enumerate(recommendations[:3], 1):
        response += f"{i}. {recipe['name']}\n"
        response += f"   主要食材：{recipe['main_ingredients']}\n"
        response += f"   預估烹飪時間：{recipe['cooking_time']}\n"
        response += f"   難度：{recipe['difficulty']}\n\n"
    
    response += "請選擇 1、2 或 3 來查看詳細食譜！"
    
    return response

def generate_recipe_details(recipe):
    """生成詳細食譜（模擬版本）"""
    recipe_name = recipe['name']
    
    # 根據料理名稱生成詳細食譜（實際使用時會調用 LLM）
    if '蛋炒飯' in recipe_name:
        details = """【黃金蛋炒飯 - 詳細食譜】

【食材準備】
- 雞蛋 2顆
- 白飯 2碗
- 蔥 1根
- 醬油 1大匙
- 鹽 少許
- 油 適量

【烹調時間】
15分鐘

【難度等級】
簡單

【詳細步驟】
1. 將雞蛋打散，加入少許鹽調味
2. 蔥切碎備用
3. 熱鍋下油，倒入蛋液炒至半熟
4. 加入白飯翻炒均勻
5. 加入醬油調味
6. 最後加入蔥花翻炒即可

【小技巧】
- 使用隔夜飯會更好吃
- 蛋液不要炒太熟，保持嫩滑口感
- 可以加入火腿丁增加風味"""
    
    elif '豬肉' in recipe_name:
        details = """【蒜香炒豬肉 - 詳細食譜】

【食材準備】
- 豬肉 300g
- 蒜 3瓣
- 青菜 適量
- 醬油 2大匙
- 鹽 少許
- 油 適量

【烹調時間】
20分鐘

【難度等級】
中等

【詳細步驟】
1. 豬肉切片，蒜切碎
2. 青菜洗淨切段
3. 熱鍋下油，爆香蒜末
4. 加入豬肉翻炒至變色
5. 加入青菜翻炒
6. 加入醬油和鹽調味即可

【小技巧】
- 豬肉可以先用醬油醃製更入味
- 青菜最後加入保持脆嫩"""
    
    else:
        details = f"""【{recipe_name} - 詳細食譜】

【食材準備】
- 主要食材：{recipe['main_ingredients']}
- 調味料：適量

【烹調時間】
{recipe['cooking_time']}

【難度等級】
{recipe['difficulty']}

【詳細步驟】
1. 準備食材
2. 熱鍋下油
3. 依序加入食材
4. 調味即可

【小技巧】
- 根據個人口味調整調味
- 注意火候控制"""
    
    return details

def generate_alternatives(message):
    """生成替代方案（模擬版本）"""
    return """【替代方案建議】

根據您提到的缺少食材，我為您提供以下替代方案：

【調味料替代】
- 沒有醬油 → 可以用鹽或魚露
- 沒有蒜 → 可以用薑或洋蔥
- 沒有蔥 → 可以用韭菜或香菜

【主要食材替代】
- 沒有豬肉 → 可以用雞肉或豆腐
- 沒有雞蛋 → 可以用豆腐或豆芽
- 沒有青菜 → 可以用其他蔬菜

【烹調方式調整】
- 如果缺少某些調味料，可以簡化調味
- 如果缺少主要食材，可以調整為其他料理

請告訴我您具體缺少什麼，我可以提供更精確的建議！"""

# --- LineBot 設定 ---
configuration = Configuration(access_token=LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

# --- 模擬 LLM 回應（不主動調用 LLM） ---
def generate_recipe_response(user_message: str) -> str:
    """
    模擬 LLM 回應，實際使用時會替換為真正的 LLM 調用
    目前返回一個固定的回應，避免消耗 API 額度
    """
    # 這裡是模擬回應，實際使用時會調用 Google Gemini
    return f"""親愛的朋友，我收到您的訊息：「{user_message}」

目前系統正在測試階段，我暫時無法為您生成食譜。
當您準備好測試 LLM 功能時，請告訴我，我會為您提供美味的食譜建議！

目前資料庫中已儲存了 {get_recipe_count()} 個食譜記錄。
"""

# --- Webhook 路由 ---
@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

# --- 訊息處理 ---
@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    user_id = event.source.user_id
    user_message = event.message.text
    
    # 記錄用戶訊息
    logging.info(f"收到來自用戶 {user_id} 的訊息: {user_message}")
    
    # 使用多輪對話處理
    ai_response = handle_conversation(user_id, user_message)
    
    # 儲存到資料庫（即使只是模擬回應也儲存，累積資料）
    try:
        recipe = Recipe(
            user_id=user_id,
            user_message=user_message,
            recipe_title="多輪對話回應",  # 實際使用時會從 LLM 回應中提取
            recipe_content=ai_response,
            ingredients="多輪對話",
            cooking_time="測試時間",
            difficulty="簡單"
        )
        save_recipe(recipe)
    except Exception as e:
        logging.error(f"儲存食譜時發生錯誤: {e}")
    
    # 回傳給用戶
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        line_bot_api.reply_message_with_http_info(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text=ai_response)]
            )
        )

# --- 健康檢查路由 ---
@app.route("/health", methods=['GET'])
def health_check():
    recipe_count = get_recipe_count()
    return {
        "status": "healthy",
        "recipe_count": recipe_count,
        "message": f"資料庫中有 {recipe_count} 個食譜記錄",
        "conversation_users": len(conversation_state.user_states)
    }

# --- 測試多輪對話路由 ---
@app.route("/test_conversation", methods=['GET', 'POST'])
def test_conversation():
    """測試多輪對話功能"""
    if request.method == 'GET':
        # 返回測試頁面
        return render_template('test_conversation.html')
    
    # POST 請求處理
    data = request.get_json()
    user_id = data.get('user_id', 'test_user')
    user_message = data.get('message', '我有雞蛋和白飯')
    
    response = handle_conversation(user_id, user_message)
    state = conversation_state.get_user_state(user_id)
    
    return {
        "user_message": user_message,
        "response": response,
        "current_stage": state['stage'],
        "ingredients": state['ingredients'],
        "recommendations_count": len(state['recommendations'])
    }

# --- 主程式 ---
if __name__ == "__main__":
    print("=== MomsHero 多輪對話版本啟動 ===")
    print(f"資料庫中現有食譜數量: {get_recipe_count()}")
    print("注意：目前設定為不主動調用 LLM，避免消耗 API 額度")
    print("多輪對話功能已啟用，支援食材上傳、推薦選擇、詳細食譜、替代方案")
    print("測試端點: http://localhost:5000/test_conversation")
    print("=" * 50)
    
    app.run(debug=True, host='0.0.0.0', port=5000) 