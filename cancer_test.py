import numpy as np
import cv2
import imutils


cap = cv2.VideoCapture('cancer.avi')
first_frame_flag = False
background = []
background_storage = []
print(type(background_storage))
min_area = 50
kernel = np.ones((7,7),np.uint8)
number_of_background = 5
background_index = 0
while(cap.isOpened()):

    ret, frame = cap.read()
    if not first_frame_flag:
        helpy = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        # helpy = cv2.Canny(helpy, 100, 200)
        background_storage.append(helpy)
        background_index += 1
        if background_index == number_of_background:
            first_frame_flag = True
            background = np.average(background_storage,axis=0)
            background = background.astype(np.uint8)
    if first_frame_flag:

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        # gray = cv2.Canny(gray, 100, 200)
        subtracted = cv2.absdiff(gray, cv2.UMat(background))
        thresh = cv2.threshold(subtracted, 35, 255, cv2.THRESH_BINARY)[1] #thresh 35
        cv2.imshow("threshed", thresh)
        thresh = cv2.erode(thresh, np.ones((1,1),np.uint8), iterations=1)
        cv2.imshow("eroded", thresh)
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
            # compute the bounding box for the contour, draw it on the frame,
            # and update the text+
            (x, y, w, h) = cv2.boundingRect(c)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cv2.imshow('frame',thresh)
        cv2.imshow("real", frame)
        cv2.imshow("subtracted", subtracted)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()