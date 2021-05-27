import cv2
import numpy as np


# https://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_imgproc/py_geometric_transformations/py_geometric_transformations.html
def perspective_transform(image, pts1):
    height, width = image.shape[:2]
    min_dimension = min(height, width)
    if (min_dimension % 8) != 0:
        min_dimension = 480
    pts2 = np.float32([[0, 0], [0, min_dimension], [min_dimension, 0], [min_dimension, min_dimension]])
    M = cv2.getPerspectiveTransform(pts1, pts2)
    dst = cv2.warpPerspective(image, M, (min_dimension, min_dimension))
    return dst


# https://www.geeksforgeeks.org/inplace-rotate-square-matrix-by-90-degrees/
def rotateMatrix(mat):
    N = len(mat)
    # Consider all squares one by one
    for x in range(0, int(N / 2)):

        # Consider elements in group
        # of 4 in current square
        for y in range(x, N - x - 1):
            # store current cell in temp variable
            temp = mat[x][y]

            # move values from right to top
            mat[x][y] = mat[y][N - 1 - x]

            # move values from bottom to right
            mat[y][N - 1 - x] = mat[N - 1 - x][N - 1 - y]

            # move values from left to bottom
            mat[N - 1 - x][N - 1 - y] = mat[N - 1 - y][x]

            # assign temp to left
            mat[N - 1 - y][x] = temp
