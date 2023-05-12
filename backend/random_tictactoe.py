import copy
import random
import direction as Direction
from enum import Enum
class Piece(Enum):
    ALLY = 'x'
    ENEMY = 'o'
class RandomTicTacToeAI:
     def __init__(self, player):
        self.current_player = player
        self.next_player = Piece.ENEMY if self.current_player == Piece.ALLY else Piece.ALLY

     def get_move(self, board, size):
        # Find all available positions on the board
        size = int(size)
        available_moves = []
        for i in range(size):
            for j in range(size):
                if board[i][j] == ' ':
                    available_moves.append((i, j))
                    
        # If there are no available moves, return None
        if not available_moves:
            return None
        # Choose a random available move
        return available_moves[random.randint(0, len(available_moves) - 1)]