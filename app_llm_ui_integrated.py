# app_llm_ui_integrated.py - LLM + UI 整合版本 MomsHero Line Bot
import logging
import os
import json
from flask import Flask, request, abort, render_template, jsonify
from dotenv import load_dotenv

# --- LineBot 核心元件 ---
from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import (
    Configuration, ApiClient, MessagingApi,
    ReplyMessageRequest, TextMessage, TemplateMessage,
    CarouselTemplate, CarouselColumn, MessageAction,
    QuickReply, QuickReplyItem
)
from linebot.v3.webhooks import MessageEvent, TextMessageContent, AudioMessageContent, ImageMessageContent
from linebot.v3.messaging.api import MessagingApiBlob

# --- 資料庫模組 ---
from database.models import init_db, save_recipe, Recipe, get_recipe_count

# --- Google Gemini LLM ---
import google.generativeai as genai

# --- 離線食譜模組已移除 ---

# --- 語音處理模組 ---
from speech_processor import init_speech_processor, get_speech_processor

# --- 圖片處理模組 ---
from image_processor import init_image_processor, get_image_processor

# --- 載入環境變數 ---
load_dotenv()

# --- 初始化 Flask 應用 ---
app = Flask(__name__)

# --- 設定金鑰 ---
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")
AZURE_SPEECH_KEY = os.getenv("AZURE_SPEECH_KEY")
AZURE_SPEECH_REGION = os.getenv("AZURE_SPEECH_REGION")

# --- 設定日誌 ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='momshero_llm_ui.log',
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

# --- 初始化 Azure Speech Service ---
try:
    if AZURE_SPEECH_KEY and AZURE_SPEECH_REGION:
        init_speech_processor(AZURE_SPEECH_KEY, AZURE_SPEECH_REGION)
        SPEECH_AVAILABLE = True
        print("Azure Speech Service 初始化成功！")
    else:
        print("未設定 Azure Speech Service 金鑰，語音功能將不可用")
        SPEECH_AVAILABLE = False
except Exception as e:
    print(f"Azure Speech Service 初始化失敗: {e}")
    SPEECH_AVAILABLE = False

# --- 初始化圖片處理器 ---
try:
    if LLM_AVAILABLE:
        init_image_processor(llm_model)
        IMAGE_AVAILABLE = True
        print("圖片處理器初始化成功！")
    else:
        print("LLM 不可用，圖片功能將不可用")
        IMAGE_AVAILABLE = False
except Exception as e:
    print(f"圖片處理器初始化失敗: {e}")
    IMAGE_AVAILABLE = False

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
                'stage': 'idle',  # idle, waiting_for_ingredients, waiting_for_choice, substitution_mode
                'ingredients': [],
                'recommendations': [],
                'selected_recipe': None,
                'recipe_details': None,
                'substitutions': {}  # 替代方案記錄
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
            'recipe_details': None,
            'substitutions': {}
        }

# 全域對話狀態管理器
conversation_state = ConversationState()

# --- UI 功能函數 ---
def create_recipe_carousel(recommendations):
    """創建輪播樣板顯示推薦食譜"""
    logging.info(f"🎠 開始創建輪播樣板，推薦數量: {len(recommendations)}")
    print(f"🎠 開始創建輪播樣板，推薦數量: {len(recommendations)}")
    
    columns = []
    for i, recipe in enumerate(recommendations[:3]):  # 只顯示3個推薦
        logging.info(f"  📋 處理推薦 {i+1}: {recipe}")
        print(f"  📋 處理推薦 {i+1}: {recipe}")
        
        title = recipe.get('name', f'料理 {i+1}')
        ingredients = recipe.get('ingredients', [])
        if isinstance(ingredients, list):
            ingredients_text = ','.join(ingredients[:3])  # 只顯示前3個食材
        else:
            ingredients_text = str(ingredients)[:20]  # 限制長度
        
        text = f"主要食材：{ingredients_text}\n時間：{recipe.get('time', '未知')} 難度：{recipe.get('difficulty', '未知')}"
        
        logging.info(f"  🏷️  輪播項目 {i+1}: 標題='{title}', 內容='{text}'")
        print(f"  🏷️  輪播項目 {i+1}: 標題='{title}', 內容='{text}'")
        
        column = CarouselColumn(
            title=title[:40],
            text=text[:60],
            actions=[
                MessageAction(label="查看詳細食譜", text=f"我要做{title}"),
                MessageAction(label="重新開始", text="重新開始")
            ],
            thumbnailImageUrl=None,
            imageBackgroundColor=None,
            defaultAction=None
        )
        columns.append(column)
    
    logging.info(f"✅ 輪播樣板創建完成，共 {len(columns)} 個項目")
    print(f"✅ 輪播樣板創建完成，共 {len(columns)} 個項目")
    
    return TemplateMessage(
        altText="為您推薦的料理",
        template=CarouselTemplate(columns=columns),
        quickReply=None
    )

