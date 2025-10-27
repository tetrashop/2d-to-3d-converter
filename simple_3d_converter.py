import numpy as np
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from mpl_toolkits.mplot3d import Axes3D
from PIL import Image
import os
import time

class Simple2DTo3DConverter:
    def __init__(self):
        self.progress_callback = None
    
    def set_progress_callback(self, callback):
        self.progress_callback = callback
    
    def load_image(self, file_path):
        """بارگذاری و پیش‌پردازش تصویر"""
        try:
            if self.progress_callback:
                self.progress_callback("در حال بارگذاری تصویر...")
            
            # بارگذاری تصویر با PIL
            img = Image.open(file_path)
            
            # تبدیل به خاکستری
            if img.mode != 'L':
                img = img.convert('L')
            
            # تغییر اندازه برای کارایی بهتر
            max_size = 300
            if max(img.size) > max_size:
                ratio = max_size / max(img.size)
                new_size = (int(img.size[0] * ratio), int(img.size[1] * ratio))
                img = img.resize(new_size, Image.Resampling.LANCZOS)
            
            # تبدیل به numpy array
            img_array = np.array(img, dtype=np.float32) / 255.0
            
            if self.progress_callback:
                self.progress_callback("تصویر بارگذاری شد")
            
            return img_array, np.array(img)
            
        except Exception as e:
            if self.progress_callback:
                self.progress_callback(f"خطا: {str(e)}")
            return None, None
    
    def convert_to_3d(self, image):
        """تبدیل ساده تصویر 2D به نقاط 3D"""
        try:
            if self.progress_callback:
                self.progress_callback("شروع تبدیل به 3D...")
            
            h, w = image.shape
            points_3d = []
            colors = []
            
            # نمونه‌برداری
            step = max(1, min(h, w) // 80)
            total_pixels = (h // step) * (w // step)
            processed = 0
            
            center_x, center_y = w // 2, h // 2
            
            for y in range(0, h, step):
                for x in range(0, w, step):
                    intensity = image[y, x]
                    
                    # فقط پیکسل‌های با شدت کافی
                    if intensity > 0.1:
                        # مختصات نرمال‌شده
                        norm_x = (x - center_x) / center_x
                        norm_y = (y - center_y) / center_y
                        
                        # عمق بر اساس شدت
                        depth = intensity
                        
                        # تبدیل به مختصات 3D
                        x_3d = norm_x * 2
                        y_3d = norm_y * 2
                        z_3d = depth * 2
                        
                        points_3d.append([x_3d, y_3d, z_3d])
                        gray_val = int(intensity * 255)
                        colors.append([gray_val, gray_val, gray_val])
                    
                    processed += 1
                    if processed % 500 == 0 and self.progress_callback:
                        progress = (processed / total_pixels) * 100
                        self.progress_callback(f"پردازش: {progress:.1f}%")
            
            points_array = np.array(points_3d)
            colors_array = np.array(colors)
            
            if self.progress_callback:
                self.progress_callback(f"تبدیل کامل! {len(points_array)} نقطه تولید شد")
            
            return points_array, colors_array
            
        except Exception as e:
            if self.progress_callback:
                self.progress_callback(f"خطا در تبدیل: {str(e)}")
            return None, None
    
    def apply_smoothing(self, points, colors, strength=0.5):
        """اعمال هموارسازی ساده"""
        try:
            if len(points) < 10:
                return points, colors
            
            if self.progress_callback:
                self.progress_callback("اعمال هموارسازی...")
            
            # هموارسازی ساده
            smoothed_points = points.copy()
            for i in range(len(points)):
                # میانگین با همسایگان نزدیک
                distances = np.linalg.norm(points - points[i], axis=1)
                neighbors = points[distances < strength]
                if len(neighbors) > 1:
                    smoothed_points[i] = np.mean(neighbors, axis=0)
            
            return smoothed_points, colors
            
        except Exception as e:
            if self.progress_callback:
                self.progress_callback(f"خطا در هموارسازی: {str(e)}")
            return points, colors

class Simple3DViewer:
    def __init__(self, root):
        self.root = root
        self.root.title("تبدیلگر 2D به 3D - نسخه ساده")
        self.root.geometry("900x700")
        
        self.converter = Simple2DTo3DConverter()
        self.current_points = None
        self.current_colors = None
        self.original_image = None
        
        self.setup_ui()
        
        # تنظیم callback برای پیشرفت
        self.converter.set_progress_callback(self.update_progress)
    
    def setup_ui(self):
        """ایجاد رابط کاربری"""
        # فریم اصلی
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # فریم کنترل‌ها
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=5)
        
        # دکمه‌ها
        btn_style = ttk.Style()
        btn_style.configure('Large.TButton', font=('Tahoma', 10))
        
        ttk.Button(control_frame, text="📁 بارگذاری تصویر", 
                  command=self.load_image, style='Large.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="🔄 تبدیل به 3D", 
                  command=self.convert_image, style='Large.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="👁️ نمایش 3D", 
                  command=self.show_3d, style='Large.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="💾 ذخیره", 
                  command=self.save_model, style='Large.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="🧹 پاک کردن", 
                  command=self.clear_all, style='Large.TButton').pack(side=tk.LEFT, padx=5)
        
        # نوار پیشرفت
        self.progress_var = tk.StringVar(value="آماده")
        progress_label = ttk.Label(control_frame, textvariable=self.progress_var, 
                                  font=('Tahoma', 9))
        progress_label.pack(side=tk.RIGHT, padx=5)
        
        # فریم نمایش
        display_frame = ttk.Frame(main_frame)
        display_frame.pack(fill=tk.BOTH, expand=True)
        
        # ایجاد نمودار
        self.fig = plt.Figure(figsize=(8, 6), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.fig, display_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # نمایش پیام خوشامد
        self.show_welcome_message()
    
    def show_welcome_message(self):
        """نمایش پیام خوشامد"""
        self.fig.clear()
        ax = self.fig.add_subplot(111)
        ax.text(0.5, 0.5, 'تبدیلگر تصاویر 2D به مدل‌های 3D\n\n'
                         '📁 برای شروع یک تصویر بارگذاری کنید\n'
                         '🔄 سپس آن را به 3D تبدیل نمایید\n'
                         '👁️ و نتیجه را مشاهده کنید\n\n'
                         'ساخته شده با پایتون',
               horizontalalignment='center', verticalalignment='center',
               transform=ax.transAxes, fontsize=12, 
               bbox=dict(boxstyle="round,pad=0.3", facecolor="lightblue"))
        ax.set_title('خوش آمدید!', fontsize=14, fontweight='bold')
        ax.axis('off')
        self.canvas.draw()
    
    def update_progress(self, message):
        """به‌روزرسانی وضعیت پیشرفت"""
        self.progress_var.set(message)
        self.root.update_idletasks()
    
    def load_image(self):
        """بارگذاری تصویر"""
        file_types = [
            ("تصاویر", "*.jpg *.jpeg *.png *.bmp *.tiff"),
            ("همه فایل‌ها", "*.*")
        ]
        
        file_path = filedialog.askopenfilename(title="انتخاب تصویر", filetypes=file_types)
        
        if file_path:
            self.original_image, self.gray_image = self.converter.load_image(file_path)
            
            if self.original_image is not None:
                self.show_loaded_image()
                messagebox.showinfo("موفق", "تصویر با موفقیت بارگذاری شد!")
            else:
                messagebox.showerror("خطا", "خطا در بارگذاری تصویر")
    
    def show_loaded_image(self):
        """نمایش تصویر بارگذاری شده"""
        self.fig.clear()
        ax = self.fig.add_subplot(111)
        ax.imshow(self.original_image, cmap='gray')
        ax.set_title('تصویر بارگذاری شده', fontweight='bold')
        ax.axis('off')
        self.canvas.draw()
    
    def convert_image(self):
        """تبدیل تصویر به 3D"""
        if not hasattr(self, 'gray_image'):
            messagebox.showerror("خطا", "لطفا ابتدا یک تصویر بارگذاری کنید")
            return
        
        # اجرا در thread جداگانه برای جلوگیری از قفل شدن UI
        import threading
        thread = threading.Thread(target=self._conversion_thread)
        thread.daemon = True
        thread.start()
    
    def _conversion_thread(self):
        """تبدیل در thread جداگانه"""
        try:
            # تبدیل به 3D
            points, colors = self.converter.convert_to_3d(self.gray_image)
            
            if points is not None and len(points) > 0:
                # اعمال هموارسازی
                points, colors = self.converter.apply_smoothing(points, colors)
                
                self.current_points = points
cat > simple_3d_converter.py << 'EOF'
import numpy as np
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from mpl_toolkits.mplot3d import Axes3D
from PIL import Image
import os
import time

class Simple2DTo3DConverter:
    def __init__(self):
        self.progress_callback = None
    
    def set_progress_callback(self, callback):
        self.progress_callback = callback
    
    def load_image(self, file_path):
        """بارگذاری و پیش‌پردازش تصویر"""
        try:
            if self.progress_callback:
                self.progress_callback("در حال بارگذاری تصویر...")
            
            # بارگذاری تصویر با PIL
            img = Image.open(file_path)
            
            # تبدیل به خاکستری
            if img.mode != 'L':
                img = img.convert('L')
            
            # تغییر اندازه برای کارایی بهتر
            max_size = 300
            if max(img.size) > max_size:
                ratio = max_size / max(img.size)
                new_size = (int(img.size[0] * ratio), int(img.size[1] * ratio))
                img = img.resize(new_size, Image.Resampling.LANCZOS)
            
            # تبدیل به numpy array
            img_array = np.array(img, dtype=np.float32) / 255.0
            
            if self.progress_callback:
                self.progress_callback("تصویر بارگذاری شد")
            
            return img_array, np.array(img)
            
        except Exception as e:
            if self.progress_callback:
                self.progress_callback(f"خطا: {str(e)}")
            return None, None
    
    def convert_to_3d(self, image):
        """تبدیل ساده تصویر 2D به نقاط 3D"""
        try:
            if self.progress_callback:
                self.progress_callback("شروع تبدیل به 3D...")
            
            h, w = image.shape
            points_3d = []
            colors = []
            
            # نمونه‌برداری
            step = max(1, min(h, w) // 80)
            total_pixels = (h // step) * (w // step)
            processed = 0
            
            center_x, center_y = w // 2, h // 2
            
            for y in range(0, h, step):
                for x in range(0, w, step):
                    intensity = image[y, x]
                    
                    # فقط پیکسل‌های با شدت کافی
                    if intensity > 0.1:
                        # مختصات نرمال‌شده
                        norm_x = (x - center_x) / center_x
                        norm_y = (y - center_y) / center_y
                        
                        # عمق بر اساس شدت
                        depth = intensity
                        
                        # تبدیل به مختصات 3D
                        x_3d = norm_x * 2
                        y_3d = norm_y * 2
                        z_3d = depth * 2
                        
                        points_3d.append([x_3d, y_3d, z_3d])
                        gray_val = int(intensity * 255)
                        colors.append([gray_val, gray_val, gray_val])
                    
                    processed += 1
                    if processed % 500 == 0 and self.progress_callback:
                        progress = (processed / total_pixels) * 100
                        self.progress_callback(f"پردازش: {progress:.1f}%")
            
            points_array = np.array(points_3d)
            colors_array = np.array(colors)
            
            if self.progress_callback:
                self.progress_callback(f"تبدیل کامل! {len(points_array)} نقطه تولید شد")
            
            return points_array, colors_array
            
        except Exception as e:
            if self.progress_callback:
                self.progress_callback(f"خطا در تبدیل: {str(e)}")
            return None, None
    
    def apply_smoothing(self, points, colors, strength=0.5):
        """اعمال هموارسازی ساده"""
        try:
            if len(points) < 10:
                return points, colors
            
            if self.progress_callback:
                self.progress_callback("اعمال هموارسازی...")
            
            # هموارسازی ساده
            smoothed_points = points.copy()
            for i in range(len(points)):
                # میانگین با همسایگان نزدیک
                distances = np.linalg.norm(points - points[i], axis=1)
                neighbors = points[distances < strength]
                if len(neighbors) > 1:
                    smoothed_points[i] = np.mean(neighbors, axis=0)
            
            return smoothed_points, colors
            
        except Exception as e:
            if self.progress_callback:
                self.progress_callback(f"خطا در هموارسازی: {str(e)}")
            return points, colors

class Simple3DViewer:
    def __init__(self, root):
        self.root = root
        self.root.title("تبدیلگر 2D به 3D - نسخه ساده")
        self.root.geometry("900x700")
        
        self.converter = Simple2DTo3DConverter()
        self.current_points = None
        self.current_colors = None
        self.original_image = None
        
        self.setup_ui()
        
        # تنظیم callback برای پیشرفت
        self.converter.set_progress_callback(self.update_progress)
    
    def setup_ui(self):
        """ایجاد رابط کاربری"""
        # فریم اصلی
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # فریم کنترل‌ها
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=5)
        
        # دکمه‌ها
        btn_style = ttk.Style()
        btn_style.configure('Large.TButton', font=('Tahoma', 10))
        
        ttk.Button(control_frame, text="📁 بارگذاری تصویر", 
                  command=self.load_image, style='Large.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="🔄 تبدیل به 3D", 
                  command=self.convert_image, style='Large.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="👁️ نمایش 3D", 
                  command=self.show_3d, style='Large.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="💾 ذخیره", 
                  command=self.save_model, style='Large.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="🧹 پاک کردن", 
                  command=self.clear_all, style='Large.TButton').pack(side=tk.LEFT, padx=5)
        
        # نوار پیشرفت
        self.progress_var = tk.StringVar(value="آماده")
        progress_label = ttk.Label(control_frame, textvariable=self.progress_var, 
                                  font=('Tahoma', 9))
        progress_label.pack(side=tk.RIGHT, padx=5)
        
        # فریم نمایش
        display_frame = ttk.Frame(main_frame)
        display_frame.pack(fill=tk.BOTH, expand=True)
        
        # ایجاد نمودار
        self.fig = plt.Figure(figsize=(8, 6), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.fig, display_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # نمایش پیام خوشامد
        self.show_welcome_message()
    
    def show_welcome_message(self):
        """نمایش پیام خوشامد"""
        self.fig.clear()
        ax = self.fig.add_subplot(111)
        ax.text(0.5, 0.5, 'تبدیلگر تصاویر 2D به مدل‌های 3D\n\n'
                         '📁 برای شروع یک تصویر بارگذاری کنید\n'
                         '🔄 سپس آن را به 3D تبدیل نمایید\n'
                         '👁️ و نتیجه را مشاهده کنید\n\n'
                         'ساخته شده با پایتون',
               horizontalalignment='center', verticalalignment='center',
               transform=ax.transAxes, fontsize=12, 
               bbox=dict(boxstyle="round,pad=0.3", facecolor="lightblue"))
        ax.set_title('خوش آمدید!', fontsize=14, fontweight='bold')
        ax.axis('off')
        self.canvas.draw()
    
    def update_progress(self, message):
        """به‌روزرسانی وضعیت پیشرفت"""
        self.progress_var.set(message)
        self.root.update_idletasks()
    
    def load_image(self):
        """بارگذاری تصویر"""
        file_types = [
            ("تصاویر", "*.jpg *.jpeg *.png *.bmp *.tiff"),
            ("همه فایل‌ها", "*.*")
        ]
        
        file_path = filedialog.askopenfilename(title="انتخاب تصویر", filetypes=file_types)
        
        if file_path:
            self.original_image, self.gray_image = self.converter.load_image(file_path)
            
            if self.original_image is not None:
                self.show_loaded_image()
                messagebox.showinfo("موفق", "تصویر با موفقیت بارگذاری شد!")
            else:
                messagebox.showerror("خطا", "خطا در بارگذاری تصویر")
    
    def show_loaded_image(self):
        """نمایش تصویر بارگذاری شده"""
        self.fig.clear()
        ax = self.fig.add_subplot(111)
        ax.imshow(self.original_image, cmap='gray')
        ax.set_title('تصویر بارگذاری شده', fontweight='bold')
        ax.axis('off')
        self.canvas.draw()
    
    def convert_image(self):
        """تبدیل تصویر به 3D"""
        if not hasattr(self, 'gray_image'):
            messagebox.showerror("خطا", "لطفا ابتدا یک تصویر بارگذاری کنید")
            return
        
        # اجرا در thread جداگانه برای جلوگیری از قفل شدن UI
        import threading
        thread = threading.Thread(target=self._conversion_thread)
        thread.daemon = True
        thread.start()
    
    def _conversion_thread(self):
        """تبدیل در thread جداگانه"""
        try:
            # تبدیل به 3D
            points, colors = self.converter.convert_to_3d(self.gray_image)
            
            if points is not None and len(points) > 0:
                # اعمال هموارسازی
                points, colors = self.converter.apply_smoothing(points, colors)
                
                self.current_points = points
                self.current_colors = colors
                
                # نمایش نتیجه
                self.root.after(0, lambda: self._on_conversion_success(len(points)))
            else:
                self.root.after(0, self._on_conversion_failed)
                
        except Exception as e:
            self.root.after(0, lambda: self._on_conversion_error(str(e)))
    
    def _on_conversion_success(self, point_count):
        """وقتی تبدیل موفق بود"""
        messagebox.showinfo("موفق", f"تبدیل کامل شد!\n{point_count} نقطه تولید شد")
        self.show_3d()
    
    def _on_conversion_failed(self):
        """وقتی تبدیل شکست خورد"""
        messagebox.showerror("خطا", "تبدیل انجام نشد. لطفا تصویر دیگری امتحان کنید.")
    
    def _on_conversion_error(self, error_msg):
        """وقتی خطا رخ داد"""
        messagebox.showerror("خطا", f"خطا در تبدیل: {error_msg}")
    
    def show_3d(self):
        """نمایش مدل 3D"""
        if self.current_points is None or len(self.current_points) == 0:
            messagebox.showerror("خطا", "هیچ داده 3D برای نمایش وجود ندارد")
            return
        
        self.fig.clear()
        ax = self.fig.add_subplot(111, projection='3d')
        
        # نمایش نقاط 3D
        scatter = ax.scatter3D(
            self.current_points[:, 0],
            self.current_points[:, 1], 
            self.current_points[:, 2],
            c=self.current_colors[:, 0] / 255.0,
            cmap='viridis',
            s=10,
            alpha=0.7,
            depthshade=True
        )
        
        # تنظیمات نمودار
        ax.set_xlabel('محور X')
        ax.set_ylabel('محور Y')
        ax.set_zlabel('محور Z')
        ax.set_title(f'مدل سه بعدی - {len(self.current_points)} نقطه', fontweight='bold')
        
        # اضافه کردن grid
        ax.grid(True, alpha=0.3)
        
        # تنظیم نمای بهتر
        ax.view_init(elev=20, azim=45)
        
        self.canvas.draw()
        self.progress_var.set("مدل 3D نمایش داده شد")
    
    def save_model(self):
        """ذخیره مدل 3D"""
        if self.current_points is None:
            messagebox.showerror("خطا", "هیچ مدلی برای ذخیره وجود ندارد")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="ذخیره مدل 3D",
            defaultextension=".npy",
            filetypes=[("فایل NPY", "*.npy"), ("همه فایل‌ها", "*.*")]
        )
        
        if file_path:
            try:
                data = {
                    'points': self.current_points,
                    'colors': self.current_colors,
                    'timestamp': time.time()
                }
                np.save(file_path, data)
                messagebox.showinfo("موفق", f"مدل در {file_path} ذخیره شد")
            except Exception as e:
                messagebox.showerror("خطا", f"خطا در ذخیره: {str(e)}")
    
    def clear_all(self):
        """پاک کردن همه داده‌ها"""
        self.current_points = None
        self.current_colors = None
        if hasattr(self, 'gray_image'):
            del self.gray_image
        if hasattr(self, 'original_image'):
            del self.original_image
        
        self.show_welcome_message()
        self.progress_var.set("آماده")
        messagebox.showinfo("پاکسازی", "همه داده‌ها پاک شدند")

def main():
    """تابع اصلی"""
    try:
        root = tk.Tk()
        app = Simple3DViewer(root)
        root.mainloop()
    except Exception as e:
        print(f"خطا: {e}")
        messagebox.showerror("خطا", f"برنامه نمی‌تواند اجرا شود: {e}")

if __name__ == "__main__":
    main()
