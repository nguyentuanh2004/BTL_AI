import pygame
from .glob_misc import GOLD, GREEN, BLUE, SQR_DIM, LINE_WIDTH, TIME_DELAY, M_FONT
from checkers.board import Board


class Game:
    def __init__(self, surface, gui, difficulty, verbose, playerTurn):
        self.selected_counter = None
        self.valid_moves = []
        self.surface = surface
        self.dificulty = difficulty
        self.verbose = verbose
        self.playerTurn = playerTurn
        self.board = Board(self.playerTurn)
        self.gui = gui

    def player_win(self):
        """
        :return: the output of game_board's player surface function
        """
        return self.board.player_win()

    def update(self):
        """
        update draws the game game_board and valid moves, then updates the screen.
        :return:
        """
        self.board.draw(self.surface)
        self.draw_valid_counters()
        self.draw_moves(self.valid_moves)
        pygame.display.update()
        if not self.playerTurn and self.verbose:
            pygame.time.delay(TIME_DELAY)

    def draw_valid_counters(self):
        """
        draw_valid_counters draws the counters that can be moved (in the case of a force capture only
        these counters will be valid)
        :return:
        """
        radius = SQR_DIM // 2 - (LINE_WIDTH + 5)
        valid_counters = self.board.get_valid_counters(self.playerTurn)
        for counter in valid_counters:
            row = counter.row
            col = counter.col
            x = SQR_DIM * col + SQR_DIM // 2
            y = SQR_DIM * row + SQR_DIM // 2
            if counter is self.selected_counter:
                pygame.draw.circle(self.surface, GREEN, (x, y), radius + LINE_WIDTH)
            else:
                pygame.draw.circle(self.surface, BLUE, (x, y), radius + LINE_WIDTH)
            if counter.king:
                pygame.draw.circle(
                    self.surface, GOLD, (x, y), radius + (LINE_WIDTH // 2)
                )
            pygame.draw.circle(self.surface, counter.get_colour(), (x, y), radius)

    def click_on_square(self, row, col):
        """
        click_on_square handles the user clicking on a square
        :param row: row of square being clicked
        :param col: col of square being clicked
        :return:
        """
        if self.selected_counter is not None and (row, col) in self.valid_moves:
            jumped, new_king = self.board.move_counter(self.selected_counter, row, col)
            new_counter = self.board.get_counter(row, col)
            if jumped and len(self.board.jump_moves(new_counter)) > 0 and not new_king:
                self.valid_moves = []
            else:
                self.change_turn()
        elif self.selected_counter is not None and self.board.get_counter(
            row, col
        ) not in self.board.get_sides_counters(True):
            self.gui.output_message("Move out of range!", M_FONT)
            pygame.time.delay(TIME_DELAY)
        elif self.board.get_counter(row, col) in self.board.get_sides_counters(False):
            self.gui.output_message("This isn't your counter!", M_FONT)
            pygame.time.delay(TIME_DELAY)
        elif self.board.get_counter(row, col) not in self.board.get_sides_counters(
            True
        ) + self.board.get_sides_counters(False):
            self.gui.output_message("There is no counter here!", M_FONT)
            pygame.time.delay(TIME_DELAY)
        else:
            valid_counters = self.board.get_valid_counters(True)
            temp_counter = self.board.get_counter(row, col)
            if temp_counter in valid_counters:
                self.selected_counter = temp_counter
            else:
                self.selected_counter = None
            self.valid_moves = self.board.get_valid_moves(self.selected_counter)
        self.update()

    def change_turn(self):
        """
        change_turn inverts the changes the side playing and removes the current
        valid_moves
        """
        self.valid_moves = []
        self.selected_counter = None
        self.playerTurn = not self.playerTurn

    def draw_moves(self, moves):
        """
        draw_moves draws the moves
        :param moves: list of moves to draw
        """
        for move in moves:
            row, col = move
            pygame.draw.rect(
                self.surface,
                GREEN,
                (col * SQR_DIM, row * SQR_DIM, SQR_DIM, SQR_DIM),
            )

    def ai_move(self, board, multi_leg):
        """
        ai_move updates the game to reflect the ai's move_counter choice
        :param board: the new game game_board layout
        """
        self.board = board
        if not multi_leg:
            self.change_turn()
        else:
            self.valid_moves = []

    # GETTERS
    def get_board(self):
        """
        get_board returns the game board
        :return: game board
        """
        return self.board
