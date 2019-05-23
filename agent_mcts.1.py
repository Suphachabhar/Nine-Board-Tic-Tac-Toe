#!/usr/bin/python3
# Sample starter bot by Zac Partridge
# Contact me at z.partridge@unsw.edu.au
# 06/04/19
# Feel free to use this and modify it however you wish

import socket,sys,time,math
import numpy as np
from random import choice

# a board cell can hold:
#   0 - Empty
#   1 - I played here
#   2 - They played here

# the boards are of size 10 because index 0 isn't used


class State(object):
    def __init__(self,boards,curr_board,player):
        self.boards = boards
        self.curr_board = curr_board
        self.player = player

    def to_hashable(self):
        return (tuple(map(tuple, self.boards)),self.curr_board)

    def __hash__(self):
        return hash(self.to_hashable())

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.curr_board == other.curr_board and self.player == other.player and np.array_equal(self.boards,other.boards)
        else:
            return False

class Board(object):
    def __init__(self,mtcs=None):
        self.symbol = [".","X","O"]
        self.mtcs = mtcs

    def print_board_row(self,board, a, b, c, i, j, k):
        print(" "+self.symbol[board[a][i]]+" "+self.symbol[board[a][j]]+" "+self.symbol[board[a][k]]+" | " \
             +self.symbol[board[b][i]]+" "+self.symbol[board[b][j]]+" "+self.symbol[board[b][k]]+" | " \
             +self.symbol[board[c][i]]+" "+self.symbol[board[c][j]]+" "+self.symbol[board[c][k]])

    def print_board(self,board):
        self.print_board_row(board, 1,2,3,1,2,3)
        self.print_board_row(board, 1,2,3,4,5,6)
        self.print_board_row(board, 1,2,3,7,8,9)
        print(" ------+-------+------")
        self.print_board_row(board, 4,5,6,1,2,3)
        self.print_board_row(board, 4,5,6,4,5,6)
        self.print_board_row(board, 4,5,6,7,8,9)
        print(" ------+-------+------")
        self.print_board_row(board, 7,8,9,1,2,3)
        self.print_board_row(board, 7,8,9,4,5,6)
        self.print_board_row(board, 7,8,9,7,8,9)
        print()

    def random_play(self):
        last_state = self.mtcs.states[-1]
        boards = last_state.boards
        curr_board = last_state.curr_board

        n = np.random.randint(1,9)
        while boards[curr_board][n] != 0:
            n = np.random.randint(1,9)

        # print("playing", n)
        self.place(boards, n, 1)
        return n

    # place a move in the global boards
    def place(self,board, num, player):
        last_state = self.mtcs.states[-1]
        boards = last_state.boards

        boards[board][num] = player
        tmp_boards = boards.copy()
        new_state = State(tmp_boards,num,player)
        self.mtcs.update(new_state)

    
    def is_subboard_won(self,p, sub_board):
        return(  ( sub_board[1] == p and sub_board[2] == p and sub_board[3] == p )
                or( sub_board[4] == p and sub_board[5] == p and sub_board[6] == p )
                or( sub_board[7] == p and sub_board[8] == p and sub_board[9] == p )
                or( sub_board[1] == p and sub_board[4] == p and sub_board[7] == p )
                or( sub_board[2] == p and sub_board[5] == p and sub_board[8] == p )
                or( sub_board[3] == p and sub_board[6] == p and sub_board[9] == p )
                or( sub_board[1] == p and sub_board[5] == p and sub_board[9] == p )
                or( sub_board[3] == p and sub_board[5] == p and sub_board[7] == p ))

    def is_full_board(self,sub_board):
        for i in range(1,10):
            if sub_board[i] == 0:
                return False
        return True

    def parse(self,string):
        if "(" in string:
            command, args = string.split("(")
            args = args.split(")")[0]
            args = args.split(",")
        else:
            command, args = string, []

        if command == "second_move":
            self.place(int(args[0]), int(args[1]), 2)
            return self.mtcs.get_play()
        elif command == "third_move":
            # place the move that was generated for us
            self.place(int(args[0]), int(args[1]), 1)
            # place their last move
            curr_board = self.mtcs.states[-1].curr_board
            self.place(curr_board, int(args[2]), 2)
            return self.mtcs.get_play()
        elif command == "next_move":
            curr_board = self.mtcs.states[-1].curr_board
            self.place(curr_board, int(args[0]), 2)
            return self.mtcs.get_play()
        elif command == "win":
            print("Yay!! We win!! :)")
            return -1
        elif command == "loss":
            print("We lost :(")
            return -1
        return 0

    def legal_move(self,boards,curr_board):
        legal_moves = []
        for i in range(1,10):
            if boards[curr_board][i] == 0:
                legal_moves.append(i)
        return legal_moves

    def current_player(self,state):
        return 1 if state.player == 2 else 2

    def next_state(self,state,move):
        new_boards = state.boards.copy()
        next_player = self.current_player(state)
        new_boards[state.curr_board][move] = next_player
        return State(new_boards,move,next_player)

    def is_terminate(self,state):
        for i in range(1,10):
            sub_board = state.boards[i]
            if self.is_subboard_won(1,sub_board):
                return 1
            if self.is_subboard_won(2,sub_board):
                return 2
            if self.is_full_board(sub_board):
                return 0
        return -1

