#!/bin/bash

echo "🚀 راه‌اندازی سریع مبدل 2D به 3D..."

cd ~/2d-to-3d-converter

# ایجاد پوشه آپلود
mkdir -p backend/uploads

echo "🔧 راه‌اندازی سرور بک‌اند (Flask)..."
cd backend
python3 simple_server.py &
BACKEND_PID=$!

echo "⏳ منتظر راه‌اندازی سرور..."
sleep 3

echo "🎨 راه‌اندازی سرور فرانت‌اند..."
cd ../frontend
python3 -m http.server 3000 &
FRONTEND_PID=$!

echo ""
echo "✅ راه‌اندازی کامل شد!"
echo "🌐 فرانت‌اند: http://localhost:3000"
echo "🤝 صفحه مشارکت: http://localhost:3000/partnership.html"
echo "🔧 بک‌اند: http://localhost:8000"
echo ""
echo "📱 برای تست در مرورگر باز کن:"
echo "termux-open http://localhost:3000"
echo ""
echo "برای متوقف کردن: Ctrl+C"

# نگه داشتن اسکریپت
wait
