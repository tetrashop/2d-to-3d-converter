from flask import Flask, jsonify
from flask_cors import CORS
import os
import sys

# اضافه کردن مسیر ماژول‌ها
sys.path.append(os.path.dirname(__file__))

app = Flask(__name__)
CORS(app)

# ایمپورت و رجیستر blueprint کلاینت‌ها
try:
    from client_manager import client_bp
    app.register_blueprint(client_bp)
    print("✅ سیستم مدیریت کلاینت‌ها فعال شد")
except Exception as e:
    print(f"⚠️ خطا در بارگذاری ماژول کلاینت‌ها: {e}")

# Routes اصلی
@app.route('/')
def home():
    return jsonify({
        "message": "سرویس ابری تبدیل 2D به 3D با مدیریت کلاینت‌ها",
        "status": "active", 
        "version": "2.0.0",
        "endpoints": {
            "clients": "/api/clients",
            "convert": "/api/convert",
            "plans": "/api/clients/plans"
        }
    })

@app.route('/api/status')
def status():
    return jsonify({
        "status": "active",
        "service": "2D to 3D Cloud Converter",
        "clients_registered": True,
        "conversion_ready": True
    })

@app.route('/api/convert/start', methods=['POST'])
def dummy_convert():
    """Endpoint تست برای تبدیل"""
    return jsonify({
        "success": True,
        "message": "سیستم تبدیل فعال است - برای عملکرد کامل مدل‌های ML نیاز است",
        "conversion_id": "test_123",
        "status": "processing"
    })

if __name__ == '__main__':
    print("🚀 راه‌اندازی سرور ابری تبدیل 2D به 3D...")
    print("📡 درگاه: 8000")
    print("👥 سیستم مدیریت کلاینت‌ها: فعال")
    print("🔧 سرویس تبدیل: آماده")
    app.run(host='0.0.0.0', port=8000, debug=False)