def create_recipe_details_with_ui(recipe_details):
    """創建帶有 UI 按鈕的詳細食譜"""
    details = f"【{recipe_details.get('name', '未知料理')}】詳細食譜\n\n"
    
    # 食材部分
    details += "【食材準備】\n"
    ingredients = recipe_details.get('ingredients', [])
    if isinstance(ingredients, list):
        for ingredient in ingredients:
            if isinstance(ingredient, dict):
                name = ingredient.get('name', '')
                amount = ingredient.get('amount', '')
                note = ingredient.get('note', '')
                details += f"• {name} {amount} {note}\n"
            else:
                details += f"• {ingredient}\n"
    else:
        details += f"• {ingredients}\n"
    
    details += f"\n【烹調時間】\n• {recipe_details.get('time', '未知')}\n\n"
    details += f"【難度等級】\n• {recipe_details.get('difficulty', '未知')}\n\n"
    
    # 步驟部分
    details += "【詳細步驟】\n"
    steps = recipe_details.get('steps', [])
    if isinstance(steps, list):
        for i, step in enumerate(steps):
            details += f"{i+1}. {step}\n"
    else:
        details += f"1. {steps}\n"
    
    details += f"\n【小技巧】\n• {recipe_details.get('tips', '無')}\n\n"
    
    if 'nutrition' in recipe_details:
        details += f"【營養價值】\n• {recipe_details['nutrition']}\n\n"
    
    details += "---\n💡 如果缺少某些食材，請點擊下方按鈕查看替代方案！"
    
    # 建立 Quick Reply 按鈕
    quick_reply_items = [
        QuickReplyItem(action=MessageAction(label="我食材有缺", text="我食材有缺"), imageUrl=None, type="action"),
        QuickReplyItem(action=MessageAction(label="重新開始", text="重新開始"), imageUrl=None, type="action")
    ]
    quick_reply = QuickReply(items=quick_reply_items)
    
    return TextMessage(text=details, quickReply=quick_reply, quoteToken=None)

# --- LLM 輔助函數 ---
def generate_llm_recommendations(user_id, ingredients):
    """使用 LLM 生成食譜推薦（帶重試機制）"""
    import time
    
    if not LLM_AVAILABLE:
        logging.error("LLM 不可用，無法生成推薦")
        return None
    
    ingredients_text = "、".join(ingredients)
    logging.info(f"🤖 開始調用 LLM 生成推薦，食材: {ingredients_text}")
    
    # 簡化 prompt 以減少處理時間
    prompt = f"""根據食材：{ingredients_text}，推薦3道料理，JSON格式回覆：

{{
    "recommendations": [
        {{"name": "料理名", "ingredients": ["食材1", "食材2"], "time": "時間", "difficulty": "難度", "description": "描述"}},
        {{"name": "料理名", "ingredients": ["食材1", "食材2"], "time": "時間", "difficulty": "難度", "description": "描述"}},
        {{"name": "料理名", "ingredients": ["食材1", "食材2"], "time": "時間", "difficulty": "難度", "description": "描述"}}
    ]
}}

要求：簡單實用料理，時間格式如「15分鐘」，難度：簡單/中等/困難，只回覆JSON。"""
    
    # 重試機制
    max_retries = 3
    retry_delay = 2
    
    for attempt in range(max_retries):
        try:
            logging.info(f"🔄 LLM 調用嘗試 {attempt + 1}/{max_retries}")
            
            # 直接使用原有的 LLM 模型
            response = llm_model.generate_content(prompt)
            logging.info(f"✅ LLM 調用完成")
            
            if response and response.text:
                # 清理回應文字
                text = response.text.strip()
                if text.startswith('```json'):
                    text = text[7:]
                if text.endswith('```'):
                    text = text[:-3]
                text = text.strip()
                
                try:
                    data = json.loads(text)
                    recommendations = data.get('recommendations', [])
                    
                    if recommendations:
                        logging.info(f"✅ LLM 成功生成 {len(recommendations)} 個推薦")
                        return recommendations
                    else:
                        logging.warning("LLM 回應中沒有找到推薦")
                        if attempt < max_retries - 1:
                            continue  # 重試
                        return None
                        
                except json.JSONDecodeError as e:
                    logging.error(f"❌ JSON 解析失敗: {e} (嘗試 {attempt + 1})")
                    if attempt < max_retries - 1:
                        continue  # 重試
                    return None
            else:
                logging.error("LLM 沒有返回有效回應")
                if attempt < max_retries - 1:
                    continue  # 重試
                return None
                
        except Exception as e:
            logging.error(f"LLM 調用失敗 (嘗試 {attempt + 1}): {e}")
            if attempt < max_retries - 1:
                logging.info(f"⏰ 等待 {retry_delay} 秒後重試...")
                time.sleep(retry_delay)
                retry_delay *= 2  # 指數退避
                continue
            else:
                logging.error("LLM 推薦生成最終失敗")
                return None
    
    return None

