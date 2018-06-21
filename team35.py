import random
import copy
import time

MAX = 20000000
MIN = -20000000

class Team35:
    def __init__(self):
        self.old_move = (-1,-1)
        self.player_map = {}
        self.timer = 0
        self.mini_win = 0
        self.mini_lose = 0
        self.dyn_depth = 3
        self.loc_score = {0:150,1:200,2:250}
        self.block_score = {0:0, 1:1, 2:10, 3:100 , 4:2000}
        self.bl_block_score = {0:0, 1:10, 2:100, 3:1000 ,4:10000}
        self.cur_block_util = [0 for i in range(16)]
        self.flg = 0

    def move(self,board,old_move,flag):
        cells = board.find_valid_move_cells(old_move)
        self.timer = time.time()
        if old_move[0] < 0 and old_move[1] < 0:
            return (3,8)
        if flag == 'x':
            self.player_map[True] = 'x'
            self.player_map[False] = 'o'
        else:
            self.player_map[True] = 'o'
            self.player_map[False] = 'x'
        temp_block = board.block_status
        if self.flg == 0:
            self.flg = 1
            for i in range(16):
                self.cur_block_util[i] = self.get_util_cur(board,i,old_move,True)

        for i in temp_block:
            for j in i:
                if j == self.player_map[True]:
                    self.mini_win += 1
                elif j == self.player_map[False]:
                    self.mini_lose += 1
        if self.mini_win + 1 < self.mini_lose :
            self.dyn_board = 4
        temp_board = copy.deepcopy(board)
        move = self.temp_move_checker(temp_board, old_move, 3, cells)
        return move


    def temp_move_checker(self, board, old_move, depth, cells):
        maximum = MIN
        index_list = []
        best = MIN
        for i in range(len(cells)):
            board.update(old_move, cells[i], self.player_map[True])
            best = self.minimax(board, depth, cells[i], False, MIN, MAX)
            board.board_status[cells[i][0]][cells[i][1]] = '-'
            board.block_status[cells[i][0]/4][cells[i][1]/4] = '-'
            if best > maximum:
                maximum = best
                index_list = []
                index_list.append(i)
            elif best == maximum:
                index_list.append(i)
        temp = cells[random.choice(index_list)]
        return temp

    def minimax(self,board,depth,old_move,isMaxim,alpha,beta):
        check_win = board.find_terminal_state()

        if depth == self.dyn_depth or check_win != ('CONTINUE', '-'):
            return self.heuristic(board,old_move,isMaxim)

        else:
            cells = board.find_valid_move_cells(old_move)

            if len(cells) == 0:
                best = self.heuristic(board,old_move,isMaxim)
                self.dyn_depth = max(depth, 3)

            if depth == 0 :
                if len(cells) > 12:
                    self.dyn_depth = min(self.dyn_depth, 2)

            if isMaxim:
                best = MIN
                for i in range(len(cells)):
                    board.update(old_move, cells[i], self.player_map[True])
                    cur_value = self.minimax(board,depth-1,cells[i],False,alpha,beta)
                    best = max(best, cur_value)
                    board.board_status[cells[i][0]][cells[i][1]] = '-'
                    board.block_status[cells[i][0]/4][cells[i][1]/4] = '-'
                    alpha = max(alpha,best)
                    if (beta <= alpha):
                        break
                return best
            else:
                best = MAX
                for i in range(len(cells)):
                    board.update(old_move, cells[i], self.player_map[False])
                    cur_value = self.minimax(board,depth-1,cells[i],True,alpha,beta)
                    best = min(best, cur_value)
                    board.board_status[cells[i][0]][cells[i][1]] = '-'
                    board.block_status[cells[i][0]/4][cells[i][1]/4] = '-'
                    beta = min(beta,best)
                    if (beta <= alpha):
                        break
                return best


    def heuristic(self,board,old_move,isMaxim):
        #Check the Match is won or not : Don't need to continue of won or lost
        cur_state =  board.find_terminal_state()


        slice_x = old_move[0]/4
        slice_y = old_move[1]/4
        cur_pos = (slice_x*4) + slice_y

        self.cur_block_util[cur_pos] = self.get_util_cur(board,cur_pos,old_move,isMaxim)

        board_gain = self.get_all_block_util(board,old_move,isMaxim)

        cur_win = 0
        cur_lose = 0
        for m in board.block_status:
            for n in m:
                if n == self.player_map[True]:
                    cur_win += 1
                elif n == self.player_map[False]:
                    cur_lose += 1

        if self.mini_win < cur_win and cur_lose == self.mini_lose:
            board_gain += 500.0
        elif cur_win > self.mini_win and (cur_win - self.mini_win) < (cur_lose - self.mini_lose):
            board_gain -= 200.0
        elif cur_lose > self.mini_lose:
            board_gain -= 500.0

        return board_gain

    def get_util_cur(self,board,board_no,old_move,isMaxim):

        us = self.player_map[True]
        slice_x = board_no/4
        slice_y = board_no%4
        if slice_x < 0:
            slice_x = 0
        if slice_y < 0:
            slice_y = 0
        block_temp = [row[slice_y * 4: slice_y*4 + 4] for row in board.board_status[slice_x * 4: slice_x * 4 + 4]]
        row_score = 0
        col_score = 0
        one_diag_score = 0
        two_diag_score = 0
        three_diag_score = 0
        four_diag_score = 0

        for i in range(4):

            row_count = 0
            row_neg_count = 0
            col_count = 0
            col_neg_count = 0
            one_diag_count = 0
            one_neg_diag_count = 0
            two_diag_count = 0
            two_neg_diag_count = 0
            three_diag_count = 0
            three_neg_diag_count = 0
            four_diag_count = 0
            four_neg_diag_count = 0

            for j in range(4):
                if block_temp[i][j] == us:
                    row_count += 1
                elif block_temp[i][j] == '-':
                    pass
                else:
                    row_neg_count += 1
            row_score = self.get_val_zero(row_count,row_neg_count,row_score)
            if row_count == 4:
                return 3000
            elif row_neg_count == 4:
                return -3000
            for j in range(4):
                if block_temp[j][i] == us:
                    col_count += 1
                elif block_temp[j][i] == '-':
                    pass
                else:
                    col_neg_count += 1
            col_score = self.get_val_zero(col_count,col_neg_count,col_score)
            if col_count == 4:
                return 3000
            elif col_neg_count == 4:
                return -3000


        # Diagonal check - Board
        if((us == block_temp[0][1]) ):
            one_diag_count += 1
        elif block_temp[0][1] == '-':
            pass
        else:
            one_neg_diag_count += 1
        if ((us == block_temp[2][1]) ):
            one_diag_count += 1
        elif block_temp[2][1] == '-':
            pass
        else:
            one_neg_diag_count += 1
        if ((us == block_temp[1][0]) ):
            one_diag_count += 1
        elif block_temp[1][0] == '-':
            pass
        else:
            one_neg_diag_count += 1
        if ((us == block_temp[1][2]) ):
            one_diag_count += 1
        elif block_temp[1][2] == '-':
            pass
        else:
            one_neg_diag_count += 1


        if((us == block_temp[0][2])):
            two_diag_count += 1
        elif block_temp[0][2] == '-':
            pass
        else:
            two_neg_diag_count += 1
        if((us == block_temp[2][2])):
            two_diag_count += 1
        elif block_temp[2][2] == '-':
            pass
        else:
            two_neg_diag_count += 1
        if((us == block_temp[1][1])):
            two_diag_count += 1
        elif block_temp[1][1] == '-':
            pass
        else:
            two_neg_diag_count += 1
        if((us == block_temp[1][3])):
            two_diag_count += 1
        elif block_temp[1][3] == '-':
            pass
        else:
            two_neg_diag_count += 1


        if((us == block_temp[1][1])):
            three_diag_count += 1
        elif block_temp[1][1] == '-':
            pass
        else:
            three_neg_diag_count += 1
        if((us == block_temp[3][1])):
            three_diag_count += 1
        elif block_temp[3][1] == '-':
            pass
        else:
            three_neg_diag_count += 1
        if((us == block_temp[2][0])):
            three_diag_count += 1
        elif block_temp[2][0] == '-':
            pass
        else:
            three_neg_diag_count += 1
        if((us == block_temp[2][2])):
            three_diag_count += 1
        elif block_temp[2][2] == '-':
            pass
        else:
            three_neg_diag_count += 1


        if((us == block_temp[1][2])):
            four_diag_count += 1
        elif block_temp[1][2] == '-':
            pass
        else:
            four_neg_diag_count += 1
        if((us == block_temp[3][2])):
            four_diag_count += 1
        elif block_temp[3][2] == '-':
            pass
        else:
            four_neg_diag_count += 1
        if((us == block_temp[2][1])):
            four_diag_count += 1
        elif block_temp[2][1] == '-':
            pass
        else:
            four_neg_diag_count += 1
        if((us == block_temp[2][3])):
            four_diag_count += 1

        one_diag_score = self.get_val_zero(one_diag_count,one_neg_diag_count,one_diag_score)
        two_diag_score = self.get_val_zero(two_diag_count,two_neg_diag_count,two_diag_score)
        three_diag_score = self.get_val_zero(three_diag_count,three_neg_diag_count,three_diag_score)
        four_diag_score = self.get_val_zero(four_diag_count,four_neg_diag_count,four_diag_score)
        if one_diag_count == 4 or two_diag_count == 4 or three_diag_count == 4 or four_diag_count == 4:
            return 3000
        elif one_neg_diag_count == 4 or two_neg_diag_count == 4 or three_neg_diag_count == 4 or four_neg_diag_count == 4:
            return -3000

        return col_score + row_score + one_diag_score + two_diag_score + three_diag_score + four_diag_score

    def get_all_block_util(self,board,old_move,isMaxim):
        us = self.player_map[True]
        block_temp = board.block_status
        lin_block = []
        total = 0
        for i in block_temp:
            for j in i:
                lin_block.append(j)
        for i in range(16):
            if (i == 0 or i == 3 or i == 12 or i == 15)and lin_block[i] == us:
                total += self.loc_score[2]
            if (i == 0 or i == 3 or i == 12 or i == 15)and lin_block[i] == us:
                total += self.loc_score[1]
            if (i == 0 or i == 3 or i == 12 or i == 15)and lin_block[i] == us:
                total += self.loc_score[0]
        slice_x = old_move[0]/4
        slice_y = old_move[1]/4
        cur_pos = (slice_x*4) + slice_y
        row_score = 0
        col_score = 0
        one_diag_score = 0
        two_diag_score = 0
        three_diag_score = 0
        four_diag_score = 0

        for i in range(4):

            p = 0
            p1 = 0
            p2 = 0
            row_count = 0
            row_neg_count = 0
            col_count = 0
            col_neg_count = 0
            total = 0
            one_diag_count = 0
            one_neg_diag_count = 0
            two_diag_count = 0
            two_neg_diag_count = 0
            three_diag_count = 0
            three_neg_diag_count = 0
            four_diag_count = 0
            four_neg_diag_count = 0

            for j in range(4):
                p += self.cur_block_util[(i*4)+j]
                if block_temp[i][j] == us:
                    row_count += 1
                elif block_temp[i][j] == '-' or block_temp[i][j] == 'd':
                    pass
                else:
                    row_neg_count += 1
                    break

            for j in range(4):
                p1 += self.cur_block_util[(j*4)+i]
                if block_temp[j][i] == us:
                    col_count += 1
                elif block_temp[j][i] == '-' or block_temp[i][j] == 'd':
                    pass
                else:
                    col_neg_count += 1
                    break

            if(i == 0):
                p2 = self.cur_block_util[1] + self.cur_block_util[4] + self.cur_block_util[9] + self.cur_block_util[6]
            elif(i == 1):
                p2 = self.cur_block_util[2] + self.cur_block_util[10] + self.cur_block_util[5] + self.cur_block_util[7]
            elif(i == 2):
                p2 = self.cur_block_util[5] + self.cur_block_util[8] + self.cur_block_util[10] + self.cur_block_util[13]
            elif(i == 3):
                p2 = self.cur_block_util[6] + self.cur_block_util[14] + self.cur_block_util[9] + self.cur_block_util[11]

            row_score = self.get_val_zero(row_count,row_neg_count,row_score)
            col_score = self.get_val_zero(col_count,col_neg_count,col_score)

            if((us == block_temp[0][1]) ):
                one_diag_count += 1
            elif block_temp[0][1] == '-':
                pass
            else:
                one_neg_diag_count += 1
            if ((us == block_temp[2][1]) ):
                one_diag_count += 1
            elif block_temp[2][1] == '-':
                pass
            else:
                one_neg_diag_count += 1
            if ((us == block_temp[1][0]) ):
                one_diag_count += 1
            elif block_temp[1][0] == '-':
                pass
            else:
                one_neg_diag_count += 1
            if ((us == block_temp[1][2]) ):
                one_diag_count += 1
            elif block_temp[1][2] == '-':
                pass
            else:
                one_neg_diag_count += 1


            if((us == block_temp[0][2])):
                two_diag_count += 1
            elif block_temp[0][2] == '-':
                pass
            else:
                two_neg_diag_count += 1
            if((us == block_temp[2][2])):
                two_diag_count += 1
            elif block_temp[2][2] == '-':
                pass
            else:
                two_neg_diag_count += 1
            if((us == block_temp[1][1])):
                two_diag_count += 1
            elif block_temp[1][1] == '-':
                pass
            else:
                two_neg_diag_count += 1
            if((us == block_temp[1][3])):
                two_diag_count += 1
            elif block_temp[1][3] == '-':
                pass
            else:
                two_neg_diag_count += 1


            if((us == block_temp[1][1])):
                three_diag_count += 1
            elif block_temp[1][1] == '-':
                pass
            else:
                three_neg_diag_count += 1
            if((us == block_temp[3][1])):
                three_diag_count += 1
            elif block_temp[3][1] == '-':
                pass
            else:
                three_neg_diag_count += 1
            if((us == block_temp[2][0])):
                three_diag_count += 1
            elif block_temp[2][0] == '-':
                pass
            else:
                three_neg_diag_count += 1
            if((us == block_temp[2][2])):
                three_diag_count += 1
            elif block_temp[2][2] == '-':
                pass
            else:
                three_neg_diag_count += 1


            if((us == block_temp[1][2])):
                four_diag_count += 1
            elif block_temp[1][2] == '-':
                pass
            else:
                four_neg_diag_count += 1
            if((us == block_temp[3][2])):
                four_diag_count += 1
            elif block_temp[3][2] == '-':
                pass
            else:
                four_neg_diag_count += 1
            if((us == block_temp[2][1])):
                four_diag_count += 1
            elif block_temp[2][1] == '-':
                pass
            else:
                four_neg_diag_count += 1
            if((us == block_temp[2][3])):
                four_diag_count += 1

            one_diag_score = self.get_val_zero(one_diag_count,one_neg_diag_count,one_diag_score)
            two_diag_score = self.get_val_zero(two_diag_count,two_neg_diag_count,two_diag_score)
            three_diag_score = self.get_val_zero(three_diag_count,three_neg_diag_count,three_diag_score)
            four_diag_score = self.get_val_zero(four_diag_count,four_neg_diag_count,four_diag_score)


            total += p + p1 + p2 + col_score + row_score + one_diag_score + two_diag_score + three_diag_score + four_diag_score

            return total

    def get_val_zero(self,count,neg_count,score):
        if neg_count > 0 and count > 0:
            score = 0
        elif neg_count > 0:
            score -= self.block_score[neg_count]
        elif count > 0:
            score += self.block_score[count]
        return score
