# 🔄 2D to 3D Image Converter

تبدیل تصاویر دو بعدی به مدل‌های سه بعدی با Python و JavaScript

## 🚀 ویژگی‌ها

- 📷 آپلود تصاویر (JPG, PNG, WebP)
- 🎯 تبدیل به مدل 3D (GLB format)
- 📱 طراحی ریسپانسیو
- ⚡ پردازش ابری
- 🌐 API RESTful

## 🔧 راه‌اندازی

```bash
# نصب و اجرا
./run.sh

**پروژه آماده است!** 🎉 

**ویژگی‌های کلیدی:**
- ✅ Backend: Python + FastAPI
- ✅ Frontend: Vanilla JavaScript + HTML/CSS  
- ✅ آپلود فایل + Drag & Drop
- ✅ نمایش پیشرفت
- ✅ دانلود مدل 3D
- ✅ طراحی ریسپانسیو

**برای اجرا:**
```bash
cd 2d-to-3d-converter
./run.sh
cd ~/2d-to-3d-converter

# ایجاد سیستم کسب درآمد و مشارکت
mkdir -p backend/payments backend/partnerships backend/licensing
cat > backend/app/payments.py << 'EOF'
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
import uuid
from datetime import datetime, timedelta
import json

router = APIRouter(prefix="/api/payments", tags=["payments"])

# مدل‌های داده
class PaymentRequest(BaseModel):
    amount: float
    currency: str = "USD"
    description: str
    customer_email: str

class PartnershipAgreement(BaseModel):
    partner_email: str
    revenue_share: float  # between 0.1 to 0.5 (10% to 50%)
    agreement_type: str  # "revenue_share" or "one_time_payment"

class LicenseRequest(BaseModel):
    model_id: str
    license_type: str  # "personal", "commercial", "exclusive"
    duration_days: int

# دیتابیس موقت (در تولید از دیتابیس واقعی استفاده کنید)
payments_db = {}
partnerships_db = {}
licenses_db = {}

@router.post("/initiate")
async def initiate_payment(payment: PaymentRequest):
    """شروع پرداخت برای تبدیل تصویر"""
    payment_id = str(uuid.uuid4())
    
    payment_data = {
        "payment_id": payment_id,
        "amount": payment.amount,
        "currency": payment.currency,
        "description": payment.description,
        "customer_email": payment.customer_email,
        "status": "pending",
        "created_at": datetime.utcnow().isoformat()
    }
    
    payments_db[payment_id] = payment_data
    
    # در اینجا باید با درگاه پرداخت (مثلاً Stripe, PayPal) یکپارچه شوید
    # برای نمونه، یک لینک پرداخت آزمایشی برمی‌گردانیم
    return {
        "success": True,
        "payment_id": payment_id,
        "payment_url": f"/payment/checkout/{payment_id}",
        "message": "Payment initiated successfully"
    }

@router.post("/partnership/create")
async def create_partnership(agreement: PartnershipAgreement):
    """ایجاد توافق‌نامه مشارکت"""
    partnership_id = str(uuid.uuid4())
    
    partnership_data = {
        "partnership_id": partnership_id,
        "partner_email": agreement.partner_email,
        "revenue_share": agreement.revenue_share,
        "agreement_type": agreement.agreement_type,
        "status": "active",
        "created_at": datetime.utcnow().isoformat(),
        "total_earnings": 0.0
    }
    
    partnerships_db[partnership_id] = partnership_data
    
    return {
        "success": True,
        "partnership_id": partnership_id,
        "message": "Partnership agreement created successfully"
    }

@router.post("/license/generate")
async def generate_license(license_req: LicenseRequest):
    """تولید لایسنس برای مدل 3D"""
    license_id = str(uuid.uuid4())
    expiration_date = datetime.utcnow() + timedelta(days=license_req.duration_days)
    
    # محاسبه هزینه بر اساس نوع لایسنس
    license_prices = {
        "personal": 10.0,
        "commercial": 50.0,
        "exclusive": 200.0
    }
    
    price = license_prices.get(license_req.license_type, 10.0)
    
    license_data = {
        "license_id": license_id,
        "model_id": license_req.model_id,
        "license_type": license_req.license_type,
        "price": price,
        "expiration_date": expiration_date.isoformat(),
        "is_active": True
    }
    
    licenses_db[license_id] = license_data
    
    return {
        "success": True,
        "license_id": license_id,
        "price": price,
        "expiration_date": expiration_date.isoformat()
    }

@router.get("/revenue/share/{partnership_id}")
async def calculate_revenue_share(partnership_id: str):
    """محاسبه سود مشارکت"""
    partnership = partnerships_db.get(partnership_id)
    if not partnership:
        raise HTTPException(status_code=404, detail="Partnership not found")
    
    # محاسبه سود (در تولید از دیتابیس واقعی استفاده کنید)
    total_revenue = 1000.0  # این مقدار از دیتابیس واقعی می‌آید
    partner_share = total_revenue * partnership["revenue_share"]
    
    return {
        "partnership_id": partnership_id,
        "total_revenue": total_revenue,
        "revenue_share_percentage": partnership["revenue_share"] * 100,
        "partner_share": partner_share,
        "platform_share": total_revenue - partner_share
    }

@router.get("/analytics/overview")
async def get_revenue_analytics():
    """آمار کلی درآمد و مشارکت‌ها"""
    total_revenue = sum(payment["amount"] for payment in payments_db.values() if payment["status"] == "completed")
    active_partnerships = len([p for p in partnerships_db.values() if p["status"] == "active"])
    total_licenses = len(licenses_db)
    
    return {
        "total_revenue": total_revenue,
        "active_partnerships": active_partnerships,
        "total_licenses_sold": total_licenses,
        "currency": "USD"
    }
