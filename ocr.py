import cv2
from paddleocr import PaddleOCR
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import filedialog, messagebox
import numpy as np
import os

ROI_CONFIG_PATH = "roi_config.npy"
ocr = PaddleOCR(use_angle_cls=True, lang='ch')

def read_image_with_chinese_path(image_path):
    image_stream = np.fromfile(image_path, dtype=np.uint8)
    img = cv2.imdecode(image_stream, cv2.IMREAD_COLOR)
    return img

def save_roi_config(roi1, roi2):
    np.save(ROI_CONFIG_PATH, np.array([roi1, roi2], dtype=object))
    print("识别区域已保存！")

def load_roi_config():
    if os.path.exists(ROI_CONFIG_PATH):
        return np.load(ROI_CONFIG_PATH, allow_pickle=True)
    return None

def select_roi(image_path):
    img = read_image_with_chinese_path(image_path)
    if img is None:
        print("错误：无法加载图像")
        return None
    roi = cv2.selectROI("选择区域", img, fromCenter=False, showCrosshair=True)
    cv2.destroyAllWindows()
    return roi

def extract_chinese_text(image_path, roi):
    img = read_image_with_chinese_path(image_path)
    if img is None:
        return ""

    x, y, w, h = roi
    roi_img = img[y:y+h, x:x+w]
    processed_image_path = "processed_region.png"
    cv2.imwrite(processed_image_path, roi_img)

    results = ocr.ocr(processed_image_path, cls=True)
    extracted_text = "\n".join([line[1][0] for result in results for line in result])
    
    return extracted_text.strip()

class OCRApp:
    def __init__(self, root):
        self.root = root
        self.root.title("批量OCR识别")

        self.roi_config = load_roi_config()
        self.roi1, self.roi2 = self.roi_config if self.roi_config is not None else (None, None)

        self.image_paths = []
        self.current_image_index = 0

        # 按钮
        self.btn_select_folder = tk.Button(root, text="选择文件夹", command=self.select_folder)
        self.btn_select_folder.pack(pady=5)

        self.btn_set_roi1 = tk.Button(root, text="设定区域1", command=self.set_roi1)
        self.btn_set_roi1.pack(pady=5)

        self.btn_set_roi2 = tk.Button(root, text="设定区域2", command=self.set_roi2)
        self.btn_set_roi2.pack(pady=5)

        self.btn_use_roi1 = tk.Button(root, text="使用区域1识别并显示下一张", command=self.process_next_image_roi1, state=tk.DISABLED)
        self.btn_use_roi1.pack(pady=5)

        self.btn_use_roi2 = tk.Button(root, text="使用区域2识别并显示下一张", command=self.process_next_image_roi2, state=tk.DISABLED)
        self.btn_use_roi2.pack(pady=5)

        self.btn_skip = tk.Button(root, text="跳过当前图片", command=self.skip_image, state=tk.DISABLED)
        self.btn_skip.pack(pady=5)

        self.btn_prev_image = tk.Button(root, text="返回上一张图片", command=self.prev_image, state=tk.DISABLED)
        self.btn_prev_image.pack(pady=5)

        self.img_label = tk.Label(root)
        self.img_label.pack(pady=10)

        self.text_result = tk.Text(root, height=20, width=50)
        self.text_result.pack(pady=10)

        self.btn_save_text = tk.Button(root, text="保存识别文本", command=self.save_text)
        self.btn_save_text.pack(pady=5)

    def select_folder(self):
        folder_path = filedialog.askdirectory(title="选择图片文件夹")
        if folder_path:
            self.image_paths = [os.path.join(folder_path, file) for file in os.listdir(folder_path) if file.lower().endswith(('.png', '.jpg', '.jpeg'))]
            self.current_image_index = 0
            self.update_buttons()
            if self.image_paths:
                self.display_image(self.image_paths[self.current_image_index])

    def display_image(self, image_path):
        img = Image.open(image_path)
        img.thumbnail((400, 400))
        img_tk = ImageTk.PhotoImage(img)
        self.img_label.config(image=img_tk)
        self.img_label.image = img_tk

    def set_roi1(self):
        image_path = filedialog.askopenfilename(title="选择图片来设定区域1")
        if image_path:
            roi = select_roi(image_path)
            if roi:
                self.roi1 = roi
                self.save_roi()
                messagebox.showinfo("成功", "区域1 已设定！")

    def set_roi2(self):
        image_path = filedialog.askopenfilename(title="选择图片来设定区域2")
        if image_path:
            roi = select_roi(image_path)
            if roi:
                self.roi2 = roi
                self.save_roi()
                messagebox.showinfo("成功", "区域2 已设定！")

    def process_next_image_roi1(self):
        """ 使用区域1进行识别并跳到下一张图片 """
        self.process_next_image(self.roi1)

    def process_next_image_roi2(self):
        """ 使用区域2进行识别并跳到下一张图片 """
        self.process_next_image(self.roi2)

    def process_next_image(self, roi):
        if roi is None:
            messagebox.showwarning("错误", "请先设定识别区域！")
            return

        if self.current_image_index < len(self.image_paths):
            image_path = self.image_paths[self.current_image_index]
            text = extract_chinese_text(image_path, roi)
            # self.text_result.insert(tk.END, f"Image: {os.path.basename(image_path)}\n{text}\n\n")
            self.text_result.insert(tk.END, f"\n------{os.path.basename(image_path)}------\n{text}\n\n")
            self.current_image_index += 1
            self.update_buttons()
            if self.current_image_index < len(self.image_paths):
                self.display_image(self.image_paths[self.current_image_index])
            else:
                messagebox.showinfo("完成", "所有图片已处理！")

    def prev_image(self):
        """ 返回上一张图片 """
        if self.current_image_index > 0:
            self.current_image_index -= 1
            self.display_image(self.image_paths[self.current_image_index])
            self.update_buttons()

    def skip_image(self):
        """ 跳过当前图片，不进行识别 """
        if self.current_image_index < len(self.image_paths) - 1:
            self.current_image_index += 1
            self.display_image(self.image_paths[self.current_image_index])
            self.update_buttons()
        else:
            messagebox.showinfo("完成", "已到最后一张图片！")

    def save_text(self):
        with open("recognized_text.txt", "a", encoding="utf-8") as f:
            f.write(self.text_result.get("1.0", tk.END))
            messagebox.showinfo("成功", "识别文本已保存")

    def save_roi(self):
        save_roi_config(self.roi1, self.roi2)

    def update_buttons(self):
        """ 更新按钮状态 """
        has_images = self.current_image_index < len(self.image_paths)
        self.btn_use_roi1.config(state=tk.NORMAL if has_images else tk.DISABLED)
        self.btn_use_roi2.config(state=tk.NORMAL if has_images else tk.DISABLED)
        self.btn_skip.config(state=tk.NORMAL if has_images else tk.DISABLED)
        self.btn_prev_image.config(state=tk.NORMAL if self.current_image_index > 0 else tk.DISABLED)

if __name__ == "__main__":
    root = tk.Tk()
    app = OCRApp(root)
    root.mainloop()
