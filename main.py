import pygame
import board
import sys
import caretaker
import memento
from copy import deepcopy
import tkinter as tk
from tkinter import simpledialog
import pickle
from constants import *
import os

class Checkers:
    def __init__(self):
        pygame.init()
        pygame.font.init()
        pygame.display.set_caption('Draughts')
        self.font = pygame.font.Font(None, 36)
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.running = True
        self.clock = pygame.time.Clock()
        self.fps = FPS
        self.board = board.Board(self.screen)
        self.turn = BLACK
        self.KEYUP = False
        self.caretaker = caretaker.Caretaker(memento.Memento(deepcopy(self.board.board), self.turn))

    def check_win_condition(self):
        simple_moves, jump_moves = self.board.possible_moves(self.turn)
        if not simple_moves and not jump_moves:
            return "BLACK" if self.turn is WHITE else "WHITE"

    def draw_start_screen(self):
        self.screen.fill(LIGHTBROWN)
        
        title = self.font.render("Game Instructions", True, BLACK)
        self.screen.blit(title, (260, 50))

        instructions = [
            "Press ENTER to start a game - always",
            "Press LEFT ARROW to undo the last move - always",
            "Press RIGHT ARROW to redo the last move - always",
            "Press 'L' to load game - only on start screen",
            "Press 'S' to save the current game - always"
        ]

        y_offset = 150
        for instruction in instructions:
            text = self.font.render(instruction, True, DARKBROWN)
            self.screen.blit(text, (100, y_offset))
            y_offset += 50

        pygame.display.flip()

    def draw_win(self, winner):
        self.screen.fill(LIGHTBROWN)
            
        winner_text = self.font.render(f"Player {winner} wins!", True, BLACK)
        self.screen.blit(winner_text, (250, 200))

        restart_text = self.font.render("Press ENTER to quit", True, DARKBROWN)
        self.screen.blit(restart_text, (250, 300))
        pygame.display.update()
        while True:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        return

    def play(self):
        while self.running:
            win = self.check_win_condition()
            if win:
                return win
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONUP:
                    movex, movey = self.get_square_clicked(event.pos[0], event.pos[1])
                    move = self.board.execute_mousepress(movex, movey, self.turn)
                    if move:                      
                        self.turn = BLACK if self.turn == WHITE else WHITE
                        self.caretaker.add_memento(memento.Memento(deepcopy(self.board.board), self.turn))
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        print("Undoing last move...")
                        curr_memento = self.caretaker.undo()
                        self.board.board = deepcopy(curr_memento.board)
                        self.turn = curr_memento.turn

                    if event.key == pygame.K_RIGHT:
                        print("Redoing last move...")
                        curr_memento = self.caretaker.redo()
                        self.board.board = deepcopy(curr_memento.board)
                        self.turn = curr_memento.turn

                    if event.key == pygame.K_s:
                        print("Saving current state of the game...")
                        self.save_game_state(self.caretaker)

            self.board.draw_board()
            self.clock.tick(self.fps)

    def wrap_play(self):
        self.draw_win(self.play())

    def start(self):
        self.draw_start_screen()
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        print("Starting new game...") 
                        self.wrap_play()
                        return
                    elif event.key == pygame.K_l:
                        print("Loading game state...") 
                        self.load_game_state()
                        memento = self.caretaker.get_current_memento()
                        self.board.board = deepcopy(memento.board)
                        self.turn = memento.turn
                        print("Game state loaded, starting game...")
                        self.wrap_play()
                        return
            pygame.display.update()

    def save_game_state(self, state):
        file_name = "game_state.pkl"

        counter = 0
        while os.path.exists(file_name):
            file_name = f"game_state_{counter}.pkl"
            counter += 1

        with open(file_name, 'wb') as outp:
            pickle.dump(state, outp)


    def load_game_state(self):
        root = tk.Tk()
        root.withdraw()
        try:
            file_name = simpledialog.askstring("Input", "Enter the name of the .pkl file:")
            
            if file_name:
                file_path = file_name + ".pkl"
                print("Selected file:", file_path)
                with open(file_path, 'rb') as inp:
                    self.caretaker = pickle.load(inp)
            else:
                print("No file name entered.")
        except Exception as e:
            print("An error occurred:", str(e))      


    def get_square_clicked(self, mousex, mousey):
        for x in range(ROWS):
            for y in range(COLS):
                if mousex > x * SQUARESIZE and mousex < (x + 1) * SQUARESIZE and \
                    mousey > y * SQUARESIZE and mousey < (y + 1) * SQUARESIZE:
                    return (x, y)
        return (None, None)

def main():
    checkers = Checkers()
    checkers.start()

    pygame.quit()

if __name__ == "__main__":
    main()
