from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import uuid
from werkzeug.utils import secure_filename

app = Flask(__name__)
CORS(app)  # فعال کردن CORS برای همه domainها

# تنظیمات آپلود
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def home():
    return jsonify({"message": "2D to 3D Converter API", "status": "active"})

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "service": "2D to 3D Converter"})

@app.route('/api/convert', methods=['POST'])
def convert_image():
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file uploaded"}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        
        if file and allowed_file(file.filename):
            # ذخیره فایل
            filename = secure_filename(file.filename)
            file_id = str(uuid.uuid4())
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{file_id}_{filename}")
            file.save(file_path)
            
            # شبیه‌سازی تبدیل به 3D
            return jsonify({
                "success": True,
                "message": "Conversion completed",
                "file_id": file_id,
                "download_url": f"/api/download/{file_id}"
            })
        else:
            return jsonify({"error": "Invalid file type"}), 400
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/test', methods=['GET'])
def test_connection():
    return jsonify({
        "message": "Connection successful!",
        "status": "connected",
        "timestamp": "2024-01-01T00:00:00Z"
    })

if __name__ == '__main__':
    # ایجاد پوشه آپلود
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    
    # اجرا روی همه interfaceها
    app.run(host='0.0.0.0', port=8000, debug=True)
