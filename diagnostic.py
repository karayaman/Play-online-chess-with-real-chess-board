import cv2
import numpy as np
import pickle
from helper import perspective_transform, predict
import platform
import sys
import tkinter as tk
from tkinter import messagebox

filename = 'constants.bin'
infile = open(filename, 'rb')
corners, side_view_compensation, rotation_count, roi_mask = pickle.load(infile)
infile.close()

pts1 = np.float32([list(corners[0][0]), list(corners[8][0]), list(corners[0][8]),
                   list(corners[8][8])])

piece_model = cv2.dnn.readNetFromONNX("cnn_piece.onnx")
color_model = cv2.dnn.readNetFromONNX("cnn_color.onnx")


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

root = tk.Tk()
root.withdraw()
messagebox.showinfo("Diagnostic",
                    "The diagnostic process will start. It will mark white pieces with a blue circle and black pieces with a green circle. Press the 'q' key to exit.")

cap = cv2.VideoCapture(cap_index, cap_api)
if not cap.isOpened():
    print("Couldn't open your webcam. Please check your webcam connection.")
    sys.exit(0)

for _ in range(10):
    ret, frame = cap.read()
    if ret == False:
        print("Error reading frame. Please check your webcam connection.")
        continue

while True:
    ret, frame = cap.read()
    if ret == False:
        print("Error reading frame. Please check your webcam connection.")
        continue

    frame = perspective_transform(frame, pts1)
    processed_frame = process(frame.copy())

    cv2.imshow('Diagnostic', np.hstack((processed_frame, frame)))

    if cv2.waitKey(1000) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()
