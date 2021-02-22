import cv2
import pickle
import pyttsx3
from game import Game
from board_basics import Board_basics
import numpy as np
from helper import perspective_transform

MOTION_END_THRESHOLD = 0.01
MOTION_START_THRESHOLD = 0.5

move_fgbg = cv2.createBackgroundSubtractorKNN(history=10, detectShadows=False)
motion_fgbg = cv2.createBackgroundSubtractorKNN(history=50, detectShadows=False)

engine = pyttsx3.init()

filename = 'constants.bin'
infile = open(filename, 'rb')
corners = pickle.load(infile)
infile.close()

board_basics = Board_basics()
game = Game(board_basics, engine)

cap = cv2.VideoCapture(0)

pts1 = np.float32([list(corners[0][0]), list(corners[8][0]), list(corners[0][8]),
                   list(corners[8][8])])


def waitUntilMotionCompletes():
    while True:
        ret, frame = cap.read()
        frame = perspective_transform(frame, pts1)
        fgmask = motion_fgbg.apply(frame)
        mean = fgmask.mean()
        # print(mean)
        if mean < MOTION_END_THRESHOLD:
            break


def initialize_background_subtractors():
    while True:
        ret, frame = cap.read()
        frame = perspective_transform(frame, pts1)
        move_fgbg.apply(frame)
        fgmask = motion_fgbg.apply(frame)
        mean = fgmask.mean()
        # print(mean)
        if mean < MOTION_END_THRESHOLD:
            break


initialize_background_subtractors()

engine.say("Game started")
engine.runAndWait()

while True:
    ret, frame = cap.read()
    frame = perspective_transform(frame, pts1)
    fgmask = motion_fgbg.apply(frame)
    mean = fgmask.mean()
    # print(fgmask.mean())
    if mean > MOTION_START_THRESHOLD:
        cv2.imwrite("prev_frame.jpg", frame)
        # print("Motion detected")
        waitUntilMotionCompletes()

        ret, frame = cap.read()
        frame = perspective_transform(frame, pts1)
        fgmask = move_fgbg.apply(frame)
        motion_fgbg.apply(frame)

        if game.register_move(fgmask):
            cv2.imwrite("frame.jpg", frame)
            cv2.imwrite("mask.jpg", fgmask)
        else:
            cv2.imwrite("frame_fail.jpg", frame)
            cv2.imwrite("mask_fail.jpg", fgmask)

    move_fgbg.apply(frame)
    fgmask = motion_fgbg.apply(frame)
    # print(fgmask.mean())

cap.release()
cv2.destroyAllWindows()