class MCTS(object):
    def __init__(self):
        self.game_board = Board()
        self.turn_time = 3
        new_state = State(np.zeros((10, 10), dtype="int8"),0,0)
        self.states = [new_state]
        self.num_wins = {}
        self.num_plays = {}
        self.tune_UCB1 = math.sqrt(2)

    def update(self,state):
        self.states.append(state)

    def get_play(self):
    
        state = self.states[-1]
        print("last state is")
        self.game_board.print_board(state.boards)
        print("state.curr_board",state.curr_board)
        print("state.player",state.player)
        player = self.game_board.current_player(state)
        legal_moves = self.game_board.legal_move(state.boards,state.curr_board)

        if not legal_moves:
            return
        if len(legal_moves) ==1 :
            return legal_moves[0]

        num_games = 0
        start_time = time.time()

        while time.time() - start_time < self.turn_time:
            self.run_simulation()
            num_games += 1
        print("===========")
        print(num_games)
        print("===========")

        possible_move_states = [(move, self.game_board.next_state(state,move)) for move in legal_moves]

        best_move = None
        best_win_possibility = -1
        for _move, _state in possible_move_states:
            prob = self.num_wins.get((player,_state),0) / self.num_plays.get((player,_state),1)
            print("prob",prob,"_move",_move)
            if prob > best_win_possibility:
                best_win_possibility = prob
                best_move = _move
                best_state = _state

        print("next state is")
        self.update(best_state)
        print("best_move,",best_move)
        self.game_board.print_board(best_state.boards)
        print("state.curr_board",best_state.curr_board)
        print("state.player",best_state.player)
        return best_move

    def run_simulation(self):
        visited_states = set()
        temp_states = self.states.copy()
        state = temp_states[-1]
        player = self.game_board.current_player(state)

        is_expand = False
        while True:
            legal_moves = self.game_board.legal_move(state.boards,state.curr_board)
            possible_move_states = [(move, self.game_board.next_state(state,move)) for move in legal_moves]

            if all((player,_state) in self.num_plays for _move,_state in possible_move_states):
                parent_play_total = sum([self.num_plays[(player,_state)] for _move, _state in possible_move_states])
                UCB1_best = float("-inf")
                for _move, _state in possible_move_states:
                    this_UCB1 = self.num_wins[(player,_state)] / self.num_plays[(player,_state)] + (self.tune_UCB1 * math.sqrt(parent_play_total/self.num_plays[(player,_state)]))
                    if this_UCB1 > UCB1_best:
                        UCB1_best = this_UCB1
                        play_move = _move
                        state = _state
            else:
                play_move,state = choice(possible_move_states)
            temp_states.append(state)

            if not is_expand and (player,state) not in self.num_plays:
                is_expand = True
                self.num_plays[(player,state)] = 0
                self.num_wins[(player,state)] = 0

            visited_states.add((player,state))

            player = self.game_board.current_player(state)
            winner = self.game_board.is_terminate(state)
            if winner >= 0:
                break

        for player, state in visited_states:
            if (player,state) not in self.num_plays:
                continue
            self.num_plays[(player,state)] += 1
            if player == winner:
                self.num_wins[(player,state)] += 1

# connect to socket
def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    port = int(sys.argv[2]) # Usage: ./agent.py -p (port)

    mtcs = MCTS()
    board_game = Board(mtcs)
    
    
    
    s.connect(('localhost', port))
    while True:
        text = s.recv(1024).decode()
        if not text:
            continue
        for line in text.split("\n"):
            response = board_game.parse(line)
            if response == -1:
                s.close()
                return
            elif response > 0:
                s.sendall((str(response) + "\n").encode())

if __name__ == "__main__":
    main()
