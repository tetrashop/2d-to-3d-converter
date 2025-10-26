from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import uuid
import json
import threading
from datetime import datetime
from pathlib import Path
import logging
from werkzeug.utils import secure_filename

# کلاس تبدیل که قبلاً ساختیم
from .image_to_3d_converter import ImageTo3DConverter

app = Flask(__name__)
CORS(app)

# تنظیمات
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# ایجاد پوشه‌ها
Path(UPLOAD_FOLDER).mkdir(exist_ok=True)
Path(OUTPUT_FOLDER).mkdir(exist_ok=True)

# صف کارها
conversion_tasks = {}
task_queue = []

# تنظیمات لاگ
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

class ConversionTask:
    """کلاس مدیریت کارهای تبدیل"""
    
    def __init__(self, task_id, input_path, output_format):
        self.task_id = task_id
        self.input_path = input_path
        self.output_format = output_format
        self.status = "pending"  # pending, processing, completed, failed
        self.progress = 0
        self.message = ""
        self.output_path = ""
        self.start_time = None
        self.end_time = None
        
    def to_dict(self):
        return {
            "task_id": self.task_id,
            "status": self.status,
            "progress": self.progress,
            "message": self.message,
            "output_path": self.output_path,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None
        }

def process_conversion_task(task):
    """پردازش تبدیل در background"""
    try:
        task.status = "processing"
        task.start_time = datetime.utcnow()
        task.progress = 10
        
        logger.info(f"شروع تبدیل تسک {task.task_id}")
        
        # ایجاد مبدل
        converter = ImageTo3DConverter()
        
        # مسیر خروجی
        output_filename = f"{task.task_id}_3d_model.{task.output_format}"
        output_path = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)
        
        task.progress = 30
        
        # انجام تبدیل
        result = converter.convert_2d_to_3d(
            input_image_path=task.input_path,
            output_model_path=output_path,
            output_format=task.output_format
        )
        
        task.progress = 90
        
        if result["success"]:
            task.status = "completed"
            task.output_path = output_path
            task.message = "تبدیل با موفقیت انجام شد"
            task.progress = 100
            
            logger.info(f"تبدیل تسک {task.task_id} موفقیت‌آمیز بود")
        else:
            task.status = "failed"
            task.message = result["message"]
            logger.error(f"خطا در تبدیل تسک {task.task_id}: {result['message']}")
        
        task.end_time = datetime.utcnow()
        
    except Exception as e:
        task.status = "failed"
        task.message = f"خطای سیستمی: {str(e)}"
        task.end_time = datetime.utcnow()
        logger.error(f"خطا در پردازش تسک {task.task_id}: {str(e)}")

def task_worker():
    """کارگر برای پردازش تسک‌ها در صف"""
    while True:
        if task_queue:
            task_id = task_queue.pop(0)
            task = conversion_tasks.get(task_id)
            
            if task and task.status == "pending":
                # اجرای تبدیل در thread جداگانه
                thread = threading.Thread(target=process_conversion_task, args=(task,))
                thread.daemon = True
                thread.start()
        
        threading.Event().wait(1)  # خواب 1 ثانیه

# راه‌اندازی کارگر
worker_thread = threading.Thread(target=task_worker)
worker_thread.daemon = True
worker_thread.start()

# Routes
@app.route('/')
def home():
    return jsonify({
        "message": "سرویس ابری تبدیل 2D به 3D",
        "status": "active",
        "version": "1.0.0"
    })

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "healthy",
        "service": "2D to 3D Cloud Converter",
        "active_tasks": len([t for t in conversion_tasks.values() if t.status == "processing"]),
        "queued_tasks": len(task_queue)
    })

