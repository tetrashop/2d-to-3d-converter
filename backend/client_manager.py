from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
import uuid
import hashlib
import json
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum

client_bp = Blueprint('clients', __name__, url_prefix='/api/clients')

class SubscriptionTier(Enum):
    FREE = "free"
    BASIC = "basic"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"

class ClientStatus(Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    INACTIVE = "inactive"

@dataclass
class Client:
    client_id: str
    email: str
    company_name: str
    contact_person: str
    subscription_tier: SubscriptionTier
    status: ClientStatus
    created_at: datetime
    monthly_quota: int
    used_quota: int
    api_key: str
    webhook_url: Optional[str] = None
    billing_info: Optional[Dict] = None

@dataclass
class ConversionStats:
    total_conversions: int
    successful_conversions: int
    failed_conversions: int
    total_processing_time: float
    average_processing_time: float

# دیتابیس موقت کلاینت‌ها
clients_db: Dict[str, Client] = {}
conversion_stats: Dict[str, ConversionStats] = {}

class ClientManager:
    """مدیریت کلاینت‌ها و اشتراک‌ها"""
    
    def __init__(self):
        self.subscription_plans = {
            SubscriptionTier.FREE: {
                "monthly_price": 0,
                "conversion_quota": 10,
                "max_file_size": 10 * 1024 * 1024,  # 10MB
                "support_level": "community",
                "features": ["basic_conversion", "web_download"]
            },
            SubscriptionTier.BASIC: {
                "monthly_price": 29,
                "conversion_quota": 100,
                "max_file_size": 25 * 1024 * 1024,  # 25MB
                "support_level": "email",
                "features": ["basic_conversion", "api_access", "priority_queue", "web_download"]
            },
            SubscriptionTier.PROFESSIONAL: {
                "monthly_price": 99,
                "conversion_quota": 500,
                "max_file_size": 50 * 1024 * 1024,  # 50MB
                "support_level": "priority",
                "features": ["all_basic", "batch_processing", "custom_formats", "analytics"]
            },
            SubscriptionTier.ENTERPRISE: {
                "monthly_price": 299,
                "conversion_quota": 2000,
                "max_file_size": 100 * 1024 * 1024,  # 100MB
                "support_level": "dedicated",
                "features": ["all_professional", "white_label", "sla", "custom_development"]
            }
        }
    
    def create_client(self, email: str, company_name: str, contact_person: str, 
                     subscription_tier: SubscriptionTier = SubscriptionTier.FREE) -> Client:
        """ایجاد کلاینت جدید"""
        
        # بررسی وجود کلاینت
        for client in clients_db.values():
            if client.email == email:
                raise ValueError("کلاینت با این ایمیل قبلاً ثبت شده است")
        
        client_id = str(uuid.uuid4())
        api_key = self._generate_api_key(email, client_id)
        
        plan = self.subscription_plans[subscription_tier]
        
        client = Client(
            client_id=client_id,
            email=email,
            company_name=company_name,
            contact_person=contact_person,
            subscription_tier=subscription_tier,
            status=ClientStatus.ACTIVE,
            created_at=datetime.utcnow(),
            monthly_quota=plan["conversion_quota"],
            used_quota=0,
            api_key=api_key
        )
        
        clients_db[client_id] = client
        conversion_stats[client_id] = ConversionStats(0, 0, 0, 0, 0)
        
        return client
    
    def _generate_api_key(self, email: str, client_id: str) -> str:
        """تولید API Key منحصر به فرد"""
        secret = f"{email}{client_id}{datetime.utcnow().isoformat()}"
        return hashlib.sha256(secret.encode()).hexdigest()[:32]
    
    def get_client(self, client_id: str) -> Optional[Client]:
        """دریافت اطلاعات کلاینت"""
        return clients_db.get(client_id)
    
    def get_client_by_api_key(self, api_key: str) -> Optional[Client]:
        """دریافت کلاینت بر اساس API Key"""
        for client in clients_db.values():
            if client.api_key == api_key:
                return client
        return None
    
    def update_client_quota(self, client_id: str, conversion_success: bool, processing_time: float):
        """بروزرسانی سهمیه و آمار کلاینت"""
        client = clients_db.get(client_id)
        stats = conversion_stats.get(client_id)
        
        if client and stats:
            client.used_quota += 1
            stats.total_conversions += 1
            
            if conversion_success:
                stats.successful_conversions += 1
            else:
                stats.failed_conversions += 1
            
            stats.total_processing_time += processing_time
            stats.average_processing_time = stats.total_processing_time / stats.total_conversions
    
    def can_make_conversion(self, client_id: str, file_size: int) -> bool:
        """بررسی امکان انجام تبدیل برای کلاینت"""
        client = clients_db.get(client_id)
        if not client or client.status != ClientStatus.ACTIVE:
            return False
        
        plan = self.subscription_plans[client.subscription_tier]
        
        # بررسی سهمیه ماهیانه
        if client.used_quota >= client.monthly_quota:
            return False
        
        # بررسی اندازه فایل
        if file_size > plan["max_file_size"]:
            return False
        
        return True
    
    def upgrade_subscription(self, client_id: str, new_tier: SubscriptionTier) -> bool:
        """ارتقای اشتراک کلاینت"""
        client = clients_db.get(client_id)
        if not client:
            return False
        
        client.subscription_tier = new_tier
        plan = self.subscription_plans[new_tier]
        client.monthly_quota = plan["conversion_quota"]
        
        return True
    
    def get_client_analytics(self, client_id: str) -> Dict:
        """دریافت آمار تحلیلی کلاینت"""
        client = clients_db.get(client_id)
        stats = conversion_stats.get(client_id)
        
        if not client or not stats:
            return {}
        
        quota_usage = (client.used_quota / client.monthly_quota) * 100
        success_rate = (stats.successful_conversions / stats.total_conversions * 100) if stats.total_conversions > 0 else 0
        
        return {
            "client_id": client_id,
            "subscription_tier": client.subscription_tier.value,
            "quota_usage": {
                "used": client.used_quota,
                "total": client.monthly_quota,
                "percentage": round(quota_usage, 2)
            },
            "conversion_stats": {
                "total": stats.total_conversions,
                "successful": stats.successful_conversions,
                "failed": stats.failed_conversions,
                "success_rate": round(success_rate, 2),
                "avg_processing_time": round(stats.average_processing_time, 2)
            },
            "status": client.status.value
        }

# ایجاد نمونه مدیر کلاینت
client_manager = ClientManager()

# Routes
@client_bp.route('/register', methods=['POST'])
def register_client():
    """ثبت‌نام کلاینت جدید"""
    try:
        data = request.get_json()
        
        if not data or 'email' not in data:
            return jsonify({"error": "ایمیل الزامی است"}), 400
        
        email = data['email']
        company_name = data.get('company_name', '')
        contact_person = data.get('contact_person', '')
        subscription_tier = SubscriptionTier(data.get('subscription_tier', 'free'))
        
        client = client_manager.create_client(
            email=email,
            company_name=company_name,
            contact_person=contact_person,
            subscription_tier=subscription_tier
        )
        
        return jsonify({
            "success": True,
            "client_id": client.client_id,
            "api_key": client.api_key,
            "message": "کلاینت با موفقیت ثبت شد"
        })
        
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"خطای سرور: {str(e)}"}), 500

