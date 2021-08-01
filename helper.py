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
