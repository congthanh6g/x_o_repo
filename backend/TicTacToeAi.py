import copy
import random
import direction as Direction
from enum import Enum

class Direction(Enum):
    VERTICAL = ((-1, 0), (1, 0))
    HORIZONTAL = ((0, -1), (0, 1))
    MAIN_DIAG = ((-1, -1), (1, 1))
    ANTI_DIAG = ((-1, 1), (1, -1))
    TRAVERSE_VERTICALLY = (1, 0)
    TRAVERSE_HORIZONTALY = (0, 1)
    TRAVERSE_MAIN_DIAG = (1, 1)
    TRAVERSE_ANTI_DIAG = (1, -1)
    DIR = ((-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, 1), (-1, 1), (1, -1))


DV = Direction.VERTICAL
DH = Direction.HORIZONTAL
DM = Direction.MAIN_DIAG
DA = Direction.ANTI_DIAG
dV = Direction.TRAVERSE_VERTICALLY
dH = Direction.TRAVERSE_HORIZONTALY
dM = Direction.TRAVERSE_MAIN_DIAG
dA = Direction.TRAVERSE_ANTI_DIAG
dirs = Direction.DIR
STREAK_LEN = 5
win_situation_score = 1000
lose_situation_score = 900

class Piece(Enum):
    ALLY = 'x'
    ENEMY = 'o'

