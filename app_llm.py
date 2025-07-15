# app_llm.py - LLM 版本 MomsHero Line Bot (加入多輪對話)
import logging
import os
from flask import Flask, request, abort, render_template, jsonify
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

# --- Google Gemini LLM ---
import google.generativeai as genai

# --- 離線食譜模組 ---
from offline_recipes import (
    get_offline_recommendations, 
    get_offline_recipe_details,
    format_offline_recommendations,
    format_offline_recipe_details
)

# --- 載入環境變數 ---
load_dotenv()

# --- 初始化 Flask 應用 ---
app = Flask(__name__)

# --- 設定金鑰 ---
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")

# --- 設定日誌 ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='momshero_llm.log',
    filemode='a'
)

# --- 初始化資料庫 ---
print("正在初始化資料庫...")
init_db()

# --- 初始化 Google Gemini ---
def init_gemini():
    """初始化 Google Gemini LLM"""
    if not GOOGLE_API_KEY:
        raise ValueError("未設定 GOOGLE_API_KEY")
    
    genai.configure(api_key=GOOGLE_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
    print("Google Gemini LLM 初始化成功！")
    return model

try:
    llm_model = init_gemini()
    LLM_AVAILABLE = True
except Exception as e:
    print(f"LLM 初始化失敗: {e}")
    LLM_AVAILABLE = False

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
    
    # 檢查訊息是否與食譜相關
    if not is_recipe_related(user_message):
        return "抱歉，我是專門協助料理和食譜的助手。請詢問與食材、料理、烹調相關的問題，我很樂意為您提供幫助！"
    
    # 如果 LLM 不可用，提供明確提示
    if not LLM_AVAILABLE:
        return "抱歉，AI 服務目前暫時無法使用。請稍後再試，我會盡快恢復為您提供食譜建議！"
    
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
        return generate_recommendations_with_llm(user_id, ingredients)
    else:
        # 如果沒有識別到食材，直接引導用戶提供食材
        return """歡迎來到 MomsHero！👩‍🍳

我是您的專屬料理助手，請告訴我您有哪些食材，我會為您推薦適合的料理！

例如：
- 「我有雞蛋、白飯、蔥」
- 「家裡有豬肉、青菜、豆腐」
- 「冰箱裡有雞胸肉、胡蘿蔔」
- 「我有鮭魚、秋葵、松露」

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
            return generate_recommendations_with_llm(user_id, ingredients)
    
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
            return generate_recipe_details_with_llm(selected_recipe)
    
    # 檢查是否包含新的食材資訊
    ingredients = extract_ingredients(user_message)
    if ingredients:
        conversation_state.update_user_state(user_id, {
            'ingredients': ingredients
        })
        return generate_recommendations_with_llm(user_id, ingredients)
    
    # 檢查是否詢問特定料理（如「有推薦的炒飯嗎」）
    if any(keyword in user_message for keyword in ['推薦', '炒飯', '料理', '食譜']):
        conversation_state.update_user_state(user_id, {
            'stage': 'idle'
        })
        return """歡迎來到 MomsHero！👩‍🍳

我是您的專屬料理助手，請告訴我您有哪些食材，我會為您推薦適合的料理！

例如：
- 「我有雞蛋、白飯、蔥」
- 「家裡有豬肉、青菜、豆腐」
- 「冰箱裡有雞胸肉、胡蘿蔔」
- 「我有鮭魚、秋葵、松露」

請分享您的食材吧！"""
    
    return "請選擇 1、2 或 3 來選擇您想要的料理，或者告訴我您有其他食材！"

def handle_choice_stage(user_id, user_message):
    """處理選擇階段的訊息"""
    # 檢查是否詢問替代方案
    if any(keyword in user_message for keyword in ['沒有', '缺少', '替代', '換', '其他']):
        conversation_state.update_user_state(user_id, {
            'stage': 'waiting_for_feedback'
        })
        return generate_alternatives_with_llm(user_id, user_message)
    
    # 檢查是否要重新選擇
    if any(keyword in user_message for keyword in ['重新選擇', '換一個', '其他選項']):
        state = conversation_state.get_user_state(user_id)
        return generate_recommendations_with_llm(user_id, state['ingredients'])
    
    # 檢查是否包含新的食材資訊
    ingredients = extract_ingredients(user_message)
    if ingredients:
        # 用戶提供了新的食材，重置狀態並進入推薦階段
        conversation_state.update_user_state(user_id, {
            'stage': 'waiting_for_ingredients',
            'ingredients': ingredients
        })
        return generate_recommendations_with_llm(user_id, ingredients)
    
    # 檢查是否詢問特定料理（如「有推薦的炒飯嗎」）
    if any(keyword in user_message for keyword in ['推薦', '料理', '食譜']):
        conversation_state.update_user_state(user_id, {
            'stage': 'idle'
        })
        return """歡迎來到 MomsHero！👩‍🍳

我是您的專屬料理助手，請告訴我您有哪些食材，我會為您推薦適合的料理！

例如：
- 「我有雞蛋、白飯、蔥」
- 「家裡有豬肉、青菜、豆腐」
- 「冰箱裡有雞胸肉、胡蘿蔔」
- 「我有鮭魚、秋葵、松露」

請分享您的食材吧！"""
    
    # 預設回應
    return """如果您需要替代方案，請告訴我缺少什麼食材！
例如：「我沒有醬油」、「家裡沒有蔥」等。

或者您可以說「重新選擇」來看看其他推薦料理。
您也可以提供新的食材，我會為您推薦其他料理！"""

def handle_feedback_stage(user_id, user_message):
    """處理反饋階段的訊息"""
    # 檢查是否要重新開始或詢問新的料理
    if any(keyword in user_message for keyword in ['謝謝', '好的', '了解', '重新開始', '重新']):
        conversation_state.update_user_state(user_id, {
            'stage': 'idle'
        })
        return "好的！讓我們重新開始。請告訴我您有哪些食材，我會為您推薦適合的料理！"
    
    # 檢查是否包含新的食材資訊
    ingredients = extract_ingredients(user_message)
    if ingredients:
        # 用戶提供了新的食材，重置狀態並進入推薦階段
        conversation_state.update_user_state(user_id, {
            'stage': 'waiting_for_ingredients',
            'ingredients': ingredients
        })
        return generate_recommendations_with_llm(user_id, ingredients)
    
    # 檢查是否詢問特定料理（如「有推薦的炒飯嗎」）
    if any(keyword in user_message for keyword in ['推薦', '炒飯', '料理', '食譜']):
        conversation_state.update_user_state(user_id, {
            'stage': 'idle'
        })
        return """歡迎來到 MomsHero！👩‍🍳

我是您的專屬料理助手，請告訴我您有哪些食材，我會為您推薦適合的料理！

例如：
- 「我有雞蛋、白飯、蔥」
- 「家裡有豬肉、青菜、豆腐」
- 「冰箱裡有雞胸肉、胡蘿蔔」
- 「我有鮭魚、秋葵、松露」

請分享您的食材吧！"""
    
    # 如果都不是，引導用戶重新開始
    return "如果您想詢問新的料理，請告訴我您有哪些食材，或者說「重新開始」來重新開始對話。"

def is_recipe_related(message):
    """檢查訊息是否與食譜相關"""
    # 如果 LLM 不可用，直接返回 True 讓系統處理
    if not LLM_AVAILABLE:
        return True
    
    try:
        # 使用 LLM 判斷訊息是否與食譜相關
        prompt = f"""請判斷以下訊息是否與食譜、料理、食材、烹調相關。

用戶訊息：「{message}」

判斷標準：
1. 食譜相關：詢問食材、料理做法、烹調方法、調味、廚藝等
2. 食材相關：提到各種食材、調味料、廚房用品等
3. 烹調相關：詢問如何煮、炒、蒸、炸、烤等烹調技巧
4. 功能相關：詢問推薦料理、替代方案、選擇料理等

請只回傳 true 或 false，不要其他文字："""

        response = llm_model.generate_content(prompt)
        llm_result = response.text.strip().lower()
        
        # 解析 LLM 回應
        if llm_result == 'true':
            return True
        elif llm_result == 'false':
            return False
        else:
            # 如果 LLM 回應格式不正確，預設為相關（寬鬆原則）
            logging.warning(f"LLM 相關性判斷回應格式不正確: {llm_result}")
            return True
            
    except Exception as e:
        logging.error(f"LLM 相關性判斷失敗: {e}")
        # 檢查是否是配額錯誤
        if "quota" in str(e).lower() or "429" in str(e):
            logging.warning("LLM 配額已用完，預設為相關")
        # 如果 LLM 失敗，預設為相關（寬鬆原則）
        return True

def extract_ingredients(message):
    """從訊息中提取食材"""
    # 常見食材清單（用於快速識別）
    common_ingredients = [
        '雞蛋', '白飯', '蔥', '蒜', '薑', '醬油', '鹽', '糖', '油',
        '豬肉', '牛肉', '雞肉', '魚', '蝦', '豆腐', '青菜', '白菜',
        '胡蘿蔔', '馬鈴薯', '洋蔥', '番茄', '青椒', '紅蘿蔔', '高麗菜',
        '香菇', '金針菇', '木耳', '粉絲', '麵條', '麵粉', '蛋', '牛奶'
    ]
    
    found_ingredients = []
    
    # 1. 先檢查常見食材
    for ingredient in common_ingredients:
        if ingredient in message:
            found_ingredients.append(ingredient)
    
    # 2. 使用 LLM 識別未知食材（如果 LLM 可用且沒有找到常見食材）
    if LLM_AVAILABLE and not found_ingredients:
        try:
            # 使用 LLM 識別食材，但加入更嚴格的驗證
            prompt = f"""請從以下訊息中識別出食材名稱，只回傳食材名稱，用逗號分隔：

訊息：{message}

規則：
1. 只識別明確提到的食材
2. 不要假設或推測用戶有什麼食材
3. 不要添加用戶沒有提到的食材
4. 如果沒有明確的食材，回傳「無」

例如：
- 「我有鮭魚、秋葵、松露」→ 鮭魚,秋葵,松露
- 「家裡有雞胸肉、甜椒、迷迭香」→ 雞胸肉,甜椒,迷迭香
- 「冰箱裡有高麗菜、紅蘿蔔、洋蔥」→ 高麗菜,紅蘿蔔,洋蔥
- 「我想做料理」→ 無
- 「今天天氣真好」→ 無

請只回傳食材名稱或「無」，不要其他文字："""

            response = llm_model.generate_content(prompt)
            llm_response = response.text.strip()
            
            # 嚴格驗證 LLM 回應
            if llm_response == '無' or not llm_response:
                return found_ingredients
            

            
            llm_ingredients = llm_response.split(',')
            
            # 清理和驗證 LLM 回應
            for ingredient in llm_ingredients:
                ingredient = ingredient.strip()
                if ingredient and len(ingredient) > 1 and ingredient != '無':  # 避免單字元或空字串
                    found_ingredients.append(ingredient)
                    
        except Exception as e:
            logging.error(f"LLM 食材識別失敗: {e}")
            # 檢查是否是配額錯誤
            if "quota" in str(e).lower() or "429" in str(e):
                logging.warning("LLM 配額已用完，跳過食材識別")
    
    # 3. 如果還是沒有找到食材，使用簡單的關鍵字匹配
    if not found_ingredients:
        # 檢查常見的食材相關詞彙
        food_keywords = [
            '肉', '魚', '蝦', '蟹', '貝', '蛋', '奶', '豆', '菜', '菇', '菌',
            '根', '莖', '葉', '花', '果', '籽', '核', '仁', '粉', '醬', '油',
            '醋', '酒', '茶', '咖啡', '糖', '鹽', '胡椒', '香料', '香草'
        ]
        
        # 簡單的詞彙匹配（可以根據需要擴展）
        words = message.split()
        for word in words:
            # 移除標點符號
            clean_word = ''.join(c for c in word if c.isalnum())
            if len(clean_word) > 1:  # 避免單字元
                # 檢查是否包含食材相關關鍵字
                for keyword in food_keywords:
                    if keyword in clean_word:
                        found_ingredients.append(clean_word)
                        break
    
    return found_ingredients

def extract_choice(message):
    """從訊息中提取選擇數字"""
    import re
    numbers = re.findall(r'\d+', message)
    if numbers:
        return int(numbers[0])
    return None

# --- LLM 整合的多輪對話函數 ---
def generate_recommendations_with_llm(user_id, ingredients):
    """使用 LLM 生成料理推薦"""
    if not ingredients:
        return "請告訴我您有哪些食材，我會為您推薦適合的料理！"
    
    if not LLM_AVAILABLE:
        return "抱歉，AI 服務目前無法使用，請稍後再試。"
    
    try:
        # 使用 LLM 生成推薦
        prompt = f"""你是一位溫暖的資深煮婦。根據用戶提供的食材：{', '.join(ingredients)}

請推薦 3 道適合的料理，格式如下：

1. [料理名稱]
   主要食材：[主要食材]
   預估烹飪時間：[時間]
   難度：[簡單/中等/困難]

2. [料理名稱]
   主要食材：[主要食材]
   預估烹飪時間：[時間]
   難度：[簡單/中等/困難]

3. [料理名稱]
   主要食材：[主要食材]
   預估烹飪時間：[時間]
   難度：[簡單/中等/困難]

請選擇 1、2 或 3 來查看詳細食譜！

注意：請保持專業和簡潔的回應風格，不要使用過於口語化或誇張的表達。"""

        response = llm_model.generate_content(prompt)
        recommendations_text = response.text
        
        # 驗證回應格式
        if not recommendations_text or len(recommendations_text) < 50:
            logging.warning(f"LLM 回應過短或異常: {recommendations_text}")
            return "抱歉，生成推薦時發生錯誤，請稍後再試。"
        

        
        # 解析推薦結果
        recommendations = parse_recommendations(recommendations_text)
        
        # 儲存推薦到用戶狀態
        conversation_state.update_user_state(user_id, {
            'recommendations': recommendations
        })
        
        return recommendations_text
        
    except Exception as e:
        logging.error(f"LLM 推薦生成失敗: {e}")
        # 檢查是否是配額錯誤
        if "quota" in str(e).lower() or "429" in str(e):
            return "抱歉，AI 服務的免費額度已用完。請稍後再試，或考慮升級到付費版本。"
        else:
            return "抱歉，生成推薦時發生錯誤，請稍後再試。"

def generate_recipe_details_with_llm(recipe):
    """使用 LLM 生成詳細食譜"""
    if not LLM_AVAILABLE:
        return "抱歉，AI 服務目前無法使用，請稍後再試。"
    
    try:
        prompt = f"""請為「{recipe['name']}」提供詳細的食譜，包含：

【食材準備】
- 詳細的食材清單和份量

【烹調時間】
- 預估烹調時間

【難度等級】
- 簡單/中等/困難

【詳細步驟】
- 步驟化的烹調說明

【小技巧】
- 烹調技巧和注意事項(言簡意賅，不要冗長)

請用繁體中文回答，格式要清楚易讀。"""

        response = llm_model.generate_content(prompt)
        response_text = response.text
        
        # 驗證回應格式
        if not response_text or len(response_text) < 20:
            logging.warning(f"LLM 食譜詳情回應過短或異常: {response_text}")
            return "抱歉，生成食譜詳情時發生錯誤，請稍後再試。"
        
        return response_text
        
    except Exception as e:
        logging.error(f"LLM 食譜詳情生成失敗: {e}")
        # 檢查是否是配額錯誤
        if "quota" in str(e).lower() or "429" in str(e):
            return "抱歉，AI 服務的免費額度已用完。請稍後再試，或考慮升級到付費版本。"
        else:
            return "抱歉，生成食譜詳情時發生錯誤，請稍後再試。"

def generate_alternatives_with_llm(user_id, message):
    """使用 LLM 生成替代方案"""
    if not LLM_AVAILABLE:
        return "抱歉，AI 服務目前無法使用，請稍後再試。"
    
    try:
        # 獲取用戶當前狀態，包含已選擇的食譜
        state = conversation_state.get_user_state(user_id)
        selected_recipe = state.get('selected_recipe', {})
        
        # 構建更簡潔的提示詞
        prompt = f"""用戶的原始需求：{message}

用戶已選擇的食譜：{selected_recipe.get('name', '未知料理')}

請提供簡潔實用的替代方案建議：

【替代方案】
- 如果食材不重要，直接說「可以不用」並說明理由
- 如果食材重要，提供 1-2 個簡單的替代選項
- 說明替代後的口感變化（簡短）

【實用建議】
- 給出具體的烹調調整建議
- 鼓勵簡化版本

請用繁體中文回答，保持簡潔，避免冗長的格式標題。重點是讓用戶快速了解可以怎麼做。"""

        response = llm_model.generate_content(prompt)
        response_text = response.text
        
        # 驗證回應格式
        if not response_text or len(response_text) < 20:
            logging.warning(f"LLM 替代方案回應過短或異常: {response_text}")
            return "抱歉，生成替代方案時發生錯誤，請稍後再試。"
        

        
        return response_text
        
    except Exception as e:
        logging.error(f"LLM 替代方案生成失敗: {e}")
        # 檢查是否是配額錯誤
        if "quota" in str(e).lower() or "429" in str(e):
            return "抱歉，AI 服務的免費額度已用完。請稍後再試，或考慮升級到付費版本。"
        else:
            return "抱歉，生成替代方案時發生錯誤，請稍後再試。"

def parse_recommendations(text):
    """解析 LLM 推薦回應"""
    recommendations = []
    lines = text.split('\n')
    
    current_recipe = {}
    for line in lines:
        line = line.strip()
        if line.startswith(('1.', '2.', '3.')):
            if current_recipe:
                recommendations.append(current_recipe)
            current_recipe = {'name': line.split('.', 1)[1].strip()}
        elif '主要食材：' in line:
            current_recipe['main_ingredients'] = line.split('：', 1)[1].strip()
        elif '預估烹飪時間：' in line:
            current_recipe['cooking_time'] = line.split('：', 1)[1].strip()
        elif '難度：' in line:
            current_recipe['difficulty'] = line.split('：', 1)[1].strip()
    
    if current_recipe:
        recommendations.append(current_recipe)
    
    return recommendations

# --- LineBot 設定 ---
configuration = Configuration(access_token=LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

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
    
    # 儲存到資料庫
    try:
        recipe = Recipe(
            user_id=user_id,
            user_message=user_message,
            recipe_title="多輪對話回應",
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
        line_bot_api.reply_message(
            ReplyMessageRequest(
                replyToken=event.reply_token,
                messages=[TextMessage(text=ai_response)],
                notificationDisabled=False
            )
        )

# --- 健康檢查路由 ---
@app.route("/health", methods=['GET'])
def health_check():
    recipe_count = get_recipe_count()
    return jsonify({
        "status": "healthy",
        "recipe_count": recipe_count,
        "message": f"資料庫中有 {recipe_count} 個食譜記錄",
        "conversation_users": len(conversation_state.user_states),
        "llm_available": LLM_AVAILABLE
    })

# --- 主程式 ---
if __name__ == "__main__":
    print("=== MomsHero LLM 多輪對話版本啟動 ===")
    print(f"資料庫中現有食譜數量: {get_recipe_count()}")
    print(f"LLM 可用狀態: {LLM_AVAILABLE}")
    print("多輪對話功能已啟用，支援食材上傳、推薦選擇、詳細食譜、替代方案")
    print("健康檢查端點: http://localhost:5000/health")
    print("=" * 50)
    
    app.run(debug=True, host='0.0.0.0', port=5000) 