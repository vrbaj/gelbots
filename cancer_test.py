import numpy as np
import cv2
import imutils
import os


# cap = cv2.VideoCapture('cancer.avi')
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
first_frame_flag = False
background = []
background_storage = []
print(type(background_storage))
min_area = 200
max_area = 4000
kernel = np.ones((7,7),np.uint8)
number_of_background = 50
background_index = 0
frame_index = 0
while(cap.isOpened()):

    ret, frame = cap.read()
    cv2.imwrite(os.path.join('video', 'frame' + str(frame_index) +'.png'), frame)
    frame_index += 1
    if not first_frame_flag:
        helpy = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        # helpy = cv2.Canny(helpy, 100, 200)
        helpy = cv2.blur(helpy, (3, 3))
        background_storage.append(helpy)
        background_index += 1
        if background_index == number_of_background:
            first_frame_flag = True
            background = np.average(background_storage,axis=0)
            background = background.astype(np.uint8)
    if first_frame_flag:

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.blur(gray, (3, 3))
        # gray = cv2.Canny(gray, 100, 200)
        subtracted = cv2.absdiff(gray, cv2.UMat(background))
        thresh = cv2.threshold(subtracted, 2, 255, cv2.THRESH_BINARY)[1] #thresh 35
        # cv2.imshow("threshed", thresh)
        # thresh = cv2.erode(thresh, np.ones((1,1),np.uint8), iterations=1)
        cv2.imshow("eroded", thresh)
        thresh = cv2.Canny(thresh, 50, 100)
        cv2.imshow('canny', thresh)
        thresh = cv2.dilate(thresh, kernel, iterations=7)
        cv2.imshow("dilated", thresh)

        cnts = cv2.findContours(thresh, cv2.RETR_EXTERNAL,
                            cv2.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)
        for c in cnts:
            # if the contour is too small, ignore it
            print(cv2.contourArea(c))
            if cv2.contourArea(c) < min_area:
                continue
            elif cv2.contourArea(c) > max_area:
                continue
            # compute the bounding box for the contour, draw it on the frame,
            # and update the text+
            (x, y, w, h) = cv2.boundingRect(c)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cv2.imshow('frame',thresh)
        cv2.imshow("real", frame)
        cv2.imshow("subtracted", subtracted)
        cv2.imshow('blurred', gray)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()