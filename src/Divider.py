import torch
from torchvision import transforms
from PIL import Image
from src.model.unet_model import UNet
import numpy as np
import os
from src.tools.kmeans_filter import *


class Divider:
    def __init__(self, model_path, device='cuda'):
        self.device = torch.device(device if torch.cuda.is_available() else 'cpu')
        self.model = UNet(n_channels=3, n_classes=6).to(self.device)
        self.model.load_state_dict(torch.load(model_path, map_location=self.device))
        self.model.eval()

        self.transform = transforms.Compose([
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])

    def predict(self, image_path, threshold=0.5):
        # 加载并预处理图像
        image = cv2.imread(image_path)
        image = extract_dark_text(image)
        image = cv2.bitwise_not(image)
        cv2.imwrite(image_path, image)
        image = Image.open(image_path).convert('RGB')

        image_tensor = self.transform(image).unsqueeze(0).to(self.device)

        # 预测
        with torch.no_grad():
            output = self.model(image_tensor)
            probabilities = torch.sigmoid(output)
            binary_output = (probabilities > threshold).float()

        result = binary_output.squeeze(0).permute(1, 2, 0).cpu().numpy()
        return result

    def divide(self, image, threshold=0.5):
        # 加载并预处理图像
        image = extract_dark_text(image)
        image = cv2.bitwise_not(image)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image = image.astype(np.float32) / 255.0

        # 应用标准化 (mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        mean = np.array([0.485, 0.456, 0.406], dtype=np.float32)
        std = np.array([0.229, 0.224, 0.225], dtype=np.float32)
        image = (image - mean) / std

        # 转换为 PyTorch 张量格式 (H, W, C) -> (C, H, W)，并增加 batch 维度
        image_tensor = torch.from_numpy(image).permute(2, 0, 1).unsqueeze(0).to(self.device)

        # 预测
        with torch.no_grad():
            output = self.model(image_tensor)
            probabilities = torch.sigmoid(output)
            binary_output = (probabilities > threshold).float()

        result = binary_output.squeeze(0).permute(1, 2, 0).cpu().numpy()

        img = image

        # 检查白色像素
        white_pixels = np.all(img >= 240, axis=-1)
        mask_o = np.where(white_pixels, 0, 1).astype(np.uint8)
        processed_images = []

        for i in range(6):
            mask = result[:, :, i]  # 取第i个类别 (500, 500)
            mask = np.logical_and(mask, mask_o)

            # 将 0/1 转换为 0~255 的像素值（0 -> 黑色，1 -> 白色）
            mask_image = (mask * 255).astype(np.uint8)

            # 使用 OpenCV 保存图像
            # cv2.imwrite(f'prediction_class_{i}.png', mask_image)
            processed_images.append(mask_image)

        return processed_images


if __name__ == '__main__':
    print(f"Working directory: {os.getcwd()}")
    predictor = Divider('./model/unet_model_3.pth')
    result = predictor.predict('4.png')
    print(f"Prediction shape: {result.shape}")
    # 假设 result 是模型返回的 (500, 500, 6) 的 numpy 数组
    print(len(result))

    img = cv2.imread('4.png')
    # img = extract_dark_text(img)  # 确保 extract_dark_text 支持 OpenCV 图像格式
    # img = cv2.bitwise_not(img)

    # 调整图像大小为 (500, 500) 如果需要
    if img.shape[0] != 500 or img.shape[1] != 500:
        img = cv2.resize(img, (500, 500))

    # 检查白色像素
    white_pixels = np.all(img >= 240, axis=-1)
    mask_o = np.where(white_pixels, 0, 1).astype(np.uint8)

    for i in range(6):
        mask = result[:, :, i]  # 取第i个类别 (500, 500)
        mask = np.logical_and(mask, mask_o)

        # 将 0/1 转换为 0~255 的像素值（0 -> 黑色，1 -> 白色）
        mask_image = (mask * 255).astype(np.uint8)

        # 使用 OpenCV 保存图像
        cv2.imwrite(f'prediction_class_{i}.png', mask_image)

        if i == 5:
            # 打印 mask 中为 1 的坐标
            for x in range(500):
                for y in range(500):
                    if mask[x, y] == 1:
                        print(x, y)
