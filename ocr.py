import cv2
from paddleocr import PaddleOCR
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import filedialog, messagebox
import numpy as np
import os
from tkinter import filedialog
import re


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

def select_roi(image_path, max_width=800, max_height=800):
    img = read_image_with_chinese_path(image_path)
    if img is None:
        print("错误：无法加载图像")
        return None

    # 获取原始尺寸
    h, w = img.shape[:2]

    # 计算缩放比例
    scale = min(max_width / w, max_height / h, 1.0)  # 不能放大，只缩小
    new_w, new_h = int(w * scale), int(h * scale)

    # 缩放图像
    resized_img = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_AREA)

    # 选择ROI
    roi = cv2.selectROI("Select ROI", resized_img, fromCenter=False, showCrosshair=True)
    cv2.destroyAllWindows()

    # 计算原始图像中的ROI坐标
    if roi != (0, 0, 0, 0):  # 避免空ROI
        x, y, w, h = roi
        x, y, w, h = int(x / scale), int(y / scale), int(w / scale), int(h / scale)
        return (x, y, w, h)
    return None


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


def correct_text_errors(text):
    # 1. 统一 `．`（全角点）为 `.`（半角点）
    text = text.replace('．', '.')

    # 2. 删除独立存在的 `.`（仅当它不在句尾，且不是省略号的一部分）
    text = re.sub(r'(?<!\S)\.(?!\S)', '', text)  # 仅删除独立的 `.`

    # 3. 如果出现 `·`，则所有连续的 `.`（点）都替换成 `...`
    if '·' in text:
        text = re.sub(r'[.·…]+', '...', text)  # 替换所有连续的 `.` 或 `·` 为 `...`

    # 4. 删除所有 `…`
    text = text.replace('…', '')

    # 5. 修正对话括号
    left_bracket_count = text.count("「")
    right_bracket_count = text.count("」")

    # 如果「比」多，就补全右括号
    while left_bracket_count > right_bracket_count:
        text += "」"
        right_bracket_count += 1

    return text



