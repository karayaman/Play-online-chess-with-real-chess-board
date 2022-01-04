from threading import Thread
import chess


class LichessCommentator(Thread):

    def __init__(self, *args, **kwargs):
        super(LichessCommentator, self).__init__(*args, **kwargs)
        self.stream = None
        self.speech_thread = None
        self.game_state = GameState()
        self.comment_me = None
        self.comment_opponent = None
        self.language = None

    def run(self):
        while not self.game_state.board.is_game_over():
            is_my_turn = (self.game_state.we_play_white) == (self.game_state.board.turn == chess.WHITE)
            found_move, move = self.game_state.register_move_if_needed(self.stream)
            if found_move and ((self.comment_me and is_my_turn) or (self.comment_opponent and (not is_my_turn))):
                self.speech_thread.put_text(self.language.comment(self.game_state.board, move))


class GameState:

    def __init__(self):
        self.we_play_white = None
        self.board = chess.Board()
        self.registered_moves = []

    def register_move_if_needed(self, stream):
        current_state = next(stream)
        if 'state' in current_state:
            current_state = current_state['state']
        if 'moves' in current_state:
            moves = current_state['moves'].split()
            if len(moves) > len(self.registered_moves):
                valid_move_string = moves[len(self.registered_moves)]
                valid_move_UCI = chess.Move.from_uci(valid_move_string)
                self.register_move(valid_move_UCI)
                return True, valid_move_UCI
        return False, "No move found"

    def register_move(self, move):
        if move in self.board.legal_moves:
            self.board.push(move)
            self.registered_moves.append(move)
            return True
        else:
            return False
