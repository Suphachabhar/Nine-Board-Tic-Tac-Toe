#!/usr/bin/python3

# Assignment 3 19T1 COMP3411/9414
# z5176892 Supphachabhar Nigrodhananda
# z5228028 Thanet Sirichanyaphong
# Sample starter bot by Zac Partridge 06/04/19

import socket, sys, time
import numpy as np


n_win = 0
n_game = 0

# 9-board tic-tac-toe Agent : using Alpha-Beta Pruning
# Heuristic function = f(subboard1) + ... + f(subboard9)
# f(subboard) = (7 * X2 + X1) - (7 * O2 + O1)
# Xn is number of rows, columns or diagonals with exactly n X's and no O's.
# On is number of rows, columns or diagonals with exactly n O's and no X's.

class GameBoard(object):
    def __init__(self):
        self.boards = np.zeros((10, 10), dtype="int8")
        self.s = [".","X","O"]
        self.curr = 0
        self.last_move_time = 2
        self.total_extra_time = 30
        self.max_depth = 5
        self.move_dict = {1:(0,0),2:(0,1),3:(0,2),4:(1,0),5:(1,1),6:(1,2),7:(2,0),8:(2,1),9:(2,2)}
        self.all_heuristic_board = {}
        self.total_move = 2


    # read what the server sent us and
    # only parses the strings that are necessary
    def parse(self,string):
        global n_game
        global n_win
        if "(" in string:
            command, args = string.split("(")
            args = args.split(")")[0]
            args = args.split(",")
        else:
            command, args = string, []

        if command == "second_move":
            self.place(int(args[0]), int(args[1]), 2)
            return self.alpha_beta_play()
        elif command == "third_move":
            # place the move that was generated for us
            self.place(int(args[0]), int(args[1]), 1)
            # place their last move
            self.place(self.curr, int(args[2]), 2)
            return self.alpha_beta_play()
        elif command == "next_move":
            self.place(self.curr, int(args[0]), 2)
            return self.alpha_beta_play()
        elif command == "win":
            print("Yay!! We win!! :)")
            n_win += 1
            n_game += 1
            return -1
        elif command == "loss":
            print("We lost :(")
            n_game += 1
            return -1
        return 0

    # print a row
    # This is just ported from game.c
    def print_board_row(self,board, a, b, c, i, j, k):
        print(" "+s[board[a][i]]+" "+s[board[a][j]]+" "+s[board[a][k]]+" | " \
                +s[board[b][i]]+" "+s[board[b][j]]+" "+s[board[b][k]]+" | " \
                +s[board[c][i]]+" "+s[board[c][j]]+" "+s[board[c][k]])

    # Print the entire board
    # This is just ported from game.c
    def print_board(self,board):
        print_board_row(board, 1,2,3,1,2,3)
        print_board_row(board, 1,2,3,4,5,6)
        print_board_row(board, 1,2,3,7,8,9)
        print(" ------+-------+------")
        print_board_row(board, 4,5,6,1,2,3)
        print_board_row(board, 4,5,6,4,5,6)
        print_board_row(board, 4,5,6,7,8,9)
        print(" ------+-------+------")
        print_board_row(board, 7,8,9,1,2,3)
        print_board_row(board, 7,8,9,4,5,6)
        print_board_row(board, 7,8,9,7,8,9)
        print()

    # choose a move to play
    def random_play(self):
        # print_board(boards)

        # just play a random move for now
        n = np.random.randint(1,9)
        while self.boards[self.curr][n] != 0:
            n = np.random.randint(1,9)

        # print("playing", n)
        self.place(self.curr, n, 1)
        return n

    # choose a move by alpha-beta pruning algorithm
    def alpha_beta_play(self):
        remaining_time = self.total_extra_time/30
        if remaining_time > 0.2 and self.total_move > 10:
            if self.last_move_time < 1.5 and self.total_extra_time > 5:
                if self.last_move_time < 1:
                    self.max_depth += 1
                self.max_depth += 1
            if self.last_move_time > 3 and self.total_extra_time < 10:
                self.max_depth -= 1

        print("self.max_depth",self.max_depth,self.total_extra_time)
        
        start_time = time.time()
        alpha = float("-inf")
        beta = float("inf")

        # print_board(boards)
        best_play = None
        best_alpha = float("-inf")

        for i in range(1,10):
            if self.boards[self.curr][i] == 0:
                temp_boards = np.copy(self.boards)
                temp_boards[self.curr][i] = 1
                this_heuristic = self.heuristic_9board(temp_boards,2,self.curr,i)
                new_alpha = self.alpha_beta(temp_boards,self.curr,2,alpha, beta,self.max_depth,i,this_heuristic)
                print("i",i,"new_alpha",new_alpha)
                if new_alpha > best_alpha:
                    best_alpha = new_alpha
                    best_play = i
                elif new_alpha == best_alpha:
                    if i == 5:
                        best_play = 5
                    if best_play != 5 and (best_play in [2,4,6,8]) and (i in [1,3,7,9]):
                        best_play = i
                    if (best_play in [2,4,6,8]) and (i in [2,4,6,8]):
                        if self.players_next_to(temp_boards[self.curr],i,2) == 0:
                            best_play = i
        
        
        self.place(self.curr, best_play, 1)
        self.last_move_time = time.time()-start_time
        self.total_extra_time -= 0 if self.last_move_time <= 2 else (self.last_move_time-2)
        self.total_move += 2
        print("best play :",best_play,"time",self.last_move_time,"move: ",self.total_move)
        return best_play

    # alpha-beta pruning algorithm
    def alpha_beta(self,boards,curr_board,player,alpha,beta,curr_depth,parent_move,heuristic_sofar):
        _terminate = self.is_terminate(boards,curr_board)
        if _terminate != -1 or curr_depth == 0 or heuristic_sofar == 100 or heuristic_sofar == -100:
            if _terminate == 1:
                return 100
            elif _terminate == 2:
                return -100
            elif _terminate == 0:
                return 0
            return heuristic_sofar
        #we play at this node
        if player == 1:
            for i in range(1,10):
                if boards[parent_move][i] == 0:
                    new_heuristic = heuristic_sofar - self.heuristic_subboard(boards[parent_move])
                    boards[parent_move][i] = player
                    new_heuristic += self.heuristic_subboard(boards[parent_move])
                    alpha = max(alpha,self.alpha_beta(boards,parent_move,2,alpha, beta,curr_depth - 1,i,new_heuristic))
                    boards[parent_move][i] = 0
                    if alpha >= beta:
                        return alpha   
            return alpha
        else :
            for i in range(1,10):
                if boards[parent_move][i] == 0:
                    new_heuristic = heuristic_sofar - self.heuristic_subboard(boards[parent_move])
                    boards[parent_move][i] = player
                    new_heuristic += self.heuristic_subboard(boards[parent_move])
                    beta = min(beta,self.alpha_beta(boards,parent_move,1,alpha, beta,curr_depth - 1,i,new_heuristic))
                    boards[parent_move][i] = 0
                    if beta <= alpha:
                        return beta
            return beta

    # count how many player'cells next to move in subboard
    def players_next_to(self,subboard,move,player):
        new_subboard = [[] for i in range(3)]
        for i in range(3):
            for j in range(3):
                new_subboard[i].append(subboard[1+j+i*3])
        _count = 0
        i,j = self.move_dict[move]
        if i-1 >= 0:
            if j-1 >= 0 and new_subboard[i-1][j-1] == player:
                _count += 1
            if j+1 < 3 and new_subboard[i-1][j+1] == player:
                _count += 1
            if new_subboard[i-1][j] == player:
                _count += 1
        if i+1 < 3:
            if j-1 >= 0 and new_subboard[i+1][j-1] == player:
                _count += 1
            if j+1 < 3 and new_subboard[i+1][j+1] == player:
                _count += 1
            if new_subboard[i+1][j] == player:
                _count += 1
        if j-1 >= 0 and new_subboard[i][j-1] == player:
            _count += 1
        if j+1 < 3 and new_subboard[i][j+1] == player:
            _count += 1   
        return _count

    # place a move in the global boards
    def place(self,board, num, player):
        self.curr = num
        self.boards[board][num] = player

    def heuristic_subboard(self,subboard):
        board_tuple = tuple([ _ for _ in subboard])
        if board_tuple in self.all_heuristic_board:
            return self.all_heuristic_board[board_tuple]
        else :
            return ((7 * self.count_player(subboard,1,2) + self.count_player(subboard,1,1)) - (7 * self.count_player(subboard,2,2) + self.count_player(subboard,2,1)))

    # heuristic function for 9 board tic-tac-toe
    def heuristic_9board(self,board,player,curr_board,move):
        win_player = self.is_terminate(board,curr_board)
        # opponent = 2 if player == 1 else 1
        if win_player != -1:
            if win_player == 1:
                return 100
            elif win_player == 2:
                return -100
            else:
                return 0
        else :
            this_heuristic = 0

            for i in range(1,10):
                board_tuple = tuple([ _ for _ in board[i]])
                if board_tuple in self.all_heuristic_board:
                    this_eval = self.all_heuristic_board[board_tuple]
                else :
                    this_eval = ((7 * self.count_player(board[i],1,2) + self.count_player(board[i],1,1)) - (7 * self.count_player(board[i],2,2) + self.count_player(board[i],2,1)))
                    self.all_heuristic_board[board_tuple] = this_eval
                this_heuristic += this_eval  
                
            return this_heuristic
            
    # return number of rows, columns or diagonals with exactly num_of_player_place X's and no O's.
    def count_player(self,subboard,player,num_of_player_place):
        # rows
        num_result = 0
        empty_pos = []
        opponent = 2 if player == 1 else 1
        for i in range(3):
            count_place = 0
            has_opponent = False
            for j in range(1,4):
                if  subboard[j + 3 * i] == player:
                    count_place += 1
                elif subboard[j + 3 * i] == opponent :
                    has_opponent = True
                    break
            if not has_opponent and count_place == num_of_player_place:
                num_result += 1

        #columns
        for i in range(1,4):
            count_place = 0
            has_opponent = False
            for j in range(3):
                if subboard[i + 3 * j] == player:
                    count_place += 1
                elif subboard[i + 3 * j] == opponent :
                    has_opponent = True
                    break
            if not has_opponent and count_place == num_of_player_place:
                num_result += 1

        #diagonals
        count_place_lr = 0
        count_place_rl = 0
        has_opponent = False
        for i in range(3):
            if subboard[1 + 4 * i] == player:
                count_place_lr += 1
            elif subboard[1 + 4 * i] == opponent :
                has_opponent = True
                break
        if not has_opponent and count_place_lr == num_of_player_place:
            num_result += 1
        has_opponent = False
        for i in range(3):
            if subboard[3 + 2 * i] == player:
                count_place_rl += 1
            elif subboard[3 + 2 * i] == opponent :
                has_opponent = True
                break
        if not has_opponent and count_place_rl == num_of_player_place:
            num_result += 1
        
        return num_result

    # check subboard is won by p
    def subboardwon(self,p, sub_board ):
        return(  ( sub_board[1] == p and sub_board[2] == p and sub_board[3] == p )
                or( sub_board[4] == p and sub_board[5] == p and sub_board[6] == p )
                or( sub_board[7] == p and sub_board[8] == p and sub_board[9] == p )
                or( sub_board[1] == p and sub_board[4] == p and sub_board[7] == p )
                or( sub_board[2] == p and sub_board[5] == p and sub_board[8] == p )
                or( sub_board[3] == p and sub_board[6] == p and sub_board[9] == p )
                or( sub_board[1] == p and sub_board[5] == p and sub_board[9] == p )
                or( sub_board[3] == p and sub_board[5] == p and sub_board[7] == p ))

    # check subboard is fulled
    def is_full_board(self,sub_board):
        for i in sub_board:
            if i == 0:
                return False
        return True

    # check gameboards is terminated
    def is_terminate(self,board,curr_board):
        if self.subboardwon(1,board[curr_board]):
            return 1
        elif self.subboardwon(2,board[curr_board]):
            return 2
        elif self.is_full_board(board[curr_board]):
            return 0
        else:
            return -1

# connect to socket
def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    port = int(sys.argv[2]) # Usage: ./agent.py -p (port)
    s.connect(('localhost', port))

    gameBoard = GameBoard()

    while True:
        text = s.recv(1024).decode()
        if not text:
            continue
        for line in text.split("\n"):
            response = gameBoard.parse(line)
            if response == -1:
                # global n_win
                # global n_game
                # gameBoard = GameBoard()
                # print("n_win",n_win)
                s.close()
                return
            elif response > 0:
                s.sendall((str(response) + "\n").encode())

if __name__ == "__main__":
    main()
