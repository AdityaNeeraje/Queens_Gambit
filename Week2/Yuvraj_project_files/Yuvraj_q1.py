import json
import copy  # use it for deepcopy if needed
import math  # for math.inf
import logging

logging.basicConfig(format='%(levelname)s - %(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S',
                    level=logging.INFO)

# Global variables in which you need to store player strategies (this is data structure that'll be used for evaluation)
# Mapping from histories (str) to probability distribution over actions
strategy_dict_x = {}
strategy_dict_o = {}

help=0

class History:
    def __init__(self, history=None):
        """
        # self.history : Eg: [0, 4, 2, 5]
            keeps track of sequence of actions played since the beginning of the game.
            Each action is an integer between 0-8 representing the square in which the move will be played as shown
            below.
              ___ ___ ____
             |_0_|_1_|_2_|
             |_3_|_4_|_5_|
             |_6_|_7_|_8_|

        # self.board
            empty squares are represented using '0' and occupied squares are either 'x' or 'o'.
            Eg: ['x', '0', 'x', '0', 'o', 'o', '0', '0', '0']
            for board
              ___ ___ ____
             |_x_|___|_x_|
             |___|_o_|_o_|
             |___|___|___|

        # self.player: 'x' or 'o'
            Player whose turn it is at the current history/board

        :param history: list keeps track of sequence of actions played since the beginning of the game.
        """
        if history is not None:
            self.history = history
            self.board = self.get_board()
        else:
            self.history = []
            self.board = ['0', '0', '0', '0', '0', '0', '0', '0', '0']
        self.player = self.current_player()

    def current_player(self):
        """ Player function
        Get player whose turn it is at the current history/board
        :return: 'x' or 'o' or None
        """
        total_num_moves = len(self.history)
        if total_num_moves < 9:
            if total_num_moves % 2 == 0:
                return 'x'
            else:
                return 'o'
        else:
            return None

    def get_board(self):
        """ Play out the current self.history and get the board corresponding to the history in self.board.

        :return: list Eg: ['x', '0', 'x', '0', 'o', 'o', '0', '0', '0']
        """
        board = ['0', '0', '0', '0', '0', '0', '0', '0', '0']
        for i in range(len(self.history)):
            if i % 2 == 0:
                board[self.history[i]] = 'x'
            else:
                board[self.history[i]] = 'o'
        return board

    def is_win(self):
        # check if the board position is a win for either players
        Winning_Positions = [[0,1,2],[3,4,5],[6,7,8],[0,3,6],[1,4,7],[2,5,8],[0,4,8],[2,4,6]]
        self.board=self.get_board()
        
        for pattern in Winning_Positions:
            check=[self.board[pattern[0]],self.board[pattern[1]],self.board[pattern[2]]]
            if ((len(set(check))==1) & (str(check[0])!=str(0))):
                return check[0]
        # Feel free to implement this in anyway if needed
        return False
        pass

    def is_draw(self):
        # check if the board position is a draw
        if len(self.history)==9:
            if self.is_win() == False:
                return True
        return False
        # Feel free to implement this in anyway if needed
        pass

    def get_valid_actions(self):
        # get the empty squares from the board
        valid_actions=[]
        board=self.get_board()
        for i in range(len(board)):
            if str(board[i]) == str(0):
                valid_actions.append(i)
        
        # Feel free to implement this in anyway if needed
        return valid_actions
    
        pass

    def is_terminal_history(self):
        # check if the history is a terminal history
        board=self.get_board()
        # print(board)
        # print(self.history)
        # print(self.is_win())
        # print(self.is_draw())
        if ((len(self.history)==9) | (self.is_win() != False ) | (self.is_draw() != False)) :
            return True
        # Feel free to implement this in anyway if needed
        return False
        pass

    def get_utility_given_terminal_history(self):
        # Feel free to implement this in anyway if needed
        if self.is_draw():
            return 0
        if str(self.is_win())=='x':
            return 1
        if str(self.is_win())=='o':
            return -1
        pass

    def update_history(self, action):
        # In case you need to create a deepcopy and update the history obj to get the next history object.
        hist=self.history
        new_hist=copy.deepcopy(hist)
        new_hist.append(action)
        return History(new_hist)
        # Feel free to implement this in anyway if needed
        pass

