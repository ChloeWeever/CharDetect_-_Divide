import cv2
import numpy as np


def binarization(image):
    # 若图像高于1000万像素，则缩放到1000万以下
    # 计算缩放比例，限制总像素数不超过1000万
    max_pixels = 100000000
    height, width = image.shape[:2]
    current_pixels = height * width

    if current_pixels > max_pixels:
        scale_factor = (max_pixels / current_pixels) ** 0.5  # 按面积缩放比例开平方
        new_width = int(width * scale_factor)
        new_height = int(height * scale_factor)
        image = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_AREA)
    # 转换为灰度图
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # 均衡化处理，改善光线不均问题
    equalized = cv2.equalizeHist(gray)

    # 高斯模糊去除噪声
    blurred = cv2.GaussianBlur(equalized, (5, 5), 0)

    # 降低图片饱和度
    blurred = cv2.convertScaleAbs(blurred, alpha=1.5, beta=0)

    # 自适应阈值分割，增强文字对比度
    binary = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)

    # 开运算去除细小噪声
    kernel = np.ones((3, 3), np.uint8)
    opening = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel, iterations=1)

    # 保留黑灰色文字，去除其他颜色
    lower_black = np.array([0, 0, 0])
    upper_black = np.array([100, 100, 100])
    mask = cv2.inRange(image, lower_black, upper_black)
    result = cv2.bitwise_and(opening, opening, mask=mask)
    result = fill_holes(result)
    inverted_result = cv2.bitwise_not(result)

    return remove_noise(inverted_result)


def remove_noise(binary_image):
    # 定义结构元素（3x3 矩形核）
    kernel = np.ones((3, 3), np.uint8)

    # 腐蚀操作，消除小的白色噪点
    eroded = cv2.erode(binary_image, kernel, iterations=1)

    # 挤压后扩展：膨胀操作，恢复文字大小
    dilated = cv2.dilate(eroded, kernel, iterations=1)

    return dilated


def mark_handwritten_characters(binary_image):

    """
    检测并标记二值化图片中的手写字

    参数:
        binary_image: 二值化图像(黑白图像，文字为白色，背景为黑色)

    返回:
        标记后的图像(用红色矩形框标记每个检测到的字符)
    """
    # 确保输入是二值图像
    if len(binary_image.shape) > 2:
        gray = cv2.cvtColor(binary_image, cv2.COLOR_BGR2GRAY)
        _, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
    else:
        binary = binary_image

    # 转换为彩色图像以便绘制彩色框
    if len(binary_image.shape) == 2:
        marked_image = cv2.cvtColor(binary_image, cv2.COLOR_GRAY2BGR)
    else:
        marked_image = binary_image.copy()

    # 查找轮廓
    contours, _ = cv2.findContours(255 - binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # 过滤和标记轮廓
    min_area = 100  # 最小区域面积阈值，避免噪声
    max_area = 1000000  # 最大区域面积阈值

    filtered_contours = []

    for contour in contours:
        # 计算轮廓的边界矩形
        x, y, w, h = cv2.boundingRect(contour)
        area = w * h

        # 过滤太小或太大的区域
        if area > min_area and area < max_area and 1.0*w/h < 5 and  1.0*h/w < 5:
            filtered_contours.append(contour)


    for contour in filtered_contours:
        x, y, w, h = cv2.boundingRect(contour)
        cv2.rectangle(marked_image, (x, y), (x+w, y+h), (0, 0, 255), 2)

    return marked_image,filtered_contours

def fill_holes(binary_image):
    """
    填补二值化图像中被黑色包围的白色区域（即“镂空”）

    参数:
        binary_image: 输入二值化图像，0为黑，255为白

    返回:
        filled_image: 填补后的图像
    """
    # 确保图像是二值化的（0和255）
    _, binary = cv2.threshold(binary_image, 127, 255, cv2.THRESH_BINARY)

    # 创建一个掩膜用于 floodFill（必须比原图多2像素宽高）
    h, w = binary.shape[:2]
    mask = np.zeros((h + 2, w + 2), np.uint8)

    # 复制图像用于填充（避免修改原始图像）
    im_floodfill = binary.copy()

    # 从 (0,0) 点进行泛洪填充（填空白洞），填充色为 255（白色）
    cv2.floodFill(im_floodfill, mask, (0, 0), 255)

    # 取反得到所有洞的区域（即被黑色包围的白色区域）
    im_floodfill_inv = cv2.bitwise_not(im_floodfill)

    # 使用或操作将洞区域合并到原图（填补为黑色）
    filled_image = binary | im_floodfill_inv

    return filled_image


def merge_contours_based_on_distance(contours, threshold_ratio=0.5):
    """
    根据中点距离是否小于最大宽度的1.5倍来合并轮廓。

    参数:
        contours: 输入的轮廓列表
        max_width: 所有轮廓中的最大宽度
        threshold_ratio: 中点距离阈值比例，默认为最大宽度的1.5倍

    返回:
        merged_bounding_boxes: 合并后的边界框列表
    """
    # 存储每个轮廓的边界框和中点
    width = []
    height = []
    bounding_boxes = []
    midpoints = []
    average_width = 0
    average_height = 0

    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        width.append(w)
        height.append(h)
        bounding_boxes.append((x, y, w, h))
        mid_x = x + w // 2
        mid_y = y + h // 2
        midpoints.append((mid_x, mid_y))

    max_width = max(width)
    average_width = sum(width) / len(width)
    average_height = sum(height) / len(height)

    # 判断哪些轮廓的中点距离小于 max_width * threshold_ratio
    threshold_distance = 0.5*(average_width + average_height) * 1.0
    num_contours = len(contours)
    merged = [False] * num_contours
    merged_bounding_boxes = []

    for i in range(num_contours):
        if merged[i]:
            continue
        current_box = bounding_boxes[i]
        current_midpoint = midpoints[i]
        merged_indices = [i]

        for j in range(i + 1, num_contours):
            if merged[j]:
                continue
            distance = ((current_midpoint[0] - midpoints[j][0]) ** 2 +
                        (current_midpoint[1] - midpoints[j][1]) ** 2) ** 0.5
            if distance < threshold_distance:
                merged_indices.append(j)
                merged[j] = True

        # 合并选中的轮廓边界框（取最小外接矩形）
        min_x = min(bounding_boxes[k][0] for k in merged_indices)
        min_y = min(bounding_boxes[k][1] for k in merged_indices)
        max_x = max(bounding_boxes[k][0] + bounding_boxes[k][2] for k in merged_indices)
        max_y = max(bounding_boxes[k][1] + bounding_boxes[k][3] for k in merged_indices)
        merged_bounding_boxes.append((min_x, min_y, max_x - min_x, max_y - min_y))

    return merged_bounding_boxes,average_width,average_height,average_width*average_height


