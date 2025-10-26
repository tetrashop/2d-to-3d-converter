from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import uuid
from datetime import datetime

router = APIRouter(prefix="/api/partnerships", tags=["partnerships"])

class PartnershipInvitation(BaseModel):
    partner_email: str
    invitation_message: str
    proposed_share: float

class PartnershipResponse(BaseModel):
    partnership_id: str
    accept: bool
    counter_share: Optional[float] = None

# دیتابیس مشارکت‌ها
partnership_invitations = {}
partnership_agreements = {}

@router.post("/invite")
async def invite_partner(invitation: PartnershipInvitation):
    """ارسال دعوت‌نامه مشارکت"""
    invitation_id = str(uuid.uuid4())
    
    invitation_data = {
        "invitation_id": invitation_id,
        "partner_email": invitation.partner_email,
        "invitation_message": invitation.invitation_message,
        "proposed_share": invitation.proposed_share,
        "status": "pending",
        "sent_at": datetime.utcnow().isoformat()
    }
    
    partnership_invitations[invitation_id] = invitation_data
    
    # در اینجا ایمیل دعوت‌نامه ارسال می‌شود
    # send_invitation_email(invitation.partner_email, invitation_data)
    
    return {
        "success": True,
        "invitation_id": invitation_id,
        "message": "Partnership invitation sent successfully"
    }

@router.post("/respond")
async def respond_to_invitation(response: PartnershipResponse):
    """پاسخ به دعوت‌نامه مشارکت"""
    invitation = partnership_invitations.get(response.partnership_id)
    if not invitation:
        raise HTTPException(status_code=404, detail="Invitation not found")
    
    if response.accept:
        # ایجاد توافق‌نامه مشارکت
        partnership_id = str(uuid.uuid4())
        final_share = response.counter_share or invitation["proposed_share"]
        
        agreement_data = {
            "partnership_id": partnership_id,
            "partner_email": invitation["partner_email"],
            "revenue_share": final_share,
            "status": "active",
            "created_at": datetime.utcnow().isoformat(),
            "total_earnings": 0.0
        }
        
        partnership_agreements[partnership_id] = agreement_data
        invitation["status"] = "accepted"
        
        return {
            "success": True,
            "partnership_id": partnership_id,
            "revenue_share": final_share,
            "message": "Partnership agreement created successfully"
        }
    else:
        invitation["status"] = "rejected"
        return {
            "success": True,
            "message": "Partnership invitation declined"
        }

@router.get("/my-partnerships/{partner_email}")
async def get_my_partnerships(partner_email: str):
    """دریافت لیست مشارکت‌های یک شریک"""
    my_partnerships = [
        agreement for agreement in partnership_agreements.values()
        if agreement["partner_email"] == partner_email
    ]
    
    return {
        "partner_email": partner_email,
        "partnerships": my_partnerships,
        "total_count": len(my_partnerships)
    }

@router.get("/revenue/{partnership_id}")
async def get_partnership_revenue(partnership_id: str):
    """دریافت درآمدهای یک مشارکت"""
    partnership = partnership_agreements.get(partnership_id)
    if not partnership:
        raise HTTPException(status_code=404, detail="Partnership not found")
    
    # محاسبه درآمد (در تولید از دیتابیس واقعی استفاده کنید)
    total_sales = 5000.0  # از دیتابیس واقعی
    partner_earnings = total_sales * partnership["revenue_share"]
    
    return {
        "partnership_id": partnership_id,
        "total_sales": total_sales,
        "revenue_share_percentage": partnership["revenue_share"] * 100,
        "partner_earnings": partner_earnings,
        "next_payout_date": (datetime.utcnow() + timedelta(days=30)).isoformat()
    }
