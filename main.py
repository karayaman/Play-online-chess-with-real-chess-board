import time
import cv2
import pickle
import numpy as np
import sys
from collections import deque
import platform
from board_calibration_machine_learning import detect_board
from game import Game
from board_basics import Board_basics
from helper import perspective_transform
from speech import Speech_thread
from videocapture import Video_capture_thread
from languages import *

webcam_width = None
webcam_height = None
fps = None
use_template = True
make_opponent = False
drag_drop = False
comment_me = False
comment_opponent = False
calibrate = False
start_delay = 5  # seconds
cap_index = 0
cap_api = cv2.CAP_ANY
voice_index = 0
language = English()
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
            language = German()
        elif "Russian" in argument:
            language = Russian()
        elif "Turkish" in argument:
            language = Turkish()
        elif "Italian" in argument:
            language = Italian()
        elif "French" in argument:
            language = French()
    elif argument.startswith("token="):
        token = argument[len("token="):].strip()
    elif argument == "calibrate":
        calibrate = True
    elif argument.startswith("width="):
        webcam_width = int(argument[len("width="):])
    elif argument.startswith("height="):
        webcam_height = int(argument[len("height="):])
    elif argument.startswith("fps="):
        fps = int(argument[len("fps="):])
MOTION_START_THRESHOLD = 1.0
HISTORY = 100
MAX_MOVE_MEAN = 50
COUNTER_MAX_VALUE = 3

move_fgbg = cv2.createBackgroundSubtractorKNN()
motion_fgbg = cv2.createBackgroundSubtractorKNN(history=HISTORY)

video_capture_thread = Video_capture_thread()
video_capture_thread.daemon = True
video_capture_thread.capture = cv2.VideoCapture(cap_index, cap_api)
if webcam_width is not None:
    video_capture_thread.capture.set(cv2.CAP_PROP_FRAME_WIDTH, webcam_width)
if webcam_height is not None:
    video_capture_thread.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, webcam_height)
if fps is not None:
    video_capture_thread.capture.set(cv2.CAP_PROP_FPS, fps)
if calibrate:
    corner_model = cv2.dnn.readNetFromONNX("yolo_corner.onnx")
    piece_model = cv2.dnn.readNetFromONNX("cnn_piece.onnx")
    color_model = cv2.dnn.readNetFromONNX("cnn_color.onnx")
    for _ in range(10):
        ret, frame = video_capture_thread.capture.read()
        if ret == False:
            print("Error reading frame. Please check your webcam connection.")
            continue
    is_detected = False
    for _ in range(100):
        ret, frame = video_capture_thread.capture.read()
        if ret == False:
            print("Error reading frame. Please check your webcam connection.")
            continue
        result = detect_board(frame, corner_model, piece_model, color_model)
        if result:
            pts1, side_view_compensation, rotation_count = result
            roi_mask = None
            is_detected = True
            break
    if not is_detected:
        print("Could not detect the chess board.")
        video_capture_thread.capture.release()
        sys.exit(0)
else:
    filename = 'constants.bin'
    infile = open(filename, 'rb')
    calibration_data = pickle.load(infile)
    infile.close()
    if calibration_data[0]:
        pts1, side_view_compensation, rotation_count = calibration_data[1]
        roi_mask = None
    else:
        corners, side_view_compensation, rotation_count, roi_mask = calibration_data[1]
        pts1 = np.float32([list(corners[0][0]), list(corners[8][0]), list(corners[0][8]),
                           list(corners[8][8])])
video_capture_thread.start()
board_basics = Board_basics(side_view_compensation, rotation_count)

speech_thread = Speech_thread()
speech_thread.daemon = True
speech_thread.index = voice_index
speech_thread.start()

game = Game(board_basics, speech_thread, use_template, make_opponent, start_delay, comment_me, comment_opponent,
            drag_drop, language, token, roi_mask)

def waitUntilMotionCompletes():
    counter = 0
    while counter < COUNTER_MAX_VALUE:
        frame = video_capture_thread.get_frame()
        frame = perspective_transform(frame, pts1)
        fgmask = motion_fgbg.apply(frame)
        ret, fgmask = cv2.threshold(fgmask, 250, 255, cv2.THRESH_BINARY)
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
        ret, fgmask = cv2.threshold(fgmask, 250, 255, cv2.THRESH_BINARY)
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
        ret, fgmask = cv2.threshold(fgmask, 250, 255, cv2.THRESH_BINARY)
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
while game.commentator.game_state.variant == 'wait':
    time.sleep(0.1)
if game.commentator.game_state.variant == 'standard':
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
        # cv2.imwrite("motion.jpg", fgmask)
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

        if (game.is_light_change(last_frame) == False) and game.register_move(fgmask, previous_frame, last_frame):
            pass
            # cv2.imwrite(game.executed_moves[-1] + " frame.jpg", last_frame)
            # cv2.imwrite(game.executed_moves[-1] + " mask.jpg", fgmask)
            # cv2.imwrite(game.executed_moves[-1] + " background.jpg", previous_frame)
        else:
            pass
            # import uuid
            # id = str(uuid.uuid1())
            # cv2.imwrite(id+"frame_fail.jpg", last_frame)
            # cv2.imwrite(id+"mask_fail.jpg", fgmask)
            # cv2.imwrite(id+"background_fail.jpg", previous_frame)
        previous_frame_queue = deque(maxlen=10)
        previous_frame_queue.append(last_frame)
    else:
        move_fgbg.apply(frame)
        previous_frame_queue.append(frame)
cv2.destroyAllWindows()
time.sleep(2)
