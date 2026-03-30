from PIL import Image
import numpy as np
import cv2
from paddleocr import PaddleOCR

def preprocess_receipt(image: Image.Image) -> np.ndarray:
    img = np.array(image.convert("RGB"))
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    gray = cv2.GaussianBlur(gray, (3, 3), 0)
    thresh = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 11
    )
    return thresh

def extract_text(image: Image.Image, ocr_model: PaddleOCR) -> str:
    processed = preprocess_receipt(image)
    result = ocr_model.ocr(processed, cls=True)
    lines = []
    for block in result:
        for item in block:
            text = item[1][0]
            lines.append(text)
    return "\n".join(lines)