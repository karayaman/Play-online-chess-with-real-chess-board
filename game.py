import time

import chess
import cv2
import numpy as np
from helper import detect_state, get_square_image
from internet_game import Internet_game
from lichess_game import Lichess_game
from commentator import Commentator_thread
from lichess_commentator import Lichess_commentator


class Game:
    def __init__(self, board_basics, speech_thread, use_template, make_opponent, start_delay, comment_me,
                 comment_opponent, drag_drop, language, token, roi_mask):
        if token:
            self.internet_game = Lichess_game(token)
        else:
            self.internet_game = Internet_game(use_template, start_delay, drag_drop)
        self.make_opponent = make_opponent
        self.board_basics = board_basics
        self.speech_thread = speech_thread
        self.executed_moves = []
        self.played_moves = []
        self.board = chess.Board()
        self.comment_me = comment_me
        self.comment_opponent = comment_opponent
        self.language = language
        self.roi_mask = roi_mask
        self.hog = cv2.HOGDescriptor((64, 64), (16, 16), (8, 8), (8, 8), 9)
        self.knn = cv2.ml.KNearest_create()
        self.features = None
        self.labels = None

        if token:
            commentator_thread = Lichess_commentator()
            commentator_thread.daemon = True
            commentator_thread.stream = self.internet_game.client.board.stream_game_state(self.internet_game.game_id)
            commentator_thread.speech_thread = self.speech_thread
            commentator_thread.game_state.we_play_white = self.internet_game.we_play_white
            commentator_thread.game_state.game = self
            commentator_thread.comment_me = self.comment_me
            commentator_thread.comment_opponent = self.comment_opponent
            commentator_thread.language = self.language
            self.commentator = commentator_thread
        else:
            commentator_thread = Commentator_thread()
            commentator_thread.daemon = True
            commentator_thread.speech_thread = self.speech_thread
            commentator_thread.game_state.game_thread = self
            commentator_thread.game_state.we_play_white = self.internet_game.we_play_white
            commentator_thread.game_state.board_position_on_screen = self.internet_game.position
            commentator_thread.comment_me = self.comment_me
            commentator_thread.comment_opponent = self.comment_opponent
            commentator_thread.language = self.language
            self.commentator = commentator_thread

    def initialize_hog(self, frame):
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        pieces = []
        squares = []
        for row in range(8):
            for column in range(8):
                square_name = self.board_basics.convert_row_column_to_square_name(row, column)
                square = chess.parse_square(square_name)
                piece = self.board.piece_at(square)
                square_image = get_square_image(row, column, frame)
                square_image = cv2.resize(square_image, (64, 64))
                if piece:
                    pieces.append(square_image)
                else:
                    squares.append(square_image)
        pieces_hog = [self.hog.compute(piece) for piece in pieces]
        squares_hog = [self.hog.compute(square) for square in squares]
        labels_pieces = np.ones((len(pieces_hog), 1), np.int32)
        labels_squares = np.zeros((len(squares_hog), 1), np.int32)
        pieces_hog = np.array(pieces_hog)
        squares_hog = np.array(squares_hog)
        features = np.float32(np.concatenate((pieces_hog, squares_hog), axis=0))
        labels = np.concatenate((labels_pieces, labels_squares), axis=0)
        self.knn.train(features, cv2.ml.ROW_SAMPLE, labels)
        self.features = features
        self.labels = labels

    def detect_state_hog(self, chessboard_image):
        chessboard_image = cv2.cvtColor(chessboard_image, cv2.COLOR_BGR2GRAY)
        chessboard = [[get_square_image(row, column, chessboard_image) for column in range(8)] for row
                      in
                      range(8)]

        board_hog = [[self.hog.compute(cv2.resize(chessboard[row][column], (64, 64))) for column in range(8)] for row
                     in
                     range(8)]
        knn_result = []
        for row in range(8):
            knn_row = []
            for column in range(8):
                ret, result, neighbours, dist = self.knn.findNearest(np.array([board_hog[row][column]]), k=3)
                knn_row.append(result[0][0])
            knn_result.append(knn_row)
        board_state = [[knn_result[row][column] > 0.5 for column in range(8)] for row
                       in
                       range(8)]
        return board_state

    def get_valid_move_hog(self, fgmask, frame):
        print("Hog working")
        board = [[self.board_basics.get_square_image(row, column, fgmask).mean() for column in range(8)] for row in
                 range(8)]
        potential_squares = []
        square_scores = {}
        for row in range(8):
            for column in range(8):
                score = board[row][column]
                if score < 10.0:
                    continue
                square_name = self.board_basics.convert_row_column_to_square_name(row, column)
                square = chess.parse_square(square_name)
                potential_squares.append(square)
                square_scores[square] = score

        move_to_register = self.get_move_to_register()
        potential_moves = []

        board_result = self.detect_state_hog(frame)
        if move_to_register:
            if (move_to_register.from_square in potential_squares) and (
                    move_to_register.to_square in potential_squares):
                self.board.push(move_to_register)
                if self.check_state_hog(board_result):
                    print("Hog!")
                    self.board.pop()
                    return True, move_to_register.uci()
                else:
                    self.board.pop()
                    return False, ""
        else:
            for move in self.board.legal_moves:
                if (move.from_square in potential_squares) and (move.to_square in potential_squares):
                    if move.promotion and move.promotion != chess.QUEEN:
                        continue
                    self.board.push(move)
                    if self.check_state_hog(board_result):
                        self.board.pop()
                        total_score = square_scores[move.from_square] + square_scores[move.to_square]
                        potential_moves.append((total_score, move.uci()))
                    else:
                        self.board.pop()
        if potential_moves:
            print("Hog!")
            return True, max(potential_moves)[1]
        else:
            return False, ""

    def get_move_to_register(self):
        if self.commentator:
            if len(self.executed_moves) < len(self.commentator.game_state.registered_moves):
                return self.commentator.game_state.registered_moves[len(self.executed_moves)]
            else:
                return None
        else:
            return None

    def is_light_change(self, frame):
        result = detect_state(frame, self.board_basics.d[0], self.roi_mask)
        result_hog = self.detect_state_hog(frame)
        state = self.check_state_for_light(result, result_hog)
        if state:
            print("Light change")
            return True
        else:
            return False

    def check_state_hog(self, result):
        for row in range(8):
            for column in range(8):
                square_name = self.board_basics.convert_row_column_to_square_name(row, column)
                square = chess.parse_square(square_name)
                piece = self.board.piece_at(square)
                if piece and (not result[row][column]):
                    print("Expected piece at " + square_name)
                    return False
                if (not piece) and (result[row][column]):
                    print("Expected empty at " + square_name)
                    return False
        return True

    def check_state_for_move(self, result):
        for row in range(8):
            for column in range(8):
                square_name = self.board_basics.convert_row_column_to_square_name(row, column)
                square = chess.parse_square(square_name)
                piece = self.board.piece_at(square)
                if piece and (True not in result[row][column]):
                    print("Expected piece at " + square_name)
                    return False
                if (not piece) and (False not in result[row][column]):
                    print("Expected empty at " + square_name)
                    return False
        return True

    def check_state_for_light(self, result, result_hog):
        for row in range(8):
            for column in range(8):
                if len(result[row][column]) > 1:
                    result[row][column] = [result_hog[row][column]]
                square_name = self.board_basics.convert_row_column_to_square_name(row, column)
                square = chess.parse_square(square_name)
                piece = self.board.piece_at(square)
                if piece and (False in result[row][column]):
                    print(square_name)
                    return False
                if (not piece) and (True in result[row][column]):
                    print(square_name)
                    return False
        return True

    def get_valid_move_canny(self, fgmask, frame):
        print("Canny working")
        board = [[self.board_basics.get_square_image(row, column, fgmask).mean() for column in range(8)] for row in
                 range(8)]
        potential_squares = []
        square_scores = {}
        for row in range(8):
            for column in range(8):
                score = board[row][column]
                if score < 10.0:
                    continue
                square_name = self.board_basics.convert_row_column_to_square_name(row, column)
                square = chess.parse_square(square_name)
                potential_squares.append(square)
                square_scores[square] = score

        move_to_register = self.get_move_to_register()
        potential_moves = []

        board_result = detect_state(frame, self.board_basics.d[0], self.roi_mask)
        if move_to_register:
            if (move_to_register.from_square in potential_squares) and (
                    move_to_register.to_square in potential_squares):
                self.board.push(move_to_register)
                if self.check_state_for_move(board_result):
                    print("Canny!")
                    self.board.pop()
                    return True, move_to_register.uci()
                else:
                    self.board.pop()
                    return False, ""
        else:
            for move in self.board.legal_moves:
                if (move.from_square in potential_squares) and (move.to_square in potential_squares):
                    if move.promotion and move.promotion != chess.QUEEN:
                        continue
                    self.board.push(move)
                    if self.check_state_for_move(board_result):
                        self.board.pop()
                        total_score = square_scores[move.from_square] + square_scores[move.to_square]
                        potential_moves.append((total_score, move.uci()))
                    else:
                        self.board.pop()
        if potential_moves:
            print("Canny!")
            return True, max(potential_moves)[1]
        else:
            return False, ""

    def register_move(self, fgmask, previous_frame, next_frame):
        potential_squares, potential_moves = self.board_basics.get_potential_moves(fgmask, previous_frame,
                                                                                   next_frame,
                                                                                   self.board)
        success, valid_move_string = self.get_valid_move(potential_squares, potential_moves)
        print("Valid move string:" + valid_move_string)
        if not success:
            success, valid_move_string = self.get_valid_move_canny(fgmask, next_frame)
            print("Valid move string 2:" + valid_move_string)
            if not success:
                success, valid_move_string = self.get_valid_move_hog(fgmask, next_frame)
                print("Valid move string 3:" + valid_move_string)
            if success:
                pass
            else:
                self.speech_thread.put_text(self.language.move_failed)
                print(self.board.fen())
                return False

        valid_move_UCI = chess.Move.from_uci(valid_move_string)

        print("Move has been registered")

        if self.internet_game.is_our_turn or self.make_opponent:
            self.internet_game.move(valid_move_UCI)
            self.played_moves.append(valid_move_UCI)
            while self.commentator:
                time.sleep(0.1)
                move_to_register = self.get_move_to_register()
                if move_to_register:
                    valid_move_UCI = move_to_register
                    break
        else:
            self.speech_thread.put_text(valid_move_string[:4])
            self.played_moves.append(valid_move_UCI)

        self.executed_moves.append(self.board.san(valid_move_UCI))
        self.board.push(valid_move_UCI)

        self.internet_game.is_our_turn = not self.internet_game.is_our_turn

        self.learn(next_frame)
        return True

    def learn(self, frame):
        result = self.detect_state_hog(frame)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        new_pieces = []
        new_squares = []

        for row in range(8):
            for column in range(8):
                square_name = self.board_basics.convert_row_column_to_square_name(row, column)
                square = chess.parse_square(square_name)
                piece = self.board.piece_at(square)
                if piece and (not result[row][column]):
                    print("Learning piece at " + square_name)
                    piece_hog = self.hog.compute(cv2.resize(get_square_image(row, column, frame), (64, 64)))
                    new_pieces.append(piece_hog)
                if (not piece) and (result[row][column]):
                    print("Learning empty at " + square_name)
                    square_hog = self.hog.compute(cv2.resize(get_square_image(row, column, frame), (64, 64)))
                    new_squares.append(square_hog)
        labels_pieces = np.ones((len(new_pieces), 1), np.int32)
        labels_squares = np.zeros((len(new_squares), 1), np.int32)
        if new_pieces:
            new_pieces = np.array(new_pieces)
            self.features = np.float32(np.concatenate((self.features, new_pieces), axis=0))
            self.labels = np.concatenate((self.labels, labels_pieces), axis=0)
        if new_squares:
            new_squares = np.array(new_squares)
            self.features = np.float32(np.concatenate((self.features, new_squares), axis=0))
            self.labels = np.concatenate((self.labels, labels_squares), axis=0)

        self.features = self.features[:100]
        self.labels = self.labels[:100]
        print(self.features.shape)
        print(self.labels.shape)
        self.knn = cv2.ml.KNearest_create()
        self.knn.train(self.features, cv2.ml.ROW_SAMPLE, self.labels)

    def get_valid_move(self, potential_squares, potential_moves):
        print("Potential squares")
        print(potential_squares)
        print("Potential moves")
        print(potential_moves)

        move_to_register = self.get_move_to_register()

        valid_move_string = ""
        for score, start, arrival in potential_moves:
            if valid_move_string:
                break

            if move_to_register:
                if chess.square_name(move_to_register.from_square) != start:
                    continue
                if chess.square_name(move_to_register.to_square) != arrival:
                    continue

            uci_move = start + arrival
            try:
                move = chess.Move.from_uci(uci_move)
            except Exception as e:
                print(e)
                continue

            if move in self.board.legal_moves:
                valid_move_string = uci_move
            else:
                if move_to_register:
                    uci_move_promoted = move_to_register.uci()
                else:
                    uci_move_promoted = uci_move + 'q'
                promoted_move = chess.Move.from_uci(uci_move_promoted)
                if promoted_move in self.board.legal_moves:
                    valid_move_string = uci_move_promoted
                    # print("There has been a promotion")

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

        if move_to_register and (move_to_register.uci() != valid_move_string):
            return False, valid_move_string

        if valid_move_string:
            print("ssim!")
            return True, valid_move_string
        else:
            return False, valid_move_string
