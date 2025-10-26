#!/bin/bash

echo "🚀 Starting 2D to 3D Converter..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 is not installed. Please install Python 3.8+"
    exit 1
fi

# Create virtual environment
echo "📦 Setting up Python environment..."
cd backend
python3 -m venv venv
source venv/bin/activate

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt

# Start backend server
echo "🔧 Starting backend server..."
python app/main.py &

# Wait for backend to start
sleep 3

# Start frontend server
echo "🎨 Starting frontend server..."
cd ../frontend
python3 -m http.server 3000 &

echo "✅ Application is running!"
echo "🌐 Frontend: http://localhost:3000"
echo "🔧 Backend API: http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"

# Keep script running
wait
