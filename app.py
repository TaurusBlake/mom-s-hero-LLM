# app.py
import logging
import os
from flask import Flask, request, abort

# --- LangChain 核心元件 ---
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain_community.callbacks import get_openai_callback

# --- LineBot 核心元件 ---
from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import (
    Configuration, ApiClient, MessagingApi,
    ReplyMessageRequest, TextMessage
)
from linebot.v3.webhooks import MessageEvent, TextMessageContent

# --- 1. 初始化與設定 ---
app = Flask(__name__)

# --- 請填入您的金鑰 ---
# 設定您的 Google API 金鑰
os.environ["GOOGLE_API_KEY"] = "AIzaSyBVFqQc14brzOkKHDfTdkzsuzAkEy_6c1o"
# 設定 LineBot 的憑證
LINE_CHANNEL_ACCESS_TOKEN = "okTpZjGGPFjS9VW+rvt6od3CZZ/iANPqcnRBZwB1OEPNICTlIQA8J3fwCVROkBv9UgrKMcxUIPVwMW6den4u8LTxs5xFDhOBNG1QYoDWYEx5fr57vZh5QsfOaDhh3ZdzKcmykxn5gz+GAd1MWM6WhAdB04t89/1O/w1cDnyilFU="
LINE_CHANNEL_SECRET = "24caeecda56a7cb57c90aeb553767ec9"
# ---------------------

# --- 2. 設定日誌 (Logging) ---
# 設定日誌記錄器，將日誌寫入到 token_usage.log 檔案中
logging.basicConfig(
    level=logging.INFO, # 設定記錄的最低等級為 INFO
    format='%(asctime)s - %(levelname)s - %(message)s', # 設定日誌格式
    filename='token_usage.log', # 指定日誌檔案名稱
    filemode='a' # 'a' 表示附加模式，'w' 表示覆寫模式
)

# --- 2. 載入 LangChain 元件 ---

print("正在啟動並載入 LangChain RAG 系統...")

# a. 初始化 LLM (大型語言模型) - 使用我們決定的 1.5 Flash 版本
llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.5)

# b. 初始化嵌入模型 (Embedding Model) - 必須和建立資料庫時用的模型一致
embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

# c. 載入您剛剛建立好的本地 ChromaDB 向量資料庫
#    請確保這個路徑與您 index.py 中的 PERSIST_DIRECTORY 完全一致
persist_directory = "./chroma_db_china_travel"
db = Chroma(persist_directory=persist_directory, embedding_function=embeddings)

# d. 建立一個檢索器 (Retriever)
retriever = db.as_retriever()

# --- 2. 建立一個更明確的 Prompt 模板 ---
prompt_template = """
請依據以下提供的「參考資料」，使用專業、友善的語氣，並以「繁體中文」來回答使用者的「問題」。
- 請完全根據「參考資料」的內容來回答，不要使用您自己的任何外部知識。
- 如果參考資料中找不到答案，或者資料不足以回答問題，請明確地回答「根據我手邊的旅遊文件，目前找不到相關資訊。」

---
[參考資料]:
{context}
---
[問題]:
{question}
---
[回答 (繁體中文)]:
"""

# 3. 將模板字串轉換為 LangChain 的 Prompt 物件
PROMPT = PromptTemplate(
    template=prompt_template, input_variables=["context", "question"]
)

# e. 建立一個 RetrievalQA 鏈
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=retriever,
    chain_type_kwargs={"prompt": PROMPT}, # <--- 關鍵在這裡！
    return_source_documents=True # 建議開啟，方便除錯時查看檢索到的來源
)

print("LangChain RAG 系統已成功載入並準備就緒！")

# --- 3. LineBot Webhook 程式碼 ---
configuration = Configuration(access_token=LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

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

@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    user_question = event.message.text
    
    # 使用 LangChain Callback 來追蹤 Token 使用量
    with get_openai_callback() as cb:
        # 呼叫 RAG 鏈來處理問題並生成答案
        result = qa_chain.invoke(user_question)
        
        # 3. 將 Token 資訊寫入日誌檔案
        log_message = (
            f"Question: \"{user_question}\", "
            f"Total Tokens: {cb.total_tokens}, "
            f"Prompt Tokens: {cb.prompt_tokens}, "
            f"Completion Tokens: {cb.completion_tokens}, "
            f"Total Cost (USD): ${cb.total_cost:.6f}"
        )
        logging.info(log_message)
        # 同時也在終端機印出，方便即時觀察
        print(log_message)

    ai_answer = result['result']
    
    # 將 AI 生成的答案透過 Line 回傳給使用者
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        line_bot_api.reply_message_with_http_info(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text=ai_answer)]
            )
        )

if __name__ == "__main__":
    # 啟動 Flask 伺服器
    # 注意：在部署到雲端平台時，通常不會用 app.run()，而是由 Gunicorn 等 WSGI 伺服器來啟動
    # 但在本地端測試，app.run() 是最方便的
    app.run()