class ClientDashboard {
    constructor() {
        this.apiBaseUrl = 'http://localhost:8000';
        this.currentClients = [];
        this.currentTab = 'overview';
        
        this.init();
    }

    init() {
        console.log('👥 پنل مدیریت کلاینت‌ها فعال شد');
        this.loadDashboardData();
        this.setupEventListeners();
    }

    setupEventListeners() {
        // مدیریت کلیک روی تب‌ها
        document.querySelectorAll('.tab').forEach(tab => {
            tab.addEventListener('click', (e) => {
                const tabName = e.target.getAttribute('onclick').match(/'([^']+)'/)[1];
                this.showTab(tabName);
            });
        });
    }

    showTab(tabName) {
        // مخفی کردن همه تب‌ها
        document.querySelectorAll('.tab-content').forEach(tab => {
            tab.classList.remove('active');
        });
        
        document.querySelectorAll('.tab').forEach(tab => {
            tab.classList.remove('active');
        });

        // نمایش تب انتخاب شده
        document.getElementById(`${tabName}-tab`).classList.add('active');
        event.target.classList.add('active');
        
        this.currentTab = tabName;
        
        // بارگذاری داده‌های تب
        switch(tabName) {
            case 'overview':
                this.loadOverview();
                break;
            case 'clients':
                this.loadClients();
                break;
            case 'plans':
                this.loadPlans();
                break;
            case 'analytics':
                this.loadAnalytics();
                break;
            case 'api':
                this.loadApiManagement();
                break;
        }
    }

    async loadDashboardData() {
        await Promise.all([
            this.loadOverview(),
            this.loadClients(),
            this.loadPlans()
        ]);
    }

    async loadOverview() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/api/clients/list`);
            const result = await response.json();

            if (result.success) {
                this.currentClients = result.clients;
                
                // محاسبه آمار
                const totalClients = result.clients.length;
                const activeClients = result.clients.filter(c => c.status === 'active').length;
                
                // بروزرسانی آمار کلی
                document.getElementById('totalClients').textContent = totalClients;
                document.getElementById('activeClients').textContent = activeClients;
                
                // نمایش خلاصه
                this.renderOverview();
            }
        } catch (error) {
            console.error('Error loading overview:', error);
        }
    }

    renderOverview() {
        const overviewContent = document.getElementById('overviewContent');
        
        const recentClients = this.currentClients
            .sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
            .slice(0, 5);
        
        overviewContent.innerHTML = `
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 2rem;">
                <div>
                    <h3 style="margin-bottom: 1rem; color: var(--primary);">👥 کلاینت‌های اخیر</h3>
                    <div style="background: var(--darker); padding: 1rem; border-radius: 10px;">
                        ${recentClients.map(client => `
                            <div style="display: flex; justify-content: between; align-items: center; padding: 0.5rem 0; border-bottom: 1px solid rgba(255,255,255,0.1);">
                                <div>
                                    <div style="font-weight: 600;">${client.company_name || 'بدون نام'}</div>

cat > frontend/public/client_dashboard.js << 'EOF'
class ClientDashboard {
    constructor() {
        this.apiBaseUrl = 'http://localhost:8000';
        this.currentClients = [];
        this.currentTab = 'overview';
        
        this.init();
    }

    init() {
        console.log('👥 پنل مدیریت کلاینت‌ها فعال شد');
        this.loadDashboardData();
        this.setupEventListeners();
    }

    setupEventListeners() {
        // مدیریت کلیک روی تب‌ها
        document.querySelectorAll('.tab').forEach(tab => {
            tab.addEventListener('click', (e) => {
                const tabName = e.target.getAttribute('onclick').match(/'([^']+)'/)[1];
                this.showTab(tabName);
            });
        });
    }

    showTab(tabName) {
        // مخفی کردن همه تب‌ها
        document.querySelectorAll('.tab-content').forEach(tab => {
            tab.classList.remove('active');
        });
        
        document.querySelectorAll('.tab').forEach(tab => {
            tab.classList.remove('active');
        });

        // نمایش تب انتخاب شده
        document.getElementById(`${tabName}-tab`).classList.add('active');
        event.target.classList.add('active');
        
        this.currentTab = tabName;
        
        // بارگذاری داده‌های تب
        switch(tabName) {
            case 'overview':
                this.loadOverview();
                break;
            case 'clients':
                this.loadClients();
                break;
            case 'plans':
                this.loadPlans();
                break;
            case 'analytics':
                this.loadAnalytics();
                break;
            case 'api':
                this.loadApiManagement();
                break;
        }
    }

    async loadDashboardData() {
        await Promise.all([
            this.loadOverview(),
            this.loadClients(),
            this.loadPlans()
        ]);
    }

    async loadOverview() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/api/clients/list`);
            const result = await response.json();

            if (result.success) {
                this.currentClients = result.clients;
                
                // محاسبه آمار
                const totalClients = result.clients.length;
                const activeClients = result.clients.filter(c => c.status === 'active').length;
                
                // بروزرسانی آمار کلی
                document.getElementById('totalClients').textContent = totalClients;
                document.getElementById('activeClients').textContent = activeClients;
                
                // نمایش خلاصه
                this.renderOverview();
            }
        } catch (error) {
            console.error('Error loading overview:', error);
        }
    }

    renderOverview() {
        const overviewContent = document.getElementById('overviewContent');
        
        const recentClients = this.currentClients
            .sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
            .slice(0, 5);
        
        overviewContent.innerHTML = `
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 2rem;">
                <div>
                    <h3 style="margin-bottom: 1rem; color: var(--primary);">👥 کلاینت‌های اخیر</h3>
                    <div style="background: var(--darker); padding: 1rem; border-radius: 10px;">
                        ${recentClients.map(client => `
                            <div style="display: flex; justify-content: between; align-items: center; padding: 0.5rem 0; border-bottom: 1px solid rgba(255,255,255,0.1);">
                                <div>
                                    <div style="font-weight: 600;">${client.company_name || 'بدون نام'}</div>
                                    <div style="font-size: 0.8rem; color: #94a3b8;">${client.email}</div>
                                </div>
                                <span class="tier-badge">${client.subscription_tier}</span>
                            </div>
                        `).join('')}
                    </div>
                </div>
                
                <div>
                    <h3 style="margin-bottom: 1rem; color: var(--primary);">📈 توزیع اشتراک‌ها</h3>
                    <div style="background: var(--darker); padding: 1rem; border-radius: 10px;">
                        ${this.renderSubscriptionDistribution()}
                    </div>
                </div>
            </div>
        `;
    }

    renderSubscriptionDistribution() {
        const tiers = {};
        this.currentClients.forEach(client => {
            tiers[client.subscription_tier] = (tiers[client.subscription_tier] || 0) + 1;
        });

        return Object.entries(tiers).map(([tier, count]) => `
            <div style="display: flex; justify-content: between; align-items: center; padding: 0.5rem 0; border-bottom: 1px solid rgba(255,255,255,0.1);">
                <span>${this.getTierName(tier)}</span>
                <div>
                    <span style="font-weight: 600;">${count}</span>
                    <span style="font-size: 0.8rem; color: #94a3b8;"> کلاینت</span>
                </div>
            </div>
        `).join('');
    }

    getTierName(tier) {
        const tierNames = {
            'free': '🆓 رایگان',
            'basic': '⭐ پایه',
            'professional': '🚀 حرفه‌ای',
            'enterprise': '🏢 سازمانی'
        };
        return tierNames[tier] || tier;
    }

    async loadClients() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/api/clients/list`);
            const result = await response.json();

            if (result.success) {
                this.currentClients = result.clients;
                this.renderClientsTable();
            }
        } catch (error) {
            console.error('Error loading clients:', error);
        }
    }

    renderClientsTable() {
        const tbody = document.getElementById('clientsTableBody');
        
        if (this.currentClients.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="6" style="text-align: center; padding: 2rem; color: #94a3b8;">
                        هیچ کلاینتی ثبت نشده است
                    </td>
                </tr>
            `;
            return;
        }

        tbody.innerHTML = this.currentClients.map(client => `
            <tr>
                <td>
                    <div style="font-weight: 600;">${client.company_name || 'بدون نام'}</div>
                    <div style="font-size: 0.8rem; color: #94a3b8;">${client.contact_person}</div>
                </td>
                <td>${client.email}</td>
                <td><span class="tier-badge">${client.subscription_tier}</span></td>
                <td><span class="status-badge status-${client.status}">${this.getStatusText(client.status)}</span></td>
                <td>
                    <div style="display: flex; align-items: center; gap: 0.5rem;">
                        <div style="flex: 1; background: #374151; height: 8px; border-radius: 4px; overflow: hidden;">
                            <div style="height: 100%; background: var(--primary); width: ${(client.used_quota / client.monthly_quota) * 100}%"></div>
                        </div>
                        <span style="font-size: 0.8rem;">${client.used_quota}/${client.monthly_quota}</span>
                    </div>
                </td>
                <td>
                    <button class="btn btn-primary" style="padding: 0.5rem 1rem; font-size: 0.8rem;" 
                            onclick="clientDashboard.viewClient('${client.client_id}')">
                        مشاهده
                    </button>
                </td>
            </tr>
        `).join('');
    }

    getStatusText(status) {
        const statusMap = {
            'active': 'فعال',
            'suspended': 'معلق',
            'inactive': 'غیرفعال'
        };
        return statusMap[status] || status;
    }

    async loadPlans() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/api/clients/plans`);
            const result = await response.json();

            if (result.success) {
                this.renderPlans(result.plans);
            }
        } catch (error) {
            console.error('Error loading plans:', error);
        }
    }

    renderPlans(plans) {
        const container = document.getElementById('plansContainer');
        
        container.innerHTML = Object.entries(plans).map(([tier, plan]) => `
            <div class="plan-card ${tier === 'professional' ? 'featured' : ''}">
                <h3>${this.getTierName(tier)}</h3>
                <div class="plan-price">$${plan.monthly_price}</div>
                <div style="color: #94a3b8; margin-bottom: 1rem;">ماهیانه</div>
                
                <ul class="plan-features">
                    <li>${plan.conversion_quota} تبدیل در ماه</li>
                    <li>حداکثر ${plan.max_file_size / (1024 * 1024)}MB فایل</li>
                    <li>پشتیبانی ${plan.support_level}</li>
                    ${plan.features.map(feature => `<li>${feature}</li>`).join('')}
                </ul>
                
                <button class="btn ${tier === 'professional' ? 'btn-primary' : 'btn-success'}" 
                        style="width: 100%;"
                        onclick="clientDashboard.showPlanDetails('${tier}')">
                    جزئیات بیشتر
                </button>
            </div>
        `).join('');
    }

    viewClient(clientId) {
        // نمایش جزئیات کلاینت
        const client = this.currentClients.find(c => c.client_id === clientId);
        if (client) {
            alert(`جزئیات کلاینت:\n\nشرکت: ${client.company_name}\nایمیل: ${client.email}\nاشتراک: ${client.subscription_tier}`);
        }
    }

    showPlanDetails(tier) {
        alert(`جزئیات پلن ${this.getTierName(tier)}`);
    }

    showAddClientForm() {
        const formHtml = `
            <div style="background: var(--darker); padding: 2rem; border-radius: 10px; margin-top: 1rem;">
                <h3 style="margin-bottom: 1rem; color: var(--primary);">➕ ثبت کلاینت جدید</h3>
                
                <div class="form-group">
                    <label>ایمیل</label>
                    <input type="email" id="newClientEmail" placeholder="email@example.com">
                </div>
                
                <div class="form-group">
                    <label>نام شرکت (اختیاری)</label>
                    <input type="text" id="newClientCompany" placeholder="نام شرکت">
                </div>
                
                <div class="form-group">
                    <label>نام مسئول</label>
                    <input type="text" id="newClientContact" placeholder="نام کامل">
                </div>
                
                <div class="form-group">
                    <label>پلن اشتراک</label>
                    <select id="newClientTier">
                        <option value="free">رایگان</option>
                        <option value="basic">پایه</option>
                        <option value="professional">حرفه‌ای</option>
                        <option value="enterprise">سازمانی</option>
                    </select>
                </div>
                
                <button class="btn btn-success" onclick="clientDashboard.registerNewClient()" style="width: 100%;">
                    ثبت کلاینت
                </button>
            </div>
        `;

        // اضافه کردن فرم به صفحه
        const clientsTab = document.getElementById('clients-tab');
        const existingForm = clientsTab.querySelector('.client-form');
        if (existingForm) existingForm.remove();

        const formDiv = document.createElement('div');
        formDiv.className = 'client-form';
        formDiv.innerHTML = formHtml;
        clientsTab.querySelector('.section').appendChild(formDiv);
    }

    async registerNewClient() {
        const email = document.getElementById('newClientEmail').value;
        const company = document.getElementById('newClientCompany').value;
        const contact = document.getElementById('newClientContact').value;
        const tier = document.getElementById('newClientTier').value;

        if (!email) {
            alert('لطفاً ایمیل را وارد کنید');
            return;
        }

        try {
            const response = await fetch(`${this.apiBaseUrl}/api/clients/register`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    email: email,
                    company_name: company,
                    contact_person: contact,
                    subscription_tier: tier
                })
            });

            const result = await response.json();

            if (result.success) {
                alert('✅ کلاینت با موفقیت ثبت شد!\n\nAPI Key: ' + result.api_key);
                this.loadClients();
                
                // حذف فرم
                document.querySelector('.client-form').remove();
            } else {
                alert('❌ خطا: ' + result.error);
            }
        } catch (error) {
            alert('❌ خطا در ثبت کلاینت');
            console.error('Registration error:', error);
        }
    }

    async loadAnalytics() {
        // بارگذاری داده‌های تحلیل
        document.getElementById('analyticsContent').innerHTML = `
            <div style="text-align: center; padding: 2rem; color: #94a3b8;">
                📊 بخش تحلیل‌ها به زودی اضافه خواهد شد
            </div>
        `;
    }

    async loadApiManagement() {
        // بارگذاری مدیریت API
        document.getElementById('apiContent').innerHTML = `
            <div style="background: var(--darker); padding: 2rem; border-radius: 10px;">
                <h3 style="margin-bottom: 1rem; color: var(--primary);">🔑 مدیریت API Keys</h3>
                <p style="margin-bottom: 1rem; color: #94a3b8;">
                    از API Keys برای احراز هویت در API سرویس استفاده کنید.
                </p>
                
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 2rem;">
                    <div>
                        <h4 style="margin-bottom: 1rem;">📖 مستندات API</h4>
                        <div style="background: rgba(0,0,0,0.3); padding: 1rem; border-radius: 8px;">
                            <pre style="color: #94a3b8; font-size: 0.9rem;">
