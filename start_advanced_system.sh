#!/bin/bash

echo "🚀 راه‌اندازی سیستم پیشرفته تبدیل 2D به 3D..."
echo "⏳ لطفاً منتظر بمانید..."

cd ~/2d-to-3d-converter

# توقف سرویس‌های قبلی
pkill -f "python.*advanced_converter" 2>/dev/null
sleep 2

# نصب وابستگی‌های اضافی
echo "🔧 نصب وابستگی‌های پیشرفته..."
pip3 install opencv-python numpy pillow --quiet

# راه‌اندازی سرور پیشرفته
echo "🏗️ راه‌اندازی سرور پیشرفته..."
cd backend
python3 advanced_converter.py > ../logs/advanced_server.log 2>&1 &
ADVANCED_PID=$!

echo "⏳ منتظر راه‌اندازی سرور پیشرفته..."
sleep 8

echo ""
echo "✅ سیستم پیشرفته فعال شد!"
echo "=========================================="
echo "🎨 رابط پیشرفته: http://localhost:3002/advanced_converter.html"
echo "🔧 API پیشرفته: http://localhost:8001"
echo "📊 پنل مدیریت: http://localhost:3002/client_dashboard.html"
echo "=========================================="

echo ""
echo "🎯 ویژگی‌های سیستم پیشرفته:"
echo "✅ تبدیل پیشرفته تصاویر به 3D"
echo "✅ ابزار چرخش و زوم روی مدل"
echo "✅ خروجی برای مایا (.ma)"
echo "✅ خروجی برای 3ds Max (.max)" 
echo "✅ خروجی OBJ, FBX, STL"
echo "✅ پیش‌نمایش زنده مدل"
echo "✅ کنترل‌های تعاملی"

wait
