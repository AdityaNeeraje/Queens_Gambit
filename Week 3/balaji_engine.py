import chess
import chess.svg
import json
import math
import numpy as np

storage = dict()

class Engine:
    """A class to represent a chess engine written by Balaji."""

    pieces = np.load('pieces.npy')

    def __init__(self, fen='rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq'):
        """Initializes the board with the given FEN string. If no FEN string is given, initializes the board with the default starting position."""
        self.board = chess.Board(fen)
        self.hash = self.get_hash()

    def get_child(self, move) -> 'Engine':
        """Returns a new board with the move executed on the current board."""
        new = Engine(self.board.fen())
        new.make_move(move)
        return new

    def get_legal_moves(self) -> list:
        """Returns a list of legal moves from the current board."""
        return list(self.board.legal_moves)
    
    @staticmethod
    def get_index(piece) -> int:
        """Returns the index of the piece in the pieces array."""
        piece_map = {'p': 0, 'n': 1, 'b': 2, 'r': 3, 'q': 4, 'k': 5, 'P': 6, 'N': 7, 'B': 8, 'R': 9, 'Q': 10, 'K': 11}
        # print(piece, str(piece))
        return piece_map[str(piece)]
    
    def make_move(self, move) -> int:
        """Makes the move on the board and updates the hash."""
        hash = self.hash >> 8
        if self.board.is_castling(move):
            if move.uci() == 'e1g1' and self.board.piece_at(chess.E1) == chess.Piece(chess.KING, chess.WHITE):
                hash ^= int(self.pieces[chess.E1][self.get_index(chess.Piece(chess.KING, chess.WHITE))])
                hash ^= int(self.pieces[chess.G1][self.get_index(chess.Piece(chess.KING, chess.WHITE))])
                hash ^= int(self.pieces[chess.H1][self.get_index(chess.Piece(chess.ROOK, chess.WHITE))])
                hash ^= int(self.pieces[chess.F1][self.get_index(chess.Piece(chess.ROOK, chess.WHITE))])
            elif move.uci() == 'e1c1' and self.board.piece_at(chess.E1) == chess.Piece(chess.KING, chess.WHITE):
                hash ^= int(self.pieces[chess.E1][self.get_index(chess.Piece(chess.KING, chess.WHITE))])
                hash ^= int(self.pieces[chess.C1][self.get_index(chess.Piece(chess.KING, chess.WHITE))])
                hash ^= int(self.pieces[chess.A1][self.get_index(chess.Piece(chess.ROOK, chess.WHITE))])
                hash ^= int(self.pieces[chess.D1][self.get_index(chess.Piece(chess.ROOK, chess.WHITE))])
            elif move.uci() == 'e8g8' and self.board.piece_at(chess.E8) == chess.Piece(chess.KING, chess.BLACK):
                hash ^= int(self.pieces[chess.E8][self.get_index(chess.Piece(chess.KING, chess.BLACK))])
                hash ^= int(self.pieces[chess.G8][self.get_index(chess.Piece(chess.KING, chess.BLACK))])
                hash ^= int(self.pieces[chess.H8][self.get_index(chess.Piece(chess.ROOK, chess.BLACK))])
                hash ^= int(self.pieces[chess.F8][self.get_index(chess.Piece(chess.ROOK, chess.BLACK))])
            elif move.uci() == 'e8c8' and self.board.piece_at(chess.E8) == chess.Piece(chess.KING, chess.BLACK):
                hash ^= int(self.pieces[chess.E8][self.get_index(chess.Piece(chess.KING, chess.BLACK))])
                hash ^= int(self.pieces[chess.C8][self.get_index(chess.Piece(chess.KING, chess.BLACK))])
                hash ^= int(self.pieces[chess.A8][self.get_index(chess.Piece(chess.ROOK, chess.BLACK))])
                hash ^= int(self.pieces[chess.D8][self.get_index(chess.Piece(chess.ROOK, chess.BLACK))])
        elif self.board.is_en_passant(move):
            hash ^= int(self.pieces[move.from_square][self.get_index(self.board.piece_at(move.from_square))])
            hash ^= int(self.pieces[move.to_square][self.get_index(self.board.piece_at(move.from_square))])
            square = chess.square(chess.square_file(move.to_square), chess.square_rank(move.from_square))
            hash ^= int(self.pieces[square][self.get_index(self.board.piece_at(square))])
        elif move.promotion is not None:
            hash ^= int(self.pieces[move.from_square][self.get_index(self.board.piece_at(move.from_square))])
            promotion_piece = chess.Piece(move.promotion, self.board.turn)
            hash ^= int(self.pieces[move.to_square][self.get_index(promotion_piece)])
            if self.board.is_capture(move):
                hash ^= int(self.pieces[move.to_square][self.get_index(self.board.piece_at(move.to_square))])
        else:
            hash ^= int(self.pieces[move.from_square][self.get_index(self.board.piece_at(move.from_square))])
            hash ^= int(self.pieces[move.to_square][self.get_index(self.board.piece_at(move.from_square))])
            if self.board.is_capture(move):
                hash ^= int(self.pieces[move.to_square][self.get_index(self.board.piece_at(move.to_square))])
        self.board.push(move)
        # Update hash for en passant
        hash <<= 3
        if self.board.ep_square is not None:
            hash += int(self.board.ep_square % 8)
        # Castling rights
        hash <<= 1
        if self.board.has_kingside_castling_rights(chess.WHITE):
            hash ^= 1
        hash <<= 1
        if self.board.has_queenside_castling_rights(chess.WHITE):
            hash ^= 1
        hash <<= 1
        if self.board.has_kingside_castling_rights(chess.BLACK):
            hash ^= 1
        hash <<= 1
        if self.board.has_queenside_castling_rights(chess.BLACK):
            hash ^= 1
        # Turn
        hash <<= 1
        if self.board.turn == chess.WHITE:
            hash ^= 1
        self.hash = hash
        # self.hash = self.get_hash()
        return hash
    
    def undo_move(self) -> int:
        """Undoes the last move and updates the hash."""
        hash = self.hash >> 8
        board1 = self.board.copy()
        move = board1.pop()
        if self.board.is_castling(move):
            if move.uci() == 'e1g1' and board1.piece_at(chess.E1) == chess.Piece(chess.KING, chess.WHITE):
                hash ^= int(self.pieces[chess.E1][self.get_index(chess.Piece(chess.KING, chess.WHITE))])
                hash ^= int(self.pieces[chess.G1][self.get_index(chess.Piece(chess.KING, chess.WHITE))])
                hash ^= int(self.pieces[chess.H1][self.get_index(chess.Piece(chess.ROOK, chess.WHITE))])
                hash ^= int(self.pieces[chess.F1][self.get_index(chess.Piece(chess.ROOK, chess.WHITE))])
            elif move.uci() == 'e1c1' and board1.piece_at(chess.E1) == chess.Piece(chess.KING, chess.WHITE):
                hash ^= int(self.pieces[chess.E1][self.get_index(chess.Piece(chess.KING, chess.WHITE))])
                hash ^= int(self.pieces[chess.C1][self.get_index(chess.Piece(chess.KING, chess.WHITE))])
                hash ^= int(self.pieces[chess.A1][self.get_index(chess.Piece(chess.ROOK, chess.WHITE))])
                hash ^= int(self.pieces[chess.D1][self.get_index(chess.Piece(chess.ROOK, chess.WHITE))])
            elif move.uci() == 'e8g8' and board1.piece_at(chess.E8) == chess.Piece(chess.KING, chess.BLACK):
                hash ^= int(self.pieces[chess.E8][self.get_index(chess.Piece(chess.KING, chess.BLACK))])
                hash ^= int(self.pieces[chess.G8][self.get_index(chess.Piece(chess.KING, chess.BLACK))])
                hash ^= int(self.pieces[chess.H8][self.get_index(chess.Piece(chess.ROOK, chess.BLACK))])
                hash ^= int(self.pieces[chess.F8][self.get_index(chess.Piece(chess.ROOK, chess.BLACK))])
            elif move.uci() == 'e8c8' and board1.piece_at(chess.E8) == chess.Piece(chess.KING, chess.BLACK):
                hash ^= int(self.pieces[chess.E8][self.get_index(chess.Piece(chess.KING, chess.BLACK))])
                hash ^= int(self.pieces[chess.C8][self.get_index(chess.Piece(chess.KING, chess.BLACK))])
                hash ^= int(self.pieces[chess.A8][self.get_index(chess.Piece(chess.ROOK, chess.BLACK))])
                hash ^= int(self.pieces[chess.D8][self.get_index(chess.Piece(chess.ROOK, chess.BLACK))])
            
        elif board1.is_en_passant(move):
            hash ^= int(self.pieces[move.from_square][self.get_index(board1.piece_at(move.from_square))])
            hash ^= int(self.pieces[move.to_square][self.get_index(board1.piece_at(move.from_square))])
            square = chess.square(chess.square_file(move.to_square), chess.square_rank(move.from_square))
            hash ^= int(self.pieces[square][self.get_index(board1.piece_at(square))])
        elif move.promotion is not None:
            hash ^= int(self.pieces[move.from_square][self.get_index(board1.piece_at(move.from_square))])
            promotion_piece = chess.Piece(move.promotion, board1.turn)
            hash ^= int(self.pieces[move.to_square][self.get_index(promotion_piece)])
            if board1.is_capture(move):
                hash ^= int(self.pieces[move.to_square][self.get_index(board1.piece_at(move.to_square))])
        else:
            hash ^= int(self.pieces[move.from_square][self.get_index(board1.piece_at(move.from_square))])
            hash ^= int(self.pieces[move.to_square][self.get_index(board1.piece_at(move.from_square))])
            if board1.is_capture(move):
                hash ^= int(self.pieces[move.to_square][self.get_index(board1.piece_at(move.to_square))])            
        self.board.pop()
        # Update hash for en passant
        hash <<= 3
        if board1.ep_square is not None:
            hash += int(board1.ep_square % 8)
        # Castling rights
        hash <<= 1
        if board1.has_kingside_castling_rights(chess.WHITE):
            hash ^= 1
        hash <<= 1
        if board1.has_queenside_castling_rights(chess.WHITE):
            hash ^= 1
        hash <<= 1
        if board1.has_kingside_castling_rights(chess.BLACK):
            hash ^= 1
        hash <<= 1
        if board1.has_queenside_castling_rights(chess.BLACK):
            hash ^= 1
        # Turn
        hash <<= 1
        if board1.turn == chess.WHITE:
            hash ^= 1
        self.hash = hash
        return hash
    
    # Zobrist Hashing
    def get_hash(self) -> int:
        """Returns the Zobrist hash of the current board position."""
        hash = 0
        map = self.board.piece_map()
        for key in map:
            piece = map[key]
            if piece is not None:
                hash ^= int(self.pieces[key][self.get_index(piece)])
        hash <<= 3
        if self.board.ep_square is not None:
            hash += int(self.board.ep_square % 8)
        # Castling rights
        hash <<= 1
        if self.board.has_kingside_castling_rights(chess.WHITE):
            hash ^= 1
        hash <<= 1
        if self.board.has_queenside_castling_rights(chess.WHITE):
            hash ^= 1
        hash <<= 1
        if self.board.has_kingside_castling_rights(chess.BLACK):
            hash ^= 1
        hash <<= 1
        if self.board.has_queenside_castling_rights(chess.BLACK):
            hash ^= 1
        # Turn
        hash <<= 1
        if self.board.turn == chess.WHITE:
            hash ^= 1
        return hash
    

    def get_ordered_moves(self) -> list:
        """Returns a list of legal moves ordered according to the number of legal moves in the next state, then by check. If a move leads to a checkmate, it is returned immediately."""
        legal_moves = self.get_legal_moves()
        moves_dict = dict()
        for move in legal_moves:
            self.board.push(move)
            if self.board.is_checkmate():
                self.board.pop()
                return [move]
            moves_dict[move] = len(self.get_legal_moves())
            if self.board.is_check():
                moves_dict[move] -= 10**64
            self.board.pop()
        return sorted(moves_dict, key=lambda x: moves_dict[x])

    def eval(self, max_player) -> int:
        """Returns the static evaluation of the current board position."""
        if self.board.is_checkmate():
            if max_player:
                return -math.inf
            else:
                return math.inf
        if self.board.is_stalemate():
            return 0
        map = self.board.piece_map()
        ref = {'p': 1, 'n': 3, 'b': 3, 'r': 5, 'q': 9, 'k': 100}
        count = dict()
        pieces = ['k', 'q', 'r', 'b', 'n', 'p']
        for piece in pieces:
            count[piece] = 0
            count[piece.upper()] = 0
        score = 0
        for key in map:
            count[str(map[key])] += 1
        for piece in pieces:
            if max_player and self.board.turn == chess.WHITE:
                score += (count[piece.upper()] - count[piece]) * ref[piece]
            elif max_player and self.board.turn == chess.BLACK:
                score += (count[piece] - count[piece.upper()]) * ref[piece]
            elif not max_player and self.board.turn == chess.WHITE:
                score += (count[piece] - count[piece.upper()]) * ref[piece]
            elif not max_player and self.board.turn == chess.BLACK:
                score += (count[piece.upper()] - count[piece]) * ref[piece]
        return score

    def alpha_beta_pruning(self, alpha, beta, depth, max_player) -> tuple:
        """Returns the evaluation of the current board position and the best move for the current player, using alpha-beta pruning with a depth of `depth`, and the player to maximize the evaluation is `max_player`."""
        global storage
        # print(self.hash)
        if depth == 0 or self.board.is_game_over():
            return self.eval(max_player), None
        if self.hash == 2956996370746770784263:
            print('hehehe')
        if max_player:
            max_eval = -math.inf
            best_move = None
            for move in self.get_ordered_moves():
                new = self.get_child(move)
                if (new.hash) in storage:
                    eval, _move = storage[new.hash]
                else:
                    eval, _move = new.alpha_beta_pruning(alpha, beta, depth - 1, not max_player)
                if eval >= max_eval:
                    best_move = move
                max_eval = max(max_eval, eval)
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            storage[self.hash] = (max_eval, best_move)
            return max_eval, best_move
        else:
            min_eval = math.inf
            best_move = None
            for move in self.get_ordered_moves():
                new = self.get_child(move)
                if (new.hash) in storage:
                    eval, _move = storage[new.hash]
                else:
                    eval, _move = new.alpha_beta_pruning(alpha, beta, depth - 1, not max_player)
                if eval <= min_eval:
                    best_move = move
                min_eval = min(min_eval, eval)
                beta = min(beta, eval)
                if beta <= alpha:
                    break
            storage[self.hash] = (min_eval, best_move)
            return min_eval, best_move
    
    def alphabet(self, depth) -> None:
        """Makes the best move for the current player using alpha-beta pruning until the depth of `depth`."""
        global storage
        _val, move = self.alpha_beta_pruning(-math.inf, math.inf, depth, True)
        for i in range(depth):
            self.make_move(move)
            if self.board.is_game_over():
                return
            _val, move = self.alpha_beta_pruning(-math.inf, math.inf, depth-i, True)
    
    def get_move(self, depth):
        """Returns the best move for the current player using alpha-beta pruning with a depth of `depth`."""
        _val, move = self.alpha_beta_pruning(-math.inf, math.inf, depth, True)
        return _val, move

    def __str__(self) -> str:
        """Returns the string representation of the board."""
        return self.board.__str__()

    def __repr__(self) -> str:
        """Returns the string representation of the board."""
        return self.board.__repr__()
    
if __name__ == '__main__':
    with open("mate_in_2.json", "r") as file:
        mate_in_two=json.load(file)
    index=0
    for key, value in mate_in_two.items():
        board=Engine(key)
        if board.board.turn == True:
            continue
        index+=1
        print(board.alpha_beta_pruning(-math.inf, math.inf, 4, board.board.turn))        
        if (index==20):
            break

