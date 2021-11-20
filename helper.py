import cv2
import numpy as np


def perspective_transform(image, pts1):
    dimension = 480
    pts2 = np.float32([[0, 0], [0, dimension], [dimension, 0], [dimension, dimension]])
    M = cv2.getPerspectiveTransform(pts1, pts2)
    dst = cv2.warpPerspective(image, M, (dimension, dimension))
    return dst


def rotateMatrix(matrix):
    size = len(matrix)
    for row in range(size // 2):
        for column in range(row, size - row - 1):
            temp = matrix[row][column]
            matrix[row][column] = matrix[column][size - 1 - row]
            matrix[column][size - 1 - row] = matrix[size - 1 - row][size - 1 - column]
            matrix[size - 1 - row][size - 1 - column] = matrix[size - 1 - column][row]
            matrix[size - 1 - column][row] = temp


def auto_canny(image):
    sigma_upper = 0.2
    sigma_lower = 0.8
    median_intensity = np.median(image)
    lower = int(max(0, (1.0 - sigma_lower) * median_intensity))
    upper = int(min(255, (1.0 + sigma_upper) * median_intensity))
    edged = cv2.Canny(image, lower, upper)
    return edged


def edge_detection(frame):
    kernel = np.ones((3, 3), np.uint8)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    edges = []
    for gray in cv2.split(frame):
        gray = cv2.morphologyEx(gray, cv2.MORPH_CLOSE, kernel)
        gray = clahe.apply(gray)
        gray = cv2.GaussianBlur(gray, (3, 3), 0)
        edge = auto_canny(gray)
        edges.append(edge)
    edges = cv2.bitwise_or(cv2.bitwise_or(edges[0], edges[1]), edges[2])
    kernel2 = np.ones((3, 3), np.uint8)
    edges = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel2)
    return edges

def get_square_image(row, column,
                     board_img):
    height, width = board_img.shape[:2]
    minX = int(column * width / 8)
    maxX = int((column + 1) * width / 8)
    minY = int(row * height / 8)
    maxY = int((row + 1) * height / 8)
    square = board_img[minY:maxY, minX:maxX]
    square_without_borders = square[3:-3, 3:-3]
    return square_without_borders


def contains_piece(square, view):
    height, width = square.shape[:2]
    if view == (0, -1):
        half = square[:, width // 2:]
    elif view == (0, 1):
        half = square[:, :width // 2]
    elif view == (1, 0):
        half = square[height // 2:, :]
    elif view == (-1, 0):
        half = square[:height // 2, :]
    if half.mean() < 1.0:
        return [False]
    elif square.mean() > 15.0:
        return [True]
    elif square.mean() > 6.0:
        return [True, False]
    else:
        if square.mean() > 2.0:
            print("empty " + str(square.mean()))
        return [False]


def detect_state(frame, view, roi_mask):
    edges = edge_detection(frame)
    edges = cv2.bitwise_and(edges, roi_mask)
    # cv2.imwrite("edge.jpg", edges)
    board_image = [[get_square_image(row, column, edges) for column in range(8)] for row
                   in
                   range(8)]
    result = [[contains_piece(board_image[row][column], view) for column in range(8)] for row in
              range(8)]
    return result
