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
equivalent_positions = {}
mdp={}

def generate_equivalent_positions(state):
    global equivalent_positions
    if state in equivalent_positions:
        return equivalent_positions[state]
    equivalent_states = [(state, 0)]
    powers=[1, 3, 9, 27, 81, 243, 729, 2187, 6561]
    digits=[state%3, (state//3)%3, (state//9)%3, (state//27)%3, (state//81)%3, (state//243)%3, (state//729)%3, (state//2187)%3, (state//6561)%3]
    equivalent_states.append((sum([digits[i]*powers[3*(i//3)+2-i%3] for i in range(9)]), 2)) # Reflection about the vertical
    equivalent_states.append((sum([digits[i]*powers[3*(i%3)+i//3] for i in range(9)]), 3)) # Rotation 90 degree
    equivalent_states.append((sum([digits[i]*powers[3*(i%3)+2-i//3] for i in range(9)]), 4)) # Reflection about the diagonal from 0 to 8
    equivalent_states.append((sum([digits[i]*powers[3*(2-i//3)+2-i%3] for i in range(9)]), 5)) # Rotation 180 degree
    equivalent_states.append((sum([digits[i]*powers[3*(2-i//3)+i%3] for i in range(9)]), 6)) # Reflection about the horizontal
    equivalent_states.append((sum([digits[i]*powers[3*(2-i%3)+i//3] for i in range(9)]), 7)) # Rotation 270 degree
    equivalent_states.append((sum([digits[i]*powers[3*(2-i%3)+i//3] for i in range(9)]), 8)) # Reflection about the diagonal from 2 to 6
    min_state = min(equivalent_states, key=lambda x: x[0])
    for state in equivalent_states:
        equivalent_positions[state[0]] = (min_state[0], (state[1]-min_state[1])%8)

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
        board=['0']*9
        for i in range(len(self.history)):
            if i % 2 == 0:
                board[int(self.history[i])] = 'x'
            else:
                board[int(self.history[i])] = 'o'
        return board

    def is_win(self):
        for i in range(3):
            if self.board[3*i] != '0' and self.board[3*i] == self.board[3*i+1] == self.board[3*i+2]:
                return True
        for i in range(3):
            if self.board[i] != '0' and self.board[i] == self.board[3+i] == self.board[6+i]:
                return True
        if self.board[0] != '0' and self.board[0]==self.board[4]==self.board[8]:
            return True
        if self.board[2] != '0' and self.board[2]==self.board[4]==self.board[6]:
            return True
        return False

    def is_draw(self):
        if self.board.count('0') != 0:
            return False
        if not self.is_win():
            return True
        return False

    def get_valid_actions(self):
        # get the empty squares from the board
        # Feel free to implement this in anyway if needed
        pass

    def is_terminal_history(self):
        # check if the history is a terminal history
        # Feel free to implement this in anyway if needed
        pass

    def get_utility_given_terminal_history(self):
        # Feel free to implement this in anyway if needed
        pass

    def update_history(self, action):
        # In case you need to create a deepcopy and update the history obj to get the next history object.
        # Feel free to implement this in anyway if needed
        pass

def fill_mdp_up_to_equivalence(state, result):
    global mdp
    if result==0:
        sign=1
    else:      
        sign=result/abs(result)
    result=abs(result)
    digits=[state%3, (state//3)%3, (state//9)%3, (state//27)%3, (state//81)%3, (state//243)%3, (state//729)%3, (state//2187)%3, (state//6561)%3]
    powers=[1, 3, 9, 27, 81, 243, 729, 2187, 6561]
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
    if result==10 or result==0:
        for function in funcs:
            mdp[sum([digits[i]*powers[function(i)] for i in range(9)])]=result
    else:
        for function in funcs:
            mdp[sum([digits[i]*powers[function(i)] for i in range(9)])]=sign*function(result-1)
        return

def permutation(lst):
    if len(lst)==0:
        return []
    if len(lst)==1:
        return [lst]
    l=[]
    for i in range(len(lst)):
        m=lst[i]
        remLst=lst[:i]+lst[i+1:]
        for p in permutation(remLst):
            l.append([m]+p)
    return l


def backward_induction(history_obj):
    """
    :param history_obj: Histroy class object
    :return: best achievable utility (float) for the current history_obj
    """
    global strategy_dict_x, strategy_dict_o, mdp
    # TODO implement
    # (1) Implement backward induction for tictactoe
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
    board=history_obj.get_board()
    state=(3**9-1)//2
    for i in range(9):
        if board[i] == 'x':
            state+=3**(8-i)
        elif board[i] == 'o':
            state-=3**(8-i)
    # If the state already has its strategy mapped out, then we know if it is a N win or a P win. In mdp, to save space, let us only store the value of the equivalent position
    if state in mdp:
        if mdp[state] < 0:
            return -1
        if mdp[state] < 1:
            return 0
        return 1
    # If the state is a win, then it has never been reached before. Hence we generate all equivalent positions
    if history_obj.is_win():
        fill_mdp_up_to_equivalence(state, 10)
        return 1
    substates = [History(history_obj.history + [str(char)]) for char in range(9) if str(char) not in history_obj.history]
    if len(substates) == 0:
        fill_mdp_up_to_equivalence(state, 0)
        return 0
    for substate in substates:
        result=backward_induction(substate)
        if result >= 1:
            fill_mdp_up_to_equivalence(state, -(int(substate.history[-1])+1))
            return -1
        if result == 0:
            mdp[state]=(int(substate.history[-1])+1)/10          
    if mdp.get(state) is not None and mdp.get(state) >= 0:
        if state==(3**9-1)//2:
            fill_policies()
        return 0
    fill_mdp_up_to_equivalence(state, int(substates[0].history[-1])+1)
    return 1

def test_to_ensure_all_states_are_mapped():
    with open('mdp.json', 'r') as f:
        data=json.load(f)
    array=list(range(9))
    perms=permutation(array)
    for perm in perms:
        history=History(perm)
        if history.board.count('o')>history.board.count('x'):
            continue
        if history.is_win() or history.is_draw():
            continue
        state=(3**9-1)//2
        for i in range(9):
            if history.board[i] == 'x':
                state+=3**(8-i)
            elif history.board[i] == 'o':
                state-=3**(8-i)
        if data.get(state) is None:
            print(state)

def solve_tictactoe():
    backward_induction(History())
    with open('./policy_x.json', 'w') as f:
        json.dump(strategy_dict_x, f)
    with open('./policy_o.json', 'w') as f:
        json.dump(strategy_dict_o, f)
    with open('mdp.json', 'w') as f:
        json.dump(mdp, f)
    return strategy_dict_x, strategy_dict_o


def fill_policies():
    global strategy_dict_x, strategy_dict_o, mdp
    for stored_state, value in mdp.items():
        if value == 10 or value == 0:
            continue
        given_state=int(stored_state)
        x_positions=[]
        o_positions=[]
        for i in range(9):
            if given_state%3==2:
                x_positions.append(8-i)
            elif given_state%3==0:
                o_positions.append(8-i)
            given_state//=3
        if len(x_positions) == 0:
            sequence=""
            if value < 0:
                strategy_dict_x[sequence]={i: 0 for i in range(9)}
                strategy_dict_x[sequence][(-value)-1]=1
            elif value < 1:
                strategy_dict_x[sequence]={i: 0 for i in range(9)}
                strategy_dict_x[sequence][int(value*10)-1]=1
            else:
                strategy_dict_x[sequence]={i: 0 for i in range(9)}
                strategy_dict_x[sequence][value-1]=1
            continue
        if len(o_positions)==0:
            sequence=str(x_positions[0])
            if value < 0:
                strategy_dict_o[sequence]={i: 0 for i in range(9)}
                strategy_dict_o[sequence][(-value)-1]=1
            elif value < 1:
                strategy_dict_o[sequence]={i: 0 for i in range(9)}
                strategy_dict_o[sequence][int(value*10)-1]=1
            else:
                strategy_dict_o[sequence]={i: 0 for i in range(9)}
                strategy_dict_o[sequence][(value-1)]=1
            continue
        x_perms=permutation(x_positions)
        o_perms=permutation(o_positions)
        for x_perm in x_perms:
            for o_perm in o_perms:
                if len(x_perms) > len(o_perms):
                    sequence=str(x_perm[0])+"".join([str(o_perm[i])+str(x_perm[i+1]) for i in range(len(o_perm))])
                    if mdp.get(stored_state) < 0:
                        strategy_dict_o[sequence]={i: 0 for i in range(0,9)}
                        strategy_dict_o[sequence][-value-1]=1
                    elif mdp.get(stored_state) < 1:
                        strategy_dict_o[sequence]={i: 0 for i in range(9)}
                        strategy_dict_o[sequence][int(value*10)-1]=1
                    else:
                        strategy_dict_o[sequence]={i: 0 for i in range(9)}
                        strategy_dict_o[sequence][value-1]=1
                else:
                    sequence="".join([str(x_perm[i]) + str(o_perm[i]) for i in range(len(o_perm))])
                    if mdp.get(stored_state) < 0:
                        strategy_dict_x[sequence]={i: 0 for i in range(9)}
                        strategy_dict_x[sequence][(-value)-1]=1
                    elif mdp.get(stored_state) < 1:
                        strategy_dict_x[sequence]={i: 0 for i in range(9)}
                        strategy_dict_x[sequence][int(value*10)-1]=1
                    else:
                        strategy_dict_x[sequence]={i: 0 for i in range(9)}
                        strategy_dict_x[sequence][value-1]=1

if __name__ == "__main__":
    logging.info("Start")
    solve_tictactoe()
    logging.info("End")
