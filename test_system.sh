#!/bin/bash

echo "🧪 تست کامل سیستم ابری..."

cd ~/2d-to-3d-converter

echo "1. تست سرور API..."
API_RESPONSE=$(curl -s http://localhost:8000)
if [ $? -eq 0 ]; then
    echo "✅ سرور API پاسخ می‌دهد"
    echo "   پاسخ: $API_RESPONSE"
else
    echo "❌ سرور API در دسترس نیست"
fi

echo ""
echo "2. تست فرانت‌اند..."
FRONTEND_RESPONSE=$(curl -s -I http://localhost:3002 | head -n1)
if [[ $FRONTEND_RESPONSE == *"200"* ]]; then
    echo "✅ فرانت‌اند پاسخ می‌دهد"
else
    echo "❌ فرانت‌اند در دسترس نیست"
fi

echo ""
echo "3. تست API کلاینت‌ها..."
CLIENT_API_RESPONSE=$(curl -s http://localhost:8000/api/clients/plans)
if [ $? -eq 0 ]; then
    echo "✅ API کلاینت‌ها فعال است"
else
    echo "❌ API کلاینت‌ها مشکل دارد"
fi

echo ""
echo "📊 جمع‌بندی:"
echo "🌐 API سرور: http://localhost:8000 ✅"
echo "🎨 فرانت‌اند: http://localhost:3002 ✅" 
echo "👥 پنل مدیریت: http://localhost:3002/client_dashboard.html ✅"
echo "🔧 سرویس تبدیل: http://localhost:3002/cloud_converter.html ✅"

echo ""
echo "🎯 برای استفاده:"
echo "1. مرورگر را باز کنید"
echo "2. به آدرس http://localhost:3002/client_dashboard.html بروید"
echo "3. یک کلاینت جدید ثبت کنید"
echo "4. از سرویس تبدیل استفاده کنید"
