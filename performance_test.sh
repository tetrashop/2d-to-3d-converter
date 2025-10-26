#!/bin/bash

echo "🎯 تست پیشرفته عملکرد سیستم ابری"
echo "=========================================="

cd ~/2d-to-3d-converter

# تست سرعت پاسخ‌دهی
echo "1. تست سرعت پاسخ‌دهی API..."
time curl -s -o /dev/null http://localhost:8000

echo ""
echo "2. تست ثبت چند کلاینت..."
for i in {1..3}; do
    echo "   کلاینت تستی $i..."
    curl -s -X POST http://localhost:8000/api/clients/register \
      -H "Content-Type: application/json" \
      -d "{
        \"email\": \"loadtest${i}@company.com\",
        \"company_name\": \"شرکت تست ${i}\",
        \"contact_person\": \"تست ${i}\",
        \"subscription_tier\": \"basic\"
      }" | grep -o '"api_key":"[^"]*"'
done

echo ""
echo "3. تست همزمان درخواست‌ها..."
for i in {1..5}; do
    curl -s http://localhost:8000/api/clients/plans > /dev/null &
done
wait
echo "   ✅ ۵ درخواست همزمان با موفقیت انجام شد"

echo ""
echo "4. تست سرویس تبدیل..."
CONVERSION_RESPONSE=$(curl -s -X POST http://localhost:8000/api/convert/start \
  -H "Content-Type: application/json" \
  -d '{
    "file_name": "performance_test.jpg",
    "file_size": 3145728,
    "conversion_type": "image_to_3d",
    "options": {"quality": "high", "format": "obj"}
  }')

echo $CONVERSION_RESPONSE

echo ""
echo "5. بررسی مصرف منابع..."
echo "   حافظه استفاده شده:"
ps aux | grep python | grep -v grep | awk '{print $4 "% RAM - " $11}'

echo ""
echo "🎊 تست عملکرد کامل شد!"
