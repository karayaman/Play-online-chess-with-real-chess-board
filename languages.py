import chess


class English:
    def __init__(self):
        self.game_started = "Game started"
        self.move_failed = "Move registration failed. Please redo your move."

    def comment(self, board, move):
        check = ""
        if board.is_checkmate():
            check = " checkmate"
        elif board.is_check():
            check = " check"
        board.pop()
        if board.is_kingside_castling(move):
            board.push(move)
            return "castling short" + check
        if board.is_queenside_castling(move):
            board.push(move)
            return "castling long" + check

        piece = board.piece_at(move.from_square)
        from_square = chess.square_name(move.from_square)
        to_square = chess.square_name(move.to_square)
        promotion = move.promotion

        is_capture = board.is_capture(move)
        board.push(move)
        comment = ""
        if piece.piece_type == chess.PAWN:
            comment += "pawn"
        elif piece.piece_type == chess.KNIGHT:
            comment += "knight"
        elif piece.piece_type == chess.BISHOP:
            comment += "bishop"
        elif piece.piece_type == chess.ROOK:
            comment += "rook"
        elif piece.piece_type == chess.QUEEN:
            comment += "queen"
        elif piece.piece_type == chess.KING:
            comment += "king"

        comment += " " + from_square
        comment += " takes" if is_capture else " to"
        comment += " " + to_square
        if promotion:
            comment += " promotion to queen"
        comment += check
        return comment


class German:
    def __init__(self):
        self.game_started = "Das Spiel hat gestartet."
        self.move_failed = "Der Zug ist ungültig, bitte wiederholen."

    def comment(self, board, move):
        check = ""
        if board.is_checkmate():
            check = " Schachmatt"
        elif board.is_check():
            check = " Schach"
        board.pop()
        if board.is_kingside_castling(move):
            board.push(move)
            return "kurze Rochade" + check
        if board.is_queenside_castling(move):
            board.push(move)
            return "lange Rochade" + check

        piece = board.piece_at(move.from_square)
        from_square = chess.square_name(move.from_square)
        to_square = chess.square_name(move.to_square)
        promotion = move.promotion

        is_capture = board.is_capture(move)
        board.push(move)
        comment = ""
        if piece.piece_type == chess.PAWN:
            comment += "Bauer"
        elif piece.piece_type == chess.KNIGHT:
            comment += "Springer"
        elif piece.piece_type == chess.BISHOP:
            comment += "Läufer"
        elif piece.piece_type == chess.ROOK:
            comment += "Turm"
        elif piece.piece_type == chess.QUEEN:
            comment += "Dame"
        elif piece.piece_type == chess.KING:
            comment += "König"

        comment += " " + from_square
        comment += " schlägt" if is_capture else " nach"
        comment += " " + to_square
        if promotion:
            comment += " Umwandlung in Dame"
        comment += check
        return comment


class Russian:
    def __init__(self):
        self.game_started = "игра началась"
        self.move_failed = "Ошибка регистрации хода. Пожалуйста, повторите свой ход"

    def comment(self, board, move):
        check = ""
        if board.is_checkmate():
            check = " шах и мат"
        elif board.is_check():
            check = " шах"
        board.pop()
        if board.is_kingside_castling(move):
            board.push(move)
            return "короткая рокировка" + check
        if board.is_queenside_castling(move):
            board.push(move)
            return "длинная рокировка" + check

        piece = board.piece_at(move.from_square)
        from_square = chess.square_name(move.from_square)
        to_square = chess.square_name(move.to_square)
        promotion = move.promotion

        is_capture = board.is_capture(move)
        board.push(move)
        comment = ""
        if piece.piece_type == chess.PAWN:
            comment += "пешка"
        elif piece.piece_type == chess.KNIGHT:
            comment += "конь"
        elif piece.piece_type == chess.BISHOP:
            comment += "слон"
        elif piece.piece_type == chess.ROOK:
            comment += "ладья"
        elif piece.piece_type == chess.QUEEN:
            comment += "ферзь"
        elif piece.piece_type == chess.KING:
            comment += "король"

        comment += " " + from_square
        comment += " бьёт" if is_capture else ""
        comment += " " + to_square
        if promotion:
            comment += " превращение в ферзя"
        comment += check
        return comment


class Turkish:
    def __init__(self):
        self.game_started = "Oyun başladı."
        self.move_failed = "Hamle geçersiz. Lütfen hamlenizi yeniden yapın."

    def capture_suffix(self, to_square):
        if to_square[-1] in "158":
            return "i"
        elif to_square[-1] in "27":
            return "yi"
        elif to_square[-1] in "34":
            return "ü"
        else:  # 6
            return "yı"

    def from_suffix(self, from_square):
        if from_square[-1] in "1278":
            return "den"
        elif from_square[-1] in "345":
            return "ten"
        else:  # 6
            return "dan"

    def to_suffix(self, to_square):
        if to_square[-1] in "13458":
            return "e"
        elif to_square[-1] in "27":
            return "ye"
        else:  # 6
            return "ya"

    def comment(self, board, move):
        check = ""
        if board.is_checkmate():
            check = " şahmat"
        elif board.is_check():
            check = " şah"
        board.pop()
        if board.is_kingside_castling(move):
            board.push(move)
            return "kısa rok" + check
        if board.is_queenside_castling(move):
            board.push(move)
            return "uzun rok" + check

        piece = board.piece_at(move.from_square)
        from_square = chess.square_name(move.from_square)
        to_square = chess.square_name(move.to_square)
        promotion = move.promotion

        is_capture = board.is_capture(move)
        board.push(move)
        comment = ""
        if piece.piece_type == chess.PAWN:
            comment += "piyon"
        elif piece.piece_type == chess.KNIGHT:
            comment += "at"
        elif piece.piece_type == chess.BISHOP:
            comment += "fil"
        elif piece.piece_type == chess.ROOK:
            comment += "kale"
        elif piece.piece_type == chess.QUEEN:
            comment += "vezir"
        elif piece.piece_type == chess.KING:
            comment += "şah"

        comment += " " + from_square
        if is_capture:
            comment += " alır"
            comment += " " + to_square + "'" + self.capture_suffix(to_square)
        else:
            comment += "'" + self.from_suffix(from_square) + " " + to_square + "'" + self.to_suffix(to_square)

        if promotion:
            comment += " vezire terfi"
        comment += check
        return comment