def generate_llm_recipe_details(recipe_name):
    """使用 LLM 生成詳細食譜"""
    try:
        if not LLM_AVAILABLE:
            return None
        
        prompt = f"""
{PROMPT_TEMPLATE}

請為「{recipe_name}」提供詳細的食譜，以JSON格式回覆：

{{
    "name": "{recipe_name}",
    "ingredients": [
        {{"name": "食材名稱", "amount": "份量", "note": "備註"}}
    ],
    "time": "總烹調時間",
    "difficulty": "難度等級",
    "steps": [
        "步驟1",
        "步驟2",
        "步驟3"
    ],
    "tips": "烹調小技巧",
    "nutrition": "營養價值"
}}

請確保：
1. 步驟要詳細且容易理解
2. 食材份量要明確
3. 小技巧要實用
4. 只回覆JSON格式，不要其他文字
"""
        
        response = llm_model.generate_content(prompt)
        
        if response and response.text:
            # 清理回應文字
            text = response.text.strip()
            if text.startswith('```json'):
                text = text[7:]
            if text.endswith('```'):
                text = text[:-3]
            text = text.strip()
            
            try:
                data = json.loads(text)
                return data
                    
            except json.JSONDecodeError as e:
                logging.error(f"JSON 解析失敗: {e}")
                logging.error(f"LLM 回應: {response.text}")
                return None
        else:
            logging.error("LLM 沒有返回有效回應")
            return None
            
    except Exception as e:
        logging.error(f"LLM 詳細食譜生成失敗: {e}")
        return None

def generate_llm_substitutions(missing_ingredients):
    """使用 LLM 生成替代方案"""
    try:
        if not LLM_AVAILABLE:
            return None
        
        ingredients_text = "、".join(missing_ingredients)
        prompt = f"""
用戶缺少以下食材：{ingredients_text}

請為每個缺少的食材提供3個替代方案，以JSON格式回覆：

{{
    "substitutions": {{
        "食材1": ["替代方案1", "替代方案2", "替代方案3"],
        "食材2": ["替代方案1", "替代方案2", "替代方案3"]
    }},
    "notes": "替代建議說明"
}}

請確保：
1. 替代方案要實用且容易取得
2. 考慮營養價值和口感
3. 提供烹調調整建議
4. 只回覆JSON格式，不要其他文字
"""
        
        response = llm_model.generate_content(prompt)
        
        if response and response.text:
            # 清理回應文字
            text = response.text.strip()
            if text.startswith('```json'):
                text = text[7:]
            if text.endswith('```'):
                text = text[:-3]
            text = text.strip()
            
            try:
                data = json.loads(text)
                return data
                    
            except json.JSONDecodeError as e:
                logging.error(f"JSON 解析失敗: {e}")
                logging.error(f"LLM 回應: {response.text}")
                return None
        else:
            logging.error("LLM 沒有返回有效回應")
            return None
            
    except Exception as e:
        logging.error(f"LLM 替代方案生成失敗: {e}")
        return None

def generate_alternatives_with_llm_simple(user_id, message, selected_recipe):
    """使用 LLM 生成替代方案建議（簡化版，類似 app_llm.py）"""
    if not LLM_AVAILABLE:
        logging.error("LLM 不可用，無法生成替代方案")
        return None
    
    try:
        logging.info(f"🤖 開始調用 LLM 生成替代方案")
        print(f"🤖 開始調用 LLM 生成替代方案")
        
        # 構建提示詞（簡潔版）
        prompt = f"""用戶想做：{selected_recipe.get('name', '未知料理')}
用戶說：{message}

請提供簡潔的替代方案建議，格式要求：

1. 不要開場白，直接給建議
2. 每個建議1-2行即可
3. 如果食材可以省略，直接說「可以不用」
4. 用點列式呈現，簡潔明瞭

範例格式：
• 沒有醬油 → 用鹽+糖調味，或直接省略
• 沒有蒜 → 用蒜粉代替，或可以不用
• 沒有雞蛋 → 用澱粉水代替

請保持簡短實用。"""

        logging.info(f"📝 LLM 替代方案提示詞長度: {len(prompt)} 字元")
        print(f"📝 LLM 替代方案提示詞長度: {len(prompt)} 字元")
        
        response = llm_model.generate_content(prompt)
        
        logging.info(f"✅ LLM 替代方案調用完成")
        print(f"✅ LLM 替代方案調用完成")
        
        if response and response.text:
            response_text = response.text.strip()
            
            # 驗證回應格式
            if len(response_text) < 20:
                logging.warning(f"LLM 替代方案回應過短: {response_text}")
                return None
            
            logging.info(f"✅ LLM 替代方案生成成功，長度: {len(response_text)} 字元")
            print(f"✅ LLM 替代方案生成成功，長度: {len(response_text)} 字元")
            
            return response_text
        else:
            logging.error("LLM 替代方案沒有返回有效回應")
            return None
            
    except Exception as e:
        logging.error(f"LLM 替代方案生成失敗: {e}")
        print(f"❌ LLM 替代方案生成失敗: {e}")
        
        # 檢查是否是配額錯誤
        if "quota" in str(e).lower() or "429" in str(e):
            return "抱歉，AI 服務的免費額度已用完。請稍後再試，或考慮升級到付費版本。"
        else:
            return None

