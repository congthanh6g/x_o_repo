import direction as Direction

class Node:

    def __init__(self, board, player, parent=None):
        '''
        Parameters:
            board: a 2D list of the board
            parent: the parent node
            player: player
        '''
        self._board = board
        self._parent = parent
        self._player = player

    def _march(self, coord, direction, len):
        '''
        Parameters:
            coord: the starting coordinate
            direction: the direction of the march
            len: the length of the march
        Returns:
            the ending coordinate of the march
        '''
        start_row, start_col = coord
        dir_row, dir_col = direction
        end_row = start_row + dir_row * len
        end_col = start_col + dir_col * len

        while not self._board.validate(end_row, end_col):
            end_row -= dir_row
            end_col -= dir_col
        
        return end_row, end_col
    
    def possible_moves(self, board, size):
        
        taken = []
        for i in range(size):
            for j in range(size):
                if board[i][j] != ' ':
                    taken.append((i , j))
        
        possible_moves = []
        for dir in Direction.dirs.value:
            for coord in taken:
                for length in range(1, Direction.STREAK_LEN):
                    move = self._march(coord, dir, length)
                    if move not in taken and move not in possible_moves:
                        possible_moves.append(move)
        return possible_moves