@client_bp.route('/<client_id>', methods=['GET'])
def get_client_info(client_id):
    """دریافت اطلاعات کلاینت"""
    client = client_manager.get_client(client_id)
    
    if not client:
        return jsonify({"error": "کلاینت یافت نشد"}), 404
    
    return jsonify({
        "success": True,
        "client": {
            "client_id": client.client_id,
            "email": client.email,
            "company_name": client.company_name,
            "contact_person": client.contact_person,
            "subscription_tier": client.subscription_tier.value,
            "status": client.status.value,
            "created_at": client.created_at.isoformat(),
            "monthly_quota": client.monthly_quota,
            "used_quota": client.used_quota,
            "webhook_url": client.webhook_url
        }
    })

@client_bp.route('/<client_id>/analytics', methods=['GET'])
def get_client_analytics(client_id):
    """دریافت آمار تحلیلی کلاینت"""
    analytics = client_manager.get_client_analytics(client_id)
    
    if not analytics:
        return jsonify({"error": "کلاینت یافت نشد"}), 404
    
    return jsonify({
        "success": True,
        "analytics": analytics
    })

@client_bp.route('/<client_id>/upgrade', methods=['POST'])
def upgrade_subscription(client_id):
    """ارتقای اشتراک کلاینت"""
    try:
        data = request.get_json()
        
        if not data or 'new_tier' not in data:
            return jsonify({"error": "سطح اشتراک جدید الزامی است"}), 400
        
        new_tier = SubscriptionTier(data['new_tier'])
        
        success = client_manager.upgrade_subscription(client_id, new_tier)
        
        if not success:
            return jsonify({"error": "کلاینت یافت نشد"}), 404
        
        return jsonify({
            "success": True,
            "message": f"اشتراک به {new_tier.value} ارتقا یافت",
            "new_tier": new_tier.value
        })
        
    except ValueError as e:
        return jsonify({"error": "سطح اشتراک نامعتبر است"}), 400
    except Exception as e:
        return jsonify({"error": f"خطای سرور: {str(e)}"}), 500

@client_bp.route('/plans', methods=['GET'])
def get_subscription_plans():
    """دریافت لیست پلن‌های اشتراک"""
    plans = {}
    
    for tier, plan in client_manager.subscription_plans.items():
        plans[tier.value] = {
            "monthly_price": plan["monthly_price"],
            "conversion_quota": plan["conversion_quota"],
            "max_file_size": plan["max_file_size"],
            "support_level": plan["support_level"],
            "features": plan["features"]
        }
    
    return jsonify({
        "success": True,
        "plans": plans
    })

@client_bp.route('/verify', methods=['POST'])
def verify_client():
    """احراز هویت کلاینت با API Key"""
    data = request.get_json()
    
    if not data or 'api_key' not in data:
        return jsonify({"error": "API Key الزامی است"}), 400
    
    client = client_manager.get_client_by_api_key(data['api_key'])
    
    if not client:
        return jsonify({"error": "API Key نامعتبر است"}), 401
    
    return jsonify({
        "success": True,
        "client_id": client.client_id,
        "subscription_tier": client.subscription_tier.value,
        "status": client.status.value
    })

@client_bp.route('/list', methods=['GET'])
def list_clients():
    """لیست تمام کلاینت‌ها"""
    clients_list = []
    
    for client in clients_db.values():
        clients_list.append({
            "client_id": client.client_id,
            "email": client.email,
            "company_name": client.company_name,
            "subscription_tier": client.subscription_tier.value,
            "status": client.status.value,
            "created_at": client.created_at.isoformat(),
            "used_quota": client.used_quota,
            "monthly_quota": client.monthly_quota
        })
    
    return jsonify({
        "success": True,
        "clients": clients_list,
        "total_count": len(clients_list)
    })