class TicTacToeAI:
    def __init__(self, player):
        self.current_player = player
        self.next_player = Piece.ENEMY if self.current_player == Piece.ALLY else Piece.ALLY

    def check_empty(self, board, size):
        for i in range(size):
            for j in range(size):
                if board[i][j] != ' ':
                    return False
        return True
    
    def printBoard(self, board, size):
        new_board = [['_' for _ in range(size)] for _ in range(size)]
        for i in range(size):
            for j in range(size):
                if board[i][j] != ' ':
                    new_board[i][j] = board[i][j]
        for i in range(size):
            print(new_board[i])

    def get_move(self, board, size):
        # Find all available positions on the board
        size = int(size)
        
        if self.check_empty(board, size) == True:
            if size % 2 == 1:
                best_move = ((size - 1) / 2 , (size - 1) / 2)
            else :
                best_move = (size / 2 , size / 2)
        else:
            taken = []
            for i in range(size):
                for j in range(size):
                    if board[i][j] != " ":
                        taken.append((i , j))

            possible_moves = []
            for dir in dirs.value:
                for coord in taken:
                    for length in range(1, STREAK_LEN):
                        move = self._march(coord, dir, length, size)
                        if move not in taken and move not in possible_moves:
                            possible_moves.append(move)
            best_score = float('-inf')
            print(len(possible_moves))
            for move in possible_moves:
                score = self.score_move(board, move , size)
                print(f"Move : {move} with point = {score}")
                if score > best_score:
                    best_score = score
                    best_move = move
        return best_move
    
    def get_move_input(self):
        r, c = input('Enter row, col: ').split()
        return int(r), int(c) 

        
    def validate(self, r, c, size):
        return r >= 0 and r < size and c >= 0 and c < size
    
    def _march(self, coord, direction, len, size):

        start_row, start_col = coord
        dir_row, dir_col = direction
        end_row = start_row + dir_row * len
        end_col = start_col + dir_col * len

        while not self.validate(end_row, end_col, size):
            end_row -= dir_row
            end_col -= dir_col
        
        return end_row, end_col
    
    # piece = self.player
    def _score_cell(self, piece, coord, board, size):
        r, c = coord
        score_dir = {DV.name: [], DH.name: [], DM.name: [], DA.name: []}

        score_dir[DV.name].extend(self._score_series(self._march(coord, DV.value[0], STREAK_LEN - 1, size), dV.value, 
                                                     self._march(coord, DV.value[1], STREAK_LEN - 1, size), piece, board))
        
        score_dir[DH.name].extend(self._score_series(self._march(coord, DH.value[0], STREAK_LEN - 1, size), dH.value, 
                                                     self._march(coord, DH.value[1], STREAK_LEN - 1, size), piece, board))
        
        score_dir[DM.name].extend(self._score_series(self._march(coord, DM.value[0], STREAK_LEN - 1, size), dM.value, 
                                                     self._march(coord, DM.value[1], STREAK_LEN - 1, size), piece, board))
        
        score_dir[DA.name].extend(self._score_series(self._march(coord, DA.value[0], STREAK_LEN - 1, size), dA.value, 
                                                     self._march(coord, DA.value[1], STREAK_LEN - 1, size), piece, board))
        
        return self._statistics_score(score_dir)
    
    def _score_series(self, start_coord, direction, end_coord, piece, board):

        def get_series(board, start_coord, end_coord, direction):
            start_row, start_col = start_coord
            dir_row, dir_col = direction
            end_row, end_col = end_coord

            series = []
            while start_row != end_row + dir_row or start_col != end_col + dir_col:
                series.append(board[start_row][start_col])
                start_row += dir_row
                start_col += dir_col
            return series
        
        series = get_series(board, start_coord, end_coord, direction)
        series_scores = []
        def score_of_five_cell(cell_list, piece):

            blank = cell_list.count(" ")
            filled = cell_list.count(piece)

            if blank + filled < 5:
                return -1
            else:
                return filled
        
        for start in range(len(series) - 4):
            score = score_of_five_cell(series[start:start + 5], piece)
            series_scores.append(score)

        return series_scores
    
    def _statistics_score(self, score_dir):
        statistics_score = {1: {}, 2: {}, 3: {}, 4: {}, 5: {}, -1: {}}
        for dir in score_dir:
            direction = Direction[dir].value[1]
            for score in score_dir[dir]:
                if direction in statistics_score[score]:
                    statistics_score[score][direction] += 1
                else:
                    statistics_score[score][direction] = 1
        return statistics_score
    
    def _synthesize_score(self, statistics_score):
        synthesized_scores = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, -1: 0}
        for score in statistics_score:
            if score == STREAK_LEN:
                synthesized_scores[score] = 1 if statistics_score[score] else 0
            else:
                synthesized_scores[score] = sum(statistics_score[score].values())
        return synthesized_scores
    
    def score_move(self, board , move, size):
        res = dis = adv = 0
        r, c = move
        # O
        ally = self.current_player.value
        
        # X
        enemy = self.next_player.value
        
        
        # Advantage of ally if ally makes the move
        board[r][c] = ally
        
        statistics_score = self._score_cell(ally, move, board, size)
        win_situation = self._win_situation(statistics_score)
        attack_score = self._synthesize_score(statistics_score)
        adv += (win_situation * win_situation_score + attack_score[-1] + attack_score[1] + 4 * attack_score[2] 
                + 9 * attack_score[3] + 16 * attack_score[4])
        
        # Disadvantage of ally if enemy makes the move
        board[r][c] = enemy
        
        statistics_score = self._score_cell(enemy, move, board, size)
        lose_situation = self._win_situation(statistics_score)
        defend_score = self._synthesize_score(statistics_score)
        dis += (lose_situation * lose_situation_score + defend_score[-1] + defend_score[1] + 4 * defend_score[2]
                + 9 * defend_score[3] + 16 * defend_score[4])
        

        res = adv + dis
        board[r][c] = " "
        return res
    
    def _win_situation(self, statistics_score):
        if statistics_score[STREAK_LEN]:
            return 5
        else:
            # Two 4 streaks with different directions can win
            if len(statistics_score[4]) >= 2:
                return 4
            elif len(statistics_score[4]) == 1:
                # In one direction if has two 4 streaks, it can win
                dir_4 = list(statistics_score[4].keys())[0]
                if statistics_score[4][dir_4] >= 2:
                    return 4
                else:
                    # If a diretion has a 4 streaks and another direction has a 3 streaks that not be blocked, it can win
                    for dir_3 in statistics_score[3]:
                        if statistics_score[3][dir_3] >= 2 and dir_3 != dir_4:
                            return 4
            else:
                # If two directions has 3 streaks that not be blocked, it can win
                score_3 = sorted(statistics_score[3].values(), reverse=True)
                if len(score_3) >= 2 and score_3[0] >= score_3[1] >= 2:
                    return 3
        return 0
