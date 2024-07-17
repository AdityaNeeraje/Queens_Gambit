import copy  # use it for deepcopy if needed
import math
import logging
import json
import sys
import chess
from chess import Move

logging.basicConfig(format='%(levelname)s - %(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S',
                    level=logging.INFO)

# Global variable to keep track of visited board positions. This is a dictionary with keys as self.boards as str and
# value represents the maxmin value. Use the get_boards_str function in History class to get the key corresponding to
# self.boards.
board_positions_val_dict = {}
# Global variable to store the visited histories in the process of alpha beta pruning.
visited_histories_list = []
winning_moves={}
dictionary_of_positions={}

class History:
    def __init__(self, num_boards=1, history=None):
        """
        # self.history : Eg: [0, 4, 2, 5]
            keeps track of sequence of actions played since the beginning of the game.
            Each action is an integer between 0-(9n-1) representing the square in which the move will be played as shown
            below (n=2 is the number of boards).

             Board 1
              ___ ___ ____
             |_0_|_1_|_2_|
             |_3_|_4_|_5_|
             |_6_|_7_|_8_|

             Board 2
              ____ ____ ____
             |_9_|_10_|_11_|
             |_12_|_13_|_14_|
             |_15_|_16_|_17_|

        # self.boards
            empty squares are represented using '0' and occupied squares are 'x'.
            Eg: [['x', '0', 'x', '0', 'x', 'x', '0', '0', '0'], ['0', 0', '0', 0', '0', 0', '0', 0', '0']]
            for two board game

            Board 1
              ___ ___ ____
             |_x_|___|_x_|
             |___|_x_|_x_|
             |___|___|___|

            Board 2
              ___ ___ ____
             |___|___|___|
             |___|___|___|
             |___|___|___|

        # self.player: 1 or 2
            Player whose turn it is at the current history/board

        :param num_boards: Number of boards in the game of Notakto.
        :param history: list keeps track of sequence of actions played since the beginning of the game.
        """
        self.num_boards = num_boards
        if history is not None:
            self.history = history
        else:
            self.history = 0
        # Maintain a list to keep track of active boards
        # self.active_board_stats = self.check_active_boards()
        # self.current_player = self.get_current_player()
    
    def check_active_boards(self):
        """ Return a list to keep track of active boards

        :return: list of int (zeros and ones)
                Eg: [0, 1]
                for two board game

                Board 1
                  ___ ___ ____
                 |_x_|_x_|_x_|
                 |___|_x_|_x_|
                 |___|___|___|

                Board 2
                  ___ ___ ____
                 |___|___|___|
                 |___|___|___|
                 |___|___|___|
        """
        active_board_stat = 0
        for i in range(self.num_boards):
            if not self.is_board_win((self.history>>(9*i))&511):
                active_board_stat+=(1<<i)
        return active_board_stat

    @staticmethod
    def is_board_win(i):
        if i&7==7 or i&(7<<3) == 7<<3 or i&(7<<6) == 7<<6 or i&73 == 73 or i&146 == 146 or i&292 == 292 or i&273 == 273 or i&84 == 84:
            return True
        return False

    def get_boards_str(self):
        return tuple(i for i in range(9*self.num_boards) if self.history&(1<<i) > 0)


    def is_win(self):
        for i in range(self.num_boards):
            if not self.is_board_win((self.history>>(9*i))&511):
                return False
        return True

    def get_valid_actions(self):
        #Note: Expects history to be as a list of strings, and returns a list of strings
        self.active_board_stats=self.check_active_boards()
        valid_boards=[i for i in range(self.num_boards) if self.active_board_stats&(1<<i)>0]
        result=[]
        for move in [4, 0, 2, 6, 8, 1, 3, 5, 7]:
            result+= [9*i+move for i in valid_boards if self.history&(1<<(9*i+move)) == 0]
        return result
    
    def is_terminal_history(self):
        # Feel free to implement this in anyway if needed
        pass

    def get_value_given_terminal_history(self):
        # Feel free to implement this in anyway if needed
        pass


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
    for action in legal_moves:
        move=str(action)
        moves_value[move]=0
        if len(move) == 5:
            if (move[-1] == 'r' or move[-1]=="b" or move[-1] =="n"):
                continue
            else:
                if white_to_play:
                    moves_value[move]+=values['Q']
                else:
                    moves_value[move]-=values['Q']
        board_obj.push(action)
        if board_obj.is_checkmate():
            board_obj.pop()
            return [action]
        board_obj.pop()
        resulting_list.append(action)
        moves_value[move]-=dictionary_of_positions[chess.parse_square(move[2:4])]
        moves_value[move]*=1000
    return list(sorted(resulting_list, key=lambda action: -moves_value[str(action)]))


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
    global dictionary_of_positions
    if depth==0:
        if board_obj.turn == max_player_flag:
            result = value_for_white(board_obj)
            return result
        else:
            result = -value_for_white(board_obj)
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
            board_obj.push(action)
            best=max(best, alpha_beta_pruning(board_obj, alpha, beta, not max_player_flag, depth-1))
            alpha=max(alpha, best)
            board_obj.pop()
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
            board_obj.push(action)
            best=min(best, alpha_beta_pruning(board_obj, alpha, beta, not max_player_flag, depth-1))
            beta=min(beta, best)
            board_obj.pop()
            dictionary_of_positions[moved_from]=value_of_piece_moved
            dictionary_of_positions[moved_to]=value_of_piece_captured
            if beta<=alpha:
                break
        return best
    
def fill_dictionary_of_positions(board_obj):
    global dictionary_of_positions
    for position in range(64):
        if board_obj.piece_at(position) is not None:
            dictionary_of_positions[position]=\
                values[board_obj.piece_at(position).symbol()]
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
        print(solve_alpha_beta_pruning(board, -math.inf, math.inf, board.turn, 4))        
        if (index==20):
            break