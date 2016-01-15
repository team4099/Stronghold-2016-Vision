#!/usr/bin/env python

import cv2
import numpy

B_RANGE = (235, 255)
G_RANGE = (235, 255)
R_RANGE = (235, 255)

# cv.NamedWindow("Vision")

def threshold_image_for_tape(orig_image):
    # print orig_image.size
    orig_image = cv2.medianBlur(orig_image, 9)
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
    cv2.blur(eight_bit_image, (7, 7))
    return eight_bit_image


def get_contours(orig_image):
    new_image = numpy.copy(orig_image)
    orig_image, contours, hierarchy = cv2.findContours(orig_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
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
    return numpy.array(contours), box


def get_corners_from_contours(contours):
    epsilon = .005 * cv2.arcLength(contours[0], True)
    poly_approx = cv2.approxPolyDP(contours[0], epsilon, True)
    hull = cv2.convexHull(poly_approx)
    return hull

def sort_corners(corners, center):
    top = []
    bot = []
    print("center:", center)
    for i in range(len(corners)):
        print("corners[i][0][1]:", corners[i][0][1])
        if(corners[i][0][1] > center[1]):
            top.append(corners[i])
        else:
            bot.append(corners[i])
    print("top:", top)
    tl = top[1] if top[0][0][0] > top[1][0][0] else top[0]
    tr = top[0] if top[0][0][0] > top[1][0][0] else top[1]
    bl = bot[1] if bot[0][0][0] > bot[1][0][0] else bot[0]
    br = bot[0] if bot[0][0][0] > bot[1][0][0] else bot[1]
    return numpy.array([tl, tr, br, bl], numpy.float32)

image_to_process = cv2.imread("img/tower_flash.jpg")
# print type(image_to_process)
thresholded_image = threshold_image_for_tape(image_to_process)
cv2.imwrite("img/thresholded.png", thresholded_image)
contours, box = get_contours(thresholded_image)
# contoured_image = cv2.drawContours(image_to_process, contours, -1, (0, 0, 0))
# cv2.imwrite("img/contoured.png", contoured_image)
# total_image = cv2.drawContours(image_to_process, [box], -1, (0, 0, 0))
# cv2.imwrite("img/total_image.png", total_image)
x = get_corners_from_contours(contours)
new_image = numpy.copy(image_to_process)
new_image = cv2.drawContours(new_image, x, -1, (255, 255, 255))
cv2.imwrite("img/new_image.png", new_image)
# print(type(contours))

quad = numpy.zeros((300, 210))
quad_pts = numpy.array([[[0,0]], [[300, 0]], [[300, 210]], [[0, 210]]], numpy.float32)
corners = get_corners_from_contours(contours)

# print(corners)

center = numpy.array([0,0])
for i in range(len(corners)):
    center[0] += corners[i][0][0]
    center[1] += corners[i][0][1]
center[0] /= len(corners)
center[1] /= len(corners)
# print(center)
corners = sort_corners(corners, center)

print("corners:\n", corners)
print("quad_pts:\n", quad_pts)

new_image_to_process = numpy.array(image_to_process, numpy.float32)
quad_pts = cv2.getPerspectiveTransform(corners, quad_pts)
# print(thing)
# print(type(new_image_to_process[0][0][0]))
warped_image = cv2.warpPerspective(new_image_to_process, quad_pts, (300, 210))
# total_image = cv2.drawContours(image_to_process, [corners], -1, (0, 0, 0))
cv2.imwrite("img/warped_image.png", warped_image)
# print(x)
# while 1:
#     cv.ShowImage("Vision", image_to_process)
