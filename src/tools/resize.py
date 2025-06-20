import cv2
import numpy as np

def resize_and_center(img, target=(500, 500)):
    if len(img.shape) < 3:
        img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
    height, width = img.shape[:2]  # OpenCV uses height first

    # Calculate scaling ratio while maintaining aspect ratio
    if height > width:
        new_height = target[1]
        new_width = int(width * (new_height / height))
    else:
        new_width = target[0]
        new_height = int(height * (new_width / width))

    # Resize the image
    img_resized = cv2.resize(img, (new_width, new_height), interpolation=cv2.INTER_LANCZOS4)

    # Create white background
    background = np.ones((target[1], target[0], 3), dtype=np.uint8) * 255

    # Calculate offset to center the image
    offset_x = (target[0] - new_width) // 2
    offset_y = (target[1] - new_height) // 2

    # Place the resized image on the background
    background[offset_y:offset_y + new_height, offset_x:offset_x + new_width] = img_resized


    return background