# --- 多輪對話處理函數 ---
def handle_conversation(user_id, user_message):
    """處理多輪對話邏輯"""
    state = conversation_state.get_user_state(user_id)
    
    # 檢查是否要重置對話
    if any(keyword in user_message for keyword in ['重新開始', '重置', '重新', '開始']):
        conversation_state.reset_user_state(user_id)
        return TextMessage(text="好的！讓我們重新開始。請告訴我您有哪些食材，我會為您推薦適合的料理！", quickReply=None, quoteToken=None)
    
    # 檢查是否要看詳細食譜
    if user_message.startswith("我要做"):
        recipe_name = user_message.replace("我要做", "").strip()
        return handle_recipe_details_request(user_id, recipe_name)
    
    # 檢查是否要詢問替代方案
    if "我食材有缺" in user_message:
        conversation_state.update_user_state(user_id, {'stage': 'substitution_mode'})
        quick_reply_items = [
            QuickReplyItem(action=MessageAction(label="重新開始", text="重新開始"), imageUrl=None, type="action"),
            QuickReplyItem(action=MessageAction(label="完成查詢", text="完成查詢"), imageUrl=None, type="action")
        ]
        quick_reply = QuickReply(items=quick_reply_items)
        return TextMessage(
            text="請告訴我您缺少哪些食材，我會為您提供替代建議。\n\n例如：沒有雞蛋、沒有醬油、沒有蒜...",
            quickReply=quick_reply,
            quoteToken=None
        )
    
    # 檢查是否要完成查詢
    if "完成查詢" in user_message:
        conversation_state.reset_user_state(user_id)
        quick_reply_items = [
            QuickReplyItem(action=MessageAction(label="重新開始", text="重新開始"), imageUrl=None, type="action")
        ]
        quick_reply = QuickReply(items=quick_reply_items)
        return TextMessage(
            text="查詢已完成！✅\n\n希望這些建議對您有幫助。如果您想要查看其他料理推薦，請點擊「重新開始」。",
            quickReply=quick_reply,
            quoteToken=None
        )
    
    # 處理替代方案多輪問答
    if state['stage'] == 'substitution_mode':
        return handle_substitution_input(user_id, user_message)
    
    # 檢查訊息是否與食譜相關（對於來自圖片分析的短回應要寬鬆處理）
    if len(user_message) > 10 and not is_recipe_related(user_message):
        return TextMessage(text="抱歉，我是專門協助料理和食譜的助手。請詢問與食材、料理、烹調相關的問題，我很樂意為您提供幫助！", quickReply=None, quoteToken=None)
    
    # 如果 LLM 不可用，提供明確提示
    if not LLM_AVAILABLE:
        return TextMessage(text="抱歉，AI 服務目前暫時無法使用。請稍後再試，我會盡快恢復為您提供食譜建議！", quickReply=None, quoteToken=None)
    
    # 根據當前階段處理訊息
    if state['stage'] == 'idle':
        return handle_idle_stage(user_id, user_message)
    elif state['stage'] == 'waiting_for_ingredients':
        return handle_ingredients_stage(user_id, user_message)
    elif state['stage'] == 'waiting_for_choice':
        return handle_choice_stage(user_id, user_message)
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
        return generate_recommendations_with_ui(user_id, ingredients)
    else:
        # 如果沒有識別到食材，直接引導用戶提供食材
        return TextMessage(text="""歡迎來到 MomsHero！👩‍🍳

我是您的專屬料理助手，請告訴我您有哪些食材，我會為您推薦適合的料理！

例如：
- 「我有雞蛋、白飯、蔥」
- 「家裡有豬肉、青菜、豆腐」
- 「冰箱裡有雞胸肉、胡蘿蔔」
- 「我有鮭魚、秋葵、松露」

請分享您的食材吧！""", quickReply=None, quoteToken=None)