class OCRApp:
    def __init__(self, root):
        self.root = root
        self.root.title("批量OCR识别")
        self.root.geometry("900x600")  # 设定窗口大小

        self.roi_config = load_roi_config()
        self.roi1, self.roi2 = self.roi_config if self.roi_config is not None else (None, None)
        self.image_paths = []
        self.current_image_index = 0
        self.current_txt_file = None
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)


        # 左侧按钮区域
        self.frame_left = tk.Frame(root)
        self.frame_left.grid(row=0, column=0, padx=10, pady=10, sticky="n")
        
        self.btn_select_folder = tk.Button(self.frame_left, text="选择文件夹", command=self.select_folder)
        self.btn_select_folder.pack(pady=5)

        self.btn_select_file = tk.Button(self.frame_left, text="选择单张图片", command=self.select_file)
        self.btn_select_file.pack(pady=5)
        
        self.btn_set_roi1 = tk.Button(self.frame_left, text="设定区域1", command=self.set_roi1)
        self.btn_set_roi1.pack(pady=5)

        self.btn_set_roi2 = tk.Button(self.frame_left, text="设定区域2", command=self.set_roi2)
        self.btn_set_roi2.pack(pady=5)
        
        self.btn_use_roi1 = tk.Button(self.frame_left, text="使用区域1识别", command=self.process_next_image_roi1, state=tk.DISABLED)
        self.btn_use_roi1.pack(pady=5)

        self.btn_use_roi2 = tk.Button(self.frame_left, text="使用区域2识别", command=self.process_next_image_roi2, state=tk.DISABLED)
        self.btn_use_roi2.pack(pady=5)
        
        self.btn_skip = tk.Button(self.frame_left, text="跳过当前图片", command=self.skip_image, state=tk.DISABLED)
        self.btn_skip.pack(pady=5)
        
        self.btn_prev_image = tk.Button(self.frame_left, text="返回上一张图片", command=self.prev_image, state=tk.DISABLED)
        self.btn_prev_image.pack(pady=5)
        
        self.btn_load_text = tk.Button(self.frame_left, text="加载已有或空文本", command=self.load_text)
        self.btn_load_text.pack(pady=5)

        self.btn_save_text = tk.Button(self.frame_left, text="保存识别文本", command=self.save_text)
        self.btn_save_text.pack(pady=5)

        # 中间图片显示
        self.frame_middle = tk.Frame(root)
        self.frame_middle.grid(row=0, column=1, padx=10, pady=10)
        
        self.img_label = tk.Label(self.frame_middle, width=400, height=400)
        self.img_label.pack()
        
        # 右侧文本区域
        self.frame_right = tk.Frame(root)
        self.frame_right.grid(row=0, column=2, padx=10, pady=10, sticky="n")

        self.text_result = tk.Text(self.frame_right, height=40, width=40)  # 增加高度
        self.text_result.pack(expand=True, fill="both")  # 让文本框尽可能填充可用空间


    def select_folder(self):
        folder_path = filedialog.askdirectory(title="选择图片文件夹")
        if folder_path:
            self.image_paths = [os.path.join(folder_path, file) for file in os.listdir(folder_path) if file.lower().endswith(('.png', '.jpg', '.jpeg'))]
            self.current_image_index = 0
            self.update_buttons()
            if self.image_paths:
                self.display_image(self.image_paths[self.current_image_index])

    def select_file(self):
        file_path = filedialog.askopenfilename(title="选择单张图片", filetypes=[("图片文件", "*.png;*.jpg;*.jpeg")])
        if file_path:
            self.image_paths = [file_path]
            self.current_image_index = 0
            self.update_buttons()
            self.display_image(file_path)

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
            text = correct_text_errors(text)  # 修正文本中的错误
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

    def load_text(self):
        """ 选择一个已存在的 txt 文件并加载内容 """
        file_path = filedialog.askopenfilename(title="选择要加载的TXT文件", filetypes=[("文本文件", "*.txt")])
        if file_path:
            self.current_txt_file = file_path
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            self.text_result.delete("1.0", tk.END)  # 清空文本框
            self.text_result.insert(tk.END, content)
            messagebox.showinfo("成功", f"已加载文件：{os.path.basename(file_path)}")

    def save_text(self):
        """ 将识别文本覆盖保存到加载的 TXT 文件 """
        if not self.current_txt_file:
            messagebox.showwarning("错误", "请先加载一个 TXT 文件！")
            return
        
        with open(self.current_txt_file, "w", encoding="utf-8") as f:  # 改为 "w" 以覆盖文件
            f.write(self.text_result.get("1.0", tk.END))
        
        messagebox.showinfo("成功", f"文本已覆盖保存至 {os.path.basename(self.current_txt_file)}")

    # 保存ROI
    def save_roi(self):
        # 调用save_roi_config函数，传入self.roi1和self.roi2作为参数
        save_roi_config(self.roi1, self.roi2)

    def update_buttons(self):
        """ 更新按钮状态 """
        has_images = self.current_image_index < len(self.image_paths)
        self.btn_use_roi1.config(state=tk.NORMAL if has_images else tk.DISABLED)
        self.btn_use_roi2.config(state=tk.NORMAL if has_images else tk.DISABLED)
        self.btn_skip.config(state=tk.NORMAL if has_images else tk.DISABLED)
        self.btn_prev_image.config(state=tk.NORMAL if self.current_image_index > 0 else tk.DISABLED)

    def on_closing(self):
        """ 退出程序时自动保存文本 """
        if self.current_txt_file:
            with open(self.current_txt_file, "w", encoding="utf-8") as f:
                f.write(self.text_result.get("1.0", tk.END))
            print(f"文本已自动保存至 {self.current_txt_file}")
        
        root.destroy()  # 关闭窗口


if __name__ == "__main__":
    root = tk.Tk()
    app = OCRApp(root)
    root.mainloop()
