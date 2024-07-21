import copy  # use it for deepcopy if needed
import math
import logging
import json
import sys
import chess
from chess import Move

board_positions_val_dict = {}
visited_histories_list = []
winning_moves = {}
dictionary_of_positions = {}
total_value = 0
counter = 0

pst = {
    'P': (0, 0, 0, 0, 0, 0, 0, 0,
          -31, 8, -7, -37, -36, -14, 3, -31,
          -22, 9, 5, -11, -10, -2, 3, -19,
          -26, 3, 10, 9, 6, 1, 0, -23,
          -17, 16, -2, 15, 14, 0, 15, -13,
          7, 29, 21, 44, 40, 31, 44, 7,
          78, 83, 86, 73, 102, 82, 85, 90,
          0, 0, 0, 0, 0, 0, 0, 0),
    'N': (-74, -23, -26, -24, -19, -35, -22, -69,
          -23, -15, 2, 0, 2, 0, -23, -20,
          -18, 10, 13, 22, 18, 15, 11, -14,
          -1, 5, 31, 21, 22, 35, 2, 0,
          24, 24, 45, 37, 33, 41, 25, 17,
          10, 67, 1, 74, 73, 27, 62, -2,
          -3, -6, 100, -36, 4, 62, -4, -14,
          -66, -53, -75, -75, -10, -55, -58, -70),
    'B': (-7, 2, -15, -12, -14, -15, -10, -10,
          19, 20, 11, 6, 7, 6, 20, 16,
          14, 25, 24, 15, 8, 25, 20, 15,
          13, 10, 17, 23, 17, 16, 0, 7,
          25, 17, 20, 34, 26, 25, 15, 10,
          -9, 39, -32, 41, 52, -10, 28, -14,
          -11, 20, 35, -42, -39, 31, 2, -22,
          -59, -78, -82, -76, -23, -107, -37, -50),
    'R': (-30, -24, -18, 5, -2, -18, -31, -32,
          -53, -38, -31, -26, -29, -43, -44, -53,
          -42, -28, -42, -25, -25, -35, -26, -46,
          -28, -35, -16, -21, -13, -29, -46, -30,
          0, 5, 16, 13, 18, -4, -9, -6,
          19, 35, 28, 33, 45, 27, 25, 15,
          55, 29, 56, 67, 55, 62, 34, 60,
          35, 29, 33, 4, 37, 33, 56, 50),
    'Q': (-39, -30, -31, -13, -31, -36, -34, -42,
          -36, -18, 0, -19, -15, -15, -21, -38,
          -30, -6, -13, -11, -16, -11, -16, -27,
          -14, -15, -2, -5, -1, -10, -20, -22,
          1, -16, 22, 17, 25, 20, -13, -6,
          -2, 43, 32, 60, 72, 63, 43, 2,
          14, 32, 60, -10, 20, 76, 57, 24,
          6, 1, -8, -104, 69, 24, 88, 26),
    'K': (17, 30, -3, -14, 6, -1, 40, 18,
          -4, 3, -14, -50, -57, -18, 13, 4,
          -47, -42, -43, -79, -64, -32, -29, -32,
          -55, -43, -52, -28, -51, -47, -8, -50,
          -55, 50, 11, -4, -19, 13, 0, -49,
          -62, 12, -57, 44, -67, 28, 37, -31,
          -32, 10, 55, 56, 56, 55, 10, 3,
          4, 54, 47, -99, -99, 60, 83, -62)
}

values = {'p': -100, 'P': 100, 'r': -479, 'R': 479, 'n': -280, 'N': 280, 'b': -320, 'B': 320, 'q': -929, 'Q': 929, 'k': -60000, 'K': 60000, '/': 0, '1': 0, '2': 0, '3': 0, '4': 0, '5': 0, '6': 0, '7': 0, '8': 0}

def value_for_white(board_obj):
    if moves_value.get(board_obj.board_fen()) is not None:
        return moves_value[board_obj.board_fen()]
    piece_map = board_obj.board_fen()
    return sum([values[piece] for piece in piece_map])

moves_value = dict()
def order_moves(board_obj, white_to_play):
    global moves_value
    legal_moves = board_obj.legal_moves
    resulting_list = []
    moves_value = {}
    for action in legal_moves:
        move = str(action)
        moves_value[move] = 0
        board_obj.push(action)
        if board_obj.is_checkmate():
            board_obj.pop()
            return [action]
        moves_value[move] = len(list(board_obj.legal_moves))
        board_obj.pop()
        moves_value[move] *= 1000000
        if len(move) == 5:
            if move[-1] == 'r' or move[-1] == "b" or move[-1] == "n":
                continue
            else:
                if white_to_play:
                    moves_value[move] -= values['Q']
                else:
                    moves_value[move] += values['Q']
        resulting_list.append(action)
        symbol = board_obj.piece_at(chess.parse_square(move[2:4]))
        if symbol is not None:
            if 'a' <= symbol.symbol() <= 'z':
                moves_value[move] -= pst[symbol.symbol().upper()][63-chess.parse_square(move[2:4])] + values[symbol.symbol()]
            else:
                moves_value[move] += pst[symbol.symbol()][chess.parse_square(move[2:4])] + values[symbol.symbol()]
    return list(sorted(resulting_list, key=lambda action: moves_value[str(action)]))

