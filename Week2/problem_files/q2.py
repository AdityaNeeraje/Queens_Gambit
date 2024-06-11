import copy  # use it for deepcopy if needed
import math
import logging
import json
import sys

logging.basicConfig(format='%(levelname)s - %(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S',
                    level=logging.INFO)

# Global variable to keep track of visited board positions. This is a dictionary with keys as self.boards as str and
# value represents the maxmin value. Use the get_boards_str function in History class to get the key corresponding to
# self.boards.
board_positions_val_dict = {}
# Global variable to store the visited histories in the process of alpha beta pruning.
visited_histories_list = []
winning_moves={}

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


def alpha_beta_pruning(history_obj, alpha, beta, max_player_flag):
    """
        Calculate the maxmin value given a History object using alpha beta pruning. Use the specific move order to
        speedup (more pruning, less memory).

    :param history_obj: History class object
    :param alpha: -math.inf
    :param beta: math.inf
    :param max_player_flag: Bool (True if maximizing player plays)
    :return: float
    """
    global board_positions_val_dict, visited_histories_list
    if history_obj.history in board_positions_val_dict:
        return board_positions_val_dict[history_obj.history]
    visited_histories_list.append(history_obj.history)
    if history_obj.is_win():
        if max_player_flag:
            fill_up_to_equivalence(history_obj.history, 1, history_obj.num_boards)
            return 1
        fill_up_to_equivalence(history_obj.history, -1, history_obj.num_boards)
        return -1
    if max_player_flag:
        best=-math.inf
        for action in history_obj.get_valid_actions():
            best=max(best,alpha_beta_pruning(History(history=history_obj.history+(1<<action), num_boards=history_obj.num_boards),alpha,beta,False))
            alpha=max(alpha,best)
            if beta<=alpha:
                break
        fill_up_to_equivalence(history_obj.history, best, history_obj.num_boards)
        return best
    else:
        best=math.inf
        for action in history_obj.get_valid_actions():
            best=min(best,alpha_beta_pruning(History(history=history_obj.history+(1<<action), num_boards=history_obj.num_boards),alpha,beta,True))
            beta=min(beta,best)
            if beta<=alpha:
                break
        fill_up_to_equivalence(history_obj.history, best, history_obj.num_boards)
        return best


