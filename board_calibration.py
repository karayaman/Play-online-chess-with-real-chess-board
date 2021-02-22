import cv2
from math import inf
import pickle
from helper import rotateMatrix, perspective_transform
import numpy as np

cap = cv2.VideoCapture(0)
board_dimensions = (7, 7)

for _ in range(10):
    ret, frame = cap.read()

while True:
    ret, frame = cap.read()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    retval, corners = cv2.findChessboardCorners(gray, patternSize=board_dimensions)
    if retval:
        if corners[0][0][0] > corners[-1][0][0]:  # corners returned in reverse order
            corners = corners[::-1]
        minX, maxX, minY, maxY = inf, -inf, inf, -inf
        augmented_corners = []
        row = []
        for i in range(6):
            corner1 = corners[i]
            corner2 = corners[i + 8]
            x = corner1[0][0] + (corner1[0][0] - corner2[0][0])
            y = corner1[0][1] + (corner1[0][1] - corner2[0][1])
            row.append((x, y))

        for i in range(4, 7):
            corner1 = corners[i]
            corner2 = corners[i + 6]
            x = corner1[0][0] + (corner1[0][0] - corner2[0][0])
            y = corner1[0][1] + (corner1[0][1] - corner2[0][1])
            row.append((x, y))

        augmented_corners.append(row)

        for i in range(7):
            row = []
            corner1 = corners[i * 7]
            corner2 = corners[i * 7 + 1]
            x = corner1[0][0] + (corner1[0][0] - corner2[0][0])
            y = corner1[0][1] + (corner1[0][1] - corner2[0][1])
            row.append((x, y))

            for corner in corners[i * 7:(i + 1) * 7]:
                x = corner[0][0]
                y = corner[0][1]
                row.append((x, y))

            corner1 = corners[i * 7 + 6]
            corner2 = corners[i * 7 + 5]
            x = corner1[0][0] + (corner1[0][0] - corner2[0][0])
            y = corner1[0][1] + (corner1[0][1] - corner2[0][1])
            row.append((x, y))
            augmented_corners.append(row)

        row = []
        for i in range(6):
            corner1 = corners[42 + i]
            corner2 = corners[42 + i - 6]
            x = corner1[0][0] + (corner1[0][0] - corner2[0][0])
            y = corner1[0][1] + (corner1[0][1] - corner2[0][1])
            row.append((x, y))

        for i in range(4, 7):
            corner1 = corners[42 + i]
            corner2 = corners[42 + i - 8]
            x = corner1[0][0] + (corner1[0][0] - corner2[0][0])
            y = corner1[0][1] + (corner1[0][1] - corner2[0][1])
            row.append((x, y))

        augmented_corners.append(row)
        print(augmented_corners)

        while augmented_corners[0][0][0] > augmented_corners[8][8][0] or augmented_corners[0][0][1] > \
                augmented_corners[8][8][1]:
            rotateMatrix(augmented_corners)

        print(augmented_corners)
        pts1 = np.float32([list(augmented_corners[0][0]), list(augmented_corners[8][0]), list(augmented_corners[0][8]),
                           list(augmented_corners[8][8])])

        empty_board = perspective_transform(gray, pts1)
        cv2.imwrite("empty_board.jpg", empty_board)

        for i in range(len(augmented_corners)):
            for j in range(len(augmented_corners[i])):
                frame = cv2.putText(frame, str(i) + "," + str(j), augmented_corners[i][j], cv2.FONT_HERSHEY_SIMPLEX,
                                    0.5, (255, 0, 0), 1, cv2.LINE_AA)
        cv2.imshow('frame', frame)
        cv2.waitKey(0)
        break

    cv2.imshow('frame', frame)
    if cv2.waitKey(3) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
print("Constants " + str(augmented_corners))
filename = 'constants.bin'
outfile = open(filename, 'wb')
pickle.dump(augmented_corners, outfile)
outfile.close()
