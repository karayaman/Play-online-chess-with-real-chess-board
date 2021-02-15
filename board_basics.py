# The code is modified from https://github.com/Stanou01260/chessbot_python/blob/master/code/board_basics.py
from skimage.metrics import structural_similarity


class Board_basics:
    def __init__(self, corners):
        self.corners = corners

    def get_square_image(self, row, column,
                         board_img):  # this functions assumes that there are 8*8 squares in the image, and that it is grayscale
        minX, minY = self.corners[row][column]
        maxX, maxY = self.corners[row + 1][column + 1]
        if minX > maxX:
            minX, maxX = maxX, minX
        if minY > maxY:
            minY, maxY = maxY, minY
        square = board_img[minY:maxY, minX:maxX]
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

    def square_image_change_score(self, old_square,
                                  new_square):
        s = structural_similarity(old_square, new_square)
        return -s

    def get_potential_moves(self, old_image, new_image):
        is_white_on_bottom = True
        potential_squares = []
        for row in range(8):
            for column in range(8):
                old_square = self.get_square_image(row, column, old_image)
                new_square = self.get_square_image(row, column, new_image)
                score = self.square_image_change_score(old_square, new_square)
                square_name = self.convert_row_column_to_square_name(row, column, is_white_on_bottom)
                potential_squares.append((score, square_name))

        return potential_squares
