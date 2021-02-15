import cv2

import pickle
import pyttsx3
from game import Game
from board_basics import Board_basics
from collections import deque

engine = pyttsx3.init()

filename = 'constants.bin'
infile = open(filename, 'rb')
corners = pickle.load(infile)
infile.close()

flatten_corners = [point for row in corners for point in row]
minX = min(point[0] for point in flatten_corners)
minY = min(point[1] for point in flatten_corners)
maxX = max(point[0] for point in flatten_corners)
maxY = max(point[1] for point in flatten_corners)

minX = int(minX)
minY = int(minY)
maxX = int(maxX + 1)
maxY = int(maxY + 1)

for i in range(9):
    for j in range(9):
        x, y = corners[i][j]
        x -= minX
        y -= minY
        x = int(x)
        y = int(y)
        corners[i][j] = (x, y)

board_basics = Board_basics(corners)
game = Game(board_basics, engine)

cap = cv2.VideoCapture(0)

QUEUE_MAX_LENGTH = 10
prev_gray_queue = deque(maxlen=QUEUE_MAX_LENGTH)
prev_gray_blurred_queue = deque(maxlen=QUEUE_MAX_LENGTH)

for _ in range(QUEUE_MAX_LENGTH):
    ret, frame = cap.read()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = gray[minY:maxY, minX:maxX]
    gray_blurred = cv2.GaussianBlur(gray, (25, 25), 0)
    prev_gray_queue.append(gray)
    prev_gray_blurred_queue.append(gray_blurred)


def waitUntilMotionCompletes(prev_gray_blurred):
    consecutive_no_contours = 0
    contour_count = 0
    while consecutive_no_contours < 50:
        ret, frame = cap.read()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = gray[minY:maxY, minX:maxX]

        gray_blurred = cv2.GaussianBlur(gray, (25, 25), 0)

        delta = cv2.absdiff(prev_gray_blurred, gray_blurred)
        threshold = cv2.threshold(delta, 35, 255, cv2.THRESH_BINARY)[1]
        (contours, _) = cv2.findContours(threshold, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if contours:
            prev_gray_blurred = gray_blurred
            consecutive_no_contours = 0
            contour_count += 1
        else:
            consecutive_no_contours += 1
    print("Contour count " + str(contour_count))


while True:
    # Motion detection based on the link https://towardsdatascience.com/build-a-motion-triggered-alarm-in-5-minutes-342fbe3d5396
    ret, frame = cap.read()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = gray[minY:maxY, minX:maxX]

    gray_blurred = cv2.GaussianBlur(gray, (25, 25), 0)

    delta = cv2.absdiff(prev_gray_blurred_queue[-1], gray_blurred)
    threshold = cv2.threshold(delta, 35, 255, cv2.THRESH_BINARY)[1]
    (contours, _) = cv2.findContours(threshold, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if contours:
        print("Motion detected")
        engine.say("Motion")
        engine.runAndWait()
        waitUntilMotionCompletes(gray_blurred)

        ret, frame = cap.read()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = gray[minY:maxY, minX:maxX]

        gray_blurred = cv2.GaussianBlur(gray, (25, 25), 0)

        game.register_move(prev_gray_queue[0], gray)

    prev_gray_queue.append(gray)
    prev_gray_blurred_queue.append(gray_blurred)

cap.release()
cv2.destroyAllWindows()