@app.route('/api/convert/start', methods=['POST'])
def start_conversion():
    """شروع یک کار تبدیل جدید"""
    try:
        # بررسی فایل
        if 'file' not in request.files:
            return jsonify({"error": "هیچ فایلی آپلود نشده"}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "هیچ فایلی انتخاب نشده"}), 400
        
        if not allowed_file(file.filename):
            return jsonify({"error": "فرمت فایل مجاز نیست"}), 400
        
        # دریافت فرمت خروجی
        output_format = request.form.get('format', 'glb').lower()
        if output_format not in ['glb', 'obj', 'stl', 'ply']:
            return jsonify({"error": "فرمت خروجی نامعتبر است"}), 400
        
        # تولید ID منحصر به فرد
        task_id = str(uuid.uuid4())
        
        # ذخیره فایل آپلود شده
        filename = secure_filename(file.filename)
        input_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{task_id}_{filename}")
        file.save(input_path)
        
        # ایجاد تسک جدید
        task = ConversionTask(task_id, input_path, output_format)
        conversion_tasks[task_id] = task
        task_queue.append(task_id)
        
        logger.info(f"تسک جدید ایجاد شد: {task_id}")
        
        return jsonify({
            "success": True,
            "task_id": task_id,
            "message": "کار تبدیل در صف قرار گرفت",
            "status_url": f"/api/convert/status/{task_id}"
        })
        
    except Exception as e:
        logger.error(f"خطا در شروع تبدیل: {str(e)}")
        return jsonify({"error": f"خطای سرور: {str(e)}"}), 500

@app.route('/api/convert/status/<task_id>', methods=['GET'])
def get_conversion_status(task_id):
    """دریافت وضعیت یک کار تبدیل"""
    task = conversion_tasks.get(task_id)
    
    if not task:
        return jsonify({"error": "کار تبدیل یافت نشد"}), 404
    
    return jsonify({
        "success": True,
        "task": task.to_dict()
    })

@app.route('/api/convert/download/<task_id>', methods=['GET'])
def download_converted_model(task_id):
    """دانلود مدل تبدیل شده"""
    task = conversion_tasks.get(task_id)
    
    if not task:
        return jsonify({"error": "کار تبدیل یافت نشد"}), 404
    
    if task.status != "completed":
        return jsonify({"error": "مدل هنوز آماده نیست"}), 400
    
    if not os.path.exists(task.output_path):
        return jsonify({"error": "فایل خروجی یافت نشد"}), 404
    
    try:
        filename = os.path.basename(task.output_path)
        return send_file(
            task.output_path,
            as_attachment=True,
            download_name=filename,
            mimetype='application/octet-stream'
        )
    except Exception as e:
        logger.error(f"خطا در دانلود: {str(e)}")
        return jsonify({"error": "خطا در دانلود فایل"}), 500

@app.route('/api/convert/list', methods=['GET'])
def list_conversions():
    """لیست تمام کارهای تبدیل"""
    tasks_list = [task.to_dict() for task in conversion_tasks.values()]
    
    return jsonify({
        "success": True,
        "tasks": tasks_list,
        "total_count": len(tasks_list)
    })

@app.route('/api/system/stats', methods=['GET'])
def system_stats():
    """آمار سیستم"""
    total_tasks = len(conversion_tasks)
    completed_tasks = len([t for t in conversion_tasks.values() if t.status == "completed"])
    failed_tasks = len([t for t in conversion_tasks.values() if t.status == "failed"])
    processing_tasks = len([t for t in conversion_tasks.values() if t.status == "processing"])
    
    # محاسبه فضای استفاده شده
    upload_size = sum(f.stat().st_size for f in Path(UPLOAD_FOLDER).glob('*') if f.is_file())
    output_size = sum(f.stat().st_size for f in Path(OUTPUT_FOLDER).glob('*') if f.is_file())
    
    return jsonify({
        "tasks": {
            "total": total_tasks,
            "completed": completed_tasks,
            "failed": failed_tasks,
            "processing": processing_tasks,
            "queued": len(task_queue)
        },
        "storage": {
            "uploads_bytes": upload_size,
            "outputs_bytes": output_size,
            "total_bytes": upload_size + output_size
        }
    })

if __name__ == '__main__':
    logger.info("🚀 راه‌اندازی سرور ابری تبدیل 2D به 3D...")
    app.run(host='0.0.0.0', port=8000, debug=True)
