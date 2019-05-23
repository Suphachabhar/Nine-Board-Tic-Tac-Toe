
import itertools

import numpy as np
import pickle

def count_player(subboard,player,num_of_player_place):
        # rows
        num_result = 0
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


all_heuristic_board = {}

def heuristic_9board(subboard):
    this_heuristic = 0

    for i in range(1,10):
        board_tuple = tuple([ _ for _ in subboard])
        if board_tuple in all_heuristic_board:
            this_eval = all_heuristic_board[board_tuple]
        else :
            this_eval = ((7 * count_player(subboard,1,2) + count_player(subboard,1,1)) - (7 * count_player(subboard,2,2) + count_player(subboard,2,1)))
            all_heuristic_board[board_tuple] = this_eval
        this_heuristic += this_eval  
    return this_heuristic



for a in range(3):
    for b in range(3):
        for c in range(3):
            for d in range(3):
                for e in range(3):
                    for f in range(3):
                        for g in range(3):
                            for h in range(3):
                                for i in range(3):
                                    boards = np.zeros(10, dtype="int8")
                                    boards[1] = a
                                    boards[2] = b
                                    boards[3] = c
                                    boards[4] = d
                                    boards[5] = e
                                    boards[6] = f
                                    boards[7] = g
                                    boards[8] = h
                                    boards[9] = i
                                    heuristic_9board(boards)

with open("data.pkl","wb") as data_file:
    pickle.dump(all_heuristic_board,data_file)

print("done")