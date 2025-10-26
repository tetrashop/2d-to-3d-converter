class ImageTo3DConverter {
    constructor() {
        this.uploadSection = document.getElementById('uploadSection');
        this.fileInput = document.getElementById('fileInput');
        this.originalImage = document.getElementById('originalImage');
        this.modelViewer = document.getElementById('modelViewer');
        this.progressSection = document.getElementById('progressSection');
        this.progressFill = document.getElementById('progressFill');
        this.progressText = document.getElementById('progressText');
        this.resultSection = document.getElementById('resultSection');
        this.downloadBtn = document.getElementById('downloadBtn');
        this.errorMessage = document.getElementById('errorMessage');
        
        this.currentFileId = null;
        this.apiBaseUrl = 'http://localhost:8000'; // Backend URL
        
        this.initEventListeners();
    }

    initEventListeners() {
        // File input change
        this.fileInput.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                this.handleFileSelect(e.target.files[0]);
            }
        });

        // Drag and drop
        this.uploadSection.addEventListener('dragover', (e) => {
            e.preventDefault();
            this.uploadSection.classList.add('drag-over');
        });

        this.uploadSection.addEventListener('dragleave', () => {
            this.uploadSection.classList.remove('drag-over');
        });

        this.uploadSection.addEventListener('drop', (e) => {
            e.preventDefault();
            this.uploadSection.classList.remove('drag-over');
            if (e.dataTransfer.files.length > 0) {
                this.handleFileSelect(e.dataTransfer.files[0]);
            }
        });

        // Download button
        this.downloadBtn.addEventListener('click', () => {
            this.downloadModel();
        });
    }

    handleFileSelect(file) {
        if (!file.type.startsWith('image/')) {
            this.showError('لطفاً یک فایل تصویری انتخاب کنید');
            return;
        }

        // Show preview
        const reader = new FileReader();
        reader.onload = (e) => {
            this.originalImage.src = e.target.result;
            this.originalImage.style.display = 'block';
            this.startConversion(file);
        };
        reader.readAsDataURL(file);
    }

    async startConversion(file) {
        try {
            this.showProgress(0);
            this.hideError();
            this.hideResult();

            const formData = new FormData();
            formData.append('file', file);

            // Simulate progress
            this.simulateProgress();

            const response = await fetch(`${this.apiBaseUrl}/api/convert`, {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                throw new Error('خطا در ارتباط با سرور');
            }

            const result = await response.json();
            
            if (result.success) {
                this.currentFileId = result.file_id;
                this.showProgress(100);
                setTimeout(() => {
                    this.showResult();
                    this.updateModelViewer();
                }, 1000);
            } else {
                throw new Error(result.message || 'خطا در تبدیل تصویر');
            }

        } catch (error) {
            this.showError(error.message);
            this.hideProgress();
        }
    }

    simulateProgress() {
        let progress = 0;
        const interval = setInterval(() => {
            progress += Math.random() * 10;
            if (progress >= 90) {
                clearInterval(interval);
            }
            this.showProgress(progress);
        }, 300);
    }

    showProgress(percentage) {
        this.progressSection.style.display = 'block';
        this.progressFill.style.width = `${percentage}%`;
        this.progressText.textContent = `${Math.round(percentage)}%`;
    }

    hideProgress() {
        this.progressSection.style.display = 'none';
    }

    showResult() {
        this.resultSection.style.display = 'block';
    }

    hideResult() {
        this.resultSection.style.display = 'none';
    }

    showError(message) {
        this.errorMessage.textContent = message;
        this.errorMessage.style.display = 'block';
    }

    hideError() {
        this.errorMessage.style.display = 'none';
    }

    updateModelViewer() {
        this.modelViewer.innerHTML = `
            <div style="text-align: center;">
                <div style="font-size: 3rem;">🎯</div>
                <p>مدل سه بعدی آماده است!</p>
                <p style="font-size: 0.9rem; color: #6B7280;">فرمت: GLB</p>
            </div>
        `;
    }

    async downloadModel() {
        if (!this.currentFileId) {
            this.showError('مدلی برای دانلود موجود نیست');
            return;
        }

        try {
            const response = await fetch(`${this.apiBaseUrl}/api/download/${this.currentFileId}`);
            if (response.ok) {
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `3d_model_${this.currentFileId}.glb`;
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                document.body.removeChild(a);
            } else {
                throw new Error('خطا در دانلود مدل');
            }
        } catch (error) {
            this.showError(error.message);
        }
    }
}

// Initialize the application
document.addEventListener('DOMContentLoaded', () => {
    new ImageTo3DConverter();
});

// Service functions
function updateProgress(percentage) {
    const progressFill = document.getElementById('progressFill');
    const progressText = document.getElementById('progressText');
    if (progressFill && progressText) {
        progressFill.style.width = `${percentage}%`;
        progressText.textContent = `${percentage}%`;
    }
}

function showNotification(message, type = 'info') {
    // Simple notification implementation
    console.log(`[${type.toUpperCase()}] ${message}`);
}
