# ☁️ راهنمای استقرار CloudFlare Pages

## مراحل استقرار:

### 1. تنظیمات Build در CloudFlare Dashboard:
- **Build command:** `echo "No build needed"`
- **Build output directory:** `public`
- **Root directory:** (خالی بگذارید)

### 2. ساختار پروژه:
### 3. آدرس‌های سرویس:
- 🌐 **صفحه اصلی:** `https://2d-to-3d-converter.pages.dev`
- 🎨 **تبدیل پیشرفته:** `/advanced_converter.html`
- 🔧 **سرویس اصلی:** `/cloud_converter.html`
- 👥 **مدیریت:** `/client_dashboard.html`

### 4. نکات فنی:
- ✅ فایل‌های استاتیک در `/public` قرار دارند
- ✅ مسیریابی با `_redirects` مدیریت می‌شود
- ✅ بدون نیاز به Build Process
- ✅ استقرار خودکار از GitHub

## عیب‌یابی:

### اگر خطای Build Output Directory دیدید:
1. مطمئن شوید پوشه `public` وجود دارد
2. فایل‌های فرانت‌اند در `public` کپی شده‌اند
3. فایل `_redirects` در `public` وجود دارد

### اگر لینک‌ها کار نمی‌کنند:
1. بررسی کنید فایل `_redirects` شامل `/* /index.html 200` است
2. مسیر فایل‌ها در `public` صحیح است
