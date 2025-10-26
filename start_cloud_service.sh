#!/bin/bash

echo "☁️ راه‌اندازی سرویس ابری تبدیل 2D به 3D..."

# کشتن پروسه‌های قبلی
pkill -f "python3" 2>/dev/null
sleep 2

cd ~/2d-to-3d-converter

# ایجاد پوشه‌های مورد نیاز
mkdir -p backend/uploads backend/outputs

echo "🔧 نصب نیازمندیها..."
cd backend
pip install -r requirements_3d.txt

echo "🚀 راه‌اندازی سرور ابری..."
python3 cloud_converter.py &
CLOUD_PID=$!

echo "⏳ منتظر راه‌اندازی سرور..."
sleep 5

echo "🎨 راه‌اندازی فرانت‌اند..."
cd ../frontend
python3 -m http.server 3001 &
FRONTEND_PID=$!

echo ""
echo "✅ سرویس ابری فعال شد!"
echo "🌐 پنل مدیریت: http://localhost:3001/cloud_converter.html"
echo "🔧 API سرور: http://localhost:8000"
echo "📊 سلامت سرویس: http://localhost:8000/api/health"
echo ""
echo "برای متوقف کردن: Ctrl+C"
echo "یا: pkill -f 'python3'"

wait