def backward_induction(history_obj):
    """
    :param history_obj: Histroy class object
    :return: best achievable utility (float) for the current history_obj
    """
    
    global strategy_dict_x, strategy_dict_o,help
    # TODO implement
    # (1) Implement backward induction for tictactoe
    help=help+1
    
    playertoplay=history_obj.current_player()
    board=history_obj.get_board()
    # print("-------------------------------------")
    # print("Recursion Iteration no: ",help)
    # print("playertoplay: ",playertoplay)
    # print(board)
    
    
    histstring=""
    
    hist=history_obj.history
    
    for i in hist:
        histstring+=str(i)        
        
    # print(history_obj.is_terminal_history())
    if history_obj.is_terminal_history():
        bestUtility = history_obj.get_utility_given_terminal_history()
        return bestUtility

    # print(playertoplay)
    if playertoplay == 'x':     
        bestUtility = float('-inf')
        # print("entered here")
        # print(history_obj.get_valid_actions())
        for action in history_obj.get_valid_actions():
            # print(action)
            utility_at_child = backward_induction(history_obj.update_history(action))
            if utility_at_child > bestUtility:
                bestUtility=utility_at_child                
                bestaction=action
                
    elif playertoplay == 'o':
        bestUtility = float('inf')
        for action in history_obj.get_valid_actions():
            utility_at_child = backward_induction(history_obj.update_history(action))
            
            if utility_at_child < bestUtility:
                bestUtility = utility_at_child
                bestaction=action 
        
    if playertoplay == 'x':
        # print(strategy_dict_x)
        # print(histstring)
        prob={}
        for i in range(9):
            if str(i)!=str(bestaction):
                prob[str(i)]=0
            else:
                prob[str(i)]=1
        strategy_dict_x[histstring]=prob
    elif playertoplay == 'o':
        # print(strategy_dict_o)
        # print(histstring)
        prob={}
        for i in range(9):
            if str(i)!=str(bestaction):
                prob[str(i)]=0
            else:
                prob[str(i)]=1
        strategy_dict_o[histstring]=prob
    # (2) Update the global variables strategy_dict_x or strategy_dict_o which are a mapping from histories to
    # probability distribution over actions.
    # (2a)These are dictionary with keys as string representation of the history list e.g. if the history list of the
    # history_obj is [0, 4, 2, 5], then the key is "0425". Each value is in turn a dictionary with keys as actions 0-8
    # (str "0", "1", ..., "8") and each value of this dictionary is a float (representing the probability of
    # choosing that action). Example: {”0452”: {”0”: 0, ”1”: 0, ”2”: 0, ”3”: 0, ”4”: 0, ”5”: 0, ”6”: 1, ”7”: 0, ”8”:
    # 0}}
    # (2b) Note, the strategy for each history in strategy_dict_x and strategy_dict_o is probability distribution over
    # actions. But since tictactoe is a PIEFG, there always exists an optimal deterministic strategy (SPNE). So your
    # policy will be something like this {"0": 1, "1": 0, "2": 0, "3": 0, "4": 0, "5": 0, "6": 0, "7": 0, "8": 0} where
    # "0" was the one of the best actions for the current player/history.
    return bestUtility
    # TODO implement


def solve_tictactoe():
    backward_induction(History())
    with open('./policy_x.json', 'w') as f:
        json.dump(strategy_dict_x, f)
    with open('./policy_o.json', 'w') as f:
        json.dump(strategy_dict_o, f)
    return strategy_dict_x, strategy_dict_o


if __name__ == "__main__":
    logging.info("Start")
    solve_tictactoe()
    logging.info("End")
    print(help)
