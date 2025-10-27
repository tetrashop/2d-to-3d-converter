import numpy as np
import cv2
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from sklearn.cluster import DBSCAN
from scipy import ndimage
from scipy.spatial import KDTree
import torch
import torch.nn as nn
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import threading
from queue import Queue
import time
import os

class NeuralDepthEstimator(nn.Module):
    def __init__(self):
        super(NeuralDepthEstimator, self).__init__()
        self.conv1 = nn.Conv2d(1, 32, 3, padding=1)
        self.conv2 = nn.Conv2d(32, 64, 3, padding=1)
        self.conv3 = nn.Conv2d(64, 128, 3, padding=1)
        self.deconv1 = nn.ConvTranspose2d(128, 64, 3, padding=1)
        self.deconv2 = nn.ConvTranspose2d(64, 32, 3, padding=1)
        self.deconv3 = nn.ConvTranspose2d(32, 1, 3, padding=1)
        self.relu = nn.ReLU()
        self.sigmoid = nn.Sigmoid()
    
    def forward(self, x):
        x = self.relu(self.conv1(x))
        x = self.relu(self.conv2(x))
        x = self.relu(self.conv3(x))
        x = self.relu(self.deconv1(x))
        x = self.relu(self.deconv2(x))
        x = self.sigmoid(self.deconv3(x))
        return x

class FuzzySphericalTransformer:
    def __init__(self):
        self.membership_cache = {}
    
    def cartesian_to_spherical(self, x, y, z):
        r = np.sqrt(x**2 + y**2 + z**2)
        if r == 0:
            return 0, 0, 0
        theta = np.arccos(z / r)
        phi = np.arctan2(y, x)
        return r, theta, phi
    
    def calculate_pixel_membership(self, x, y, image):
        """محاسبه درجه عضویت فازی برای پیکسل"""
        intensity = image[y, x] if len(image.shape) == 2 else np.mean(image[y, x])
        
        # تابع عضویت فازی ساده‌شده
        intensity_membership = 1.0 - abs(intensity - 0.5) / 0.5
        
        return intensity_membership
    
    def fuzzy_cartesian_to_spherical(self, x, y, image, center_x, center_y):
        # نرمال‌سازی مختصات
        norm_x = (x - center_x) / max(center_x, 1)
        norm_y = (y - center_y) / max(center_y, 1)
        
        # محاسبه درجه عضویت
        membership = self.calculate_pixel_membership(x, y, image)
        
        # اعمال منطق فازی در تبدیل
        fuzzy_r = np.sqrt(norm_x**2 + norm_y**2) * (0.3 + 0.7 * membership)
        fuzzy_theta = np.arctan2(norm_y, norm_x)
        fuzzy_phi = (np.pi / 2) * membership  # زاویه ارتفاع بر اساس عضویت
        
        return fuzzy_r, fuzzy_theta, fuzzy_phi, membership

