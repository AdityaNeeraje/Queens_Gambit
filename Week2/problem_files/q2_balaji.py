import copy  # use it for deepcopy if needed
import math
import logging

from matplotlib.pyplot import hist

logging.basicConfig(format='%(levelname)s - %(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S',
                    level=logging.INFO)

# Global variable to keep track of visited board positions. This is a dictionary with keys as self.boards as str and
# value represents the maxmin value. Use the get_boards_str function in History class to get the key corresponding to
# self.boards.
board_positions_val_dict = {}
# Global variable to store the visited histories in the process of alpha beta pruning.
visited_histories_list = []

mdp = {}

class History:
    def __init__(self, num_boards=2, history=None):
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
            self.boards = self.get_boards()
        else:
            self.history = []
            self.boards = []
            for i in range(self.num_boards):
                # empty boards
                self.boards.append(['0', '0', '0', '0', '0', '0', '0', '0', '0'])
        # Maintain a list to keep track of active boards
        self.active_board_stats = self.check_active_boards()
        self.current_player = self.get_current_player()

    def get_boards(self):
        """ Play out the current self.history and get the boards corresponding to the history.

        :return: list of lists
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
        """
        boards = []
        for i in range(self.num_boards):
            boards.append(['0', '0', '0', '0', '0', '0', '0', '0', '0'])
        for i in range(len(self.history)):
            board_num = math.floor(self.history[i] / 9)
            play_position = self.history[i] % 9
            boards[board_num][play_position] = 'x'
        return boards

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
        active_board_stat = []
        for i in range(self.num_boards):
            if self.is_board_win(self.get_boards()[i]):
                active_board_stat.append(0)
            else:
                active_board_stat.append(1)
        return active_board_stat

    @staticmethod
    def is_board_win(board):
        for i in range(3):
            if board[3 * i] == board[3 * i + 1] == board[3 * i + 2] != '0':
                return True

            if board[i] == board[i + 3] == board[i + 6] != '0':
                return True

        if board[0] == board[4] == board[8] != '0':
            return True

        if board[2] == board[4] == board[6] != '0':
            return True
        return False

    def get_current_player(self):
        """
        Get player whose turn it is at the current history/board
        :return: 1 or 2
        """
        total_num_moves = len(self.history)
        if total_num_moves % 2 == 0:
            return 1
        else:
            return 2

    def get_boards_str(self):
        boards_str = ""
        for i in range(self.num_boards):
            boards_str = boards_str + ''.join([str(j) for j in self.get_boards()[i]])
        return boards_str

    def is_win(self):
        # Feel free to implement this in anyway if needed
        for board in self.get_boards():
            if not self.is_board_win(board):
                return False
        return True

    def get_valid_actions(self):
        # Feel free to implement this in anyway if needed
        valid_actions = []
        self.boards = self.get_boards()
        for i in range(self.num_boards):
            if self.check_active_boards()[i] == 1:
                for j in range(9):
                    if self.boards[i][j] == '0':
                        valid_actions.append(i * 9 + j)
        return valid_actions

    def get_valid_actions_(self):
        valid_actions = []
        for i in range(self.num_boards):
            if self.check_active_boards()[i] == 1:
                for j in range(9):
                    if self.get_boards()[i][j] == '0':
                        valid_actions.append(i * 9 + j)
        new_valid_actions = []
        for i in range(len(valid_actions)):
            if valid_actions[i] in [9*j + 4 for j in range(self.num_boards)]:
                new_valid_actions.append(valid_actions[i])
        for i in range(len(valid_actions)):
            corner_list = []
            corner_list.extend([9*j for j in range(self.num_boards)])
            corner_list.extend([9*j + 2 for j in range(self.num_boards)])
            corner_list.extend([9*j + 6 for j in range(self.num_boards)])
            corner_list.extend([9*j + 8 for j in range(self.num_boards)])
            if valid_actions[i] in corner_list:
                new_valid_actions.append(valid_actions[i])
        for i in range(len(valid_actions)):
            corner_list = []
            corner_list.extend([9*j for j in range(self.num_boards)])
            corner_list.extend([9*j + 2 for j in range(self.num_boards)])
            corner_list.extend([9*j + 6 for j in range(self.num_boards)])
            corner_list.extend([9*j + 8 for j in range(self.num_boards)])
            if not (valid_actions[i] in corner_list or valid_actions[i] in [9*j + 4 for j in range(self.num_boards)]):
                new_valid_actions.append(valid_actions[i])
        # if set(new_valid_actions) != set(self.get_valid_actions()):
        #     print('Hey', new_valid_actions, self.get_valid_actions())
        return new_valid_actions

    def is_terminal_history(self):
        # Feel free to implement this in anyway if needed
        if self.is_win():
            return True

    def get_value_given_terminal_history(self):
        # Feel free to implement this in anyway if needed
        if self.is_win():
            return 1
        else:
            return -1
        
