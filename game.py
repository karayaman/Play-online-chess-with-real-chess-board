# The code is modified from https://github.com/Stanou01260/chessbot_python/blob/master/code/game_state_classes.py

import chess
from internet_game import Internet_game
import numpy as np


class Game:
    def __init__(self, board_basics, speech_thread):
        self.internet_game = Internet_game()
        self.board_basics = board_basics
        self.speech_thread = speech_thread
        self.we_play_white = True
        self.executed_moves = []  # Store the move detected on san format
        self.board = chess.Board()  # This object comes from the "chess" package, the moves are stored inside it (and it has other cool features such as showing all the "legal moves")

    def register_move(self, fgmask):
        potential_squares, potential_moves = self.board_basics.get_potential_moves(fgmask)
        success, valid_move_string1 = self.get_valid_move(potential_squares, potential_moves)
        print("Valid move string 1:" + valid_move_string1)
        if not success:
            self.speech_thread.put_text("Move registration failed. Please redo your move.")
            return False

        valid_move_UCI = chess.Move.from_uci(valid_move_string1)

        print("Move has been registered")
        self.executed_moves = np.append(self.executed_moves, self.board.san(valid_move_UCI))
        self.board.push(valid_move_UCI)

        if self.internet_game.is_our_turn:
            self.internet_game.move(valid_move_UCI)
        else:
            self.speech_thread.put_text(valid_move_string1)

        self.internet_game.is_our_turn = not self.internet_game.is_our_turn

        return True

    def get_valid_move(self, potential_squares, potential_moves):
        print("Potential squares")
        print(potential_squares)
        print("Potential moves")
        print(potential_moves)

        valid_move_string = ""
        for score, start, arrival in potential_moves:
            if valid_move_string:
                break
            uci_move = start + arrival
            try:
                move = chess.Move.from_uci(uci_move)
            except Exception as e:
                print(e)
                continue

            if move in self.board.legal_moves:
                valid_move_string = uci_move
            else:
                uci_move_promoted = uci_move + 'q'
                promoted_move = chess.Move.from_uci(uci_move_promoted)
                if promoted_move in self.board.legal_moves:
                    valid_move_string = uci_move_promoted
                    print("There has been a promotion to queen")

        potential_squares = [square[1] for square in potential_squares]
        print(potential_squares)
        # Detect castling king side with white
        if ("e1" in potential_squares) and ("h1" in potential_squares) and ("f1" in potential_squares) and (
                "g1" in potential_squares) and (chess.Move.from_uci("e1g1") in self.board.legal_moves):
            valid_move_string = "e1g1"

        # Detect castling queen side with white
        if ("e1" in potential_squares) and ("a1" in potential_squares) and ("c1" in potential_squares) and (
                "d1" in potential_squares) and (chess.Move.from_uci("e1c1") in self.board.legal_moves):
            valid_move_string = "e1c1"

        # Detect castling king side with black
        if ("e8" in potential_squares) and ("h8" in potential_squares) and ("f8" in potential_squares) and (
                "g8" in potential_squares) and (chess.Move.from_uci("e8g8") in self.board.legal_moves):
            valid_move_string = "e8g8"

        # Detect castling queen side with black
        if ("e8" in potential_squares) and ("a8" in potential_squares) and ("c8" in potential_squares) and (
                "d8" in potential_squares) and (chess.Move.from_uci("e8c8") in self.board.legal_moves):
            valid_move_string = "e8c8"

        if valid_move_string:
            return True, valid_move_string
        else:
            return False, valid_move_string
