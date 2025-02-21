from paddleocr import PaddleOCR,draw_ocr
ocr = PaddleOCR(lang='ch') # need to run only once to download and load model into memory
img_path = 'Screenshot_2025-02-17_01-52-51.png'
result = ocr.ocr(img_path, cls=False)
for idx in range(len(result)):
    res = result[idx]
    for line in res:
        print(line)

# draw result
from PIL import Image
result = result[0]
image = Image.open(img_path).convert('RGB')
boxes = [line[0] for line in result]
txts = [line[1][0] for line in result]
scores = [line[1][1] for line in result]
im_show = draw_ocr(image, boxes, txts, scores, font_path='SimSun.ttf')
im_show = Image.fromarray(im_show)
im_show.save('result.jpg')