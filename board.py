from piece import *
from copy import deepcopy
import time

class Board:
    def __init__(self, screen):
        self.screen = screen
        self.board = self.create_board()
        self.isPieceSelected = False
        self.pieceSelected = EMPTY
        self.lockSelection = False



    # create the internal board
    def create_board(self):
        board = []

        for _ in range(ROWS):
            board.append([EMPTY] * COLS)

        for row in range(ROWS):
            for col in range(COLS):
                if col % 2 == ((row + 1) % 2):
                    if row < 3:
                        board[row][col] = Piece(row, col, BLACK)

                    elif row > 4:
                        board[row][col] = Piece(row, col, WHITE)
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
                        self.n_white_pieces += 1
                    else:
                        self.n_black_pieces += 1

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

    def execute_simple_move(self, start_piece, end_piece):
        print(f"moving piece: {start_piece.row}{start_piece.col} to {end_piece.row}{end_piece.col}")
        self.board[end_piece.row][end_piece.col] = end_piece
        self.board[start_piece.row][start_piece.col] = EMPTY
        if end_piece.row == ROWS-1 or end_piece.row == 0:
            end_piece.make_king()

    def execute_jump_move(self, start_piece, end_piece, captured_piece):
        self.board[end_piece.row][end_piece.col] = end_piece
        self.board[start_piece.row][start_piece.col] = EMPTY
        self.board[captured_piece.row][captured_piece.col] = EMPTY        
        
        if end_piece.row == ROWS-1 or end_piece.row == 0:
            end_piece.make_king()

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

        # Piece already selected, check if valid move
        if self.isPieceSelected:
            move_finished = False
            another_jump_mandatory = False
            possible_simple_moves, possible_jump_moves = self.possible_moves(curr_player_color)
            for simple_move in possible_simple_moves:
                start_piece = simple_move[0]
                end_piece = simple_move[1]
                print(f'trying to move piece: {self.pieceSelected.row}, {self.pieceSelected.col} to {row}, {col}' )
                print(f'comparing to move: {start_piece.row}, {start_piece.col} to {end_piece.row} {end_piece.col}')
                print(start_piece.row == self.pieceSelected.row)
                print(start_piece.col == self.pieceSelected.col)
                print(end_piece.row == row)
                print(end_piece.col == col)
                if start_piece.row == self.pieceSelected.row and start_piece.col == self.pieceSelected.col and end_piece.row == row and end_piece.col == col:
                    self.execute_simple_move(start_piece, end_piece)
                    move_finished = True

            print(str(len(possible_jump_moves)) + " many jump moves")
            for jump_move in possible_jump_moves:
                print(str(jump_move))
                start_piece = jump_move[0]
                end_piece = jump_move[1]
                captured_piece = jump_move[2]
                if start_piece.row == self.pieceSelected.row and start_piece.col == self.pieceSelected.col and end_piece.row == row and end_piece.col == col:
                    self.execute_jump_move(start_piece, end_piece, captured_piece)
                    directions = self.get_directions_for_piece(end_piece)
                    possible_additional_jumps = self.get_jump_moves_for_piece(end_piece, directions)
                    if possible_additional_jumps:
                        move_finished = False
                        self.pieceSelected = end_piece
                        end_piece.select(True)
                        self.lockSelection = True
                    else:
                        move_finished = True
                        self.lockSelection = False


            if not self.lockSelection:
                self.isPieceSelected = False
                self.pieceSelected.select(False)
                self.pieceSelected = EMPTY

            return move_finished


    def possible_moves(self, color) -> list:
        simple_moves = []
        jump_moves = []

        for row in range(ROWS): 
            for col in range(COLS):
                piece = self.board[row][col]
                if piece == EMPTY:
                    continue
                if piece.color == color:
                    current_simple_moves, current_jump_moves = self.get_valid_moves_for_piece(piece)
                    simple_moves.extend(current_simple_moves)
                    jump_moves.extend(current_jump_moves)

        if(len(jump_moves) > 0):
            simple_moves = []

        print(str(len(simple_moves)) + " many simple moves")
        print(str(len(jump_moves)) + " many jump moves")


        return simple_moves, jump_moves


    def get_directions_for_piece(self, piece):
        y_direction = 1 if piece.color == BLACK else -1
        directions = [[y_direction, 1], [y_direction, -1]] 
        if piece.king: 
            directions.extend([[-y_direction, 1], [-y_direction, -1]])
        return directions
    
    def get_simple_moves_for_piece(self, piece, directions):
        simple_moves = []
        for direction in directions:
            new_row = piece.row + direction[0]
            new_col = piece.col + direction[1]
            if not self.is_position_on_board(new_row, new_col):
                continue

            piece_to_check = self.board[new_row][new_col]


            if piece_to_check == EMPTY:
                simple_moves.append([piece, Piece(new_row, new_col, piece.color, piece.king)])
        return simple_moves
    
    def get_jump_moves_for_piece(self, piece, directions):

        jump_moves = []
        for direction in directions:
            new_row = piece.row + direction[0]
            new_col = piece.col + direction[1]
            if not self.is_position_on_board(new_row, new_col):
                continue
            piece_to_check = self.board[new_row][new_col]

            if piece_to_check != EMPTY and piece_to_check.color != piece.color:
                landing_row = piece_to_check.row + direction[0]
                landing_col = piece_to_check.col + direction[1]
                if not self.is_position_on_board(landing_row, landing_col):
                    continue
                possible_landing = self.board[piece_to_check.row + direction[0]][piece_to_check.col + direction[1]]

                if possible_landing == EMPTY:
                    jump_moves.append([piece, Piece(landing_row, landing_col, piece.color, piece.king), piece_to_check])
        
        return jump_moves
        



    # returns two lists: List 1 contains all possible simple moves. List 2 contains all possible jump moves
    def get_valid_moves_for_piece(self, piece):
        print(f'checking adjancent positions of : {piece.row}, {piece.col}')

        directions = self.get_directions_for_piece(piece)
        simple_moves = self.get_simple_moves_for_piece(piece, directions)
        jump_moves = self.get_jump_moves_for_piece(piece, directions)

        print("Possible simple moves: " + str(len(simple_moves)))
        print("Possible jump moves: " + str(len(jump_moves))) 

        return simple_moves, jump_moves


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