def handle_ingredients_stage(user_id, user_message):
    """處理食材收集階段的訊息"""
    # 檢查是否要重新提供食材
    if any(keyword in user_message for keyword in ['重新', '換', '其他']):
        ingredients = extract_ingredients(user_message)
        if ingredients:
            conversation_state.update_user_state(user_id, {
                'ingredients': ingredients
            })
            return generate_recommendations_with_ui(user_id, ingredients)
    
    # 檢查是否包含新的食材資訊
    ingredients = extract_ingredients(user_message)
    if ingredients:
        conversation_state.update_user_state(user_id, {
            'ingredients': ingredients
        })
        return generate_recommendations_with_ui(user_id, ingredients)
    
    # 如果沒有新的食材資訊，引導用戶提供
    return TextMessage(text="請告訴我您有哪些食材，我會為您推薦適合的料理！", quickReply=None, quoteToken=None)

def handle_choice_stage(user_id, user_message):
    """處理選擇階段的訊息"""
    # 這裡可以處理用戶對詳細食譜的回應
    return TextMessage(text="如果您需要查看其他食譜或有任何問題，請告訴我！", quickReply=None, quoteToken=None)

def handle_recipe_details_request(user_id, recipe_name):
    """處理詳細食譜請求"""
    state = conversation_state.get_user_state(user_id)
    
    # 先從推薦列表中查找
    for recipe in state.get('recommendations', []):
        if recipe.get('name') == recipe_name:
            # 使用 LLM 生成更詳細的食譜
            detailed_recipe = generate_llm_recipe_details(recipe_name)
            if detailed_recipe:
                conversation_state.update_user_state(user_id, {'selected_recipe': detailed_recipe})
                return create_recipe_details_with_ui(detailed_recipe)
            else:
                # 如果 LLM 失敗，使用原始推薦資料
                conversation_state.update_user_state(user_id, {'selected_recipe': recipe})
                return create_recipe_details_with_ui(recipe)
    
    # 如果沒找到，嘗試用 LLM 直接生成
    detailed_recipe = generate_llm_recipe_details(recipe_name)
    if detailed_recipe:
        conversation_state.update_user_state(user_id, {'selected_recipe': detailed_recipe})
        return create_recipe_details_with_ui(detailed_recipe)
    
    # 離線食譜已移除
    
    return TextMessage(text=f"抱歉，找不到「{recipe_name}」的詳細食譜。", quickReply=None, quoteToken=None)

def handle_substitution_input(user_id, user_message):
    """處理替代方案輸入"""
    state = conversation_state.get_user_state(user_id)
    selected_recipe = state.get('selected_recipe', {})
    
    logging.info(f"🔄 處理替代方案輸入: 用戶 {user_id}, 訊息: '{user_message}'")
    print(f"🔄 處理替代方案輸入: 用戶 {user_id}, 訊息: '{user_message}'")
    
    # 使用 LLM 生成替代方案建議（類似 app_llm.py 的方式）
    llm_response = generate_alternatives_with_llm_simple(user_id, user_message, selected_recipe)
    
    if llm_response:
        # 創建 Quick Reply 按鈕
        quick_reply_items = [
            QuickReplyItem(action=MessageAction(label="重新開始", text="重新開始"), imageUrl=None, type="action"),
            QuickReplyItem(action=MessageAction(label="完成查詢", text="完成查詢"), imageUrl=None, type="action")
        ]
        quick_reply = QuickReply(items=quick_reply_items)
        
        return TextMessage(text=llm_response, quickReply=quick_reply, quoteToken=None)
    else:
        # 如果 LLM 失敗，提供基本回應
        quick_reply_items = [
            QuickReplyItem(action=MessageAction(label="重新開始", text="重新開始"), imageUrl=None, type="action"),
            QuickReplyItem(action=MessageAction(label="完成查詢", text="完成查詢"), imageUrl=None, type="action")
        ]
        quick_reply = QuickReply(items=quick_reply_items)
        
        return TextMessage(
            text="抱歉，我沒有找到您提到的食材的替代方案。\n\n請試試其他食材，例如：雞蛋、醬油、蒜、蔥、豬肉、牛肉、番茄、青椒、豆腐、豆瓣醬",
            quickReply=quick_reply,
            quoteToken=None
        )

