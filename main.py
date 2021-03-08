import cv2
import pickle
from game import Game
from board_basics import Board_basics
import numpy as np
from helper import perspective_transform
from speech import Speech_thread
from videocapture import Video_capture_thread

MOTION_END_THRESHOLD = 0.01
MOTION_START_THRESHOLD = 1.0

MOVE_END_THRESHOLD = 10.0
MOVE_START_THRESHOLD = 5.0
MOVE_MEAN_DIFFERENCE_THRESHOLD = 0.1

move_fgbg = cv2.createBackgroundSubtractorKNN(dist2Threshold=200)
motion_fgbg = cv2.createBackgroundSubtractorKNN(history=50)

filename = 'constants.bin'
infile = open(filename, 'rb')
corners = pickle.load(infile)
infile.close()

board_basics = Board_basics()

speech_thread = Speech_thread()
speech_thread.daemon = True
speech_thread.start()

game = Game(board_basics, speech_thread)

video_capture_thread = Video_capture_thread()
video_capture_thread.daemon = True
video_capture_thread.start()

pts1 = np.float32([list(corners[0][0]), list(corners[8][0]), list(corners[0][8]),
                   list(corners[8][8])])


def waitUntilMotionCompletes():
    while True:
        frame = video_capture_thread.get_frame()
        frame = perspective_transform(frame, pts1)
        fgmask = motion_fgbg.apply(frame)
        mean = fgmask.mean()
        if mean < MOTION_END_THRESHOLD:
            break


def waitUntilMoveCompletes():
    while True:
        frame = video_capture_thread.get_frame()
        frame = perspective_transform(frame, pts1)
        fgmask = move_fgbg.apply(frame)
        motion_fgbg.apply(frame)
        mean = fgmask.mean()
        if mean < MOVE_END_THRESHOLD:
            break

    while fgmask.mean() > MOVE_START_THRESHOLD:
        frame = video_capture_thread.get_frame()
        frame = perspective_transform(frame, pts1)
        new_fgmask = move_fgbg.apply(frame)
        motion_fgbg.apply(frame)
        if abs(new_fgmask.mean() - fgmask.mean()) <= MOVE_MEAN_DIFFERENCE_THRESHOLD:
            fgmask = new_fgmask
        else:
            break

    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    fgmask = cv2.morphologyEx(fgmask, cv2.MORPH_CLOSE, kernel)

    return frame, fgmask


def initialize_background_subtractors():
    while True:
        frame = video_capture_thread.get_frame()
        frame = perspective_transform(frame, pts1)
        move_fgbg.apply(frame)
        fgmask = motion_fgbg.apply(frame)
        mean = fgmask.mean()
        if mean < MOTION_END_THRESHOLD:
            break


initialize_background_subtractors()

speech_thread.put_text("Game started")

while not game.board.is_game_over():
    frame = video_capture_thread.get_frame()
    frame = perspective_transform(frame, pts1)
    fgmask = motion_fgbg.apply(frame)
    mean = fgmask.mean()
    if mean > MOTION_START_THRESHOLD:
        # cv2.imwrite("prev_frame.jpg", frame)
        waitUntilMotionCompletes()
        frame, fgmask = waitUntilMoveCompletes()
        if game.register_move(fgmask):
            # cv2.imwrite(game.executed_moves[-1] + " frame.jpg", frame)
            # cv2.imwrite(game.executed_moves[-1] + " mask.jpg", fgmask)
            move_fgbg.apply(frame, learningRate=1.0)
            waitUntilMoveCompletes()
        else:
            pass
            # cv2.imwrite("frame_fail.jpg", frame)
            # cv2.imwrite("mask_fail.jpg", fgmask)
    else:
        move_fgbg.apply(frame)
        fgmask = motion_fgbg.apply(frame)
cv2.destroyAllWindows()
