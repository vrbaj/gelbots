import cv2
import numpy as np
import imutils
import os


kernel = np.ones((3,3),np.uint8)
cap = cv2.VideoCapture("cancer.avi")
out = cv2.createBackgroundSubtractorMOG2()

fourcc = cv2.VideoWriter_fourcc(*'MJPG')
output = cv2.VideoWriter('output.avi', fourcc, 20.0, (640,480), isColor=False)
frame_index = 0
while(cap.isOpened()):
    ret, frame = cap.read()
    frame_index += 1
    if ret==True:
        # frame = cv2.flip(frame,180)

        outmask = out.apply(frame)
        cnts = cv2.findContours(outmask, cv2.RETR_EXTERNAL,
                                cv2.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)
        for c in cnts:
            # if the contour is too small, ignore it
            print(cv2.contourArea(c))
            if cv2.contourArea(c) < 5:
                continue
            elif cv2.contourArea(c) > 4000:
                continue
            # compute the bounding box for the contour, draw it on the frame,
            # and update the text+
            (x, y, w, h) = cv2.boundingRect(c)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        output.write(outmask)

        cv2.imshow('original', frame)
        cv2.imshow('Motion Tracker', outmask)
        cv2.imwrite(os.path.join('../vid_detection_dyn', 'frame' + str(frame_index).zfill(5) + '.png'), frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    else:
        break


output.release()
cap.release()
cv2.destroyAllWindows()