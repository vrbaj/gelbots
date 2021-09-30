import cv2
import glob
import time
import numpy as np
import os

CORR_THRESHOLD = 0.65
CENTER_ERR = 20

def get_available_cameras():
    cameras = []
    for camera in glob.glob("/dev/video?"):
        cameras.append(cv2.VideoCapture(camera))
        cameras[-1].set(cv2.CAP_PROP_FRAME_WIDTH, 800)  # works well
        time.sleep(0.1)
        cameras[-1].set(cv2.CAP_PROP_FRAME_HEIGHT, 600)  # works well
        time.sleep(0.1)
    return cameras


def get_image(camera):

    ret, image = camera.read()

    return image

def find_disks(img):
    #img = cv2.medianBlur(image, 5)
    #cimg = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    disks_location = []
    circles = cv2.HoughCircles(img, cv2.HOUGH_GRADIENT, 1, 20,
                               param1=50, param2=30, minRadius=20, maxRadius=30)
    print("circles: ", circles)
    circles = np.uint16(np.around(circles))
    for i in circles[0, :]:
        # draw the outer circle
        if i[2] > 20 and i[2] < 30:
            #cv2.circle(cimg, (i[0], i[1]), i[2], (0, 255, 0), 2)
            # draw the center of the circle
            #cv2.circle(cimg, (i[0], i[1]), 2, (0, 0, 255), 3)
            disks_location.append((i[0], i[1]))
    return disks_location


def find_disks_old(image):
    disks_location = []
    #TODO iterate over files in "disk_templates" directory
    for idx, file in enumerate(os.listdir("disk_templates")):
        print("template file:", str(file))
        template_ext = cv2.imread(os.path.join("disk_templates", file))
        template_ext = cv2.cvtColor(template_ext, cv2.COLOR_BGR2GRAY)
        print(type(template_ext))
        template = template_ext[:-1, :]
        pad1 = int(template.shape[0] / 2)
        pad2 = int(template.shape[1] / 2)
        print([(pad1,), (pad2,)])
        img = np.pad(image, [(pad1,), (pad2,)], mode='constant')
        #w, h = template.shape[::-1]
        mask_size = 25  # TODO mask_size estimation
        max_val = 1
        i = 0
        print(template.shape)
        print(img.shape)
        previous_center = [1000,100000]
        while max_val > CORR_THRESHOLD:
            i = i + 1
            res = cv2.matchTemplate(img.astype(np.uint8), template, cv2.TM_CCOEFF_NORMED)
            print("found disk ", i)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
            if previous_center == max_loc:
                break
            previous_center = max_loc
            print(max_loc)
            center_not_found_yet = True
            for center in disks_location:
                if abs(center[0] - max_loc[0]) < CENTER_ERR and abs(center[1] - max_loc[1]) < CENTER_ERR:
                    center_not_found_yet = False
            if max_val > CORR_THRESHOLD and center_not_found_yet:
                disks_location.append(max_loc)
                img[max_loc[1] - mask_size + pad1: max_loc[1] + mask_size + pad1, max_loc[0]
                        - mask_size + pad2: max_loc[0] + mask_size + pad2] = 0
                print(img.shape)
                cv2.imshow("wtf", img)
    return disks_location


def find_disks_roi(image, center_of_disk):
    #TODO rework completly
    for idx, file in enumerate(os.listdir(os.path.join("disk_templates"))):
        pass
    template_ext = cv2.imread('template.png', 0)
    template = template_ext[:-1, :]
    pad1 = int(template.shape[0] / 2)
    pad2 = int(template.shape[1] / 2)
    print([(pad1,), (pad2,)])
    img = np.pad(image, [(pad1,), (pad2,)], mode='constant')
    w, h = template.shape[::-1]
    mask_size = 55  # TODO mask_size estimation
    max_val = 1
    disks_location = []
    i = 0
    while i <= 0:

        i = i + 1
        res = cv2.matchTemplate(img[center_of_disk[0]-50:center_of_disk[0]+50, center_of_disk[1]-50:center_of_disk[1]+50], template, cv2.TM_CCOEFF_NORMED)
        print("found disk ", i)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
        max_loc[0] = max_loc[0] + center_of_disk[0] - 50
        max_loc[1] = max_loc[1] + center_of_disk[1] - 50
        print(max_loc)

        disks_location.append(max_loc)
        img[max_loc[1] - mask_size + pad1: max_loc[1] + mask_size + pad1, max_loc[0]
                    - mask_size + pad2: max_loc[0] + mask_size + pad2] = 178
        print(img.shape)
        cv2.imshow("wtf roi", img[center_of_disk[0]-50:center_of_disk[0]+50, center_of_disk[1]-50:center_of_disk[1]+50])

    return disks_location
