import uuid

from flask import Flask, request, jsonify
import base64
from PIL import Image
import os
from src.Detecter import *
from src.Divider import Divider
from src.StyleTansform import image_style_transfer_enhance

app = Flask(__name__)
divider = Divider('src/model/unet_model_2.pth')

from flask_cors import CORS
CORS(app)


@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'


# 配置上传文件夹
UPLOAD_FOLDER = 'processed_images'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route('/api/detect', methods=['POST'])
def process_image():
    try:
        # 获取上传的文件
        if 'image' not in request.files:
            return jsonify({'error': 'No image provided'}), 400

        file = request.files['image']
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400

        # 将上传的文件转换为OpenCV图像
        image = Image.open(file.stream)
        image = np.array(image)

        # 如果图像是RGBA，转换为RGB
        if image.shape[2] == 4:
            image = cv2.cvtColor(image, cv2.COLOR_RGBA2RGB)

        # 获取参数
        width = request.form.get('width')
        height = request.form.get('height')
        style = request.form.get('style', 'default')

        _ , boxes = extract_text(image)

        if style!= 'no':
            image = image_style_transfer_enhance(image, style)

        # 如果image是单通道图，扩展成三通道
        if len(image.shape) < 3:
            image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
        processed_images = []
        processed_images.append(_)
        processed_images += divide_text(image, boxes, size=(int(width), int(height)))

        encoded_images = []
        for img in processed_images:
            _, buffer = cv2.imencode('.png', img)
            encoded = base64.b64encode(buffer).decode('utf-8')
            encoded_images.append(f"data:image/png;base64,{encoded}")

        return jsonify({'processed_images': encoded_images}), 200

    except Exception as e:
            return jsonify({'error': str(e)}), 500

@app.route('/api/divide', methods=['POST'])
def divide_image():
    try:
        # 获取上传的文件
        if 'image' not in request.files:
            return jsonify({'error': 'No image provided'}), 400

        file = request.files['image']
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400

        # 将上传的文件转换为OpenCV图像
        image = Image.open(file.stream)
        image = np.array(image)

        # 如果图像是单通道，转换为三通道
        if len(image.shape) < 3:
            image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)

        # 如果图像是RGBA，转换为RGB
        if image.shape[2] == 4:
            image = cv2.cvtColor(image, cv2.COLOR_RGBA2RGB)

        # 获取参数
        width = request.form.get('width')
        height = request.form.get('height')

        image = resize_and_center(image, target=(500, 500))

        result = divider.divide(image)

        for img in result:
            resize_and_center(img, target=(int(width), int(height)))

        encoded_images = []
        for img in result:
            _, buffer = cv2.imencode('.png', img)
            encoded = base64.b64encode(buffer).decode('utf-8')
            encoded_images.append(f"data:image/png;base64,{encoded}")

        return jsonify({'processed_images': encoded_images}), 200

    except Exception as e:
            return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
