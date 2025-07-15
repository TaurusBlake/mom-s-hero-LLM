#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
簡化的測試伺服器
"""

from flask import Flask, request, render_template, jsonify

app = Flask(__name__)

@app.route("/")
def home():
    return "MomsHero 測試伺服器運行中！"

@app.route("/health")
def health():
    return jsonify({
        "status": "healthy",
        "message": "伺服器正常運行"
    })

@app.route("/test_conversation", methods=['GET', 'POST'])
def test_conversation():
    if request.method == 'GET':
        return render_template('test_conversation.html')
    
    data = request.get_json()
    user_id = data.get('user_id', 'test_user')
    user_message = data.get('message', '測試訊息')
    
    return jsonify({
        "user_message": user_message,
        "response": f"收到您的訊息：{user_message}",
        "current_stage": "idle",
        "ingredients": [],
        "recommendations_count": 0
    })

if __name__ == "__main__":
    print("=== 簡化測試伺服器啟動 ===")
    print("測試端點: http://localhost:5000/test_conversation")
    print("=" * 30)
    
    app.run(debug=True, host='0.0.0.0', port=5000) 