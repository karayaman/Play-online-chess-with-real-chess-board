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


# https://github.com/Stanou01260/chessbot_python/blob/master/code/chessboard_detection.py
def auto_find_chessboard():
    # We do a first classical screenshot to see the screen size:
    screenshot_shape = np.array(pyautogui.screenshot()).shape
    monitor = {'top': 0, 'left': 0, 'width': screenshot_shape[1], 'height': screenshot_shape[0]}
    sct = mss.mss()
    img = np.array(np.array(sct.grab(monitor)))
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    is_found, current_chessboard_image, minX, minY, maxX, maxY, test_image = find_chessboard_from_image(img)
    position = Board_position(minX, minY, maxX, maxY)
    return position, is_white_on_bottom(current_chessboard_image)


# https://github.com/Stanou01260/chessbot_python/blob/master/code/chessboard_detection.py
def is_white_on_bottom(current_chessboard_image):
    # This functions compares the mean intensity from two squares that have the same background (opposite corners) but different pieces on it.
    # The one brighter one must be white
    m1 = get_square_image(0, 0, current_chessboard_image).mean()  # Rook on the top left
    m2 = get_square_image(7, 7, current_chessboard_image).mean()  # Rook on the bottom right
    if m1 < m2:  # If the top is darker than the bottom
        return True
    else:
        return False


# https://github.com/Stanou01260/chessbot_python/blob/master/code/chessboard_detection.py
def get_square_image(row, column, board_img):
    height, width = board_img.shape
    minX = int(column * width / 8)
    maxX = int((column + 1) * width / 8)
    minY = int(row * width / 8)
    maxY = int((row + 1) * width / 8)
    square = board_img[minY:maxY, minX:maxX]
    square_without_borders = square[3:-3, 3:-3]
    return square_without_borders


# https://github.com/Stanou01260/chessbot_python/blob/master/code/chessboard_detection.py
def find_chessboard_from_image(img):
    # Converting the image in grayscale:
    image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    kernelH = np.array([[-1, 1]])
    kernelV = np.array([[-1], [1]])

    horizontal_lines = np.absolute(cv2.filter2D(image.astype('float'), -1, kernelV))
    ret, thresh1 = cv2.threshold(horizontal_lines, 30, 255, cv2.THRESH_BINARY)

    kernelSmall = np.ones((1, 3), np.uint8)
    kernelBig = np.ones((1, 50), np.uint8)

    # Remove holes:
    imgH1 = cv2.dilate(thresh1, kernelSmall, iterations=1)
    imgH2 = cv2.erode(imgH1, kernelSmall, iterations=1)

    # Remove small lines
    imgH3 = cv2.erode(imgH2, kernelBig, iterations=1)
    imgH4 = cv2.dilate(imgH3, kernelBig, iterations=1)

    linesStarts = cv2.filter2D(imgH4, -1, kernelH)
    linesEnds = cv2.filter2D(imgH4, -1, -kernelH)

    lines = linesStarts.sum(axis=0) / 255
    lineStart = 0
    nbLineStart = 0
    for idx, val in enumerate(lines):
        if val > 6:
            nbLineStart += 1
            lineStart = idx

    lines = linesEnds.sum(axis=0) / 255
    lineEnd = 0
    nbLineEnd = 0
    for idx, val in enumerate(lines):
        if val > 6:
            nbLineEnd += 1
            lineEnd = idx

    vertical_lines = np.absolute(cv2.filter2D(image.astype('float'), -1, kernelH))
    ret, thresh1 = cv2.threshold(vertical_lines, 30, 255, cv2.THRESH_BINARY)

    kernelSmall = np.ones((3, 1), np.uint8)
    kernelBig = np.ones((50, 1), np.uint8)

    # Remove holes:
    imgV1 = cv2.dilate(thresh1, kernelSmall, iterations=1)
    imgV2 = cv2.erode(imgV1, kernelSmall, iterations=1)

    # Remove small lines
    imgV3 = cv2.erode(imgV2, kernelBig, iterations=1)
    imgV4 = cv2.dilate(imgV3, kernelBig, iterations=1)

    columnStarts = cv2.filter2D(imgV4, -1, kernelV)
    columnEnds = cv2.filter2D(imgV4, -1, -kernelV)

    column = columnStarts.sum(axis=1) / 255
    columnStart = 0
    nbColumnStart = 0
    for idx, val in enumerate(column):
        if val > 6:
            columnStart = idx
            nbColumnStart += 1

    column = columnEnds.sum(axis=1) / 255
    columnEnd = 0
    nbColumnEnd = 0
    for idx, val in enumerate(column):
        if val > 6:
            columnEnd = idx
            nbColumnEnd += 1

    found_board = False
    if (nbLineStart == 1) and (nbLineEnd == 1) and (nbColumnStart == 1) and (nbColumnEnd == 1):
        print("We found a board")
        if abs((columnEnd - columnStart) - (lineEnd - lineStart)) > 3:
            print("However, the board is not a square")
        else:
            print(columnStart, columnEnd, lineStart, lineEnd)
            if (columnEnd - columnStart) % 8 == 1:
                columnEnd -= 1
            if (columnEnd - columnStart) % 8 == 7:
                columnEnd += 1
            if (lineEnd - lineStart) % 8 == 1:
                lineStart += 1
            if (lineEnd - lineStart) % 8 == 7:
                lineStart -= 1
            print(columnStart, columnEnd, lineStart, lineEnd)

            found_board = True
    else:
        print("We did not found the borders of the board")

    if found_board:
        print("Found chessboard sized:", (columnEnd - columnStart), (lineEnd - lineStart), " x:", columnStart,
              columnEnd, " y: ", lineStart, lineEnd)
        dim = (800, 800)  # perform the actual resizing of the chessboard
        print(lineStart, lineEnd, columnStart, columnEnd)
        resizedChessBoard = cv2.resize(image[columnStart:columnEnd, lineStart:lineEnd], dim,
                                       interpolation=cv2.INTER_AREA)
        return True, resizedChessBoard, lineStart, columnStart, lineEnd, columnEnd, resizedChessBoard

    return False, image, 0, 0, 0, 0, image
