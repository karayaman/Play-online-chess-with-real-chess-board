class Lichess_game:
    def __init__(self, client, game):
        self.we_play_white = game['color'] == 'white'
        self.is_our_turn = self.we_play_white
        self.client = client
        self.game_id = game['gameId']

    def move(self, move):
        move_string = move.uci()
        self.client.board.make_move(self.game_id, move_string)
        print("Done playing move " + move_string)
