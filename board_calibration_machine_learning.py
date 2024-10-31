import numpy as np
import cv2

from helper import euclidean_distance, perspective_transform, predict


def detect_board(original_image, corner_model, piece_model, color_model):
    [height, width, _] = original_image.shape

    length = max((height, width))
    image = np.zeros((length, length, 3), np.uint8)
    image[0:height, 0:width] = original_image

    scale = length / 640

    blob = cv2.dnn.blobFromImage(image, scalefactor=1 / 255, size=(640, 640), swapRB=True)
    corner_model.setInput(blob)
    outputs = corner_model.forward()
    outputs = np.array([cv2.transpose(outputs[0])])
    rows = outputs.shape[1]

    boxes = []
    scores = []
    class_ids = []

    for i in range(rows):
        classes_scores = outputs[0][i][4:]
        (minScore, maxScore, minClassLoc, (x, maxClassIndex)) = cv2.minMaxLoc(classes_scores)
        if maxScore >= 0.25:
            box = [
                outputs[0][i][0] - (0.5 * outputs[0][i][2]), outputs[0][i][1] - (0.5 * outputs[0][i][3]),
                outputs[0][i][2], outputs[0][i][3]]
            boxes.append(box)
            scores.append(maxScore)
            class_ids.append(maxClassIndex)

    result_boxes = cv2.dnn.NMSBoxes(boxes, scores, 0.25, 0.45, 0.5)

    detections = []
    for i in range(len(result_boxes)):
        index = result_boxes[i]
        box = boxes[index]
        detection = {
            'confidence': scores[index],
            'box': box,
        }
        detections.append(detection)

    if len(detections) < 4:
        return

    detections.sort(key=lambda detection: detection['confidence'], reverse=True)
    detections = detections[:4]

    middle_points = []
    for detection in detections:
        box = detection['box']
        x, y, w, h = box
        middle_x = (x + (w / 2)) * scale
        middle_y = (y + (h / 2)) * scale
        middle_points.append([middle_x, middle_y])

    minX = min(point[0] for point in middle_points)
    minY = min(point[1] for point in middle_points)
    maxX = max(point[0] for point in middle_points)
    maxY = max(point[1] for point in middle_points)

    top_left = min(middle_points, key=lambda point: euclidean_distance(point, [minX, minY]))
    top_right = min(middle_points, key=lambda point: euclidean_distance(point, [maxX, minY]))
    bottom_left = min(middle_points, key=lambda point: euclidean_distance(point, [minX, maxY]))
    bottom_right = min(middle_points, key=lambda point: euclidean_distance(point, [maxX, maxY]))

    first_row = euclidean_distance(top_left, top_right)
    last_row = euclidean_distance(bottom_left, bottom_right)
    first_column = euclidean_distance(top_left, bottom_left)
    last_column = euclidean_distance(top_right, bottom_right)

    if abs(first_row - last_row) >= abs(first_column - last_column):
        if first_row >= last_row:
            side_view_compensation = (1, 0)
        else:
            side_view_compensation = (-1, 0)
    else:
        if first_column >= last_column:
            side_view_compensation = (0, -1)
        else:
            side_view_compensation = (0, 1)

    pts1 = np.float32([top_left, bottom_left, top_right, bottom_right])
    board_image = perspective_transform(original_image, pts1)

    squares_to_check_for_rotation_count = [
        [(0, i) for i in range(7)],
        [(i, 0) for i in range(7)],
        [(7, i) for i in range(7)],
        [(i, 7) for i in range(7)],
    ]

    rotation_count = 0
    score = 0
    for i in range(len(squares_to_check_for_rotation_count)):
        current_score = 0
        for row, column in squares_to_check_for_rotation_count[i]:
            height, width = board_image.shape[:2]
            minX = int(column * width / 8)
            maxX = int((column + 1) * width / 8)
            minY = int(row * height / 8)
            maxY = int((row + 1) * height / 8)
            square_image = board_image[minY:maxY, minX:maxX]
            is_piece = predict(square_image, piece_model)
            if is_piece:
                is_white = predict(square_image, color_model)
                if not is_white:
                    current_score += 1
        if current_score > score:
            score = current_score
            rotation_count = i

    green_color = (0, 255, 0)
    blue_color = (255, 0, 0)
    red_color = (0, 0, 255)

    top_left, top_right, bottom_left, bottom_right = [(int(point[0]), int(point[1])) for point in
                                                      (top_left, top_right, bottom_left, bottom_right)]

    if rotation_count == 0:
        cv2.line(original_image, top_left, top_right, green_color, 5)
        cv2.line(original_image, top_right, bottom_right, red_color, 5)
        cv2.line(original_image, bottom_left, bottom_right, blue_color, 5)
        cv2.line(original_image, top_left, bottom_left, red_color, 5)
    elif rotation_count == 1:
        cv2.line(original_image, top_left, top_right, red_color, 5)
        cv2.line(original_image, top_right, bottom_right, blue_color, 5)
        cv2.line(original_image, bottom_left, bottom_right, red_color, 5)
        cv2.line(original_image, top_left, bottom_left, green_color, 5)
    elif rotation_count == 2:
        cv2.line(original_image, top_left, top_right, blue_color, 5)
        cv2.line(original_image, top_right, bottom_right, red_color, 5)
        cv2.line(original_image, bottom_left, bottom_right, green_color, 5)
        cv2.line(original_image, top_left, bottom_left, red_color, 5)
    elif rotation_count == 3:
        cv2.line(original_image, top_left, top_right, red_color, 5)
        cv2.line(original_image, top_right, bottom_right, green_color, 5)
        cv2.line(original_image, bottom_left, bottom_right, red_color, 5)
        cv2.line(original_image, top_left, bottom_left, blue_color, 5)

    print("Side view compensation" + str(side_view_compensation))
    print("Rotation count " + str(rotation_count))
    return pts1, side_view_compensation, rotation_count
