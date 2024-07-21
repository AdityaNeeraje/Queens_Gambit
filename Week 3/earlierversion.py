import copy  # use it for deepcopy if needed
import math
import logging
import json
import sys
import chess
from chess import Move

board_positions_val_dict = {}
visited_histories_list = []
winning_moves={}
dictionary_of_positions={}
total_value=0
counter=0

values={'p':-1,'P':1,'r':-10,'R':10,'n':-6,'N':6,'b':-6,'B':6,'q':-50,'Q':50,'k':-1000,'K':1000,'/':0,'1':0,'2':0,'3':0,'4':0,'5':0,'6':0,'7':0,'8':0}
def value_for_white(board_obj):
    if moves_value.get(board_obj.board_fen()) is not None:
        return moves_value[board_obj.board_fen()]
    piece_map=board_obj.board_fen()
    return sum([values[piece] for piece in piece_map])

moves_value=dict()
def order_moves(board_obj, white_to_play):    
    global moves_value
    legal_moves=board_obj.legal_moves
    resulting_list=[]
    moves_value={}
    for action in legal_moves:
        move=str(action)
        moves_value[move]=0
        board_obj.push(action)
        if board_obj.is_checkmate():
            board_obj.pop()
            return [action]
        moves_value[move] = len(list(board_obj.legal_moves))
        board_obj.pop()
        resulting_list.append(action)
        moves_value[move]*=1000
        if len(move) == 5:
            if (move[-1] == 'r' or move[-1]=="b" or move[-1] =="n"):
                continue
            else:
                if white_to_play:
                    moves_value[move]-=values['Q']
                else:
                    moves_value[move]+=values['Q']
        moves_value[move]+=dictionary_of_positions[chess.parse_square(move[2:4])]
    return list(sorted(resulting_list, key=lambda action: moves_value[str(action)]))


def alpha_beta_pruning(board_obj, alpha, beta, max_player_flag, depth=3):
    """
        Calculate the maxmin value given a History object using alpha beta pruning. Use the specific move order to
        speedup (more pruning, less memory).

    :param history_obj: History class object
    :param alpha: -math.inf
    :param beta: math.inf
    :param max_player_flag: Bool (True if maximizing player plays)
    :return: float
    """
    global dictionary_of_positions, total_value, counter
    counter+=1
    if depth==0:
        if board_obj.turn == max_player_flag:
            result = total_value
            return result
        else:
            result = -total_value
            return result
    if board_obj.is_game_over():
        if board_obj.is_checkmate():
            if max_player_flag:
                return -math.inf
            else:
                return math.inf
        if board_obj.is_stalemate():
            return 0
    if max_player_flag:
        best=-math.inf
        for action in order_moves(board_obj, max_player_flag):
            move=str(action)
            moved_from=chess.parse_square(move[0:2])
            moved_to=chess.parse_square(move[2:4])
            value_of_piece_captured=dictionary_of_positions[moved_to]
            value_of_piece_moved=dictionary_of_positions[moved_from]
            dictionary_of_positions[moved_from]=0
            dictionary_of_positions[moved_to]=value_of_piece_moved
            total_value-=value_of_piece_captured
            board_obj.push(action)
            best=max(best, alpha_beta_pruning(board_obj, alpha, beta, not max_player_flag, depth-1))
            alpha=max(alpha, best)
            board_obj.pop()
            total_value+=value_of_piece_captured
            dictionary_of_positions[moved_from]=value_of_piece_moved
            dictionary_of_positions[moved_to]=value_of_piece_captured
            if beta<=alpha:
                break
        return best
    else:
        best=math.inf
        for action in order_moves(board_obj, max_player_flag):
            move=str(action)
            moved_from=chess.parse_square(move[0:2])
            moved_to=chess.parse_square(move[2:4])
            value_of_piece_captured=dictionary_of_positions[moved_to]
            value_of_piece_moved=dictionary_of_positions[moved_from]
            dictionary_of_positions[moved_from]=0
            dictionary_of_positions[moved_to]=value_of_piece_moved
            total_value-=value_of_piece_captured
            board_obj.push(action)
            best=min(best, alpha_beta_pruning(board_obj, alpha, beta, not max_player_flag, depth-1))
            beta=min(beta, best)
            board_obj.pop()
            total_value+=value_of_piece_captured
            dictionary_of_positions[moved_from]=value_of_piece_moved
            dictionary_of_positions[moved_to]=value_of_piece_captured
            if beta<=alpha:
                break
        return best
    
def fill_dictionary_of_positions(board_obj):
    global dictionary_of_positions, total_value
    total_value=0
    for position in range(64):
        if board_obj.piece_at(position) is not None:
            dictionary_of_positions[position]=\
                values[board_obj.piece_at(position).symbol()]
            total_value+=dictionary_of_positions[position]
        else:
            dictionary_of_positions[position]=0

def solve_alpha_beta_pruning(history_obj, alpha, beta, max_player_flag, depth=3):
    global visited_histories_list
    fill_dictionary_of_positions(history_obj)
    return alpha_beta_pruning(history_obj, alpha, beta, max_player_flag, depth)


if __name__ == "__main__":
    with open("mate_in_2.json", "r") as f:
        mate_in_two=json.load(f)
    index=0
    for key, value in mate_in_two.items():
        board=chess.Board(key)
        if board.turn == True:
            continue
        index+=1
        print(solve_alpha_beta_pruning(board, -math.inf, math.inf, board.turn, 6))
        print("Number of calls: ", counter)
        counter=0
        if (index==20):
            break