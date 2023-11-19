from piece import *
from jumpmove import *
from copy import deepcopy
import time

class Board:
    def __init__(self, screen):
        self.screen = screen
        self.board = self.create_board()
        self.isPieceSelected = False
        self.pieceSelected = EMPTY
        self.n_black_pieces = 12
        self.n_white_pieces = 12



    # create the internal board
    def create_board(self):
        board = []

        for _ in range(ROWS):
            board.append([EMPTY] * COLS)

        for row in range(ROWS):
            for col in range(COLS):
                if col % 2 == ((row + 1) % 2):
                    if row < 3:
                        board[row][col] = Piece(col, row, BLACK)

                    elif row > 4:
                        board[row][col] = Piece(col, row, WHITE)
        print(board)
        return board

    # update the number of pieces a player has on the board
    def update_game_state(self): 
        self.white_pieces = 0
        self.black_pieces = 0
        for row in range(ROWS):
            for col in range(COLS):
                piece = self.board[row][col]
                if piece != EMPTY:
                    if piece.color == WHITE:
                        self.white_pieces += 1
                    else:
                        self.black_pieces += 1

    # draw current state of the board
    def draw_board(self):
        self.draw_empty_board()
        for row in range(ROWS): 
            for col in range(COLS):
                piece = self.board[row][col]
                if piece != EMPTY:
                    piece.draw_piece(self.screen)
        pygame.display.update()

    # draw the background of the board
    def draw_empty_board(self):
        self.screen.fill(DARKBROWN)
        for row in range(ROWS):
            for col in range(row % 2, COLS, 2):
                pygame.draw.rect(self.screen, LIGHTBROWN, (col * SQUARESIZE, row * SQUARESIZE, SQUARESIZE, SQUARESIZE))


    def is_position_on_board(self, col, row):
        if row == None or col == None:
            return False
        if row >= 0 and row < ROWS and col >= 0 and col < COLS:
            return True
        else:
            return False

    def execute_mousepress(self, col, row, curr_player_color):
        if row is None or col is None:
            return False
        
        piece = self.board[row][col]
        print(f'curr_position: {row}, {col}')

        # No piece selected and the clicked position contains the current player's piece
        if not self.isPieceSelected and piece != EMPTY and piece.color == curr_player_color:
            piece.select()
            self.isPieceSelected = True
            self.pieceSelected = piece
            return False

        # Piece already selected, but the clicked position is not a valid move or it's the player's own piece
        if self.isPieceSelected and piece != EMPTY and piece.color == curr_player_color:
            self.pieceSelected.select(False)  # Deselect the currently selected piece
            piece.select()  # Select the new piece
            self.pieceSelected = piece
            return False



        # Piece already selected, check if valid move
        if self.isPieceSelected:
            possible_moves = self.possible_moves(curr_player_color)

            return False
            isValid, adversaries = self.is_valid_move(self.pieceSelected, piece)
            if isValid:
                self.move(col, row)  # Move the piece to the new position
                #TODO: implement this
                self.remove(adversaries)
                self.isPieceSelected = False
                self.pieceSelected.select(False)  # Deselect the piece
                return True

    def possible_moves(self, color) -> list:
        simple_moves = []
        jump_moves = []

        for row in range(ROWS): 
            for col in range(COLS):
                piece = self.board[row][col]
                if piece == EMPTY:
                    continue
                if piece.color == color:
                    self.get_valid_moves_for_piece(piece)



    def simulate_jump(previous_board, start, end, captured_stone):
        simulated_board = previous_board.copy()

        simulated_board[start.row][start.col] = EMPTY
        simulated_board[captured_stone.row][captured_stone.col] = EMPTY
        simulated_board[end.row][end.col] = end

        return simulated_board

    def get_directions_for_piece(self, piece):
        y_direction = 1 if piece.color == BLACK else -1
        directions = [[y_direction, 1], [y_direction, -1]] 
        if piece.king: 
            directions.append([[-y_direction, 1], [-y_direction, -1]])
        return directions
    
    def get_simple_moves_for_piece(self, piece, directions):
        simple_moves = []
        for direction in directions:
            piece_to_check = self.board[piece.row + direction[0]][piece.col + direction[1]]
            if not self.is_position_on_board(piece_to_check.row, piece_to_check.col):
                continue

            if piece_to_check == EMPTY:
                simple_moves.add([piece, piece_to_check])
        return simple_moves
    
    def get_jump_moves_for_piece(self, piece, directions, total_start, previous_landings, previously_captured_pieces):

        jump_moves = []
        recursion = False
        for direction in directions:
            piece_to_check = self.board[piece.row + direction[0]][piece.col + direction[1]]
            if not self.is_position_on_board(piece_to_check.row, piece_to_check.col):
                continue

            if piece_to_check != EMPTY and piece_to_check.color != piece.color:
                possible_landing = self.board[piece_to_check.row + direction[0]][piece_to_check.col + direction[1]]
                if possible_landing == EMPTY:
                    recursion = True
                    previous_landings_new = previous_landings.copy()
                    previous_landings_new.append(possible_landing)

                    previously_captured_pieces_new = previously_captured_pieces.copy()
                    previously_captured_pieces_new.append(piece_to_check)

                    simulated_board = self.simulate_jump(self, piece, possible_landing, piece_to_check)
                    jump_moves.append(simulated_board.get_jump_moves_for_piece(simulated_board, simulated_board[possible_landing.row][possible_landing.col], total_start, previous_landings_new, previously_captured_pieces_new))
        
        if recursion or len(previous_landings) == 0:
            return jump_moves
        else:
            return [Jumpmove(total_start, previous_landings, previously_captured_pieces)]



    # returns two lists: List 1 contains all possible simple moves. List 2 contains all possible jump moves
    def get_valid_moves_for_piece(self, piece):
        print(f'checking adjancent positions of : {piece.row}, {piece.col}')

        directions = self.get_directions_for_piece(self, piece)
        simple_moves = self.get_simple_moves_for_piece(self, piece, directions)
        jump_moves = self.get_jump_moves_for_piece(self, piece, directions, piece, [])

        return [simple_moves, jump_moves]


    def is_valid_move(self, from_piece: Piece, to_piece: Piece):
        # Check if the 'from' piece is a valid piece and not empty
        if from_piece == EMPTY or from_piece.color is None:
            return False
        
        # Check if the destination position is a valid position on the board
        if not self.is_position_on_board(to_piece.col, to_piece.row):
            return False

        if to_piece != EMPTY:
            return False


        return True


    def move(self, col, row):
        self.board[row][col] = self.board[self.pieceSelected.row][self.pieceSelected.col]
        self.board[self.pieceSelected.row][self.pieceSelected.col] = EMPTY
        self.pieceSelected.move(col, row)