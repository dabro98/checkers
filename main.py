import pygame
import board
import sys

# Constants
WIDTH, HEIGHT = 800, 800
ROWS, COLS = 8, 8
SQUARESIZE = 100
FPS = 30

EMPTY = 'empty'
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
LIGHTBROWN = (200, 157, 124)
DARKBROWN = (78, 53, 36)
DARKGREY = (105, 105, 105)
GRAY = (185, 185, 185)

class Checkers:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption('Checkers')
        self.running = True
        self.clock = pygame.time.Clock()
        self.fps = FPS
        self.board = board.Board(self.screen)
        self.turn = BLACK
        self.MOUSEBUTTONUP = False
        self.KEYUP = False

    def play(self):
        while self.running:
            self.get_events()
            if self.MOUSEBUTTONUP:
                movex, movey = self.get_square_clicked(self.pos[0], self.pos[1])
                move = self.board.execute_mousepress(movex, movey, self.turn)
                if move:
                    self.turn = BLACK if self.turn == WHITE else WHITE

            self.board.draw_board()
            self.clock.tick(self.fps)
    
    def get_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                sys.exit()
            if event.type == pygame.MOUSEBUTTONUP:
                self.MOUSEBUTTONUP = True
                self.pos = event.pos

    def get_square_clicked(self, mousex, mousey):
        for x in range(ROWS):
            for y in range(COLS):
                if mousex > x * SQUARESIZE and mousex < (x + 1) * SQUARESIZE and \
                    mousey > y * SQUARESIZE and mousey < (y + 1) * SQUARESIZE:
                    return (x, y)
        return (None, None)

    def resetKeys(self):  
        self.MOUSEBUTTONUP = False
        self.KEYUP = False

def main():
    # TODO: try reading saved game from config
    # create state of game using Factory pattern
    checkers = Checkers()
    checkers.play()

    pygame.quit()

if __name__ == "__main__":
    main()