def alpha_beta_pruning(board_obj, alpha, beta, max_player_flag, depth=3):
    global dictionary_of_positions, total_value, counter
    counter += 1
    if depth == 0:
        if board_obj.turn == max_player_flag:
            result = total_value
            return (None, result)
        else:
            result = -total_value
            return (None, result)
    if board_obj.is_game_over():
        if board_obj.is_checkmate():
            if max_player_flag:
                return (None, -math.inf)
            else:
                return (None, math.inf)
        if board_obj.is_stalemate():
            return (None, 0)
    best_move = None
    if max_player_flag:
        best_value = -math.inf
        for action in order_moves(board_obj, max_player_flag):
            move = str(action)
            moved_from = chess.parse_square(move[0:2])
            moved_to = chess.parse_square(move[2:4])
            value_of_piece_captured = dictionary_of_positions[moved_to]
            value_of_piece_moved = dictionary_of_positions[moved_from]
            dictionary_of_positions[moved_from] = 0
            piece_moved = board_obj.piece_at(moved_from).symbol()
            if piece_moved.islower():
                dictionary_of_positions[moved_to] = -pst[piece_moved.upper()][63-moved_to] + values[piece_moved]
            else:
                dictionary_of_positions[moved_to] = pst[piece_moved][moved_to] + values[piece_moved]
            total_value -= value_of_piece_captured
            board_obj.push(action)
            _, value = alpha_beta_pruning(board_obj, alpha, beta, not max_player_flag, depth-1)
            if value > best_value:
                best_value = value
                best_move = action
            alpha = max(alpha, best_value)
            board_obj.pop()
            total_value += value_of_piece_captured
            dictionary_of_positions[moved_from] = value_of_piece_moved
            dictionary_of_positions[moved_to] = value_of_piece_captured
            if beta <= alpha:
                break
        return (best_move, best_value)
    else:
        best_value = math.inf
        for action in order_moves(board_obj, max_player_flag):
            move = str(action)
            moved_from = chess.parse_square(move[0:2])
            moved_to = chess.parse_square(move[2:4])
            value_of_piece_captured = dictionary_of_positions[moved_to]
            value_of_piece_moved = dictionary_of_positions[moved_from]
            dictionary_of_positions[moved_from] = 0
            dictionary_of_positions[moved_to] = value_of_piece_moved
            piece_moved = board_obj.piece_at(moved_from).symbol()
            total_value -= value_of_piece_captured
            board_obj.push(action)
            _, value = alpha_beta_pruning(board_obj, alpha, beta, not max_player_flag, depth-1)
            if value < best_value:
                best_value = value
                best_move = action
            beta = min(beta, best_value)
            board_obj.pop()
            total_value += value_of_piece_captured
            dictionary_of_positions[moved_from] = value_of_piece_moved
            dictionary_of_positions[moved_to] = value_of_piece_captured
            if beta <= alpha:
                break
        return (best_move, best_value)

def fill_dictionary_of_positions(board_obj):
    global dictionary_of_positions, total_value
    total_value = 0
    for position in range(64):
        if board_obj.piece_at(position) is not None:
            symbol = board_obj.piece_at(position).symbol()
            if 'a' <= symbol <= 'z':
                dictionary_of_positions[position] = -pst[symbol.upper()][63-position] + values[symbol]
            else:
                dictionary_of_positions[position] = pst[symbol][position] + values[symbol]
            total_value += dictionary_of_positions[position]
        else:
            dictionary_of_positions[position] = 0

def solve_alpha_beta_pruning(history_obj, alpha, beta, max_player_flag, depth=3):
    global visited_histories_list
    fill_dictionary_of_positions(history_obj)
    return alpha_beta_pruning(history_obj, alpha, beta, max_player_flag, depth)

if __name__ == "__main__":
    with open("mate_in_2.json", "r") as f:
        mate_in_two = json.load(f)
    index = 0
    for key, value in mate_in_two.items():
        board = chess.Board(key)
        if board.turn == True:
            continue
        index += 1
        best_move, best_value = solve_alpha_beta_pruning(board, -math.inf, math.inf, board.turn, 6)
        print(f"Best move: {best_move}, Utility: {best_value}")
        print("Number of calls: ", counter)
        counter = 0
        if index == 20:
            break