def vertical_flip(history_string):
    return history_string[6:]+history_string[3:6]+history_string[:3]

def horizontal_flip(history_string):
    return history_string[2::-1]+history_string[5:2:-1]+history_string[8:5:-1]

def diagonal_flip(history_string):
    return history_string[0::3]+history_string[1::3]+history_string[2::3]
        
def get_mirrors(history_string):
    mirrors = set()
    board1 = history_string[:9]
    board2 = history_string[9:]
    board1_mirrors = set()
    board2_mirrors = set()
    board1_mirrors.add(board1)
    board1_mirrors.add(vertical_flip(board1))
    board1_mirrors.add(horizontal_flip(board1))
    board1_mirrors.add(horizontal_flip(vertical_flip(board1)))
    board1_mirrors.add(diagonal_flip(board1))
    board1_mirrors.add(diagonal_flip(vertical_flip(board1)))
    board1_mirrors.add(diagonal_flip(horizontal_flip(board1)))
    board1_mirrors.add(diagonal_flip(horizontal_flip(vertical_flip(board1))))
    board1_mirrors = list(board1_mirrors)
    if board2 == "":
        return list(board1_mirrors)
    board2_mirrors = get_mirrors(board2)
    for i in range(len(board1_mirrors)):
        for j in range(len(board2_mirrors)):
            mirrors.add(board1_mirrors[i]+board2_mirrors[j])
    return list(mirrors)
    


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
    # These two already given lines track the visited histories.
    global visited_histories_list, board_positions_val_dict
    visited_histories_list.append(history_obj.get_boards_str())
    # TODO implement
    if history_obj.is_terminal_history():
        if max_player_flag:
            return 1
        else:
            return -1
    if history_obj.get_boards_str() in board_positions_val_dict:
        return board_positions_val_dict[history_obj.get_boards_str()][0]
    if max_player_flag:
        v = -math.inf
        for action in history_obj.get_valid_actions_():
            new_history = History(history_obj.num_boards, copy.deepcopy(history_obj.history))
            new_history.history.append(action)
            new_history.boards = new_history.get_boards()
            # if new_history.get_boards_str() in board_positions_val_dict:
            #     value, mirror_obj = board_positions_val_dict[new_history.get_boards_str()]
            #     val1 = alpha_beta_pruning(new_history, alpha, beta, False)
            #     if value != val1:
            #         # print(val1, value, new_history.get_boards_str())
            #         print(mirror_obj.check_active_boards() == new_history.check_active_boards())
            # else:
            #     value = alpha_beta_pruning(new_history, alpha, beta, False)
            found = False
            for mirror in get_mirrors(new_history.get_boards_str()):
                if mirror in board_positions_val_dict:
                    value, mirror_obj = board_positions_val_dict[mirror]
                    val1 = alpha_beta_pruning(History(history_obj.num_boards, copy.deepcopy(new_history.history)), alpha, beta, False)
                    if value != val1:
                        print(val1, value, mirror, new_history.get_boards_str(), mirror_obj.history, new_history.history)
                        print(mirror_obj.get_valid_actions_(), new_history.get_valid_actions_())
                    found = True
                    break
            if not found:
                value = alpha_beta_pruning(History(history_obj.num_boards, copy.deepcopy(new_history.history)), alpha, beta, False)
            #     val1 = alpha_beta_pruning(History(history_obj.num_boards, copy.deepcopy(new_history.history)), alpha, beta, False)
            #     if value != val1:
            #         print('----', val1, value, mirror, new_history.get_boards_str())
                
            v = max(v, value)
            alpha = max(alpha, v)
            if beta <= alpha:
                break
        board_positions_val_dict[history_obj.get_boards_str()] = (v, history_obj)
        # mdp[history_obj.get_boards_str()] = action
        return v
    else:
        # if history_obj.get_boards_str() == "xxx"+"0"*6+"0"*9:
        #     print("here")
        #     print(history_obj.get_valid_actions())
        v = math.inf
        for action in history_obj.get_valid_actions_():
            new_history = History(history_obj.num_boards, copy.deepcopy(history_obj.history))
            new_history.history.append(action)
            new_history.boards = new_history.get_boards()
            # if new_history.get_boards_str() in board_positions_val_dict:
            #     value, mirror_obj = board_positions_val_dict[new_history.get_boards_str()]
            #     val1 = alpha_beta_pruning(new_history, alpha, beta, True)
            #     if value != val1:
            #         # print(val1, value, new_history.get_boards_str())
            #         print(mirror_obj.check_active_boards() == new_history.check_active_boards())
            # else:
            #     value = alpha_beta_pruning(new_history, alpha, beta, True)
            found = False
            for mirror in get_mirrors(new_history.get_boards_str()):
                if mirror in board_positions_val_dict:
                    value, mirror_obj = board_positions_val_dict[mirror]
                    val1 = alpha_beta_pruning(new_history, alpha, beta, True)
                    if value != val1:
                        print(val1, value, mirror, new_history.get_boards_str(), mirror_obj.history, new_history.history)
                    found = True
                    break
            if not found:
                value = alpha_beta_pruning(History(history_obj.num_boards, copy.deepcopy(new_history.history)), alpha, beta, True)
            v = min(v, value)
            beta = min(beta, v)
            if beta <= alpha:
                break
        board_positions_val_dict[history_obj.get_boards_str()] = (v, history_obj)
        # mdp[history_obj.get_boards_str()] = action
        return v
    # TODO implement


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
    global board_positions_val_dict
    # TODO implement
    if max_player_flag == (len(history_obj.history) % 2 == 1):
        print('Hey')
    if history_obj.is_terminal_history():
        if len(history_obj.history) % 2 == 0:
            return -1
        else:
            return 1
    if history_obj.get_boards_str() in board_positions_val_dict:
        return board_positions_val_dict[history_obj.get_boards_str()][0]
    if max_player_flag:
        max_val = -math.inf
        # best_action = -1
        for action in history_obj.get_valid_actions_():
            new_history = History(copy.deepcopy(history_obj.num_boards), copy.deepcopy(history_obj.history))
            new_history.history.append(action)
            new_history.boards = new_history.get_boards()
            if new_history.get_boards_str() in board_positions_val_dict:
                val, mirror_obj = board_positions_val_dict[new_history.get_boards_str()]
                val1 = maxmin(new_history, not max_player_flag)
                if val != val1:
                    print(val, val1, new_history.get_boards_str(), mirror_obj.get_boards_str(), new_history.history, mirror_obj.history)
            else:
                val = maxmin(new_history, False)
            # found = False
            # for mirror in get_mirrors(new_history.get_boards_str()):
            #     if mirror in board_positions_val_dict:
            #         val = board_positions_val_dict[mirror]
            #         val1 = maxmin(new_history, False)
            #         if val != val1:
            #             print(val1, val, mirror, new_history.get_boards_str())
            #         found = True
            #         break
            # if not found:
            #     val = maxmin(new_history, False)
            if val > max_val:
                max_val = val
                # best_action = action
        # print(max_val, history_obj.get_boards_str(), history_obj.history)
        board_positions_val_dict[history_obj.get_boards_str()] = (val, history_obj)
        # mdp[history_obj.get_boards_str()] = best_action
        return max_val
    else:
        min_val = math.inf
        # best_action = -1
        for action in history_obj.get_valid_actions_():
            new_history = History(copy.deepcopy(history_obj.num_boards), copy.deepcopy(history_obj.history))
            new_history.history.append(action)
            new_history.boards = new_history.get_boards()
            if new_history.get_boards_str() in board_positions_val_dict:
                val, mirror = board_positions_val_dict[new_history.get_boards_str()]
                val1 = maxmin(new_history, not max_player_flag)
                if val != val1:
                    print(val1, val, new_history.get_boards_str(), mirror.get_boards_str(), new_history.history, mirror.history)
            else:
                val = maxmin(new_history, not max_player_flag)
            # found = False
            # for mirror in get_mirrors(new_history.get_boards_str()):
            #     if mirror in board_positions_val_dict:
            #         val = board_positions_val_dict[mirror]
            #         found = True
            #         break
            # if not found:
            #     val = maxmin(new_history, True)
            # if val < min_val:
            #     min_val = val
                # best_action = action
        # print(min_val, history_obj.get_boards_str(), history_obj.history)
        board_positions_val_dict[history_obj.get_boards_str()] = (val, history_obj)
        # mdp[history_obj.get_boards_str()] = best_action
        return min_val
    # TODO implement


def solve_alpha_beta_pruning(history_obj, alpha, beta, max_player_flag):
    global visited_histories_list
    val = alpha_beta_pruning(history_obj, alpha, beta, max_player_flag)
    return val, visited_histories_list

import json
import time

if __name__ == "__main__":
    logging.info(msg="start")
    logging.info("alpha beta pruning")
    start_time = time.time()
    value, visited_histories = solve_alpha_beta_pruning(History(history=[], num_boards=2), -math.inf, math.inf, True)
    print(time.time() - start_time)
    print(value, len(visited_histories))
    logging.info("maxmin value {}".format(value))
    logging.info("Number of histories visited {}".format(len(visited_histories)))
    logging.info("maxmin memory")
    board_positions_val_dict = dict()
    logging.info("maxmin value {}".format(maxmin(History(history=[], num_boards=2), True)))
    print(len(board_positions_val_dict))
    with open("mdp_notakto.json", mode="w") as f:
        json.dump(mdp, f)
    logging.info("end")
    # stri = "012345678012345678"
    # print(get_mirrors(stri))
    # print(maxmin(h1, False))
    # print(maxmin(h2, False))