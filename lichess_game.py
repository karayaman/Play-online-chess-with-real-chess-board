import os
import pathlib as pl
import pickle
import sys

import berserk
import chess


class LichessGame:
    def __init__(self, token):
        session = berserk.TokenSession(token)
        client = berserk.Client(session)
        games = client.games.get_ongoing()
        if len(games) == 0:
            print("No games found. Please create your game on Lichess.")
            sys.exit(0)
        if len(games) > 1:
            print(
                "Multiple games found. Please make sure there is only one ongoing game on Lichess."
            )
            sys.exit(0)
        game = games[0]
        self.we_play_white = game["color"] == "white"
        self.is_our_turn = self.we_play_white
        self.client = client
        self.game_id = game["gameId"]
        self.token = token
        self.save_file = "promotion.bin"
        self.promotion_pieces = {
            "Queen": chess.QUEEN,
            "Knight": chess.KNIGHT,
            "Rook": chess.ROOK,
            "Bishop": chess.BISHOP,
        }

    def move(self, move):
        if move.promotion and os.path.exists(self.save_file):
            with pl.Path(self.save_file).open("rb") as infile:
                piece_name = pickle.load(infile)
            move.promotion = self.promotion_pieces[piece_name]
        move_string = move.uci()
        try:
            self.client.board.make_move(self.game_id, move_string)
        except:
            session = berserk.TokenSession(self.token)
            self.client = berserk.Client(session)
            self.client.board.make_move(self.game_id, move_string)
            print("Reconnected to Lichess.")
        print("Done playing move " + move_string)
