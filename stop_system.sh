#!/bin/bash

echo "🛑 توقف سیستم ابری تبدیل 2D به 3D..."

cd ~/2d-to-3d-converter

# توقف با PIDهای ذخیره شده
if [ -f logs/server.pid ]; then
    kill $(cat logs/server.pid) 2>/dev/null
    rm logs/server.pid
fi

if [ -f logs/frontend.pid ]; then
    kill $(cat logs/frontend.pid) 2>/dev/null
    rm logs/frontend.pid
fi

# توقف کلی
pkill -f "python.*(8000|3002)" 2>/dev/null

echo "✅ سیستم متوقف شد"