def generate_recommendations_with_ui(user_id, ingredients):
    """生成帶有 UI 的推薦食譜"""
    logging.info(f"🎯 開始生成UI推薦，用戶: {user_id}, 食材: {ingredients}")
    print(f"🎯 開始生成UI推薦，用戶: {user_id}, 食材: {ingredients}")
    
    try:
        # 嘗試使用 LLM 生成推薦
        if LLM_AVAILABLE:
            logging.info(f"📞 調用 LLM 推薦生成器")
            print(f"📞 調用 LLM 推薦生成器")
            
            recommendations = generate_llm_recommendations(user_id, ingredients)
            
            logging.info(f"📊 LLM 推薦結果: {recommendations}")
            print(f"📊 LLM 推薦結果: {recommendations}")
            
            if recommendations and isinstance(recommendations, list):
                logging.info(f"✅ LLM 推薦成功，生成 {len(recommendations)} 個推薦")
                print(f"✅ LLM 推薦成功，生成 {len(recommendations)} 個推薦")
                
                conversation_state.update_user_state(user_id, {'recommendations': recommendations})
                carousel = create_recipe_carousel(recommendations)
                
                logging.info(f"🎠 輪播樣板創建完成")
                print(f"🎠 輪播樣板創建完成")
                
                return carousel
            else:
                logging.warning(f"⚠️  LLM 推薦結果為空或格式錯誤")
                print(f"⚠️  LLM 推薦結果為空或格式錯誤")
        else:
            logging.warning(f"⚠️  LLM 不可用，跳過 LLM 推薦")
            print(f"⚠️  LLM 不可用，跳過 LLM 推薦")
            
    except Exception as e:
        logging.error(f"❌ LLM 推薦生成失敗: {e}")
        print(f"❌ LLM 推薦生成失敗: {e}")
    
    # 如果 LLM 失敗，直接提供錯誤訊息
    logging.error(f"❌ 所有推薦方法都失敗，返回錯誤訊息")
    print(f"❌ 所有推薦方法都失敗，返回錯誤訊息")
    
    return TextMessage(text="抱歉，目前無法為您生成推薦。請稍後再試！", quickReply=None, quoteToken=None)


# --- 輔助函數 ---
def is_recipe_related(message):
    """檢查訊息是否與食譜相關"""
    recipe_keywords = [
        '食材', '料理', '烹調', '煮', '炒', '蒸', '炸', '烤', '燉', '湯',
        '飯', '麵', '菜', '肉', '魚', '蛋', '豆腐', '青菜', '調味',
        '食譜', '做法', '步驟', '時間', '難度', '技巧', '小貼士'
    ]
    
    # 檢查是否包含食材名稱
    ingredient_keywords = [
        '雞蛋', '豬肉', '牛肉', '雞肉', '魚', '蝦', '豆腐', '青菜', '番茄',
        '洋蔥', '蒜', '薑', '蔥', '醬油', '鹽', '糖', '油', '米', '麵'
    ]
    
    message_lower = message.lower()
    
    # 檢查食譜相關關鍵字
    for keyword in recipe_keywords:
        if keyword in message_lower:
            return True
    
    # 檢查食材關鍵字
    for keyword in ingredient_keywords:
        if keyword in message_lower:
            return True
    
    # 檢查是否包含數量詞（可能表示食材）
    quantity_patterns = ['個', '顆', '片', '塊', '條', '根', '把', '包', '罐', '瓶']
    for pattern in quantity_patterns:
        if pattern in message:
            return True
    
    return False

def extract_ingredients(message):
    """從訊息中提取食材"""
    logging.info(f"🔍 開始提取食材，訊息: '{message}'")
    
    ingredients = []
    
    # 常見食材關鍵字
    ingredient_keywords = [
        '雞蛋', '豬肉', '牛肉', '雞肉', '魚', '蝦', '豆腐', '青菜', '番茄',
        '洋蔥', '蒜', '薑', '蔥', '醬油', '鹽', '糖', '油', '米', '麵',
        '胡蘿蔔', '馬鈴薯', '青椒', '甜椒', '芹菜', '韭菜', '香菜',
        '白菜', '高麗菜', '包菜', '香菇', '金針菇', '木耳', '紅蘿蔔',
        '花椰菜', '青花菜', '玉米', '小黃瓜', '冬瓜', '南瓜', '茄子'
    ]
    
    # 先檢查常見食材
    message_lower = message.lower()
    for ingredient in ingredient_keywords:
        if ingredient in message_lower:
            ingredients.append(ingredient)
    
    # 如果沒找到食材，嘗試用 LLM 來識別
    if not ingredients and LLM_AVAILABLE and len(message) > 2:
        try:
            prompt = f"""請從以下訊息中識別出食材名稱，只回傳食材名稱，用逗號分隔：

訊息：{message}

規則：
1. 只識別明確提到的食材
2. 不要假設或推測用戶有什麼食材
3. 不要添加用戶沒有提到的食材
4. 如果沒有明確的食材，回傳「無」

請只回傳食材名稱或「無」，不要其他文字："""

            response = llm_model.generate_content(prompt)
            llm_response = response.text.strip()
            
            if llm_response != '無' and llm_response:
                llm_ingredients = llm_response.split(',')
                for ingredient in llm_ingredients:
                    ingredient = ingredient.strip()
                    if ingredient and len(ingredient) > 1 and ingredient != '無':
                        ingredients.append(ingredient)
                        
        except Exception as e:
            logging.error(f"LLM 食材識別失敗: {e}")
    
    logging.info(f"✅ 食材提取完成，找到: {ingredients}")
    
    # 如果還是沒有找到食材，假設有基本食材來生成推薦
    if not ingredients and len(message) > 0:
        ingredients = ['雞蛋', '青菜', '白飯']  # 預設基本食材
    
    return ingredients

