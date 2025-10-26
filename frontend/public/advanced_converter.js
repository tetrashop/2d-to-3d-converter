class Advanced3DConverter {
    constructor() {
        this.apiBaseUrl = 'http://localhost:8001';
        this.selectedFile = null;
        this.selectedFormat = 'obj';
        this.currentModel = null;
        
        this.init();
    }

    init() {
        console.log('🎨 سیستم پیشرفته تبدیل 2D به 3D فعال شد');
        this.setupEventListeners();
        this.loadSupportedFormats();
    }

    setupEventListeners() {
        // آپلود فایل
        const uploadArea = document.getElementById('uploadArea');
        const fileInput = document.getElementById('fileInput');
        
        uploadArea.addEventListener('click', () => fileInput.click());
        uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadArea.style.borderColor = 'var(--success)';
            uploadArea.style.background = 'rgba(16, 185, 129, 0.1)';
        });
        
        uploadArea.addEventListener('dragleave', () => {
            uploadArea.style.borderColor = 'rgba(99, 102, 241, 0.5)';
            uploadArea.style.background = 'transparent';
        });
        
        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                this.handleFileSelect(files[0]);
            }
        });
        
        fileInput.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                this.handleFileSelect(e.target.files[0]);
            }
        });

        // انتخاب فرمت
        document.querySelectorAll('.format-option').forEach(option => {
            option.addEventListener('click', () => {
                document.querySelectorAll('.format-option').forEach(opt => {
                    opt.classList.remove('selected');
                });
                option.classList.add('selected');
                this.selectedFormat = option.dataset.format;
                console.log('فرمت انتخاب شده:', this.selectedFormat);
            });
        });

        // دکمه تبدیل
        document.getElementById('convertBtn').addEventListener('click', () => {
            this.convertImage();
        });

        // کنترل‌های مدل
        this.setupModelControls();
    }

    handleFileSelect(file) {
        if (!file.type.match('image.*')) {
            alert('لطفاً یک فایل تصویری انتخاب کنید');
            return;
        }

        this.selectedFile = file;
        
        // نمایش پیش‌نمایش تصویر
        const reader = new FileReader();
        reader.onload = (e) => {
            const preview = document.getElementById('imagePreview');
            const previewImg = document.getElementById('previewImg');
            
            previewImg.src = e.target.result;
            preview.classList.remove('hidden');
            
            // به کاربر اطلاع دهید
            document.getElementById('uploadArea').innerHTML = `
                <div style="color: var(--success);">
                    <div>✅</div>
                    <h3>فایل انتخاب شد</h3>
                    <p>${file.name}</p>
                    <p style="font-size: 0.8rem;">سایز: ${(file.size / 1024 / 1024).toFixed(2)} MB</p>
                </div>
            `;
        };
        reader.readAsDataURL(file);
    }

    async loadSupportedFormats() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/api/formats`);
            const data = await response.json();
            console.log('فرمت‌های پشتیبانی شده:', data);
        } catch (error) {
            console.error('خطا در دریافت فرمت‌ها:', error);
        }
    }

    async convertImage() {
        if (!this.selectedFile) {
            alert('لطفاً ابتدا یک تصویر انتخاب کنید');
            return;
        }

        const convertBtn = document.getElementById('convertBtn');
        const progressContainer = document.getElementById('progressContainer');
        const progressFill = document.getElementById('progressFill');
        const progressText = document.getElementById('progressText');

        // نمایش progress bar
        progressContainer.classList.remove('hidden');
        convertBtn.disabled = true;
        convertBtn.innerHTML = '⏳ در حال پردازش...';

        try {
            const formData = new FormData();
            formData.append('file', this.selectedFile);
            formData.append('format', this.selectedFormat);

            // شبیه‌سازی progress
            this.simulateProgress(progressFill, progressText);

            const response = await fetch(`${this.apiBaseUrl}/api/advanced/convert`, {
                method: 'POST',
                body: formData
            });

            const result = await response.json();

            if (result.success) {
                // تکمیل progress bar
                progressFill.style.width = '100%';
                progressText.textContent = '100%';

                // نمایش نتایج
                this.showResults(result);
                
                // شبیه‌سازی نمایش مدل 3D
                this.simulate3DModel();
                
            } else {
                throw new Error(result.error);
            }

        } catch (error) {
            alert('خطا در تبدیل تصویر: ' + error.message);
            console.error('Conversion error:', error);
        } finally {
            convertBtn.disabled = false;
            convertBtn.innerHTML = '🚀 آغاز تبدیل پیشرفته';
        }
    }

    simulateProgress(progressFill, progressText) {
        let progress = 0;
        const interval = setInterval(() => {
            progress += Math.random() * 10;
            if (progress >= 90) {
                progress = 90;
                clearInterval(interval);
            }
            progressFill.style.width = progress + '%';
            progressText.textContent = Math.round(progress) + '%';
        }, 200);
    }

    showResults(result) {
        const resultSection = document.getElementById('resultSection');
        const downloadBtn = document.getElementById('downloadOriginal');
        const fileInfo = document.getElementById('fileInfo');

        resultSection.classList.remove('hidden');
        
        // به روزرسانی اطلاعات فایل
        fileInfo.textContent = `فرمت: ${result.format.toUpperCase()} - سایز: ${(result.file_size / 1024).toFixed(1)}KB`;
        
        // تنظیم لینک دانلود
        downloadBtn.href = `${this.apiBaseUrl}${result.download_url}`;
        downloadBtn.download = `model.${result.format}`;
    }

    simulate3DModel() {
        const modelViewer = document.getElementById('modelViewer');
        
        // شبیه‌سازی یک مدل 3D ساده با CSS
        modelViewer.innerHTML = `
            <div style="
                width: 100%;
                height: 100%;
                background: linear-gradient(45deg, #6366f1, #10b981);
                border-radius: 10px;
                display: flex;
                justify-content: center;
                align-items: center;
                color: white;
                font-size: 1.2rem;
                animation: rotate 10s infinite linear;
            ">
                <div style="text-align: center;">
                    <div style="font-size: 3rem;">🎭</div>
                    <div>مدل 3D تولید شده</div>
                    <div style="font-size: 0.8rem; opacity: 0.8;">از کنترل‌ها برای چرخش و زوم استفاده کنید</div>
                </div>
            </div>
            <style>
                @keyframes rotate {
                    from { transform: rotateY(0deg); }
                    to { transform: rotateY(360deg); }
                }
            </style>
        `;
    }

    setupModelControls() {
        let scale = 1;
        let rotation = 0;

        document.getElementById('rotateBtn').addEventListener('click', () => {
            rotation += 45;
            this.applyTransform(scale, rotation);
        });

        document.getElementById('zoomInBtn').addEventListener('click', () => {
            scale += 0.1;
            this.applyTransform(scale, rotation);
        });

        document.getElementById('zoomOutBtn').addEventListener('click', () => {
            scale = Math.max(0.5, scale - 0.1);
            this.applyTransform(scale, rotation);
        });

        document.getElementById('resetBtn').addEventListener('click', () => {
            scale = 1;
            rotation = 0;
            this.applyTransform(scale, rotation);
        });
    }

    applyTransform(scale, rotation) {
        const model = document.querySelector('#modelViewer > div');
        if (model) {
            model.style.transform = `scale(${scale}) rotateY(${rotation}deg)`;
        }
    }
}

// راه‌اندازی سیستم
const advancedConverter = new Advanced3DConverter();
