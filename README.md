# GameDialogueOCR
### **Project: OCR Dialogue Extractor**  

**Description:**  
This project is a batch image text recognition tool designed for extracting dialogues, subtitles, or scripts from images. It features a customizable region selection for OCR processing, making it particularly useful for text-based adventure games or visual novel transcription. The application provides a GUI for easy interaction, allowing users to process images, recognize text within selected regions, and navigate through images seamlessly.  

**Features:**  
- Customizable region selection for OCR  
- Batch image processing  
- GUI-based interaction  
- Options to recognize text from different regions or skip images  
- Navigation buttons for next, previous, and skip actions  

**Dependencies:**  
- OpenCV  
- Tesseract OCR  
- Tkinter GUI  
- Pillow  
- NumPy  

### Run the code
This tool simplifies the process of extracting and organizing text from image-based content. 🚀
To run the code, you need to install:
1. If you want to run on cpu: 
```bash
python -m pip install paddlepaddle==3.0.0rc1 -i https://www.paddlepaddle.org.cn/packages/stable/cpu/
pip install opencv-python pytesseract Pillow numpy
pip install paddleocr
```
2. If you want to run on gpu(here we assume you cuda version is 11.8, please modify to meet your requirements):
```bash
python -m pip install paddlepaddle-gpu==3.0.0rc1 -i https://www.paddlepaddle.org.cn/packages/stable/cu118/
pip install opencv-python pytesseract Pillow numpy
pip install paddleocr
```

Run ocr.py to start.
