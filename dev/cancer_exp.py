import cv2
import numpy as np
import os
import math


im1 = cv2.imread(os.path.join("../videos", "_0009.tiff"))
im1 = cv2.cvtColor(im1, cv2.COLOR_BGR2GRAY)
im1 = cv2.medianBlur(im1, 3)
im1 = cv2.Canny(im1,100,200)
cv2.imshow("blurred", im1)
im2 = cv2.imread(os.path.join("../videos", "_0010.tiff"))
im2 = cv2.cvtColor(im2, cv2.COLOR_BGR2GRAY)
im2 = cv2.medianBlur(im2,3)
diff_im = cv2.absdiff(im1, im2)
lines = cv2.HoughLines(im1, 1, np.pi / 180, 2000, None, 0, 0)


print(np.max(diff_im))
cv2.imshow("diff", diff_im)
cv2.imshow("im1", im1)
cv2.waitKey(0)


