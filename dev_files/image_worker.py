import json
import cv2
import os
from timeit import default_timer as timer
import numpy as np

def find_bot(img, roi_bounds, previous_area, cX, cY, reset_search, filename):
    rectangle_size = 100
    start = timer()
    # print(roi_bounds)
    img_roi = img[roi_bounds[0][1]:roi_bounds[1][1], roi_bounds[0][0]:roi_bounds[1][0]]
    gray_img = cv2.cvtColor(img_roi, cv2.COLOR_BGR2GRAY)
    img_colors = img
    edges = cv2.Canny(gray_img, 0, 100)
    # cv2.imshow('edges', edges)

    img_invert = cv2.bitwise_not(edges)
    # cv2.imshow('inverted', img_invert)

    new_roi_bounds = [list(roi_bounds[0]), list(roi_bounds[1])]



    kernel = np.ones((2, 2), np.uint8)
    img_erosion = cv2.erode(img_invert, kernel, iterations=1)
    cv2.imshow('erosion', img_erosion)


    # kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    # morphed = cv2.morphologyEx(img_erosion, cv2.MORPH_CLOSE, kernel)
    # cv2.imshow('morphed', morphed)



    _, contours, hierarchy = cv2.findContours(img_erosion, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    area_found = False
    contours_area_list = [0, 0]
    contour_to_draw = []
    contour_diff_abs = 99999999
    contour_diff = 0
    new_contour_area = previous_area
    img_colors = cv2.cvtColor(gray_img, cv2.COLOR_GRAY2BGR)
    for contour in contours:
        contour_area = cv2.contourArea(contour)
        if abs(contour_area - previous_area) < contour_diff_abs and contour_area > 5000 and contour_area < 15000\
                and abs(contour_area - previous_area) < 3500 or (reset_search and contour_area > 5000 and contour_area < 15000):

            contour_diff_abs = abs(contour_area - previous_area)
            contour_diff = contour_area - previous_area
            contour_to_draw = contour
            new_contour_area = contour_area
            previous_area = contour_area
            area_found = True
        # TODO> find nearest area to previous one according to center
        # if contour_area > min(contours_area_list):
        #     area_index = contours_area_list.index(min(contours_area_list))
        #     contours_area_list[area_index] = contour_area
        #     contour_to_draw[area_index] = contour
            print("AREA, DIFF, PREVIOUS ARE>", new_contour_area, "   ", contour_diff, "    ", previous_area)
            #print(contour_to_draw)

            cv2.drawContours(img_colors, contours, -1, (0, 255, 0), 3)

            M = cv2.moments(contour_to_draw)
            print("ABS CX:", abs(cX - int(M["m10"] / M["m00"])))
            print("ABS CY:", abs(cY - int(M["m01"] / M["m00"])))
            if abs(cX - int(M["m10"] / M["m00"])) < 30 and abs(cY - int(M["m01"] / M["m00"])) < 30 or reset_search:
                cX = int(M["m10"] / M["m00"])
                cY = int(M["m01"] / M["m00"])
            reset_search = False
            # end = timer()
    # ret, thresh_img = cv2.threshold(gray_img, 160, 255, cv2.THRESH_BINARY)
    # cv2.imshow('thresh', thresh_img)
    #     else:
    #         print("contour area", contour_area)
    if area_found:

        # new_roi_bounds = roi_bounds

        if cX + roi_bounds[0][0] - rectangle_size > img.shape[0]:
            new_roi_bounds[0][0] = img.shape[0]
        elif cX + roi_bounds[0][0] - rectangle_size < 0:
            new_roi_bounds[0][0] = 0
        else:
            new_roi_bounds[0][0] = cX + roi_bounds[0][0] - rectangle_size

        if cX + roi_bounds[0][0] + rectangle_size > img.shape[0]:
            new_roi_bounds[1][0] = img.shape[0]
        elif cX + roi_bounds[0][0] + rectangle_size < 0:
            new_roi_bounds[1][0] = 0
        else:
            new_roi_bounds[1][0] = cX + roi_bounds[0][0] + rectangle_size

        if cY + roi_bounds[0][1] - rectangle_size > img.shape[1]:
            new_roi_bounds[0][1] = img.shape[1]
        elif cY + roi_bounds[0][1] - rectangle_size < 0:
            new_roi_bounds[0][1] = 0
        else:
            new_roi_bounds[0][1] = cY + roi_bounds[0][1] - rectangle_size

        if cY + roi_bounds[0][1] + rectangle_size > img.shape[1]:
            new_roi_bounds[1][1] = img.shape[1]
        elif cY + roi_bounds[0][1] + rectangle_size < 0:
            new_roi_bounds[1][1] = 0
        else:
            new_roi_bounds[1][1] = cY + roi_bounds[0][1] + rectangle_size

        # new_roi_bounds = [[cX + roi_bounds[0][0] - rectangle_size, cY + roi_bounds[0][1] - rectangle_size],
        #                [cX + roi_bounds[0][0] + rectangle_size, cY + roi_bounds[0][1] + rectangle_size]]
        #
        # if new_roi_bounds[0][0] < 0:
        #     new_roi_bounds[0][0] = 0
        # elif new_roi_bounds[0][0] > img.shape[1]:
        #     new_roi_bounds[0][0] = img.shape[1]
        # if new_roi_bounds[0][1] < 0:
        #     new_roi_bounds[0][1] = 0
        # elif new_roi_bounds[0][1] > img.shape[0]:
        #     new_roi_bounds[0][1] = img.shape[0]
        # if new_roi_bounds[1][0] < 0:
        #     new_roi_bounds[1][0] = 0
        # elif new_roi_bounds[1][0] > img.shape[1]:
        #     new_roi_bounds[1][0] = img.shape[1]
        # if new_roi_bounds[1][1] < 0:
        #     new_roi_bounds[1][1] = 0
        # elif new_roi_bounds[1][1] > img.shape[0]:
        #     new_roi_bounds[1][1] = img.shape[0]

    new_roi_bounds[0]= tuple(new_roi_bounds[0])
    new_roi_bounds[1] = tuple(new_roi_bounds[1])
    cv2.rectangle(img, new_roi_bounds[0],
                      new_roi_bounds[1], (255, 0, 0), 2)

        # cv2.imshow('subimg', sub_img)
        # print(end - start)

        # print("cX=", cX)
        # print("cY=", cY)

    cv2.line(img_colors, (cX - 5, cY ), (cX + 5, cY), (255, 0, 0), 2)
    cv2.line(img_colors, (cX, cY - 5), (cX, cY + 5), (255, 0, 0), 2)
    cv2.line(img, (roi_bounds[0][0] + cX - 5, cY + roi_bounds[0][1]), (roi_bounds[0][0] + cX + 5, cY + roi_bounds[0][1]), (255, 0, 0), 2)
    cv2.line(img, (roi_bounds[0][0] + cX, cY + roi_bounds[0][1] - 5), (roi_bounds[0][0] + cX, cY + roi_bounds[0][1] + 5), (255, 0, 0), 2)
    cv2.imshow("contoured", img_colors)
    cv2.imshow("original", img)
    cv2.waitKeyEx(0)
    #cv2.imwrite(os.path.join("videos", "test", "roi", "roi" + filename), img_colors)
    #cv2.imwrite(os.path.join("videos", "test","full", "full" + filename), img)
    bot_center = [cX + roi_bounds[0][0], cY + roi_bounds[0][1]]
    # print(bot_center)
    # print(new_roi_bounds)
    # new_roi_bounds = [(cX + roi_bounds[0][0] - rectangle_size, cY + roi_bounds[0][1] - rectangle_size),
    #                   (cX + roi_bounds[0][0] + rectangle_size, cY + roi_bounds[0][1] + rectangle_size)]
    # print("correct bounds>", [(cX + roi_bounds[0][0] - rectangle_size, cY + roi_bounds[0][1] - rectangle_size),
    #               (cX + roi_bounds[0][0] + rectangle_size, cY + roi_bounds[0][1] + rectangle_size)])
    return new_roi_bounds, bot_center, previous_area, cX, cY
