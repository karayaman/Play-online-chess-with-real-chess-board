from math import pi

import cv2
import numpy as np


# https://github.com/youyexie/Chess-Piece-Recognition-using-Oriented-Chamfer-Matching-with-a-Comparison-to-CNN
class Classifier:
    def __init__(self, game_state):
        self.dim = (480, 480)
        self.img = cv2.resize(
            game_state.previous_chessboard_image, self.dim, interpolation=cv2.INTER_AREA
        )
        self.img_x, self.img_y = self.unit_gradients(self.img)
        self.edges = cv2.Canny(self.img, 100, 200)
        self.inverted_edges = cv2.bitwise_not(self.edges)
        self.dist = cv2.distanceTransform(self.inverted_edges, cv2.DIST_L2, 3)
        self.dist_board = [
            [self.get_square_image(row, column, self.dist) for column in range(8)]
            for row in range(8)
        ]
        self.edge_board = [
            [self.get_square_image(row, column, self.edges) for column in range(8)]
            for row in range(8)
        ]
        self.gradient_x = [
            [self.get_square_image(row, column, self.img_x) for column in range(8)]
            for row in range(8)
        ]
        self.gradient_y = [
            [self.get_square_image(row, column, self.img_y) for column in range(8)]
            for row in range(8)
        ]

        def intensity(x):
            return self.edge_board[x[0]][x[1]].mean()

        pawn_templates = [
            max([(1, i) for i in range(8)], key=intensity),
            max([(6, i) for i in range(8)], key=intensity),
        ]

        self.templates = [pawn_templates] + [[(0, i), (7, i)] for i in range(5)]

        if intensity((0, 6)) > intensity((0, 1)):
            self.templates[2][0] = (0, 6)

        if intensity((7, 6)) > intensity((7, 1)):
            self.templates[2][1] = (7, 6)

        self.piece_symbol = [".", "p", "r", "n", "b", "q", "k"]
        if game_state.we_play_white is False:
            self.piece_symbol[-1], self.piece_symbol[-2] = (
                self.piece_symbol[-2],
                self.piece_symbol[-1],
            )

    def classify(self, img):
        img = cv2.resize(img, self.dim, interpolation=cv2.INTER_AREA)

        img_x, img_y = self.unit_gradients(img)
        edges = cv2.Canny(img, 100, 200)
        inverted_edges = cv2.bitwise_not(edges)
        dist = cv2.distanceTransform(inverted_edges, cv2.DIST_L2, 3)
        dist_board = [
            [self.get_square_image(row, column, dist) for column in range(8)]
            for row in range(8)
        ]
        gradient_x = [
            [self.get_square_image(row, column, img_x) for column in range(8)]
            for row in range(8)
        ]
        gradient_y = [
            [self.get_square_image(row, column, img_y) for column in range(8)]
            for row in range(8)
        ]

        result = []
        for row in range(8):
            row_result = []
            for col in range(8):
                d = dist_board[row][col]
                template_scores = []
                for piece in self.templates:
                    piece_scores = []
                    for tr, tc in piece:
                        t = self.edge_board[tr][tc]
                        e = t / 255.0
                        e_c = e.sum()
                        r_d = np.multiply(d, e).sum() / e_c

                        dp = np.multiply(
                            self.gradient_x[tr][tc], gradient_x[row][col]
                        ) + np.multiply(self.gradient_y[tr][tc], gradient_y[row][col])
                        dp = np.abs(dp)
                        dp[dp > 1.0] = 1.0
                        angle_difference = np.arccos(dp)
                        r_o = np.multiply(angle_difference, e).sum() / (e_c * (pi / 2))
                        piece_scores.append(r_d * 0.5 + r_o * 0.5)
                    template_scores.append(min(piece_scores))
                min_score = float("inf")
                min_index = -1
                for i, score in enumerate(template_scores):
                    if min_score > score:
                        min_score = score
                        min_index = i
                if min_score < 2.0:
                    row_result.append(self.piece_symbol[min_index + 1])
                else:
                    row_result.append(self.piece_symbol[0])

            result.append(row_result)
        return result

    def unit_gradients(self, gray):
        sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=5)
        sobely = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=5)
        mag, _ = cv2.cartToPolar(sobelx, sobely)
        mag[mag == 0] = 1
        unit_x = sobelx / mag
        unit_y = sobely / mag
        return unit_x, unit_y

    def get_square_image(self, row, column, board_img):
        height, width = board_img.shape[:2]
        minX = int(column * width / 8)
        maxX = int((column + 1) * width / 8)
        minY = int(row * height / 8)
        maxY = int((row + 1) * height / 8)
        square = board_img[minY:maxY, minX:maxX]
        square_without_borders = square[3:-3, 3:-3]
        return square_without_borders
