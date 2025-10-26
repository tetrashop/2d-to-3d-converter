class CloudConverter {
    constructor() {
        this.apiBaseUrl = 'http://localhost:8000';
        this.currentTasks = new Map();
        this.pollingInterval = null;
        
        this.init();
    }

    init() {
        console.log('☁️ سرویس ابری تبدیل 2D به 3D فعال شد');
        
        // راه‌اندازی event listeners
        this.setupEventListeners();
        
        // شروع بروزرسانی خودکار
        this.startPolling();
        
        // بارگذاری اولیه آمار
        this.loadSystemStats();
    }

    setupEventListeners() {
        const fileInput = document.getElementById('fileInput');
        const uploadSection = document.getElementById('uploadSection');

        // تغییر فایل
        fileInput.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                this.handleFileSelect(e.target.files[0]);
            }
        });

        // Drag and drop
        uploadSection.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadSection.classList.add('drag-over');
        });

        uploadSection.addEventListener('dragleave', () => {
            uploadSection.classList.remove('drag-over');
        });

        uploadSection.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadSection.classList.remove('drag-over');
            if (e.dataTransfer.files.length > 0) {
                this.handleFileSelect(e.dataTransfer.files[0]);
            }
        });
    }

    async handleFileSelect(file) {
        if (!this.isValidFile(file)) {
            this.showNotification('فرمت فایل مجاز نیست یا حجم آن بیش از حد مجاز است', 'error');
            return;
        }

        try {
            this.showNotification('در حال آپلود تصویر...', 'info');

            const format = document.getElementById('outputFormat').value;
            const formData = new FormData();
            formData.append('file', file);
            formData.append('format', format);

            const response = await fetch(`${this.apiBaseUrl}/api/convert/start`, {
                method: 'POST',
                body: formData
            });

            const result = await response.json();

            if (result.success) {
                this.showNotification('کار تبدیل در صف قرار گرفت', 'success');
                this.addTaskToList(result.task_id);
            } else {
                this.showNotification(result.error || 'خطا در شروع تبدیل', 'error');
            }

        } catch (error) {
            this.showNotification('خطا در ارتباط با سرور', 'error');
            console.error('Upload error:', error);
        }
    }

    isValidFile(file) {
        const allowedTypes = ['image/jpeg', 'image/png', 'image/webp'];
        const maxSize = 50 * 1024 * 1024; // 50MB

        return allowedTypes.includes(file.type) && file.size <= maxSize;
    }

    async addTaskToList(taskId) {
        // اضافه کردن تسک به لیست
        this.currentTasks.set(taskId, {
            id: taskId,
            status: 'pending',
            progress: 0
        });

        await this.updateTaskStatus(taskId);
    }

    async updateTaskStatus(taskId) {
        try {
            const response = await fetch(`${this.apiBaseUrl}/api/convert/status/${taskId}`);
            const result = await response.json();

            if (result.success) {
                this.currentTasks.set(taskId, result.task);
                this.renderTasks();
            }
        } catch (error) {
            console.error('Error updating task status:', error);
        }
    }

    renderTasks() {
        const taskList = document.getElementById('taskList');
        const tasks = Array.from(this.currentTasks.values());

        if (tasks.length === 0) {
            taskList.innerHTML = '<p style="text-align: center; color: #94a3b8;">هیچ کاری وجود ندارد</p>';
            return;
        }

        taskList.innerHTML = tasks.map(task => `
            <div class="task-item">
                <div class="task-info">
                    <div style="display: flex; justify-content: between; align-items: center; margin-bottom: 0.5rem;">
                        <strong>کار #${task.task_id.slice(0, 8)}</strong>
                        <span class="task-status status-${task.status}">
                            ${this.getStatusText(task.status)}
                        </span>
                    </div>
                    
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: ${task.progress}%"></div>
                    </div>
                    
                    <div style="font-size: 0.9rem; color: #94a3b8;">
                        پیشرفت: ${task.progress}% | ${task.message || 'در انتظار...'}
                    </div>
                </div>
                
                <div>
                    ${task.status === 'completed' ? 
                        `<button class="btn btn-primary" onclick="cloudConverter.downloadModel('${task.task_id}')">
                            📥 دانلود
                        </button>` : 
                        ''
                    }
                </div>
            </div>
        `).join('');
    }

    getStatusText(status) {
        const statusMap = {
            'pending': 'در انتظار',
            'processing': 'در حال پردازش',
            'completed': 'تکمیل شده',
            'failed': 'ناموفق'
        };
        return statusMap[status] || status;
    }

    async downloadModel(taskId) {
        try {
            const response = await fetch(`${this.apiBaseUrl}/api/convert/download/${taskId}`);
            
            if (response.ok) {
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `3d_model_${taskId}.glb`;
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                document.body.removeChild(a);
                
                this.showNotification('مدل با موفقیت دانلود شد', 'success');
            } else {
                this.showNotification('خطا در دانلود مدل', 'error');
            }
        } catch (error) {
            this.showNotification('خطا در دانلود', 'error');
            console.error('Download error:', error);
        }
    }

    async loadSystemStats() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/api/system/stats`);
            const result = await response.json();

            if (result.success) {
                document.getElementById('activeTasks').textContent = 
                    result.tasks.processing + result.tasks.queued;
                document.getElementById('completedTasks').textContent = result.tasks.completed;
                document.getElementById('queuedTasks').textContent = result.tasks.queued;
            }
        } catch (error) {
            console.error('Error loading stats:', error);
        }
    }

    startPolling() {
        // بروزرسانی هر 3 ثانیه
        this.pollingInterval = setInterval(() => {
            this.updateAllTasks();
            this.loadSystemStats();
        }, 3000);
    }

    async updateAllTasks() {
        const updatePromises = Array.from(this.currentTasks.keys()).map(taskId => 
            this.updateTaskStatus(taskId)
        );
        await Promise.all(updatePromises);
    }

    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.textContent = message;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.remove();
        }, 5000);
    }
}

// راه‌اندازی سرویس ابری
const cloudConverter = new CloudConverter();
