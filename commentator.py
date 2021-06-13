from threading import Thread
import chess
import mss
import numpy as np
import cv2
import time


class Commentator_thread(Thread):

    def __init__(self, *args, **kwargs):
        super(Commentator_thread, self).__init__(*args, **kwargs)
        self.speech_thread = None
        self.first_move_uci = None

        self.game_state = Game_state()
        self.comment_me = None
        self.comment_opponent = None
        self.language = None

    def run(self):
        resized_chessboard = self.game_state.get_chessboard()
        self.game_state.previous_chessboard_image = resized_chessboard
        self.game_state.register_move(self.first_move_uci, resized_chessboard)
        if (self.game_state.we_play_white and self.comment_me) or (
                self.game_state.we_play_white == False and self.comment_opponent):
            self.speech_thread.put_text(self.language.comment(self.game_state.board, self.first_move_uci))

        while not self.game_state.board.is_game_over():
            is_my_turn = (self.game_state.we_play_white) == (self.game_state.board.turn == chess.WHITE)
            found_move, move = self.game_state.register_move_if_needed()
            if found_move and ((self.comment_me and is_my_turn) or (self.comment_opponent and (not is_my_turn))):
                self.speech_thread.put_text(self.language.comment(self.game_state.board, move))


# https://github.com/Stanou01260/chessbot_python/blob/master/code/game_state_classes.py
class Game_state:

    def __init__(self):
        self.we_play_white = None
        self.previous_chessboard_image = None
        self.board = chess.Board()
        self.board_position_on_screen = None
        self.sct = mss.mss()

    def get_chessboard(self):
        position = self.board_position_on_screen
        monitor = {'top': 0, 'left': 0, 'width': position.maxX + 10, 'height': position.maxY + 10}
        img = np.array(np.array(self.sct.grab(monitor)))
        # Converting the image in grayscale:
        image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        dim = (800, 800)  # perform the actual resizing of the chessboard
        resizedChessBoard = cv2.resize(image[position.minY:position.maxY, position.minX:position.maxX], dim,
                                       interpolation=cv2.INTER_AREA)
        return resizedChessBoard

    def get_square_image(self, row, column,
                         board_img):
        height, width = board_img.shape
        minX = int(column * width / 8)
        maxX = int((column + 1) * width / 8)
        minY = int(row * width / 8)
        maxY = int((row + 1) * width / 8)
        square = board_img[minY:maxY, minX:maxX]
        square_without_borders = square[6:-6, 6:-6]
        return square_without_borders

    def is_square_empty(self, square):  # A square is empty if its pixels have no variations
        return square.std() < 20

    # This function checks if the chessboard image we see fits the moves we stored
    # The only check done right now is squares have the right emptiness.
    def can_image_correspond_to_chessboard(self, move, current_chessboard_image):
        self.board.push(move)
        squares = chess.SquareSet(chess.BB_ALL)
        for square in squares:
            row = chess.square_rank(square)
            column = chess.square_file(square)
            piece = self.board.piece_at(square)
            shouldBeEmpty = (piece == None)

            if self.we_play_white == True:
                rowOnImage = 7 - row
                columnOnImage = column
            else:
                rowOnImage = row
                columnOnImage = 7 - column

            squareImage = self.get_square_image(rowOnImage, columnOnImage, current_chessboard_image)

            if self.is_square_empty(squareImage) != shouldBeEmpty:
                self.board.pop()
                # print("Problem with : ", self.board.uci(move), " the square ",
                #      self.convert_row_column_to_square_name(row, column, self.we_play_white), "should ",
                #      'be empty' if shouldBeEmpty else 'contain a piece',
                #      " standard deviation is " + str(squareImage.std()))
                # cv2.imwrite("error.JPG", squareImage)
                return False
        self.board.pop()
        return True

    def get_valid_move(self, potential_starts, potential_arrivals, current_chessboard_image):
        previous_move = self.board.peek()
        previous_move_string = previous_move.uci()
        pre_from = previous_move_string[:2]
        pre_to = previous_move_string[2:4]
        if pre_from in potential_starts:  # Fixing premove effect
            potential_starts = potential_starts[potential_starts != pre_from]
            # Move pre_to to back
            if pre_to in potential_arrivals:
                potential_arrivals = potential_arrivals[potential_arrivals != pre_to]
            potential_arrivals = np.append(potential_arrivals, pre_to)
        valid_move_string = ""
        for start in potential_starts:
            if valid_move_string:
                break
            for arrival in potential_arrivals:
                if valid_move_string:
                    break
                uci_move = start + arrival
                try:
                    move = chess.Move.from_uci(uci_move)
                except:
                    continue

                if move == self.board.peek():
                    continue

                if move in self.board.legal_moves:
                    if self.can_image_correspond_to_chessboard(move,
                                                               current_chessboard_image):
                        valid_move_string = uci_move
                else:
                    uci_move_promoted = uci_move + 'q'
                    promoted_move = chess.Move.from_uci(uci_move_promoted)
                    if promoted_move == self.board.peek():
                        continue
                    if promoted_move in self.board.legal_moves:
                        if self.can_image_correspond_to_chessboard(move,
                                                                   current_chessboard_image):
                            valid_move_string = uci_move_promoted

        # Detect castling king side with white
        if ("e1" in potential_starts) and ("h1" in potential_starts) and ("f1" in potential_arrivals) and (
                "g1" in potential_arrivals) and (chess.Move.from_uci("e1g1") in self.board.legal_moves):
            if self.board.peek() != chess.Move.from_uci("e1g1"):
                valid_move_string = "e1g1"

        # Detect castling queen side with white
        if ("e1" in potential_starts) and ("a1" in potential_starts) and ("c1" in potential_arrivals) and (
                "d1" in potential_arrivals) and (chess.Move.from_uci("e1c1") in self.board.legal_moves):
            if self.board.peek() != chess.Move.from_uci("e1c1"):
                valid_move_string = "e1c1"

        # Detect castling king side with black
        if ("e8" in potential_starts) and ("h8" in potential_starts) and ("f8" in potential_arrivals) and (
                "g8" in potential_arrivals) and (chess.Move.from_uci("e8g8") in self.board.legal_moves):
            if self.board.peek() != chess.Move.from_uci("e8g8"):
                valid_move_string = "e8g8"

        # Detect castling queen side with black
        if ("e8" in potential_starts) and ("a8" in potential_starts) and ("c8" in potential_arrivals) and (
                "d8" in potential_arrivals) and (chess.Move.from_uci("e8c8") in self.board.legal_moves):
            if self.board.peek() != chess.Move.from_uci("e8c8"):
                valid_move_string = "e8c8"
        return valid_move_string

    def has_square_image_changed(self, old_square,
                                 new_square):
        diff = cv2.absdiff(old_square, new_square)
        if diff.mean() > 8:
            return True
        else:
            return False

    def convert_row_column_to_square_name(self, row, column, is_white_on_bottom):
        if is_white_on_bottom == True:
            number = repr(8 - row)
            letter = str(chr(97 + column))
            return letter + number
        else:
            number = repr(row + 1)
            letter = str(chr(97 + (7 - column)))
            return letter + number

    def get_potential_moves(self, old_image, new_image, is_white_on_bottom):
        potential_starts = []
        potential_arrivals = []
        for row in range(8):
            for column in range(8):
                old_square = self.get_square_image(row, column, old_image)
                new_square = self.get_square_image(row, column, new_image)
                if self.has_square_image_changed(old_square, new_square):
                    square_name = self.convert_row_column_to_square_name(row, column, is_white_on_bottom)
                    square_was_empty = self.is_square_empty(old_square)
                    square_is_empty = self.is_square_empty(new_square)
                    if square_was_empty == False:
                        potential_starts = np.append(potential_starts, square_name)
                    if square_is_empty == False:
                        potential_arrivals = np.append(potential_arrivals, square_name)
        return potential_starts, potential_arrivals

    def register_move_if_needed(self):
        new_board = self.get_chessboard()
        potential_starts, potential_arrivals = self.get_potential_moves(self.previous_chessboard_image, new_board,
                                                                        self.we_play_white)

        valid_move_string1 = self.get_valid_move(potential_starts, potential_arrivals, new_board)

        if len(valid_move_string1) > 0:
            time.sleep(0.1)
            # Check that we were not in the middle of a move animation
            new_board = self.get_chessboard()
            potential_starts, potential_arrivals = self.get_potential_moves(self.previous_chessboard_image, new_board,
                                                                            self.we_play_white)
            valid_move_string2 = self.get_valid_move(potential_starts, potential_arrivals, new_board)
            if valid_move_string2 != valid_move_string1:
                return False, "The move has changed"
            valid_move_UCI = chess.Move.from_uci(valid_move_string1)
            self.register_move(valid_move_UCI, new_board)
            return True, valid_move_UCI
        return False, "No move found"

    def register_move(self, move, board_image):
        if move in self.board.legal_moves:
            self.board.push(move)
            self.previous_chessboard_image = board_image
            return True
        else:
            return False
