import cv2
import numpy as np


def grayscale(image):
    # get grayscale image
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)


def remove_noise(image):
    # noise removal
    return cv2.medianBlur(image, 1)


def gaussian_blur(image, blur_amount):
    # Gaussian blur
    return cv2.GaussianBlur(image, (blur_amount, blur_amount), 0)


def thresholding(image):
    # thresholding
    return cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]


def dilate(image):
    # dilation
    kernel = np.ones((2, 2), np.uint8)
    return cv2.dilate(image, kernel, iterations=1)


def erode(image):
    # erosion
    kernel = np.ones((2, 2), np.uint8)
    return cv2.erode(image, kernel, iterations=1)


def opening(image):
    # opening - erosion followed by dilation
    kernel = np.ones((2, 2), np.uint8)
    return cv2.morphologyEx(image, cv2.MORPH_OPEN, kernel)


def canny(image):
    # canny edge detection
    return cv2.Canny(image, 100, 200)


def deskew(image):
    # skew correction
    coords = np.column_stack(np.where(image > 0))
    angle = cv2.minAreaRect(coords)[-1]
    if angle < -45:
        angle = -(90 + angle)
    else:
        angle = -angle
    (h, w) = image.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv2.warpAffine(
        image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE
    )
    return rotated


def match_template(image, template):
    # template matching
    return cv2.matchTemplate(image, template, cv2.TM_CCOEFF_NORMED)
