import chess


class English:
    def __init__(self):
        self.game_started = "Game started"
        self.move_failed = "Move registration failed. Please redo your move."

    def name(self, piece_type):
        if piece_type == chess.PAWN:
            return "pawn"
        if piece_type == chess.KNIGHT:
            return "knight"
        if piece_type == chess.BISHOP:
            return "bishop"
        if piece_type == chess.ROOK:
            return "rook"
        if piece_type == chess.QUEEN:
            return "queen"
        if piece_type == chess.KING:
            return "king"

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
        comment += self.name(piece.piece_type)

        comment += " " + from_square
        comment += " takes" if is_capture else " to"
        comment += " " + to_square
        if promotion:
            comment += " promotion to " + self.name(promotion)
        comment += check
        return comment


class German:
    def __init__(self):
        self.game_started = "Das Spiel hat gestartet."
        self.move_failed = "Der Zug ist ungültig, bitte wiederholen."

    def name(self, piece_type):
        if piece_type == chess.PAWN:
            return "Bauer"
        if piece_type == chess.KNIGHT:
            return "Springer"
        if piece_type == chess.BISHOP:
            return "Läufer"
        if piece_type == chess.ROOK:
            return "Turm"
        if piece_type == chess.QUEEN:
            return "Dame"
        if piece_type == chess.KING:
            return "König"

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
        comment += self.name(piece.piece_type)

        comment += " " + from_square
        comment += " schlägt" if is_capture else " nach"
        comment += " " + to_square
        if promotion:
            comment += " Umwandlung in " + self.name(promotion)
        comment += check
        return comment


class Russian:
    def __init__(self):
        self.game_started = "игра началась"
        self.move_failed = "Ошибка регистрации хода. Пожалуйста, повторите свой ход"

    def name(self, piece_type):
        if piece_type == chess.PAWN:
            return "пешка"
        if piece_type == chess.KNIGHT:
            return "конь"
        if piece_type == chess.BISHOP:
            return "слон"
        if piece_type == chess.ROOK:
            return "ладья"
        if piece_type == chess.QUEEN:
            return "ферзь"
        if piece_type == chess.KING:
            return "король"

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
        comment += self.name(piece.piece_type)

        comment += " " + from_square
        comment += " бьёт" if is_capture else ""
        comment += " " + to_square
        if promotion:
            comment += " превращение в " + self.name(promotion)
        comment += check
        return comment


class Turkish:
    def __init__(self):
        self.game_started = "Oyun başladı."
        self.move_failed = "Hamle geçersiz. Lütfen hamlenizi yeniden yapın."

    def capture_suffix(self, to_square):
        if to_square[-1] in "158":
            return "i"
        if to_square[-1] in "27":
            return "yi"
        if to_square[-1] in "34":
            return "ü"
        return "yı"

    def from_suffix(self, from_square):
        if from_square[-1] in "1278":
            return "den"
        if from_square[-1] in "345":
            return "ten"
        return "dan"

    def to_suffix(self, to_square):
        if to_square[-1] in "13458":
            return "e"
        if to_square[-1] in "27":
            return "ye"
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
            comment += (
                "'"
                + self.from_suffix(from_square)
                + " "
                + to_square
                + "'"
                + self.to_suffix(to_square)
            )

        if promotion:
            comment += " "
            if promotion == chess.KNIGHT:
                comment += "ata"
            elif promotion == chess.BISHOP:
                comment += "file"
            elif promotion == chess.ROOK:
                comment += "kaleye"
            elif promotion == chess.QUEEN:
                comment += "vezire"
            comment += " terfi"
        comment += check
        return comment


class Italian:
    def __init__(self):
        self.game_started = "Gioco iniziato"
        self.move_failed = (
            "Registrazione spostamento non riuscita. Per favore rifai la tua mossa."
        )

    def name(self, piece_type):
        if piece_type == chess.PAWN:
            return "pedone"
        if piece_type == chess.KNIGHT:
            return "cavallo"
        if piece_type == chess.BISHOP:
            return "alfiere"
        if piece_type == chess.ROOK:
            return "torre"
        if piece_type == chess.QUEEN:
            return "regina"
        if piece_type == chess.KING:
            return "re"

    def prefix_name(self, piece_type):
        if piece_type == chess.PAWN:
            return "il pedone"
        if piece_type == chess.KNIGHT:
            return "il cavallo"
        if piece_type == chess.BISHOP:
            return "l'alfiere"
        if piece_type == chess.ROOK:
            return "la torre"
        if piece_type == chess.QUEEN:
            return "la regina"
        if piece_type == chess.KING:
            return "il re"

    def comment(self, board, move):
        check = ""
        if board.is_checkmate():
            check = " scacco matto"
        elif board.is_check():
            check = " scacco"
        board.pop()
        if board.is_kingside_castling(move):
            board.push(move)
            return "arrocco corto" + check
        if board.is_queenside_castling(move):
            board.push(move)
            return "arrocco lungo" + check

        piece = board.piece_at(move.from_square)
        from_square = chess.square_name(move.from_square)
        to_square = chess.square_name(move.to_square)
        promotion = move.promotion

        is_capture = board.is_capture(move)
        board.push(move)
        comment = ""
        if is_capture:
            comment += self.prefix_name(piece.piece_type)
            comment += " " + from_square
            comment += " cattura"
            comment += " " + to_square
        else:
            comment += self.name(piece.piece_type)
            comment += " da " + from_square
            comment += " a " + to_square
        if promotion:
            comment += " promuove a " + self.name(promotion)
        comment += check
        return comment


class French:
    def __init__(self):
        self.game_started = "Partie démarrée"
        self.move_failed = "La reconnaissance a échoué. Veuillez réessayer."

    def name(self, piece_type):
        if piece_type == chess.PAWN:
            return "pion"
        if piece_type == chess.KNIGHT:
            return "cavalier"
        if piece_type == chess.BISHOP:
            return "fou"
        if piece_type == chess.ROOK:
            return "tour"
        if piece_type == chess.QUEEN:
            return "reine"
        if piece_type == chess.KING:
            return "roi"

    def comment(self, board, move):
        check = ""
        if board.is_checkmate():
            check = " échec et mat"
        elif board.is_check():
            check = " échec"
        board.pop()
        if board.is_kingside_castling(move):
            board.push(move)
            return "petit roc" + check
        if board.is_queenside_castling(move):
            board.push(move)
            return "grand roc" + check

        piece = board.piece_at(move.from_square)
        from_square = chess.square_name(move.from_square)
        to_square = chess.square_name(move.to_square)
        promotion = move.promotion

        is_capture = board.is_capture(move)
        board.push(move)
        comment = ""
        comment += self.name(piece.piece_type)

        comment += " " + from_square
        comment += " prend" if is_capture else " vers"
        comment += " " + to_square
        if promotion:
            comment += " promu en " + self.name(promotion)
        comment += check
        return comment
