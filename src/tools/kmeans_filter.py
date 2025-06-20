import cv2
import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.mixture import GaussianMixture  # 可选：GMM聚类


def extract_dark_text(img, n_clusters=5, use_gmm=False):
    # 1. 读取图片并转换为RGB
    if img is None:
        raise ValueError("无法读取图片，请检查路径")
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    h, w = img.shape[:2]

    # 2. 将像素转换为二维数组 (样本数 x 3通道)
    pixels = img_rgb.reshape(-1, 3).astype(np.float32)

    # 3. 使用K-Means或GMM聚类
    if use_gmm:
        model = GaussianMixture(n_components=n_clusters, random_state=42)
    else:
        model = KMeans(n_clusters=n_clusters, random_state=42)
    model.fit(pixels)
    labels = model.predict(pixels)

    # 4. 找到最接近黑色的簇（RGB均值L2范数最小）
    if use_gmm:
        centers = model.means_
    else:
        centers = model.cluster_centers_
    darkest_cluster = np.argmin(np.linalg.norm(centers, axis=1))

    # 5. 生成掩码（目标簇为白色，其余为黑色）
    mask = (labels == darkest_cluster).reshape(h, w)
    mask = mask.astype(np.uint8) * 255

    # 二值化
    mask = cv2.threshold(mask, 0, 255, cv2.THRESH_BINARY)[1]
    # 膨胀
    mask = cv2.dilate(mask, np.ones((3, 3), np.uint8), iterations=1)
    # 腐蚀
    # mask = cv2.erode(mask, np.ones((3, 3), np.uint8), iterations=1)

    # 6. 可选：形态学处理（去噪）
    # kernel = np.ones((3, 3), np.uint8)
    # mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=1)

    # 可视化
    '''
    plt.figure(figsize=(12, 6))
    plt.subplot(1, 2, 1)
    plt.imshow(img_rgb)
    plt.title("原始图片")

    plt.subplot(1, 2, 2)
    plt.imshow(mask, cmap='gray')
    plt.title("提取的文字部分")
    plt.show()
    '''

    return mask