import chessboard_detection
import pyautogui
import time


class Internet_game:
    def __init__(self, use_template, start_delay, drag_drop):
        self.drag_drop = drag_drop
        time.sleep(start_delay)
        if use_template:
            self.position, self.we_play_white = chessboard_detection.find_chessboard()
        else:
            self.position, self.we_play_white = chessboard_detection.auto_find_chessboard()
        self.is_our_turn = self.we_play_white

    def move(self, move):
        move_string = move.uci()

        origin_square = move_string[0:2]
        destination_square = move_string[2:4]

        centerXOrigin, centerYOrigin = self.get_square_center(origin_square)
        centerXDest, centerYDest = self.get_square_center(destination_square)

        if self.drag_drop:
            pyautogui.moveTo(centerXOrigin, centerYOrigin, 0.01)
            pyautogui.dragTo(centerXOrigin, centerYOrigin + 1, button='left',
                             duration=0.01)
            pyautogui.dragTo(centerXDest, centerYDest, button='left', duration=0.3)
        else:
            pyautogui.click(centerXOrigin, centerYOrigin, duration=0.1)
            pyautogui.click(centerXDest, centerYDest, duration=0.1)

        print("Done playing move", origin_square, destination_square)
        return

    def get_square_center(self, square_name):
        row, column = self.convert_square_name_to_row_column(square_name, self.we_play_white)
        position = self.position
        centerX = int(position.minX + (column + 0.5) * (position.maxX - position.minX) / 8)
        centerY = int(position.minY + (row + 0.5) * (position.maxY - position.minY) / 8)
        return centerX, centerY

    def convert_square_name_to_row_column(self, square_name, is_white_on_bottom):
        for row in range(8):
            for column in range(8):
                this_square_name = self.convert_row_column_to_square_name(row, column, is_white_on_bottom)
                if this_square_name == square_name:
                    return row, column
        return 0, 0

    def convert_row_column_to_square_name(self, row, column, is_white_on_bottom):
        if is_white_on_bottom == True:
            number = repr(8 - row)
            letter = str(chr(97 + column))
            return letter + number
        else:
            number = repr(row + 1)
            letter = str(chr(97 + (7 - column)))
            return letter + number