class Advanced2DTo3DConverter:
    def __init__(self):
        self.fuzzy_transformer = FuzzySphericalTransformer()
        self.depth_estimator = self.load_depth_estimator()
        self.progress_queue = Queue()
        
    def load_depth_estimator(self):
        """بارگذاری مدل تخمین عمق"""
        try:
            model = NeuralDepthEstimator()
            # حالت ارزیابی
            model.eval()
            return model
        except Exception as e:
            print(f"خطا در بارگذاری مدل: {e}")
            return None
    
    def load_and_preprocess_image(self, image_path):
        """بارگذاری و پیش‌پردازش تصویر"""
        try:
            # بارگذاری تصویر
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError("نمی‌توان تصویر را بارگذاری کرد")
            
            # تبدیل به خاکستری
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                gray = image
            
            # تغییر اندازه برای کارایی بهتر
            h, w = gray.shape
            max_dim = 400  # حداکثر بعد برای پردازش سریع‌تر
            if max(h, w) > max_dim:
                scale = max_dim / max(h, w)
                new_w = int(w * scale)
                new_h = int(h * scale)
                gray = cv2.resize(gray, (new_w, new_h))
            
            # نرمال‌سازی
            normalized = gray.astype(np.float32) / 255.0
            
            self.progress_queue.put("تصویر با موفقیت بارگذاری و پیش‌پردازش شد")
            return normalized, gray
            
        except Exception as e:
            self.progress_queue.put(f"خطا در بارگذاری تصویر: {str(e)}")
            return None, None
    
    def estimate_depth_map(self, image):
        """تخمین نقشه عمق"""
        try:
            if self.depth_estimator is not None and torch.cuda.is_available():
                # استفاده از مدل عصبی
                input_tensor = torch.from_numpy(image).unsqueeze(0).unsqueeze(0).float()
                with torch.no_grad():
                    depth = self.depth_estimator(input_tensor)
                depth_map = depth.squeeze().numpy()
            else:
                # روش ساده‌تر مبتنی بر گرادیان
                depth_map = self.gradient_based_depth(image)
            
            self.progress_queue.put("نقشه عمق تخمین زده شد")
            return depth_map
            
        except Exception as e:
            self.progress_queue.put(f"خطا در تخمین عمق: {str(e)}")
            return self.gradient_based_depth(image)
    
    def gradient_based_depth(self, image):
        """تخمین عمق بر اساس گرادیان"""
        sobelx = cv2.Sobel(image, cv2.CV_64F, 1, 0, ksize=3)
        sobely = cv2.Sobel(image, cv2.CV_64F, 0, 1, ksize=3)
        gradient_magnitude = np.sqrt(sobelx**2 + sobely**2)
        
        # نرمال‌سازی و معکوس کردن (مناطق با گرادیان بالا = عمق کمتر)
        if np.max(gradient_magnitude) > 0:
            depth = 1.0 - (gradient_magnitude / np.max(gradient_magnitude))
        else:
            depth = np.ones_like(image)
        return depth
    
    def convert_to_3d_points(self, image, depth_map):
        """تبدیل تصویر 2D به نقاط 3D"""
        try:
            h, w = image.shape
            center_x, center_y = w // 2, h // 2
            
            points_3d = []
            colors = []
            
            # نمونه‌برداری برای کارایی بهتر
            step = max(1, min(h, w) // 100)  # افزایش نمونه‌برداری برای نتایج بهتر
            
            total_pixels = (h // step) * (w // step)
            processed = 0
            
            for y in range(0, h, step):
                for x in range(0, w, step):
                    if image[y, x] > 0.05:  # نادیده گرفتن پیکسل‌های بسیار تاریک
                        # تبدیل فازی-کروی
                        r, theta, phi, membership = self.fuzzy_transformer.fuzzy_cartesian_to_spherical(
                            x, y, image, center_x, center_y
                        )
                        
                        # استفاده از عمق تخمین‌زده شده
                        depth_val = depth_map[y, x] if depth_map is not None else membership
                        
                        # تبدیل به مختصات کارتزین 3D
                        scale_factor = min(h, w) / 4  # فاکتور مقیاس برای نمایش بهتر
                        x_3d = r * np.cos(theta) * np.sin(phi) * depth_val * scale_factor
                        y_3d = r * np.sin(theta) * np.sin(phi) * depth_val * scale_factor
                        z_3d = r * np.cos(phi) * depth_val * scale_factor * 2
                        
                        points_3d.append([x_3d, y_3d, z_3d])
                        
                        # رنگ بر اساس شدت تصویر اصلی
                        intensity = int(image[y, x] * 255)
                        colors.append([intensity, intensity, intensity])
                    
                    processed += 1
                    if processed % 1000 == 0:
                        progress = (processed / total_pixels) * 100
                        self.progress_queue.put(f"تبدیل 3D: {progress:.1f}%")
            
            points_3d = np.array(points_3d)
            colors = np.array(colors)
            
            self.progress_queue.put(f"تعداد نقاط 3D تولید شده: {len(points_3d)}")
            return points_3d, colors, None
            
        except Exception as e:
            self.progress_queue.put(f"خطا در تبدیل 3D: {str(e)}")
            return None, None, None
    
    def apply_spatial_corrections(self, points_3d, colors, valid_indices=None):
        """اعمال تصحیحات فضایی"""
        try:
            if len(points_3d) < 10:
                return points_3d, colors
            
            # 1. حذف نقاط پرت با DBSCAN (ساده‌شده)
            if len(points_3d) > 50:
                try:
                    clustering = DBSCAN(eps=0.5, min_samples=5).fit(points_3d)
                    labels = clustering.labels_
                    
                    # نگه داشتن نقاطی که نویز نیستند (label != -1)
                    if np.sum(labels != -1) > 10:
                        points_3d = points_3d[labels != -1]
                        colors = colors[labels != -1]
                except:
                    pass  # اگر DBSCAN شکست خورد، ادامه بده
            
            # 2. هموارسازی ساده
            if len(points_3d) > 3:
                for i in range(3):
                    points_3d[:, i] = ndimage.gaussian_filter1d(points_3d[:, i], sigma=0.5)
            
            self.progress_queue.put("تصحیحات فضایی اعمال شد")
            return points_3d, colors
            
        except Exception as e:
            self.progress_queue.put(f"خطا در تصحیحات فضایی: {str(e)}")
            return points_3d, colors

class ThreeDViewer:
    def __init__(self, root):
        self.root = root
        self.root.title("سیستم پیشرفته تبدیل 2D به 3D - Persian AI")
        self.root.geometry("1000x700")
        
        self.converter = Advanced2DTo3DConverter()
        self.current_points = None
        self.current_colors = None
        
        self.setup_ui()
        self.check_progress_queue()
    
    def setup_ui(self):
        """راه‌اندازی رابط کاربری"""
        # فریم اصلی
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # فریم کنترل‌ها
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=5)
        
        # دکمه‌ها
        ttk.Button(control_frame, text="📁 بارگذاری تصویر", 
                  command=self.load_image).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="🔄 تبدیل به 3D", 
                  command=self.start_conversion).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="👁️ نمایش 3D", 
                  command=self.show_3d).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="💾 ذخیره مدل", 
                  command=self.save_model).pack(side=tk.LEFT, padx=5)
        
        # نوار پیشرفت
        self.progress = ttk.Progressbar(control_frame, mode='indeterminate')
        self.progress.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # وضعیت
        self.status_var = tk.StringVar(value="آماده برای بارگذاری تصویر")
        status_label = ttk.Label(control_frame, textvariable=self.status_var, 
                                font=('Tahoma', 10))
        status_label.pack(side=tk.RIGHT, padx=5)
        
        # فریم نمایش
        display_frame = ttk.Frame(main_frame)
        display_frame.pack(fill=tk.BOTH, expand=True)
        
        # نمودار
        self.fig = plt.Figure(figsize=(8, 6), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.fig, display_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # کنسول log
        log_frame = ttk.LabelFrame(main_frame, text="لاگ عملیات")
        log_frame.pack(fill=tk.X, pady=5)
        
        self.log_text = tk.Text(log_frame, height=4, width=80, font=('Tahoma', 9))
        scrollbar = ttk.Scrollbar(log_frame, command=self.log_text.yview)
        self.log_text.config(yscrollcommand=scrollbar.set)
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def log_message(self, message):
        """افزودن پیام به لاگ"""
        self.log_text.insert(tk.END, f"{time.strftime('%H:%M:%S')} - {message}\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()
    
    def load_image(self):
        """بارگذاری تصویر"""
        file_path = filedialog.askopenfilename(
            title="انتخاب تصویر",
            filetypes=[("فایل‌های تصویری", "*.jpg *.jpeg *.png *.bmp *.tiff"), ("همه فایل‌ها", "*.*")]
        )
        
        if file_path:
            self.status_var.set("در حال بارگذاری تصویر...")
            self.progress.start()
            self.log_message(f"بارگذاری تصویر: {os.path.basename(file_path)}")
            
            # اجرا در thread جداگانه
            thread = threading.Thread(target=self._load_image_thread, args=(file_path,))
            thread.daemon = True
            thread.start()
    
    def _load_image_thread(self, file_path):
        """Thread برای بارگذاری تصویر"""
        try:
            self.original_image, self.gray_image = self.converter.load_and_preprocess_image(file_path)
            
            if self.original_image is not None:
                self.root.after(0, lambda: self._on_image_loaded())
            else:
                self.root.after(0, lambda: self._on_image_load_failed())
                
        except Exception as e:
            self.root.after(0, lambda: self._on_image_load_error(str(e)))
    
    def _on_image_loaded(self):
        """وقتی تصویر با موفقیت بارگذاری شد"""
        self.status_var.set("تصویر بارگذاری شد - آماده برای تبدیل به 3D")
        self.progress.stop()
        self.show_original_image()
        self.log_message("تصویر با موفقیت بارگذاری و پیش‌پردازش شد")
    
    def _on_image_load_failed(self):
        """وقتی بارگذاری تصویر شکست خورد"""
        self.status_var.set("خطا در بارگذاری تصویر")
        self.progress.stop()
        messagebox.showerror("خطا", "نمی‌توان تصویر را بارگذاری کرد")
    
    def _on_image_load_error(self, error_msg):
        """وقتی خطایی در بارگذاری تصویر رخ داد"""
        self.status_var.set("خطا در بارگذاری")
        self.progress.stop()
        messagebox.showerror("خطا", f"خطا در بارگذاری تصویر: {error_msg}")
    
    def show_original_image(self):
        """نمایش تصویر اصلی"""
        self.fig.clear()
        ax = self.fig.add_subplot(111)
        if hasattr(self, 'gray_image'):
            ax.imshow(self.gray_image, cmap='gray')
        ax.set_title('تصویر اصلی (خاکستری)')
        ax.axis('off')
        self.canvas.draw()
    
    def start_conversion(self):
        """شروع تبدیل به 3D"""
        if not hasattr(self, 'gray_image'):
            messagebox.showerror("خطا", "لطفا ابتدا یک تصویر بارگذاری کنید")
            return
        
        self.status_var.set("در حال تبدیل به 3D... لطفا صبر کنید")
        self.progress.start()
        self.log_message("شروع فرآیند تبدیل 2D به 3D...")
        
        # اجرا در thread جداگانه
        thread = threading.Thread(target=self._conversion_thread)
        thread.daemon = True
        thread.start()
    
    def _conversion_thread(self):
        """Thread برای تبدیل 3D"""
        try:
            # 1. تخمین عمق
            self.converter.progress_queue.put("در حال تخمین نقشه عمق...")
            depth_map = self.converter.estimate_depth_map(self.gray_image)
            
            # 2. تبدیل به نقاط 3D
            self.converter.progress_queue.put("در حال تبدیل به نقاط 3D...")
            points_3d, colors, valid_indices = self.converter.convert_to_3d_points(
                self.gray_image, depth_map
            )
            
            if points_3d is not None and len(points_3d) > 0:
                # 3. اعمال تصحیحات
                self.converter.progress_queue.put("در حال اعمال تصحیحات فضایی...")
                points_3d, colors = self.converter.apply_spatial_corrections(
                    points_3d, colors, valid_indices
                )
                
                self.current_points = points_3d
                self.current_colors = colors
                
                self.root.after(0, lambda: self._on_conversion_success())
            else:
                self.root.after(0, lambda: self._on_conversion_failed())
                
        except Exception as e:
            self.root.after(0, lambda: self._on_conversion_error(str(e)))
    
    def _on_conversion_success(self):
        """وقتی تبدیل با موفقیت انجام شد"""
        self.status_var.set("تبدیل 3D کامل شد - آماده برای نمایش")
        self.progress.stop()
        self.log_message("تبدیل به 3D با موفقیت انجام شد")
        messagebox.showinfo("موفق", "تبدیل به 3D با موفقیت انجام شد!\nاکنون می‌توانید مدل را مشاهده کنید.")
    
    def _on_conversion_failed(self):
        """وقتی تبدیل شکست خورد"""
        self.status_var.set("خطا در تبدیل 3D")
        self.progress.stop()
        messagebox.showerror("خطا", "تبدیل به 3D انجام نشد. لطفا تصویر دیگری امتحان کنید.")
    
    def _on_conversion_error(self, error_msg):
        """وقتی خطایی در تبدیل رخ داد"""
        self.status_var.set("خطا در تبدیل")
        self.progress.stop()
        messagebox.showerror("خطا", f"خطا در تبدیل به 3D: {error_msg}")
    
    def check_progress_queue(self):
        """بررسی صف پیشرفت"""
        try:
            while True:
                message = self.converter.progress_queue.get_nowait()
                self.log_message(message)
        except:
            pass
        
        # برنامه‌ریزی بررسی مجدد
        self.root.after(100, self.check_progress_queue)
    
    def show_3d(self):
        """نمایش مدل 3D"""
        if self.current_points is None or len(self.current_points) == 0:
            messagebox.showerror("خطا", "هیچ داده 3D برای نمایش وجود ندارد")
            return
        
        self.fig.clear()
        ax = self.fig.add_subplot(111, projection='3d')
        
        # نمایش ابر نقاط
        scatter = ax.scatter(
            self.current_points[:, 0],
            self.current_points[:, 1], 
            self.current_points[:, 2],
            c=self.current_colors[:, 0] / 255.0,
            cmap='viridis',
            s=20,
            alpha=0.7,
            depthshade=True
        )
        
        # تنظیمات نمودار
        ax.set_xlabel('محور X')
        ax.set_ylabel('محور Y')
        ax.set_zlabel('محور Z')
        ax.set_title(f'مدل سه بعدی تولید شده - {len(self.current_points)} نقطه')
        
        # اضافه کردن colorbar
        plt.colorbar(scatter, ax=ax, shrink=0.5, aspect=20, label='شدت')
        
        self.canvas.draw()
        self.log_message("مدل 3D نمایش داده شد")
        self.status_var.set("مدل 3D در حال نمایش")
    
    def save_model(self):
        """ذخیره مدل 3D"""
        if self.current_points is None:
            messagebox.showerror("خطا", "هیچ مدل 3D برای ذخیره وجود ندارد")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="ذخیره مدل 3D",
            defaultextension=".npy",
            filetypes=[("فایل‌های NPY", "*.npy"), ("همه فایل‌ها", "*.*")]
        )
        
        if file_path:
            try:
                # ذخیره نقاط و رنگ‌ها
                model_data = {
                    'points': self.current_points,
                    'colors': self.current_colors
                }
                np.save(file_path, model_data)
                
                self.log_message(f"مدل 3D در {file_path} ذخیره شد")
                messagebox.showinfo("موفق", f"مدل با موفقیت ذخیره شد!\nتعداد نقاط: {len(self.current_points)}")
                
            except Exception as e:
                messagebox.showerror("خطا", f"خطا در ذخیره مدل: {str(e)}")

def main():
    """تابع اصلی"""
    try:
        root = tk.Tk()
        app = ThreeDViewer(root)
        
        # نمایش پیام خوشامد
        app.log_message("=== سیستم تبدیل 2D به 3D راه‌اندازی شد ===")
        app.log_message("لطفا یک تصویر بارگذاری کنید و سپس تبدیل به 3D را آغاز کنید")
        
        root.mainloop()
    except Exception as e:
        print(f"خطا در اجرای برنامه: {e}")
        messagebox.showerror("خطای سیستمی", f"برنامه نمی‌تواند اجرا شود: {e}")

if __name__ == "__main__":
    main()
