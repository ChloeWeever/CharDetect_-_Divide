import cv2
from src.tools.marker import mark_handwritten_characters, merge_contours_based_on_distance
from src.tools.kmeans_filter import *
from src.tools.resize import *


def extract_text(image):
    image = extract_dark_text(image)
    image = cv2.bitwise_not(image)
    processed_img,contours = mark_handwritten_characters(image)
    # cv2.imwrite('processed_image.jpg',  processed_img)
    merged_boxes,average_width,average_height,average_area = merge_contours_based_on_distance(contours)
    # print(len(merged_boxes),average_width,average_height,average_area)
    for box in merged_boxes:
        x, y, w, h = box
        cv2.rectangle(processed_img, (x, y), (x + w, y + h), (0, 255, 0), 2)
        # print(x,y,w,h)
    # cv2.imwrite('merged_image.jpg', processed_img)

    return processed_img, merged_boxes

def divide_text(image, boxes, size=(500,500)):
    result_images = []
    for box in boxes:
        x,y,w,h= box
        roi = image[y:y+h, x:x+w]
        # resize_and_center(roi, f'result/{x}_{y}.jpg')
        roi = resize_and_center(roi, size)
        result_images.append(roi)
    return result_images

if __name__ == '__main__':
    image_path = 'R.jpg'
    image = cv2.imread(image_path)
    processed_img, boxes = extract_text(image)
    divide_text(image, boxes)


