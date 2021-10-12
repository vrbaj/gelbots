import cv2


def draw_marks(gray_image, disk_list, target_list, laser_loc, sfl):
    for disk in disk_list:
        gray_image = cv2.drawMarker(gray_image, tuple(disk), (255, 255, 0),
                                    markerType=cv2.MARKER_TILTED_CROSS,
                                    markerSize=20, thickness=1,
                                    line_type=cv2.LINE_AA)
    for target in target_list:
        gray_image = cv2.drawMarker(gray_image, tuple(target), (255, 255, 0),
                                    markerType=cv2.MARKER_DIAMOND,
                                    markerSize=20, thickness=1,
                                    line_type=cv2.LINE_AA)

    gray_image = cv2.drawMarker(gray_image, (laser_loc[0], laser_loc[1]),
                                (0, 255, 0), markerType=cv2.MARKER_STAR,
                                markerSize=20, thickness=1, line_type=cv2.LINE_AA)

    gray_image = cv2.drawMarker(gray_image, (sfl[0],sfl[1]),
                                (0, 255, 0), markerType=cv2.MARKER_CROSS,
                                markerSize=20, thickness=1, line_type=cv2.LINE_AA)
    gray_image = cv2.circle(gray_image, (sfl[0], sfl[1]),
                                 sfl[2], (0, 255, 0), 2)
    return gray_image