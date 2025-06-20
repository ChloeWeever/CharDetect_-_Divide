import cv2
import numpy as np
from PIL import Image, ImageEnhance
from typing import Union
from src.tools.kmeans_filter import *


def image_style_transfer_enhance(
        input_image,
        style: str = 'enhance',
        enhance_factor: float = 1.5,
        output_path: str = None
) -> np.ndarray:
    # 读取图像
    if isinstance(input_image, str):
        img = cv2.imread(input_image)
        if img is None:
            raise ValueError(f"无法读取图像: {input_image}")
    else:
        img = input_image.copy()

    # 确保图像是彩色图像
    if len(img.shape) == 2:
        img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)

    # 根据选择的风格进行处理
    if style == 'enhance':
        # 使用PIL进行图像增强
        pil_img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))

        # 对比度增强
        enhancer = ImageEnhance.Contrast(pil_img)
        enhanced_img = enhancer.enhance(enhance_factor)

        # 锐度增强
        enhancer = ImageEnhance.Sharpness(enhanced_img)
        enhanced_img = enhancer.enhance(enhance_factor)

        # 颜色增强
        enhancer = ImageEnhance.Color(enhanced_img)
        enhanced_img = enhancer.enhance(enhance_factor * 0.8)

        result = cv2.cvtColor(np.array(enhanced_img), cv2.COLOR_RGB2BGR)

    elif style == 'sketch':
        # 素描风格
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        inverted = 255 - gray
        blurred = cv2.GaussianBlur(inverted, (21, 21), 0)
        inverted_blurred = 255 - blurred
        result = cv2.divide(gray, inverted_blurred, scale=256.0)
        result = cv2.cvtColor(result, cv2.COLOR_GRAY2BGR)

    elif style == 'watercolor':
        # 水彩风格
        res = cv2.stylization(img, sigma_s=60, sigma_r=0.6)
        result = cv2.detailEnhance(res, sigma_s=10, sigma_r=0.15)

    elif style == 'pencil_sketch':
        # 铅笔素描风格
        gray, color = cv2.pencilSketch(img, sigma_s=60, sigma_r=0.07, shade_factor=0.05)
        result = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)

    elif style == 'bit':
        result = extract_dark_text(img)

    else:
        raise ValueError(f"不支持的风格类型: {style}")

    # 如果需要保存结果
    if output_path is not None:
        cv2.imwrite(output_path, result)

    return result
