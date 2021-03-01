# The code is modified from https://github.com/Stanou01260/chessbot_python/blob/master/code/board_basics.py

import cv2


class Board_basics:
    def __init__(self):
        pass

    def get_square_image(self, row, column,
                         board_img):  # this functions assumes that there are 8*8 squares in the image, and that it is grayscale
        height, width = board_img.shape
        minX = int(column * width / 8)
        maxX = int((column + 1) * width / 8)
        minY = int(row * height / 8)
        maxY = int((row + 1) * height / 8)
        square = board_img[minY:maxY, minX:maxX]

        _, square = cv2.threshold(square, 120, 255,
                                  cv2.THRESH_BINARY)
        return square

    def convert_row_column_to_square_name(self, row, column, is_white_on_bottom):
        if is_white_on_bottom == True:
            number = repr(8 - row)
            letter = str(chr(97 + column))
            return letter + number
        else:
            number = repr(row + 1)
            letter = str(chr(97 + (7 - column)))
            return letter + number

    def convert_square_name_to_row_column(self, square_name):  # Could be optimized
        for row in range(8):
            for column in range(8):
                this_square_name = self.convert_row_column_to_square_name(row, column, True)
                if this_square_name == square_name:
                    return row, column
        return 0, 0

    def get_potential_moves(self, fgmask):
        is_white_on_bottom = True
        potential_squares = []
        for row in range(8):
            for column in range(8):
                mask_square = self.get_square_image(row, column, fgmask)
                score = mask_square.mean()
                if score < 1.0:
                    continue
                square_name = self.convert_row_column_to_square_name(row, column, is_white_on_bottom)
                potential_squares.append((score, square_name))

        potential_squares.sort(reverse=True)
        potential_squares = potential_squares[:4]
        potential_moves = []

        for start_square_score, start_square_name in potential_squares:
            for arrival_square_score, arrival_square_name in potential_squares:
                if start_square_name == arrival_square_name:
                    continue
                total_square_score = start_square_score + arrival_square_score
                potential_moves.append(
                    (total_square_score, start_square_name, arrival_square_name))

        potential_moves.sort(reverse=True)

        return potential_squares, potential_moves