# --- Line Bot 設定 ---
configuration = Configuration(access_token=LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

# --- Webhook 處理 ---
@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    app.logger.info(f"Request body: {body}")
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

@handler.add(MessageEvent, message=TextMessageContent)
def handle_text_message(event):
    """處理文字訊息"""
    user_id = event.source.user_id
    user_message = event.message.text
    
    try:
        # 使用整合的對話處理函數
        response_message = handle_conversation(user_id, user_message)
        
        with ApiClient(configuration) as api_client:
            line_bot_api = MessagingApi(api_client)
            line_bot_api.reply_message_with_http_info(
                ReplyMessageRequest(
                    replyToken=event.reply_token,
                    messages=[response_message],
                    notificationDisabled=None
                )
            )
    except Exception as e:
        logging.error(f"處理文字訊息時發生錯誤: {e}")
        # 發送錯誤訊息
        error_message = TextMessage(text="抱歉，處理您的訊息時發生錯誤。請稍後再試！", quickReply=None, quoteToken=None)
        with ApiClient(configuration) as api_client:
            line_bot_api = MessagingApi(api_client)
            line_bot_api.reply_message_with_http_info(
                ReplyMessageRequest(
                    replyToken=event.reply_token,
                    messages=[error_message],
                    notificationDisabled=None
                )
            )

@handler.add(MessageEvent, message=AudioMessageContent)
def handle_audio_message(event):
    """處理語音訊息"""
    user_id = event.source.user_id
    message_id = event.message.id
    
    logging.info(f"收到來自用戶 {user_id} 的語音訊息: {message_id}")
    
    try:
        if not SPEECH_AVAILABLE:
            response_message = TextMessage(text="抱歉，語音處理功能目前無法使用，請改用文字輸入。", quickReply=None, quoteToken=None)
        else:
            # 獲取語音內容
            with ApiClient(configuration) as api_client:
                blob_api = MessagingApiBlob(api_client)
                try:
                    content = blob_api.get_message_content(message_id)
                except Exception as download_error:
                    logging.error(f"語音下載失敗: {download_error}")
                    raise download_error
                
                # 建立暫存檔案
                temp_dir = "temp_files"
                os.makedirs(temp_dir, exist_ok=True)
                temp_file = os.path.join(temp_dir, f"{user_id}_audio_{message_id}.m4a")
                try:
                    with open(temp_file, 'wb') as f:
                        f.write(content)
                except Exception as write_error:
                    logging.error(f"語音檔案寫入失敗: {write_error}")
                    raise write_error
            
            # 使用語音處理器轉文字
            speech_processor = get_speech_processor()
            if speech_processor:
                text = speech_processor.process_line_audio(temp_file)
                
                # 清理暫存檔案
                try:
                    os.remove(temp_file)
                except Exception as e:
                    logging.warning(f"清理語音暫存檔案失敗: {e}")
                
                if text:
                    # 語音轉文字成功，使用對話邏輯處理
                    logging.info(f"🎤 語音識別成功: '{text}'")
                    response_message = handle_conversation(user_id, text)
                    
                    # 儲存到資料庫
                    try:
                        recipe = Recipe(
                            user_id=user_id,
                            user_message=f"語音訊息: {text}",
                            recipe_title="語音識別回應",
                            recipe_content=str(response_message.text) if hasattr(response_message, 'text') else str(response_message),
                            ingredients="語音識別",
                            cooking_time="測試時間",
                            difficulty="簡單"
                        )
                        save_recipe(recipe)
                        logging.info(f"✅ 語音對話記錄已儲存到資料庫")
                    except Exception as e:
                        logging.error(f"儲存語音對話記錄時發生錯誤: {e}")
                else:
                    # 語音識別失敗
                    logging.warning(f"🎤 語音識別失敗，無法轉換為文字")
                    print(f"🎤 語音識別失敗，無法轉換為文字")
                    response_message = TextMessage(text="抱歉，我無法識別您的語音內容。請改用文字輸入，例如：「我有雞蛋、白飯、蔥，想做蛋炒飯」", quickReply=None, quoteToken=None)
            else:
                # 語音處理器不可用
                response_message = TextMessage(text="抱歉，語音處理功能目前無法使用，請改用文字輸入。", quickReply=None, quoteToken=None)
        
    except Exception as e:
        logging.error(f"處理語音訊息時發生錯誤: {e}")
        response_message = TextMessage(text="抱歉，處理您的語音時發生錯誤，請改用文字輸入。", quickReply=None, quoteToken=None)
    
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        line_bot_api.reply_message_with_http_info(
            ReplyMessageRequest(
                replyToken=event.reply_token,
                messages=[response_message],
                notificationDisabled=None
            )
        )

@handler.add(MessageEvent, message=ImageMessageContent)
def handle_image_message(event):
    """處理圖片訊息"""
    user_id = event.source.user_id
    message_id = event.message.id
    
    logging.info(f"收到來自用戶 {user_id} 的圖片訊息: {message_id}")
    
    try:
        if not IMAGE_AVAILABLE:
            response_message = TextMessage(text="抱歉，圖片處理功能目前無法使用，請改用文字輸入。", quickReply=None, quoteToken=None)
        else:
            # 獲取圖片內容
            with ApiClient(configuration) as api_client:
                blob_api = MessagingApiBlob(api_client)
                try:
                    content = blob_api.get_message_content(message_id)
                except Exception as download_error:
                    logging.error(f"圖片下載失敗: {download_error}")
                    raise download_error
                
                # 建立暫存檔案
                temp_dir = "temp_files"
                os.makedirs(temp_dir, exist_ok=True)
                temp_file = os.path.join(temp_dir, f"{user_id}_image_{message_id}.jpg")
                try:
                    with open(temp_file, 'wb') as f:
                        f.write(content)
                except Exception as write_error:
                    logging.error(f"圖片檔案寫入失敗: {write_error}")
                    raise write_error
            
            # 使用圖片處理器分析
            image_processor = get_image_processor()
            if image_processor:
                analysis_result = image_processor.analyze_fridge_image(temp_file)
                
                # 清理暫存檔案
                try:
                    os.remove(temp_file)
                    logging.info(f"暫存檔案已清理: {temp_file}")
                except Exception as e:
                    logging.warning(f"清理暫存檔案失敗: {e}")
                
                if analysis_result:
                    # 圖片分析成功，使用對話邏輯處理
                    response_message = handle_conversation(user_id, analysis_result)
                else:
                    # 圖片分析失敗
                    response_message = TextMessage(text="抱歉，我無法識別圖片中的食材。請確保圖片清晰，或改用文字描述您的食材。", quickReply=None, quoteToken=None)
            else:
                # 圖片處理器不可用
                response_message = TextMessage(text="抱歉，圖片處理功能目前無法使用，請改用文字輸入。", quickReply=None, quoteToken=None)
        
    except Exception as e:
        logging.error(f"處理圖片訊息時發生錯誤: {e}")
        response_message = TextMessage(text="抱歉，處理您的圖片時發生錯誤，請改用文字輸入。", quickReply=None, quoteToken=None)
    
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        line_bot_api.reply_message_with_http_info(
            ReplyMessageRequest(
                replyToken=event.reply_token,
                messages=[response_message],
                notificationDisabled=None
            )
        )

# --- 健康檢查端點 ---
@app.route("/health", methods=['GET'])
def health_check():
    return {
        "status": "healthy",
        "message": "MomsHero LLM UI 整合版運行中",
        "features": {
            "llm_available": LLM_AVAILABLE,
            "speech_available": SPEECH_AVAILABLE,
            "image_available": IMAGE_AVAILABLE
        },
        "ui_features": [
            "輪播樣板推薦",
            "Quick Reply 按鈕",
            "LLM 替代方案功能",
            "多輪對話支援",
            "LLM 智能推薦"
        ]
    }

# --- 主程式 ---
if __name__ == "__main__":
    # 从环境变量 PORT 或 WEBSITES_PORT 读取端口，预设回退到 5000
    port = int(os.environ.get("PORT", os.environ.get("WEBSITES_PORT", 5000)))
    print("=== MomsHero LLM UI 整合版啟動 ===")
    print(f"資料庫中現有食譜數量: {get_recipe_count()}")
    print(f"LLM 可用狀態: {LLM_AVAILABLE}")
    print(f"語音處理可用狀態: {SPEECH_AVAILABLE}")
    print(f"圖片處理可用狀態: {IMAGE_AVAILABLE}")
    print("整合功能：")
    print("- ✅ LLM 智能食譜推薦")
    print("- ✅ 輪播樣板 UI 顯示")
    print("- ✅ Quick Reply 互動按鈕")
    print("- ✅ LLM 食材替代方案功能")
    print("- ✅ 多輪對話支援")
    print("- 🎤 語音轉文字功能")
    print("- 📷 圖片食材識別功能")
    print(f"健康檢查端點: http://localhost:{port}/health")
    print("=" * 50)
     # 监听所有网络接口与环境变量指定端口
    app.run(debug=True, host='0.0.0.0', port=port)