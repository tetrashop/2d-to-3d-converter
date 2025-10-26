class PartnershipManager {
    constructor() {
        this.apiBaseUrl = 'http://localhost:8000';
        this.selectedPlan = null;
        this.currentPartnership = null;
        
        this.init();
    }

    init() {
        console.log('🤝 Partnership Manager Initialized');
        this.testBackendConnection();
    }

    async testBackendConnection() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/api/health`);
            if (response.ok) {
                console.log('✅ Backend server is running');
            } else {
                console.log('❌ Backend server not responding');
            }
        } catch (error) {
            console.log('❌ Cannot connect to backend:', error.message);
            this.showConnectionError();
        }
    }

    showConnectionError() {
        const container = document.querySelector('.container');
        if (container) {
            container.innerHTML = `
                <div style="text-align: center; padding: 2rem;">
                    <h1>🔧 سیستم در حال راه‌اندازی</h1>
                    <p>سرور بک‌اند در حال راه‌اندازی است...</p>
                    <p>لطفاً چند لحظه صبر کنید و صفحه را رفرش کنید</p>
                    <button onclick="location.reload()" style="padding: 1rem 2rem; margin-top: 1rem;">
                        تلاش مجدد
                    </button>
                </div>
            `;
        }
    }

    selectPlan(planType) {
        this.selectedPlan = planType;
        document.getElementById('partnershipForm').style.display = 'block';
        
        // تنظیم درصد سهم پیشفرض بر اساس پلن
        const shareInput = document.getElementById('proposedShare');
        if (planType === 'standard') {
            shareInput.value = 20;
        } else if (planType === 'premium') {
            shareInput.value = 35;
        }
        
        // اسکرول به فرم
        document.getElementById('partnershipForm').scrollIntoView({ behavior: 'smooth' });
    }

    async submitPartnershipRequest() {
        const email = document.getElementById('partnerEmail').value;
        const proposedShare = parseInt(document.getElementById('proposedShare').value) / 100;
        const message = document.getElementById('invitationMessage').value;

        if (!email || !proposedShare) {
            alert('لطفاً تمام فیلدهای ضروری را پر کنید');
            return;
        }

        try {
            // شبیه‌سازی ارسال درخواست (تا زمانی که بک‌اند کامل شود)
            console.log('📧 Sending partnership request:', { email, proposedShare, message });
            
            // شبیه‌سازی تأخیر شبکه
            await new Promise(resolve => setTimeout(resolve, 2000));
            
            // در اینجا باید با API واقعی ارتباط برقرار شود
            // const response = await fetch(`${this.apiBaseUrl}/api/partnerships/invite`, {
            //     method: 'POST',
            //     headers: { 'Content-Type': 'application/json' },
            //     body: JSON.stringify({
            //         partner_email: email,
            //         invitation_message: message,
            //         proposed_share: proposedShare
            //     })
            // });
            
            // برای حالا، فقط یک پیام موفقیت نشان می‌دهیم
            alert('✅ درخواست مشارکت شما با موفقیت ارسال شد!\n\nبه زودی با شما تماس گرفته خواهد شد.');
            this.showRevenueDashboard();
            
        } catch (error) {
            alert('❌ خطا در ارسال درخواست: ' + error.message);
        }
    }

    showRevenueDashboard() {
        document.getElementById('partnershipForm').style.display = 'none';
        document.getElementById('revenueDashboard').style.display = 'block';
        
        // نمایش داده‌های نمونه
        document.getElementById('totalRevenue').textContent = '$1,250';
        document.getElementById('myShare').textContent = '$250';
        document.getElementById('modelsSold').textContent = '25';
    }

    requestPayout() {
        alert('✅ درخواست پرداخت شما ثبت شد.\n\nپرداخت طی ۳-۵ روز کاری انجام خواهد شد.');
    }
}

// راه‌اندازی سیستم مشارکت
document.addEventListener('DOMContentLoaded', () => {
    new PartnershipManager();
});
