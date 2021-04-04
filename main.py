import cv2
import pickle
from game import Game
from board_basics import Board_basics
import numpy as np
from helper import perspective_transform
from speech import Speech_thread
from videocapture import Video_capture_thread

MOTION_END_THRESHOLD = 0.5
MOTION_START_THRESHOLD = 1.0
MOVE_END_THRESHOLD = 100.0
HISTORY = 100
MAX_MOVE_MEAN = 50

move_fgbg = cv2.createBackgroundSubtractorKNN()
motion_fgbg = cv2.createBackgroundSubtractorKNN(history=HISTORY)

filename = 'constants.bin'
infile = open(filename, 'rb')
corners, side_view_compensation = pickle.load(infile)
infile.close()

board_basics = Board_basics(side_view_compensation)

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
        ret, fgmask = cv2.threshold(fgmask, 250, 255, cv2.THRESH_BINARY)
        mean = fgmask.mean()
        if mean < MOTION_END_THRESHOLD:
            break


def stabilize_background_subtractors():
    best_mean = float("inf")
    while True:
        frame = video_capture_thread.get_frame()
        frame = perspective_transform(frame, pts1)
        move_fgbg.apply(frame)
        fgmask = motion_fgbg.apply(frame)
        ret, fgmask = cv2.threshold(fgmask, 250, 255, cv2.THRESH_BINARY)
        mean = fgmask.mean()
        if mean >= best_mean:
            break
        best_mean = mean

    best_mean = float("inf")
    while True:
        frame = video_capture_thread.get_frame()
        frame = perspective_transform(frame, pts1)
        fgmask = move_fgbg.apply(frame, learningRate=0.1)
        ret, fgmask = cv2.threshold(fgmask, 250, 255, cv2.THRESH_BINARY)
        motion_fgbg.apply(frame)
        mean = fgmask.mean()
        if mean >= best_mean:
            break
        best_mean = mean


stabilize_background_subtractors()
speech_thread.put_text("Game started")
while not game.board.is_game_over():
    frame = video_capture_thread.get_frame()
    frame = perspective_transform(frame, pts1)
    fgmask = motion_fgbg.apply(frame)
    ret, fgmask = cv2.threshold(fgmask, 250, 255, cv2.THRESH_BINARY)
    mean = fgmask.mean()
    if mean > MOTION_START_THRESHOLD:
        waitUntilMotionCompletes()
        frame = video_capture_thread.get_frame()
        frame = perspective_transform(frame, pts1)
        fgmask = move_fgbg.apply(frame, learningRate=0.0)
        ret, fgmask = cv2.threshold(fgmask, 250, 255, cv2.THRESH_BINARY)
        if fgmask.mean() >= MAX_MOVE_MEAN:
            fgmask = np.zeros(fgmask.shape, dtype=np.uint8)
        motion_fgbg.apply(frame)
        move_fgbg.apply(frame, learningRate=1.0)
        stabilize_background_subtractors()
        if game.register_move(fgmask):
            pass
            # cv2.imwrite(game.executed_moves[-1] + " frame.jpg", frame)
            # cv2.imwrite(game.executed_moves[-1] + " mask.jpg", fgmask)
        else:
            pass
            # cv2.imwrite("frame_fail.jpg", frame)
            # cv2.imwrite("mask_fail.jpg", fgmask)
    else:
        move_fgbg.apply(frame)
cv2.destroyAllWindows()
