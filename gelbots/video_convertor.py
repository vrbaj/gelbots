"""
Simple module for joining images to video file.
"""
import os

import cv2


IMAGES_DIRECTORY = "vid_detection"

img_array = []
files_to_process = os.listdir(os.path.join(IMAGES_DIRECTORY))
files_to_process.sort()

size = (0, 0)
for idx, filename in enumerate(files_to_process):
    img = cv2.imread(os.path.join(IMAGES_DIRECTORY, str(filename)))
    height, width, layers = img.shape
    size = (width, height)
    img_array.append(img)
    img_array.append(img)
    img_array.append(img)

out = cv2.VideoWriter('cancer_2.avi', cv2.VideoWriter_fourcc(*'DIVX'), 30, size)

for i, img in enumerate(img_array):
    out.write(img_array[i])
out.release()
