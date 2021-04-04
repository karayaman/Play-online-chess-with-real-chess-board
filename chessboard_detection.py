import numpy as np
import cv2
import pyautogui
import mss


class Board_position:
    def __init__(self, minX, minY, maxX, maxY):
        self.minX = minX
        self.minY = minY
        self.maxX = maxX
        self.maxY = maxY


# https://github.com/Stanou01260/chessbot_python/blob/master/code/chessboard_detection.py
def find_chessboard():
    # We do a first classical screenshot to see the screen size:
    screenshot_shape = np.array(pyautogui.screenshot()).shape
    monitor = {'top': 0, 'left': 0, 'width': screenshot_shape[1], 'height': screenshot_shape[0]}
    sct = mss.mss()
    large_image = np.array(np.array(sct.grab(monitor)))
    large_image = cv2.cvtColor(large_image, cv2.COLOR_BGR2RGB)
    method = cv2.TM_SQDIFF_NORMED
    white_image = cv2.imread("white.JPG")
    black_image = cv2.imread("black.JPG")
    result_white = cv2.matchTemplate(white_image, large_image, method)
    result_black = cv2.matchTemplate(black_image, large_image, method)
    we_are_white = True
    result = result_white
    small_image = white_image
    if cv2.minMaxLoc(result_black)[0] < cv2.minMaxLoc(result_white)[0]:  # If black is more accurate:
        result = result_black
        we_are_white = False
        small_image = black_image
    minimum_value, maximum_value, minimum_location, maximum_location = cv2.minMaxLoc(result)

    minX, minY = minimum_location
    maxX = minX + small_image.shape[1]
    maxY = minY + small_image.shape[0]

    position = Board_position(minX, minY, maxX, maxY)
    return position, we_are_white
