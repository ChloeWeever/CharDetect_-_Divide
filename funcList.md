# 功能清单

---

## 📌 一、图像检测与识别

### ✅ 1. 文字区域检测
- **功能描述**：从输入图像中检测出文字所在的区域。
- **使用模块**：`src/Detecter.py`
- **核心方法**：
  - [extract_text(image)](file://C:\Users\Lenovo\PycharmProjects\CharDetect_&_Divide\src\Detecter.py#L6-L19)：提取图像中的文字区域并返回边界框。

---

## 📌 二、图像分割与字符切分

### ✅ 2. 基于UNet模型的图像分割
- **功能描述**：使用训练好的UNet模型对图像进行多类笔画分割。
- **使用模块**：`src/Divider.py` + `model/unet_model.py`
- **核心方法**：
  - [predict(image, threshold=0.5)](file://C:\Users\Lenovo\PycharmProjects\CharDetect_&_Divide\src\Divider.py#L21-L38)：输入图像，输出每个像素属于6个类别的概率图。
- **模型依赖**：加载训练好的 [.pth](file://C:\Users\Lenovo\PycharmProjects\CharDetect_&_Divide\src\model\unet_model_2.pth) 模型文件进行推理。

### ✅ 3. 字符级分割与切分
- **功能描述**：将检测到的文字区域按字符或笔画进行切分。
- **使用模块**：[divide_text()](file://C:\Users\Lenovo\PycharmProjects\CharDetect_&_Divide\src\Detecter.py#L21-L29) 函数（可能封装在 `src.Divider` 中）
- **应用场景**：用于汉字结构分析、手写识别前处理等。

---

## 📌 三、图像风格迁移与增强

### ✅ 4. 图像风格转换增强
- **功能描述**：根据用户选择的风格对图像进行风格化处理，提升视觉效果。
- **使用模块**：`src/StyleTansform.py`
- **核心方法**：
  - [image_style_transfer_enhance(image, style)](file://C:\Users\Lenovo\PycharmProjects\CharDetect_&_Divide\src\StyleTansform.py#L7-L73)：支持多种风格（如卡通、素描等）。
- **技术基础**：可能基于OpenCV或深度学习模型实现。

---

## 📌 四、图像预处理功能

### ✅ 5. 图像二值化与黑白提取
- **功能描述**：将图像中除白色以外的颜色设为黑色，并进行二值化处理。
- **使用模块**：`train/data/filter.py`
- **核心函数**：
  - `process_image_to_binary(image_path, output_path=None, white_threshold=200)`

### ✅ 6. 颜色过滤与红色标记中心点
- **功能描述**：仅保留图像中的黑色和红色区域，标记红色区域的质心。
- **使用模块**：[filter_colors_and_mark_red_centers()](file://C:\Users\Lenovo\PycharmProjects\CharDetect_&_Divide\train\data\filter.py#L8-L78)

### ✅ 7. K-Means/GMM聚类提取暗色文字
- **功能描述**：利用无监督聚类算法提取图像中的暗色文字区域。
- **使用模块**：`src/tools/kmeans_filter.py`
- **核心方法**：
  - `extract_dark_text(img, n_clusters=5, use_gmm=False)`
- **可视化支持**：可显示原始图像与提取结果对比。

### ✅ 8. 自适应阈值处理与形态学操作
- **功能描述**：对图像进行自适应阈值分割、开闭运算等去噪处理。
- **使用模块**：[marker.py](file://C:\Users\Lenovo\PycharmProjects\CharDetect_&_Divide\src\tools\marker.py) 和 [resize.py](file://C:\Users\Lenovo\PycharmProjects\CharDetect_&_Divide\src\tools\resize.py)

### ✅ 9. 图像缩放与居中填充
- **功能描述**：将图像等比缩放到指定大小（如500x500），并居中填充白色背景。
- **使用模块**：`resize_and_center(image_path, output_path=None, target=(500,500))`

---

## 📌 五、图像后处理与标注

### ✅ 10. 手写字标记与轮廓检测
- **功能描述**：检测并用红色矩形框标出手写字符区域。
- **使用模块**：[mark_handwritten_characters(binary_image)](file://C:\Users\Lenovo\PycharmProjects\CharDetect_&_Divide\src\tools\marker.py#L59-L106)
- **应用示例**：用于手写识别系统预处理阶段。


---

## ✅ 总结

| 功能类别   | 子功能                           | 主要模块                                                     |
| ---------- | -------------------------------- | ------------------------------------------------------------ |
| 图像检测   | 文字区域检测                     | [Detecter.py](file://C:\Users\Lenovo\PycharmProjects\CharDetect_&_Divide\src\Detecter.py) |
| 图像分割   | UNet笔画分割                     | [Divider.py](file://C:\Users\Lenovo\PycharmProjects\CharDetect_&_Divide\src\Divider.py), [unet_model.py](file://C:\Users\Lenovo\PycharmProjects\CharDetect_&_Divide\src\model\unet_model.py) |
| 风格处理   | 图像风格转换                     | [StyleTansform.py](file://C:\Users\Lenovo\PycharmProjects\CharDetect_&_Divide\src\StyleTansform.py) |
| 图像预处理 | 二值化、颜色过滤、KMeans提取文字 | [filter.py](file://C:\Users\Lenovo\PycharmProjects\CharDetect_&_Divide\train\data\filter.py), [kmeans_filter.py](file://C:\Users\Lenovo\PycharmProjects\CharDetect_&_Divide\src\tools\kmeans_filter.py) |
| 图像变换   | 缩放、居中、裁剪                 | [resize.py](file://C:\Users\Lenovo\PycharmProjects\CharDetect_&_Divide\src\tools\resize.py) |
| 图像标注   | 标记红点、手写字符边框           | [marker.py](file://C:\Users\Lenovo\PycharmProjects\CharDetect_&_Divide\src\tools\marker.py) |

