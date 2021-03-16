# The code is modified from https://github.com/Stanou01260/chessbot_python/blob/master/code/board_basics.py

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
        return square

    def convert_row_column_to_square_name(self, row, column):
        number = repr(8 - row)
        letter = str(chr(97 + column))
        return letter + number

    def square_region(self, row, column):
        region = set()
        for d_row in range(-1, 2):
            n_row = row + d_row
            if not (0 <= n_row < 8):
                continue
            region.add((n_row, column))

        for d_column in range(-1, 2):
            n_column = column + d_column
            if not (0 <= n_column < 8):
                continue
            region.add((row, n_column))
        return region

    def get_potential_moves(self, fgmask):
        board = [[self.get_square_image(row, column, fgmask).mean() for column in range(8)] for row in range(8)]

        potential_squares = []
        for row in range(8):
            for column in range(8):
                score = board[row][column]
                if score < 10.0:
                    continue
                potential_squares.append((score, row, column))

        potential_squares.sort(reverse=True)
        potential_squares = potential_squares[:4]
        potential_moves = []

        for start_square_score, start_row, start_column in potential_squares:
            start_region = self.square_region(start_row, start_column)
            for arrival_square_score, arrival_row, arrival_column in potential_squares:
                if (start_row, start_column) == (arrival_row, arrival_column):
                    continue
                arrival_region = self.square_region(arrival_row, arrival_column)
                region = start_region.union(arrival_region)
                total_square_score = sum(
                    board[row][column] for row, column in region) + start_square_score + arrival_square_score
                start_square_name = self.convert_row_column_to_square_name(start_row, start_column)
                arrival_square_name = self.convert_row_column_to_square_name(arrival_row, arrival_column)
                potential_moves.append(
                    (total_square_score, start_square_name, arrival_square_name))

        potential_moves.sort(reverse=True)

        for i in range(len(potential_squares)):
            score, row, column = potential_squares[i]
            potential_squares[i] = (score, self.convert_row_column_to_square_name(row, column))

        return potential_squares, potential_moves