def fill_up_to_equivalence(history, value, num_boards):
    global board_positions_val_dict
    # board_positions_val_dict[history]=value
    # return
    funcs=[
        lambda i: i, # Identity
        lambda i: 3*(i//3)+2-i%3, # Reflection about the vertical
        lambda i: 3*(i%3)+2-i//3, # Rotation 90 degree
        lambda i: 3*(i%3)+i//3, # Reflection about the diagonal from 0 to 8
        lambda i: 3*(2-i//3)+2-i%3, # Rotation 180 degree
        lambda i: 3*(2-i//3)+i%3, # Reflection about the horizontal
        lambda i: 3*(2-i%3)+i//3, # Rotation 270 degree
        lambda i: 3*(2-i%3)+2-i//3 # Reflection about the diagonal from 2 to 6
    ]
    state_list=[i for i in range(9*num_boards) if history&(1<<i) > 0]
    for i in range(8**num_boards):
        new_state=sum([1<<(9*(int(character)//9)+funcs[int((i//(8**(int(character)//9)))%8)](int(character)%9)) for character in state_list])
        board_positions_val_dict[new_state]=value
        if num_boards==2:
            new_state=new_state//512+(new_state%512)*512
            board_positions_val_dict[new_state]=value
        if num_boards==3:
            board1=new_state%512
            board2=(new_state>>9)%512
            board3=new_state>>18
            new_state=board1+(board2<<18)+(board3<<9)
            board_positions_val_dict[new_state]=value
            new_state=board2+(board3<<18)+(board1<<9)
            board_positions_val_dict[new_state]=value
            new_state=board2+(board1<<18)+(board3<<9)
            board_positions_val_dict[new_state]=value
            new_state=board3+(board1<<18)+(board2<<9)
            board_positions_val_dict[new_state]=value
            new_state=board3+(board2<<18)+(board1<<9)
            board_positions_val_dict[new_state]=value


def fill_win_up_to_equivalence(history, result, num_boards):
    global winning_moves
    # winning_moves[history]=value
    # return
    funcs=[
        lambda i: i, # Identity
        lambda i: 3*(i//3)+2-i%3, # Reflection about the vertical
        lambda i: 3*(i%3)+2-i//3, # Rotation 90 degree
        lambda i: 3*(i%3)+i//3, # Reflection about the diagonal from 0 to 8
        lambda i: 3*(2-i//3)+2-i%3, # Rotation 180 degree
        lambda i: 3*(2-i//3)+i%3, # Reflection about the horizontal
        lambda i: 3*(2-i%3)+i//3, # Rotation 270 degree
        lambda i: 3*(2-i%3)+2-i//3 # Reflection about the diagonal from 2 to 6
    ]
    state_list=[i for i in range(9*num_boards) if history&(1<<i) > 0]
    for i in range(8**num_boards):
        new_state=sum([1<<(9*(int(character)//9)+funcs[int((i//(8**(int(character)//9)))%8)](int(character)%9)) for character in state_list])
        winning_move=9*(int(result)//9)+funcs[int((i//(8**(int(result)//9)))%8)](int(result)%9)
        winning_moves[new_state]=winning_move
        if num_boards==2:
            new_state=new_state//512+(new_state%512)*512
            winning_moves[new_state]=winning_move
        if num_boards==3:
            board1=new_state%512
            board2=(new_state>>9)%512
            board3=new_state>>18
            new_state=board1+(board2<<18)+(board3<<9)
            winning_moves[new_state]=winning_move
            new_state=board2+(board3<<18)+(board1<<9)
            winning_moves[new_state]=winning_move
            new_state=board2+(board1<<18)+(board3<<9)
            winning_moves[new_state]=winning_move
            new_state=board3+(board1<<18)+(board2<<9)
            winning_moves[new_state]=winning_move
            new_state=board3+(board2<<18)+(board1<<9)
            winning_moves[new_state]=winning_move

def maxmin(history_obj, max_player_flag):
    """
        Calculate the maxmin value given a History object using maxmin rule. Store the value of already visited
        board positions to speed up, avoiding recursive calls for a different history with the same board position.
    :param history_obj: History class object
    :param max_player_flag: True if the player is maximizing player
    :return: float
    """
    # Global variable to keep track of visited board positions. This is a dictionary with keys as str version of
    # self.boards and value represents the maxmin value. Use the get_boards_str function in History class to get
    # the key corresponding to self.boards.
    global board_positions_val_dict, winning_moves
    if history_obj.history in winning_moves:        
        return board_positions_val_dict[history_obj.history]
    if history_obj.is_win():
        if max_player_flag:
            return 1
        return -1
    if max_player_flag:
        max_val=-2
        winning_move=None
        for action in history_obj.get_valid_actions():
            new_value=maxmin(History(history=history_obj.history+(1<<action), num_boards=history_obj.num_boards),False)
            if new_value>max_val:
                max_val=new_value
                winning_move=action
        fill_up_to_equivalence(history_obj.history, max_val, history_obj.num_boards)
        fill_win_up_to_equivalence(history_obj.history, winning_move, history_obj.num_boards)
        return max_val
    else:
        min_val=2
        winning_move=None
        for action in history_obj.get_valid_actions():
            new_value=maxmin(History(history=history_obj.history+(1<<action), num_boards=history_obj.num_boards),True)
            if new_value<min_val:
                min_val=new_value
                winning_move=action
        fill_up_to_equivalence(history_obj.history, min_val, history_obj.num_boards)
        fill_win_up_to_equivalence(history_obj.history, winning_move, history_obj.num_boards)
        return min_val

def solve_alpha_beta_pruning(history_obj, alpha, beta, max_player_flag):
    global visited_histories_list
    val = alpha_beta_pruning(history_obj, alpha, beta, max_player_flag)
    return val, visited_histories_list


if __name__ == "__main__":
    if len(sys.argv) != 2 or not sys.argv[1].isdigit() or int(sys.argv[1])<1 or int(sys.argv[1])>3:
        n=2
    else:
        n=int(sys.argv[1])
    logging.info("start")
    logging.info("alpha beta pruning")
    value, visited_histories = solve_alpha_beta_pruning(History(history=0, num_boards=n), -math.inf, math.inf, True)
    logging.info("maxmin value {}".format(value))
    logging.info("Number of histories visited {}".format(len(visited_histories)))
    logging.info("maxmin value {}".format(maxmin(History(history=0, num_boards=n), True)))
    output_dict={}
    # print(len(board_positions_val_dict))
    for key, value in winning_moves.items():
        output_dict["".join(["x" if key&(1<<i)>0 else "0" for i in range(9*n)])]=value
    with open("history_values.json", "w") as f:
        json.dump(output_dict, f, indent=4)
    print(len(output_dict))
    logging.info("end")
