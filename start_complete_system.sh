#!/bin/bash

echo "🚀 راه‌اندازی کامل سیستم ابری تبدیل 2D به 3D با مدیریت کلاینت‌ها..."
echo "⏳ لطفاً منتظر بمانید..."

# کشتن پروسه‌های قبلی
echo "🔴 متوقف کردن سرویس‌های قبلی..."
pkill -f "python.*(8000|3002)" 2>/dev/null
sleep 3

cd ~/2d-to-3d-converter

# بررسی وجود پوشه‌های لازم
mkdir -p backend/uploads backend/outputs logs

echo "🔧 نصب وابستگی‌های پایتون..."
pip3 install flask flask-cors --quiet

echo "🏗️ راه‌اندازی سرور اصلی..."
cd backend
python3 cloud_converter_with_clients.py > ../logs/server.log 2>&1 &
SERVER_PID=$!

echo "⏳ منتظر راه‌اندازی سرور (10 ثانیه)..."
sleep 10

echo "🎨 راه‌اندازی فرانت‌اند..."
cd ../frontend
python3 -m http.server 3002 > ../logs/frontend.log 2>&1 &
FRONTEND_PID=$!

# ذخیره PIDها برای مدیریت بهتر
echo $SERVER_PID > ../logs/server.pid
echo $FRONTEND_PID > ../logs/frontend.pid

echo ""
echo "✅ ✅ ✅ سیستم کامل فعال شد!"
echo "=========================================="
echo "🌐 پنل مدیریت کلاینت‌ها: http://localhost:3002/client_dashboard.html"
echo "🔧 سرویس تبدیل ابری: http://localhost:3002/cloud_converter.html" 
echo "🎯 صفحه اصلی: http://localhost:3002"
echo "📊 API سرور: http://localhost:8000"
echo "=========================================="

# نمایش وضعیت سرویس‌ها
sleep 2
echo ""
echo "🔍 بررسی وضعیت سرویس‌ها..."
if curl -s http://localhost:8000 > /dev/null; then
    echo "✅ سرور API فعال"
else
    echo "❌ سرور API مشکل دارد"
fi

if curl -s http://localhost:3002 > /dev/null; then
    echo "✅ فرانت‌اند فعال"
else
    echo "❌ فرانت‌اند مشکل دارد"
fi

echo ""
echo "📋 برای تست سیستم:"
echo "1. ابتدا به پنل مدیریت کلاینت‌ها بروید"
echo "2. یک کلاینت جدید ثبت کنید"
echo "3. API Key دریافت شده را کپی کنید"
echo "4. به سرویس تبدیل رفته و فایل آپلود کنید"
echo ""
echo "🛑 برای متوقف کردن: ./stop_system.sh"
echo "📁 لاگ‌ها: ~/2d-to-3d-converter/logs/"

wait
