from main import *

class Piece:
    def __init__(self, row, col, color, king=False):
        self.row = row
        self.col = col
        self.color = color
        self.selected = False
        self.king = king

    def make_king(self):
        self.king = True

    def select(self, selected = True):
        self.selected = selected

    def move(self, movey, movex):
        self.col = movex
        self.row = movey
        self.selected = False
        if self.row == ROWS-1 or self.row == 0:
            self.make_king()

    def draw_piece(self, screen):
        pixelCol = self.col * SQUARESIZE + SQUARESIZE // 2
        pixelRow = self.row * SQUARESIZE + SQUARESIZE // 2

        if self.selected:
            pygame.draw.circle(screen, RED, (pixelCol, pixelRow), SQUARESIZE//2-12)

        pygame.draw.circle(screen, self.color, (pixelCol, pixelRow), SQUARESIZE//2-15)

        if self.king:
            font = pygame.font.Font(None, 40)
            text = font.render('K', True, BLACK if self.color == WHITE else WHITE)
            text_rect = text.get_rect(center=(pixelCol, pixelRow))
            screen.blit(text, text_rect)
