import cv2
import numpy

B_RANGE = (235, 255)
G_RANGE = (235, 255)
R_RANGE = (235, 255)

# cv.NamedWindow("Vision")

def threshold_image_for_tape(orig_image):
    # print orig_image.size
    orig_image = cv2.medianBlur(orig_image, 5)
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

# def canny_edge_detection(orig_image):
def get_contours(orig_image):
    contours, hierarchy = cv2.findContours(orig_image,
                                            cv2.RETR_EXTERNAL,
                                            cv2.CHAIN_APPROX_NONE)
    new_image = orig_image
    cv2.drawContours(new_image, contours, -1, (255, 255, 255))
    return new_image

image_to_process = cv2.imread("backboard_bright_bg.jpg")
# print type(image_to_process)
thresholded_image = threshold_image_for_tape(image_to_process)
cv2.imwrite("thresholded.png", thresholded_image)
contoured_image = get_contours(thresholded_image)
cv2.imwrite("contoured.png", contoured_image)
# while 1:
#     cv.ShowImage("Vision", image_to_process)
