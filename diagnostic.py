import cv2
import numpy as np
import pickle

from board_calibration_machine_learning import detect_board
from helper import perspective_transform, predict
import platform
import sys
import tkinter as tk
from tkinter import messagebox

webcam_width = None
webcam_height = None
fps = None
calibrate = False
cap_index = 0
cap_api = cv2.CAP_ANY
platform_name = platform.system()
for argument in sys.argv:
    if argument.startswith("cap="):
        cap_index = int("".join(c for c in argument if c.isdigit()))
        if platform_name == "Darwin":
            cap_api = cv2.CAP_AVFOUNDATION
        elif platform_name == "Linux":
            cap_api = cv2.CAP_V4L2
        else:
            cap_api = cv2.CAP_DSHOW
    elif argument == "calibrate":
        calibrate = True
    elif argument.startswith("width="):
        webcam_width = int(argument[len("width="):])
    elif argument.startswith("height="):
        webcam_height = int(argument[len("height="):])
    elif argument.startswith("fps="):
        fps = int(argument[len("fps="):])

corner_model = cv2.dnn.readNetFromONNX("yolo_corner.onnx")
piece_model = cv2.dnn.readNetFromONNX("cnn_piece.onnx")
color_model = cv2.dnn.readNetFromONNX("cnn_color.onnx")


cap = cv2.VideoCapture(cap_index, cap_api)
if webcam_width is not None:
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, webcam_width)
if webcam_height is not None:
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, webcam_height)
if fps is not None:
    cap.set(cv2.CAP_PROP_FPS, fps)

if not cap.isOpened():
    print("Couldn't open your webcam. Please check your webcam connection.")
    sys.exit(0)


for _ in range(10):
    ret, frame = cap.read()

if calibrate:
    is_detected = False
    for _ in range(100):
        ret, frame = cap.read()
        if not ret:
            print("Error reading frame. Please check your webcam connection.")
            continue
        result = detect_board(frame, corner_model, piece_model, color_model)
        if result:
            pts1, side_view_compensation, rotation_count = result
            is_detected = True
            break

    if not is_detected:
        print("Could not detect the chess board.")
        cap.release()
        sys.exit(0)
else:
    filename = 'constants.bin'
    infile = open(filename, 'rb')
    calibration_data = pickle.load(infile)
    infile.close()
    if calibration_data[0]:
        pts1, side_view_compensation, rotation_count = calibration_data[1]
    else:
        corners, side_view_compensation, rotation_count, roi_mask = calibration_data[1]
        pts1 = np.float32([list(corners[0][0]), list(corners[8][0]), list(corners[0][8]),
                           list(corners[8][8])])


def process(image):
    for row in range(8):
        for column in range(8):
            height, width = image.shape[:2]
            minX = int(column * width / 8)
            maxX = int((column + 1) * width / 8)
            minY = int(row * height / 8)
            maxY = int((row + 1) * height / 8)
            square_image = image[minY:maxY, minX:maxX]
            is_piece = predict(square_image, piece_model)
            if is_piece:
                centerX = int((minX + maxX) / 2)
                centerY = int((minY + maxY) / 2)
                radius = 10
                is_white = predict(square_image, color_model)
                if is_white:
                    cv2.circle(image, (centerX, centerY), radius, (255, 0, 0), 2)
                else:
                    cv2.circle(image, (centerX, centerY), radius, (0, 255, 0), 2)
    return image


root = tk.Tk()
root.withdraw()
messagebox.showinfo("Diagnostic",
                    "The diagnostic process will start. It will mark white pieces with a blue circle and black pieces with a green circle. Press the 'q' key to exit.")

while True:
    ret, frame = cap.read()
    if not ret:
        print("Error reading frame. Please check your webcam connection.")
        continue

    frame = perspective_transform(frame, pts1)
    processed_frame = process(frame.copy())
    
    cv2.imshow('Diagnostic', np.hstack((processed_frame, frame)))

    if cv2.waitKey(1000) & 0xFF == ord('q'):
        break
cap.release()
cv2.destroyAllWindows()
