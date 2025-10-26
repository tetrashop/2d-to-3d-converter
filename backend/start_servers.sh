#!/bin/bash

echo "🚀 Starting 2D to 3D Converter Servers..."

# بررسی پایتون
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 is not installed"
    exit 1
fi

# بررسی پورت‌ها
echo "🔍 Checking ports..."
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null ; then
    echo "⚠️ Port 8000 is already in use"
    echo "Stopping existing process..."
    kill $(lsof -ti:8000)
fi

if lsof -Pi :3000 -sTCP:LISTEN -t >/dev/null ; then
    echo "⚠️ Port 3000 is already in use" 
    echo "Stopping existing process..."
    kill $(lsof -ti:3000)
fi

# راه‌اندازی سرور بک‌اند
echo "🔧 Starting backend server..."
cd backend
python3 simple_server.py &
BACKEND_PID=$!

# صبر کردن برای راه‌اندازی سرور
sleep 3

# راه‌اندازی سرور فرانت‌اند
echo "🎨 Starting frontend server..."
cd ../frontend
python3 -m http.server 3000 &
FRONTEND_PID=$!

echo ""
echo "✅ Servers started successfully!"
echo "🌐 Frontend: http://localhost:3000"
echo "🔧 Backend:  http://localhost:8000"
echo "📊 Health:   http://localhost:8000/api/health"
echo ""
echo "Press Ctrl+C to stop servers"

# نگه داشتن اسکریپت
wait
