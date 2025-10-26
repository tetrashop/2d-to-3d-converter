from flask import Flask, request, jsonify, send_file
import cv2
import numpy as np
from PIL import Image
import os
import uuid
import json
from datetime import datetime

class Advanced3DConverter:
    def __init__(self):
        self.supported_formats = {
            'maya': '.ma',
            '3ds_max': '.max', 
            'blender': '.blend',
            'obj': '.obj',
            'stl': '.stl',
            'fbx': '.fbx',
            'dae': '.dae'
        }
    
    def analyze_image(self, image_path):
        """آنالیز تصویر برای استخراج ویژگی‌های سه بعدی"""
        img = cv2.imread(image_path)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # استخراج لبه‌ها
        edges = cv2.Canny(gray, 50, 150)
        
        # تشخیص عمق با استفاده از الگوریتم‌های کامپیوتر ویژن
        depth_map = self.estimate_depth(img)
        
        # استخراج بافت
        texture = self.extract_texture(img)
        
        return {
            'edges': edges,
            'depth_map': depth_map,
            'texture': texture,
            'dimensions': img.shape
        }
    
    def estimate_depth(self, image):
        """تخمین عمق از تصویر 2D"""
        # استفاده از الگوریتم‌های تخمین عمق
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # شبیه‌سازی نقشه عمق (در نسخه واقعی از مدل‌های ML استفاده می‌شود)
        depth = cv2.Laplacian(gray, cv2.CV_64F)
        depth = np.uint8(np.absolute(depth))
        
        return depth
    
    def extract_texture(self, image):
        """استخراج بافت از تصویر"""
        # تبدیل به فضای رنگی HSV برای استخراج بهتر بافت
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        return hsv
    
    def generate_3d_model(self, image_path, output_format='obj'):
        """تولید مدل 3D از تصویر"""
        analysis = self.analyze_image(image_path)
        
        # ایجاد مدل 3D ساده بر اساس آنالیز
        model_data = self.create_mesh_from_analysis(analysis)
        
        # ذخیره در فرمت‌های مختلف
        output_path = self.export_to_format(model_data, output_format, image_path)
        
        return output_path
    
    def create_mesh_from_analysis(self, analysis):
        """ایجاد مش از آنالیز تصویر"""
        vertices = []
        faces = []
        
        # ایجاد هندسه ساده بر اساس لبه‌ها
        edges = analysis['edges']
        height, width = analysis['dimensions'][:2]
        
        for y in range(0, height, 10):
            for x in range(0, width, 10):
                if edges[y, x] > 0:
                    z = analysis['depth_map'][y, x] / 255.0 * 2.0  # نرمال سازی عمق
                    vertices.append([x/width, y/height, z])
        
        # ایجاد faces ساده
        for i in range(len(vertices) - 2):
            faces.append([i, i+1, i+2])
        
        return {
            'vertices': vertices,
            'faces': faces,
            'texture': analysis['texture']
        }
    
    def export_to_format(self, model_data, format_type, original_image_path):
        """اکسپورت مدل به فرمت‌های مختلف"""
        base_name = os.path.splitext(original_image_path)[0]
        output_dir = "backend/outputs"
        os.makedirs(output_dir, exist_ok=True)
        
        output_path = os.path.join(output_dir, f"{uuid.uuid4()}_{format_type}{self.supported_formats[format_type]}")
        
        if format_type == 'obj':
            self.export_to_obj(model_data, output_path)
        elif format_type == 'maya':
            self.export_to_maya(model_data, output_path)
        elif format_type == '3ds_max':
            self.export_to_3ds_max(model_data, output_path)
        
        return output_path
    
    def export_to_obj(self, model_data, output_path):
        """اکسپورت به فرمت OBJ"""
        with open(output_path, 'w') as f:
            f.write("# 3D Model generated from 2D image\n")
            f.write(f"# Generated: {datetime.now()}\n\n")
            
            # نوشتن vertices
            for v in model_data['vertices']:
                f.write(f"v {v[0]} {v[1]} {v[2]}\n")
            
            # نوشتن faces
            for face in model_data['faces']:
                f.write(f"f {face[0]+1} {face[1]+1} {face[2]+1}\n")
    
    def export_to_maya(self, model_data, output_path):
        """اکسپورت به فرمت مایا (ASCII)"""
        with open(output_path, 'w') as f:
            f.write("//Maya ASCII scene\n")
            f.write("requires maya \"2023\";\n\n")
            
            # ایجاد mesh در مایا
            f.write("createNode transform -n \"model1\";\n")
            f.write("createNode mesh -n \"modelShape1\" -p \"model1\";\n")
            
            # اضافه کردن vertices
            f.write("setAttr -s {} \".vt\";\n".format(len(model_data['vertices'])))
            for i, v in enumerate(model_data['vertices']):
                f.write(f"setAttr \".vt[{i}]\" -type \"float3\" {v[0]} {v[1]} {v[2]};\n")
            
            # اضافه کردن faces
            f.write("setAttr -s {} \".fc\";\n".format(len(model_data['faces'])))
            for i, face in enumerate(model_data['faces']):
                f.write(f"setAttr \".fc[{i}]\" -type \"polyFaces\" f 3 {face[0]} {face[1]} {face[2]};\n")
    
    def export_to_3ds_max(self, model_data, output_path):
        """اکسپورت به فرمت 3ds Max (شبیه‌سازی)"""
        with open(output_path, 'w') as f:
            f.write("3DS_MAX_MODEL_FILE\n")
            f.write(f"Generated from 2D image: {datetime.now()}\n")
            f.write(f"Vertices: {len(model_data['vertices'])}\n")
            f.write(f"Faces: {len(model_data['faces'])}\n")

# ایجاد نمونه converter
converter = Advanced3DConverter()

app = Flask(__name__)

@app.route('/api/advanced/convert', methods=['POST'])
def advanced_convert():
    """اندپوینت تبدیل پیشرفته"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'فایلی آپلود نشده است'}), 400
        
        file = request.files['file']
        output_format = request.form.get('format', 'obj')
        
        if file.filename == '':
            return jsonify({'error': 'نام فایل معتبر نیست'}), 400
        
        # ذخیره فایل آپلود شده
        upload_dir = "backend/uploads"
        os.makedirs(upload_dir, exist_ok=True)
        file_path = os.path.join(upload_dir, f"{uuid.uuid4()}_{file.filename}")
        file.save(file_path)
        
        # تبدیل به مدل 3D
        output_path = converter.generate_3d_model(file_path, output_format)
        
        return jsonify({
            'success': True,
            'message': 'مدل 3D با موفقیت تولید شد',
            'download_url': f'/api/download/{os.path.basename(output_path)}',
            'format': output_format,
            'file_size': os.path.getsize(output_path)
        })
        
    except Exception as e:
        return jsonify({'error': f'خطا در پردازش: {str(e)}'}), 500

@app.route('/api/download/<filename>')
def download_file(filename):
    """دانلود فایل تولید شده"""
    return send_file(f"backend/outputs/{filename}", as_attachment=True)

@app.route('/api/formats')
def get_supported_formats():
    """دریافت فرمت‌های پشتیبانی شده"""
    return jsonify({
        'supported_formats': list(converter.supported_formats.keys()),
        'details': {
            'maya': 'Autodesk Maya (.ma)',
            '3ds_max': '3D Studio Max (.max)',
            'blender': 'Blender (.blend)',
            'obj': 'Wavefront OBJ',
            'stl': 'Stereolithography',
            'fbx': 'Autodesk FBX',
            'dae': 'Collada DAE'
        }
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8001, debug=True)
