import cv2
import numpy as np


# https://stackoverflow.com/questions/62441106/illumination-normalization-using-python-opencv
def normalize_illumination(image):
    hh, ww = image.shape[:2]
    max_dimension = max(hh, ww)

    # illumination normalize
    ycrcb = cv2.cvtColor(image, cv2.COLOR_BGR2YCrCb)

    # separate channels
    y, cr, cb = cv2.split(ycrcb)

    # get background which paper says (gaussian blur using standard deviation 5 pixel for 300x300 size image)
    # account for size of input vs 300
    sigma = int(5 * max_dimension / 300)

    gaussian = cv2.GaussianBlur(y, (0, 0), sigma, sigma)

    # subtract background from Y channel
    y = (y - gaussian + 100)

    # merge channels back
    ycrcb = cv2.merge([y, cr, cb])

    # convert to BGR
    output = cv2.cvtColor(ycrcb, cv2.COLOR_YCrCb2BGR)

    return output


# https://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_imgproc/py_geometric_transformations/py_geometric_transformations.html
def perspective_transform(image, pts1):
    pts2 = np.float32([[0, 0], [0, 640], [640, 0], [640, 640]])

    M = cv2.getPerspectiveTransform(pts1, pts2)

    dst = cv2.warpPerspective(image, M, (640, 640))

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
