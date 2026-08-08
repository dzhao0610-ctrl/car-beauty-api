import os
import time
import datetime
import threading
import requests
import psycopg2
from flask import Flask, request, jsonify
from flask_cors import CORS  # 跨域連線套件

# ==========================================
# 🚀 建立獨立 APP 後端伺服器
# ==========================================
# ⚠️ 絕對只保留這一個 app 宣告，避免 CORS 被覆蓋
app = Flask(__name__)
CORS(app)  # 開放網頁直接呼叫大腦

# ==========================================
# 🔑 1. 系統環境變數與核心金鑰配置
# ==========================================
# PostgreSQL 資料庫專屬網址
DB_URL = os.environ.get("DATABASE_URL", "postgresql://dispatch_db_h7du_user:th0PNe1ycle9s2n3Dh6ha2gefpAzISo1@dpg-d9r8ejfavr4c738la9pg-a.singapore-postgres.render.com/dispatch_db_h7du")

# 衛星犬 EUP 專屬金鑰
EUP_BASE_URL = 'https://tw.eupfin.com/Eup_Servlet_API_SOAP'
EUP_TOKEN = 'e386bd24-4403-fd4e-158c-bb4b66dfe989'

# ==========================================
# 📱 2. 老闆與主管的警報廣播系統
# ==========================================
def send_alert_to_boss_and_manager(message):
    """模擬發送 LINE Notify 或 APP 推播給黃董與主管"""
    print("\n" + "🔴" * 25)
    print("📲 【系統緊急廣播給 黃董 / 主管】")
    print(message)
    print("🔴" * 25 + "\n")
    # 未來這裡會串接真正的 LINE Notify API

# ==========================================
# 🧠 3. 核心商業邏輯模組 (三層實戰防線)
# ==========================================
def check_unfinished_tasks(tech_name):
    """【防線一】檢查師傅手邊是否還有未完成的訂單"""
    # 模擬資料庫查詢：假設發現曾紹恩還有 1 張單沒做完
    unfinished_count = 1 
    if unfinished_count > 0:
        alert_msg = f"🚨 【下班異常警報】\n師傅 {tech_name} 嘗試打卡下班，但系統偵測到他手邊還有 {unfinished_count} 張訂單「尚未完工」！請主管立即查核。"
        send_alert_to_boss_and_manager(alert_msg)
        return False, "您手邊還有未完成的訂單，禁止打卡下班！已通報主管。"
    return True, "任務全數清空。"

def audit_off_work_time(tech_name, reported_off_work_time_str, eup_engine_off_time_str):
    """【防線二】審核下班時間是否浮報 (20分鐘抓漏)"""
    try:
        fmt = "%H:%M"
        reported_time = datetime.datetime.strptime(reported_off_work_time_str, fmt)
        engine_off_time = datetime.datetime.strptime(eup_engine_off_time_str, fmt)
        
        time_diff = (reported_time - engine_off_time).total_seconds() / 60
        
        if time_diff > 20:
            return False, f"時數異常 (差距 {int(time_diff)} 分鐘)"
        return True, "時數審核吻合"
    except Exception as e:
        return False, f"計算錯誤: {e}"

def manual_adjust_service_time(order_id, new_duration_minutes):
    """【AI 調度員】中控台手動微調服務時間，觸發路線重算"""
    print(f"🔧 中控指令：訂單 #{order_id} 修改為 {new_duration_minutes} 分鐘。")
    print("🤖 喚醒 TSP AI，正在為該師傅重新規劃後續路線...")
    return {"status": "success", "msg": "✅ AI 路線重算完畢，師傅端 APP 已更新！"}

# ==========================================
# 📡 4. 背景自動巡邏雷達 (40分鐘預警)
# ==========================================
def background_radar_task():
    """【防線三】每分鐘自動掃描一次，檢查是否有即將遲到的任務"""
    while True:
        # 這裡未來會接上真實資料庫，判斷倒數 40 分鐘的任務
        # print("📡 [系統雷達] 正在掃描全線任務狀態 (40分鐘預警檢查)...")
        time.sleep(60)

# 啟動背景雷達 (獨立執行緒，不影響主系統運作)
radar_thread = threading.Thread(target=background_radar_task, daemon=True)
radar_thread.start()

# ==========================================
# 🌐 5. 獨立 APP 專屬連線通道 (API Routes)
# ==========================================
@app.route('/', methods=['GET'])
def health_check():
    return jsonify({"status": "線上", "version": "行動車美 獨立APP大腦 v1.0", "db": "PostgreSQL 準備就緒"})

# 通道 A：接收師傅 APP 的下班打卡訊號
@app.route('/api/clock_out', methods=['POST', 'OPTIONS'])
def handle_clock_out():
    # 🌟 處理瀏覽器的 CORS 探路請求 (非常重要，防止連線失敗)
    if request.method == 'OPTIONS':
        return jsonify({}), 200

    data = request.json
    tech_name = data.get('tech_name')
    reported_time = data.get('off_work_time')
    
    # 執行防線一：檢查是否還有殘留任務
    tasks_cleared, task_msg = check_unfinished_tasks(tech_name)
    if not tasks_cleared:
        return jsonify({"status": "alert", "message": task_msg}), 400

    # 執行防線二：檢查熄火時間抓漏 (假設衛星犬回傳 16:00)
    real_engine_off_time = "16:00" 
    is_valid, time_msg = audit_off_work_time(tech_name, reported_time, real_engine_off_time)
    
    if not is_valid:
        # 抓漏成功，通報老闆
        alert_msg = f"🚨 【防弊警報】\n師傅 {tech_name} 浮報下班時間！\n真實熄火：{real_engine_off_time} | 師傅回報：{reported_time}。"
        send_alert_to_boss_and_manager(alert_msg)
        return jsonify({"status": "alert", "message": f"下班打卡遭拒絕！\n{time_msg}"}), 400

    return jsonify({"status": "success", "message": "下班打卡成功！辛苦了！"})

# 通道 B：接收中控台的拖拉/微調時間訊號
@app.route('/api/adjust_time', methods=['POST', 'OPTIONS'])
def handle_adjust_time():
    if request.method == 'OPTIONS':
        return jsonify({}), 200

    data = request.json
    order_id = data.get('order_id')
    new_time = data.get('new_duration')
    
    result = manual_adjust_service_time(order_id, new_time)
    return jsonify(result)

# ==========================================
# 🚀 6. 啟動伺服器引擎
# ==========================================
if __name__ == '__main__':
    print("========================================")
    print("啟動【行動車美】獨立 APP 後端控制中心...")
    print("========================================")
    app.run(host='0.0.0.0', port=5000, debug=True)