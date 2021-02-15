# The code is modified from https://github.com/Stanou01260/chessbot_python/blob/master/code/chessboard_detection.py

import numpy as np
import cv2  # OpenCV
import pyautogui  # Used to take screenshots and move the mouse
import mss  # Used to get superfast screenshots


class Board_position:
    def __init__(self, minX, minY, maxX, maxY):
        self.minX = minX
        self.minY = minY
        self.maxX = maxX
        self.maxY = maxY

    def print_custom(self):
        return ("from " + str(self.minX) + "," + str(self.minY) + " to " + str(self.maxX) + "," + str(self.maxY))


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


def get_chessboard(game_state):
    position = game_state.board_position_on_screen
    monitor = {'top': 0, 'left': 0, 'width': position.maxX + 10, 'height': position.maxY + 10}
    img = np.array(np.array(game_state.sct.grab(monitor)))
    # Converting the image in grayscale:
    image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    dim = (800, 800)  # perform the actual resizing of the chessboard
    resizedChessBoard = cv2.resize(image[position.minY:position.maxY, position.minX:position.maxX], dim,
                                   interpolation=cv2.INTER_AREA)
    return resizedChessBoard


def read_black_chessboard():
    img = cv2.imread('black.JPG')
    # Converting the image in grayscale:
    image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    dim = (800, 800)  # perform the actual resizing of the chessboard
    resizedChessBoard = cv2.resize(image, dim,
                                   interpolation=cv2.INTER_AREA)
    return resizedChessBoard
