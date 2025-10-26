#!/bin/bash

echo "🧪 تست کامل سیستم ابری تبدیل 2D به 3D"
echo "=========================================="

cd ~/2d-to-3d-converter

# بررسی اجرا بودن سیستم
echo "1. بررسی وضعیت سرویس‌ها..."
if ! curl -s http://localhost:8000 > /dev/null; then
    echo "❌ سرور API اجرا نیست. ابتدا سیستم را راه‌اندازی کنید:"
    echo "   ./start_complete_system.sh"
    exit 1
fi

echo "✅ سرور API فعال است"

# تست endpointهای اصلی
echo ""
echo "2. تست endpointهای API..."

echo "📡 تست سلامت سرور..."
curl -s http://localhost:8000 | python3 -m json.tool

echo ""
echo "📋 تست پلن‌های اشتراک..."
curl -s http://localhost:8000/api/clients/plans | python3 -m json.tool

echo ""
echo "👥 تست لیست کلاینت‌ها..."
curl -s http://localhost:8000/api/clients/list | python3 -m json.tool

# تست ثبت کلاینت
echo ""
echo "3. تست ثبت کلاینت جدید..."
REGISTER_RESPONSE=$(curl -s -X POST http://localhost:8000/api/clients/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test_client@example.com",
    "company_name": "شرکت تستی پارس",
    "contact_person": "محمد آزمون",
    "subscription_tier": "professional"
  }')

echo $REGISTER_RESPONSE | python3 -m json.tool

# استخراج API Key از پاسخ
API_KEY=$(echo $REGISTER_RESPONSE | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    if data.get('success'):
        print(data.get('api_key', ''))
    else:
        print('')
except:
    print('')
")

if [ -n "$API_KEY" ]; then
    echo ""
    echo "✅ کلاینت با موفقیت ثبت شد!"
    echo "🔑 API Key: $API_KEY"
    
    # تست احراز هویت
    echo ""
    echo "4. تست احراز هویت با API Key..."
    curl -s -X POST http://localhost:8000/api/clients/verify \
      -H "Content-Type: application/json" \
      -d "{\"api_key\": \"$API_KEY\"}" | python3 -m json.tool
    
    # تست تبدیل
    echo ""
    echo "5. تست سرویس تبدیل..."
    curl -s -X POST http://localhost:8000/api/convert/start \
      -H "Content-Type: application/json" \
      -H "X-API-Key: $API_KEY" \
      -d '{
        "file_name": "test_image.jpg",
        "file_size": 5242880,
        "conversion_type": "image_to_3d",
        "options": {"quality": "high"}
      }' | python3 -m json.tool
    
else
    echo "❌ خطا در ثبت کلاینت"
fi

echo ""
echo "6. تست دسترسی به فرانت‌اند..."
if curl -s http://localhost:3002 > /dev/null; then
    echo "✅ فرانت‌اند در دسترس است"
    echo "🌐 آدرس‌های قابل دسترسی:"
    echo "   - پنل مدیریت: http://localhost:3002/client_dashboard.html"
    echo "   - سرویس تبدیل: http://localhost:3002/cloud_converter.html"
    echo "   - صفحه اصلی: http://localhost:3002"
else
    echo "❌ فرانت‌اند در دسترس نیست"
fi

echo ""
echo "=========================================="
echo "🎉 تست کامل به پایان رسید!"
echo "📊 برای مشاهده لاگ‌ها: tail -f logs/server.log"