endpoint: /api/convert/start
method: POST
headers: {
    "X-API-Key": "your_api_key_here",
    "Content-Type": "multipart/form-data"
}
                            </pre>
                        </div>
                    </div>
                    
                    <div>
                        <h4 style="margin-bottom: 1rem;">🔐 تست API Key</h4>
                        <div class="form-group">
                            <input type="text" id="testApiKey" placeholder="API Key خود را وارد کنید" style="font-family: monospace;">
                        </div>
                        <button class="btn btn-primary" onclick="clientDashboard.testApiKey()">
                            تست API Key
                        </button>
                    </div>
                </div>
            </div>
        `;
    }

    async testApiKey() {
        const apiKey = document.getElementById('testApiKey').value;
        
        if (!apiKey) {
            alert('لطفاً API Key را وارد کنید');
            return;
        }

        try {
            const response = await fetch(`${this.apiBaseUrl}/api/clients/verify`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ api_key: apiKey })
            });

            const result = await response.json();

            if (result.success) {
                alert(`✅ API Key معتبر است\n\nClient ID: ${result.client_id}\nTier: ${result.subscription_tier}`);
            } else {
                alert('❌ API Key نامعتبر است');
            }
        } catch (error) {
            alert('❌ خطا در تست API Key');
            console.error('API test error:', error);
        }
    }
}

// راه‌اندازی پنل مدیریت کلاینت‌ها
const clientDashboard = new ClientDashboard();
