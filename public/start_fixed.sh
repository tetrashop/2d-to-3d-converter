#!/bin/bash

echo "🚀 راه‌اندازی مبدل 2D به 3D..."

# کشتن پروسه‌های قبلی
echo "🔍 متوقف کردن سرورهای قبلی..."
pkill -f "python3 -m http.server" 2>/dev/null
pkill -f "python3 simple_server.py" 2>/dev/null
pkill -f "simple_server.py" 2>/dev/null

# صبر کن پروسه‌ها کامل kill بشن
sleep 2

cd ~/2d-to-3d-converter

# ایجاد پوشه آپلود
mkdir -p backend/uploads

echo "🔧 راه‌اندازی سرور بک‌اند روی پورت 8001..."
cd backend
python3 simple_server.py &
BACKEND_PID=$!

echo "⏳ منتظر راه‌اندازی سرور بک‌اند (5 ثانیه)..."
sleep 5

echo "🎨 راه‌اندازی سرور فرانت‌اند روی پورت 3001..."
cd ../frontend
python3 -m http.server 3001 &
FRONTEND_PID=$!

echo ""
echo "✅ راه‌اندازی کامل شد!"
echo "🌐 فرانت‌اند: http://localhost:3001"
echo "🤝 صفحه مشارکت: http://localhost:3001/partnership.html"
echo "🔧 بک‌اند: http://localhost:8001"
echo "📊 سلامت بک‌اند: http://localhost:8001/api/health"
echo ""
echo "📱 برای تست در مرورگر:"
echo "termux-open http://localhost:3001/partnership.html"
echo ""
echo "برای متوقف کردن سرورها: Ctrl+C"
echo "یا دستور: pkill -f 'python3'"

# نگه داشتن اسکریپت
wait
