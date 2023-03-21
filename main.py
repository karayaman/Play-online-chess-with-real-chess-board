from collections import deque
import pathlib as pl
import pickle
import platform
import time
import sys

import cv2
import numpy as np

from board_basics import BoardBasics
from game import Game
from helper import perspective_transform
import languages
from speech import SpeechThread
from videocapture import VideoCaptureThread

use_template = True
make_opponent = False
drag_drop = False
comment_me = False
comment_opponent = False
start_delay = 5  # seconds
cap_index = 4
cap_api = cv2.CAP_ANY
voice_index = 0
language = languages.English()
token = ""
for argument in sys.argv:
    if argument == "no-template":
        use_template = False
    elif argument == "make-opponent":
        make_opponent = True
    elif argument == "comment-me":
        comment_me = True
    elif argument == "comment-opponent":
        comment_opponent = True
    elif argument.startswith("delay="):
        start_delay = int("".join(c for c in argument if c.isdigit()))
    elif argument == "drag":
        drag_drop = True
    elif argument.startswith("cap="):
        cap_index = int("".join(c for c in argument if c.isdigit()))
        platform_name = platform.system()
        if platform_name == "Darwin":
            cap_api = cv2.CAP_AVFOUNDATION
        elif platform_name == "Linux":
            cap_api = cv2.CAP_V4L2
        else:
            cap_api = cv2.CAP_DSHOW
    elif argument.startswith("voice="):
        voice_index = int("".join(c for c in argument if c.isdigit()))
    elif argument.startswith("lang="):
        if "German" in argument:
            language = languages.German()
        elif "Russian" in argument:
            language = languages.Russian()
        elif "Turkish" in argument:
            language = languages.Turkish()
        elif "Italian" in argument:
            language = languages.Italian()
        elif "French" in argument:
            language = languages.French()
    elif argument.startswith("token="):
        token = argument[len("token=") :].strip()
MOTION_START_THRESHOLD = 1.0
HISTORY = 100
MAX_MOVE_MEAN = 50
COUNTER_MAX_VALUE = 3

move_fgbg = cv2.createBackgroundSubtractorKNN()
motion_fgbg = cv2.createBackgroundSubtractorKNN(history=HISTORY)

with pl.Path("constants.bin").open("rb") as infile:
    corners, side_view_compensation, rotation_count, roi_mask = pickle.load(infile)
board_basics = BoardBasics(side_view_compensation, rotation_count)

speech_thread = SpeechThread()
speech_thread.daemon = True
speech_thread.index = voice_index
speech_thread.start()

game = Game(
    board_basics,
    speech_thread,
    use_template,
    make_opponent,
    start_delay,
    comment_me,
    comment_opponent,
    drag_drop,
    language,
    token,
    roi_mask,
)

video_capture_thread = VideoCaptureThread()
video_capture_thread.daemon = True
video_capture_thread.capture = cv2.VideoCapture(cap_index, cap_api)
video_capture_thread.start()

pts1 = np.float32(
    [list(corners[0][0]), list(corners[8][0]), list(corners[0][8]), list(corners[8][8])]
)


def waitUntilMotionCompletes():
    counter = 0
    while counter < COUNTER_MAX_VALUE:
        frame = video_capture_thread.get_frame()
        frame = perspective_transform(frame, pts1)
        fgmask = motion_fgbg.apply(frame)
        _, fgmask = cv2.threshold(fgmask, 250, 255, cv2.THRESH_BINARY)
        mean = fgmask.mean()
        if mean < MOTION_START_THRESHOLD:
            counter += 1
        else:
            counter = 0


def stabilize_background_subtractors():
    best_mean = float("inf")
    counter = 0
    while counter < COUNTER_MAX_VALUE:
        frame = video_capture_thread.get_frame()
        frame = perspective_transform(frame, pts1)
        move_fgbg.apply(frame)
        fgmask = motion_fgbg.apply(frame, learningRate=0.1)
        _, fgmask = cv2.threshold(fgmask, 250, 255, cv2.THRESH_BINARY)
        mean = fgmask.mean()
        if mean >= best_mean:
            counter += 1
        else:
            best_mean = mean
            counter = 0

    best_mean = float("inf")
    counter = 0
    while counter < COUNTER_MAX_VALUE:
        frame = video_capture_thread.get_frame()
        frame = perspective_transform(frame, pts1)
        fgmask = move_fgbg.apply(frame, learningRate=0.1)
        _, fgmask = cv2.threshold(fgmask, 250, 255, cv2.THRESH_BINARY)
        motion_fgbg.apply(frame)
        mean = fgmask.mean()
        if mean >= best_mean:
            counter += 1
        else:
            best_mean = mean
            counter = 0

    return frame


previous_frame = stabilize_background_subtractors()
previous_frame_queue = deque(maxlen=10)
previous_frame_queue.append(previous_frame)
speech_thread.put_text(language.game_started)
game.commentator.start()
while game.commentator.game_state.variant == "wait":
    time.sleep(0.1)
if game.commentator.game_state.variant == "standard":
    board_basics.initialize_ssim(previous_frame)
    game.initialize_hog(previous_frame)
else:
    board_basics.load_ssim()
    game.load_hog()
while not game.board.is_game_over() and not game.commentator.game_state.resign_or_draw:
    sys.stdout.flush()
    frame = video_capture_thread.get_frame()
    frame = perspective_transform(frame, pts1)
    fgmask = motion_fgbg.apply(frame)
    ret, fgmask = cv2.threshold(fgmask, 250, 255, cv2.THRESH_BINARY)
    kernel = np.ones((11, 11), np.uint8)
    fgmask = cv2.erode(fgmask, kernel, iterations=1)
    mean = fgmask.mean()
    if mean > MOTION_START_THRESHOLD:
        waitUntilMotionCompletes()
        frame = video_capture_thread.get_frame()
        frame = perspective_transform(frame, pts1)
        fgmask = move_fgbg.apply(frame, learningRate=0.0)
        if fgmask.mean() >= 10.0:
            ret, fgmask = cv2.threshold(fgmask, 250, 255, cv2.THRESH_BINARY)
        # print("Move mean " + str(fgmask.mean()))
        if fgmask.mean() >= MAX_MOVE_MEAN:
            fgmask = np.zeros(fgmask.shape, dtype=np.uint8)
        motion_fgbg.apply(frame)
        move_fgbg.apply(frame, learningRate=1.0)
        last_frame = stabilize_background_subtractors()
        previous_frame = previous_frame_queue[0]

        if game.is_light_change(last_frame) is False and game.register_move(
            fgmask, previous_frame, last_frame
        ):
            pass
        else:
            pass
        previous_frame_queue = deque(maxlen=10)
        previous_frame_queue.append(last_frame)
    else:
        move_fgbg.apply(frame)
        previous_frame_queue.append(frame)
cv2.destroyAllWindows()
time.sleep(2)
