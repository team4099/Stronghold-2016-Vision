#!/usr/bin/env python

import cv2
import numpy
import math

B_RANGE = (225, 255)
G_RANGE = (225, 255)
R_RANGE = (225, 255)


WIDTH_OF_GOAL_IN_METERS = 0.51
FOV_OF_CAMERA = math.radians(57)
# FOV_OF_CAMERA = math.radians(1)
# cv.NamedWindow("Vision")


def threshold_image_for_tape(image):
    orig_image = numpy.copy(image)
    # print orig_image.size
    orig_image = cv2.medianBlur(orig_image, 11)
    height, width = orig_image.shape[0], orig_image.shape[1]
    eight_bit_image = numpy.zeros((height, width, 1), numpy.uint8)
    cv2.inRange(orig_image,
                (B_RANGE[0], G_RANGE[0], R_RANGE[0], 0),
                (B_RANGE[1], G_RANGE[1], R_RANGE[1], 100),
                eight_bit_image)
    # eight_bit_image = cv2.adaptiveThreshold(orig_image,
    #                             255,
    #                             cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
    #                             cv2.THRESH_BINARY,
    #                             8,
    #                             0)
    cv2.medianBlur(eight_bit_image, 9)
    return eight_bit_image


def get_contours(orig_image):
    new_image = numpy.copy(orig_image)
    new_image, contours, hierarchy = cv2.findContours(new_image,
                                                      cv2.RETR_EXTERNAL,
                                                      cv2.CHAIN_APPROX_NONE)
    # print(len(contours[0]))
    largest_contour = 0
    if len(contours) > 1:
        max_area = cv2.contourArea(contours[0])
        for i in range(1, len(contours)):
            current_area = cv2.contourArea(contours[i])
            if current_area > max_area:
                max_area = current_area
                largest_contour = i

    rect = cv2.minAreaRect(contours[largest_contour])
    box = cv2.boxPoints(rect)
    box = numpy.int0(box)
    # print(box)
    return numpy.array(contours[largest_contour]), box


def get_corners_from_contours(contours):
    # print(contours)
    epsilon = .05 * cv2.arcLength(contours, True)
    # epsilon =
    print("epsilon:", epsilon)
    poly_approx = cv2.approxPolyDP(contours, epsilon, True)
    hull = cv2.convexHull(poly_approx)
    # print(poly_approx)
    return hull


def sort_corners(corners, center):
    top = []
    bot = []
    # print("center:", center)
    for i in range(len(corners)):
        # print("corners[i][0][1]:", corners[i][0][1])
        if(corners[i][0][1] < center[1]):
            top.append(corners[i])
        else:
            bot.append(corners[i])
    # print("top:", top)
    tl = top[1] if top[0][0][0] > top[1][0][0] else top[0]
    tr = top[0] if top[0][0][0] > top[1][0][0] else top[1]
    bl = bot[1] if bot[0][0][0] > bot[1][0][0] else bot[0]
    br = bot[0] if bot[0][0][0] > bot[1][0][0] else bot[1]
    return numpy.array([tl, tr, br, bl], numpy.float32)


def get_center(corners):
    center = numpy.array([0, 0])
    for i in range(len(corners)):
        center[0] += corners[i][0][0]
        center[1] += corners[i][0][1]
    center[0] /= len(corners)
    center[1] /= len(corners)
    return center


def get_warped_image_from_corners(image, corners):
    orig_image = numpy.copy(image)
    center = get_center(corners)
    corners = sort_corners(corners, center)

    height_right = int(math.sqrt((corners[1][0][0] - corners[2][0][0]) ** 2 +
                                 (corners[1][0][1] - corners[2][0][1]) ** 2))
    height_left = int(math.sqrt((corners[0][0][0] - corners[3][0][0]) ** 2 +
                                (corners[0][0][1] - corners[3][0][1]) ** 2))
    height = int((height_left + height_right) / 2)
    width = int(height * (300 / 210))

    quad = numpy.zeros((width, height))
    quad_pts = numpy.array([[[0, 0]],      [[width, 0]],
                            [[width, height]], [[0, height]]], numpy.float32)

    new_image_to_process = numpy.array(image, numpy.float32)
    quad_pts = cv2.getPerspectiveTransform(corners, quad_pts)
    warped_image = cv2.warpPerspective(new_image_to_process, quad_pts, (width, height))
    return warped_image

def get_distance_to_goal(orig_image, warped_image):
    angle_between_sides = (len(warped_image[0]) / len(orig_image[0])) * FOV_OF_CAMERA
    print(math.degrees(angle_between_sides))
    return ((WIDTH_OF_GOAL_IN_METERS / 2) / math.sin(angle_between_sides / 2)) * math.sin((math.pi + angle_between_sides) / 2)

def main(image_to_process):
    # image_to_process = cv2.imread("img/video_14528758.png")
    untouched_image = numpy.copy(image_to_process)

    thresholded_image = threshold_image_for_tape(numpy.copy(image_to_process))
    cv2.imwrite("img/thresholded.png", thresholded_image)
    contours, box = get_contours(thresholded_image)

    contoured_image = numpy.copy(untouched_image)
    contoured_image = cv2.drawContours(contoured_image, contours, -1, (0, 0, 0))
    cv2.imwrite("img/contoured.png", contoured_image)

    total_image = numpy.copy(untouched_image)
    total_image = cv2.drawContours(total_image, [box], -1, (0, 0, 0))
    cv2.imwrite("img/total_image.png", total_image)
    # x = get_corners_from_contours(contours)
    # cv2.imwrite("img/new_image.png", new_image)
    # print(type(contours))

    corners = get_corners_from_contours(contours)

    new_image = numpy.copy(untouched_image)
    new_image = cv2.drawContours(new_image, [corners], -1, (0, 0, 0))
    cv2.imwrite("img/hull_image.png", new_image)

    warped_image = numpy.copy(untouched_image)
    warped_image = get_warped_image_from_corners(warped_image, corners)

    print(get_distance_to_goal(untouched_image, warped_image))
    # total_image = cv2.drawContours(image_to_process, [corners], -1, (0, 0, 0))
    cv2.imwrite("img/warped_image.png", warped_image)
    # print(x)
    # while 1:
    #     cv.ShowImage("Vision", image_to_process)

main(cv2.imread("img/video_14528758.png"))
