import sys

import numpy as np
import cv2
import pyautogui
import mss
from statistics import median


class Board_position:
    def __init__(self, minX, minY, maxX, maxY):
        self.minX = minX
        self.minY = minY
        self.maxX = maxX
        self.maxY = maxY


def find_chessboard():
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


def auto_find_chessboard():
    screenshot_shape = np.array(pyautogui.screenshot()).shape
    monitor = {'top': 0, 'left': 0, 'width': screenshot_shape[1], 'height': screenshot_shape[0]}
    sct = mss.mss()
    img = np.array(np.array(sct.grab(monitor)))
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    is_found, current_chessboard_image, minX, minY, maxX, maxY, test_image = find_chessboard_from_image(img)
    if not is_found:
        sys.exit(0)
    position = Board_position(minX, minY, maxX, maxY)
    return position, is_white_on_bottom(current_chessboard_image)


def is_white_on_bottom(current_chessboard_image):
    m1 = get_square_image(0, 0, current_chessboard_image).mean()
    m2 = get_square_image(7, 7, current_chessboard_image).mean()
    if m1 < m2:
        return True
    else:
        return False


def get_square_image(row, column, board_img):
    height, width = board_img.shape
    minX = int(column * width / 8)
    maxX = int((column + 1) * width / 8)
    minY = int(row * width / 8)
    maxY = int((row + 1) * width / 8)
    square = board_img[minY:maxY, minX:maxX]
    square_without_borders = square[3:-3, 3:-3]
    return square_without_borders


def prepare(lines, kernel_close, kernel_open):
    ret, lines = cv2.threshold(lines, 30, 255, cv2.THRESH_BINARY)
    lines = cv2.morphologyEx(lines, cv2.MORPH_CLOSE, kernel_close)
    lines = cv2.morphologyEx(lines, cv2.MORPH_OPEN, kernel_open)
    return lines


def prepare_vertical(lines):
    kernel_close = np.ones((3, 1), np.uint8)
    kernel_open = np.ones((50, 1), np.uint8)
    return prepare(lines, kernel_close, kernel_open)


def prepare_horizontal(lines):
    kernel_close = np.ones((1, 3), np.uint8)
    kernel_open = np.ones((1, 50), np.uint8)
    return prepare(lines, kernel_close, kernel_open)


def find_chessboard_from_image(img):
    image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    kernelH = np.array([[-1, 1]])
    kernelV = np.array([[-1], [1]])
    vertical_lines = np.absolute(cv2.filter2D(image.astype('float'), -1, kernelH))
    image_vertical = prepare_vertical(vertical_lines)
    horizontal_lines = np.absolute(cv2.filter2D(image.astype('float'), -1, kernelV))
    image_horizontal = prepare_horizontal(horizontal_lines)
    vertical_lines = cv2.HoughLinesP(image_vertical.astype(np.uint8), 1, np.pi / 180, 100, minLineLength=100,
                                     maxLineGap=10)
    horizontal_lines = cv2.HoughLinesP(image_horizontal.astype(np.uint8), 1, np.pi / 180, 100, minLineLength=100,
                                       maxLineGap=10)
    v_count = [0 for _ in range(len(vertical_lines))]
    h_count = [0 for _ in range(len(horizontal_lines))]
    for i, line in enumerate(vertical_lines):
        x1, y1, x2, y2 = line[0]
        for j, other_line in enumerate(horizontal_lines):
            x3, y3, x4, y4 = other_line[0]
            if ((x3 <= x1 <= x4) or (x4 <= x1 <= x3)) and ((y2 <= y3 <= y1) or (y1 <= y3 <= y2)):
                v_count[i] += 1
                h_count[j] += 1
    v_board = []
    h_board = []
    for i, line in enumerate(vertical_lines):
        if v_count[i] <= 6:
            continue
        v_board.append(line)

    for i, line in enumerate(horizontal_lines):
        if h_count[i] <= 6:
            continue
        h_board.append(line)

    if v_board and h_board:
        y_min = int(median(min(v[0][1], v[0][3]) for v in v_board))
        y_max = int(median(max(v[0][1], v[0][3]) for v in v_board))
        x_min = int(median(min(h[0][0], h[0][2]) for h in h_board))
        x_max = int(median(max(h[0][0], h[0][2]) for h in h_board))
        if abs((x_max - x_min) - (y_max - y_min)) > 3:
            print("Board is not square.")
            return False, image, 0, 0, 0, 0, image
        board = image[y_min:y_max, x_min:x_max]
        dim = (800, 800)
        resized_board = cv2.resize(board, dim,
                                   interpolation=cv2.INTER_AREA)
        #cv2.imwrite("board.jpg", resized_board)
        return True, resized_board, int(x_min), int(y_min), int(x_max), int(y_max), resized_board
    else:
        print("Chess board of online game could not be found.")
        return False, image, 0, 0, 0, 0, image
