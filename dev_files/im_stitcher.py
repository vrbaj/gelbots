import cv2
import os
import time


images = []
start_time = time.time()
for image_file in sorted(os.listdir("y_axis_identification")):
    print(image_file)
    image = cv2.imread(os.path.join("y_axis_identification", image_file))
    print("image original size: ", image.shape)
    # cv2.imshow("ss", image)
    # cv2.waitKey(100)
    images.append(image)

print("[INFO] stitching images...")
stitcher = cv2.createStitcher()
(status, stitched) = stitcher.stitch(images)

print("STATUS:", status)

# if the status is '0', then OpenCV successfully performed image
# stitching
if status == 0:
    # write the output stitched image to disk
    print("writing img")
    cv2.imwrite("img.png", stitched)
    imS = cv2.resize(stitched, (800, 600))
    # display the output stitched image to our screen

# otherwise the stitching failed, likely due to not enough keypoints)
# being detected
else:
    print("[INFO] image stitching failed ({})".format(status))

stop_time = time.time() - start_time
print("time elapsed: ", stop_time)

print("new _shape", stitched.shape)
cv2.imshow("Stitched", imS)
cv2.waitKey(0)
