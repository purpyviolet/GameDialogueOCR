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
