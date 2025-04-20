import pygame
from .glob_misc import (
    ROW_COL,
    SQR_DIM,
    TILE_BACKGROUND,
    TILE_ALTERNATE,
)
from .counter import Counter


class Board:
    def __init__(self, playerTurn):
        self.board = []
        self.player_remaining = self.comp_remaining = 12
        self.player_kings = self.comp_kings = 0
        self.playerTurn = playerTurn
        self.create_board()

    def create_board(self):
        """
        create_board creates the game game_board and places a counters in every other square
        """
        fill_rows = 3
        for row in range(ROW_COL):
            self.board.append([])
            for col in range(ROW_COL):
                if col % 2 == ((row + 1) % 2):
                    if row < fill_rows:
                        self.board[row].append(
                            Counter(row, col, False, self.playerTurn)
                        )
                    elif row > ((ROW_COL - 1) - fill_rows):
                        self.board[row].append(Counter(row, col, True, self.playerTurn))
                    else:
                        self.board[row].append(None)
                else:
                    self.board[row].append(None)

    def draw(self, surface):
        """
        draw draws the game game_board on the surface
        :param surface: the surface surface the game is being played on
        :return:
        """
        self.draw_squares(surface)
        for row in range(ROW_COL):
            for col in range(ROW_COL):
                counter = self.board[row][col]
                if counter is not None:
                    counter.draw(surface)

    def draw_squares(self, surface):
        """
        draw_squares draws the squares on the game game_board
        :param surface: the surface surface the game is being played on
        """
        surface.fill(TILE_BACKGROUND)
        for row in range(ROW_COL):
            for col in range(row % 2, ROW_COL, 2):
                pygame.draw.rect(
                    surface,
                    TILE_ALTERNATE,
                    (col * SQR_DIM, row * SQR_DIM, SQR_DIM, SQR_DIM),
                )

    def get_sides_counters(self, player):
        """
        get_sides_counters returns all of the counters one of the sides has.

        :param player: bool for whether the counters requested are the players or not
        :return:
        """
        counters = []
        for row in self.board:
            for counter in row:
                if counter is not None and counter.player == player:
                    counters.append(counter)
        return counters

    def get_valid_counters(self, player):
        """
        get_valid_counters returns all of the counters that can move_counter. In the case of
        a force capture, only counters that can capture shall be returned.
        :param player: bool for whether the counters requested are the players or not
        :return: list of valid counters that can be moved
        """
        valid = []
        force_capture = []
        counters = self.get_sides_counters(player)

        for counter in counters:
            moves = self.moves(counter)
            jump_moves = self.jump_moves(counter)
            if len(jump_moves) > 0:
                force_capture.append(counter)
            elif len(moves) > 0:
                valid.append(counter)

        if len(force_capture) > 0:
            return force_capture
        else:
            return valid

    def get_valid_moves(self, counter):
        """
        get_valid_moves returns a list of valid moves a counter may take
        :param counter: counter being checked for movement
        :return: list of moves
        """
        moves = self.moves(counter)
        jump_moves = self.jump_moves(counter)
        if len(jump_moves) > 0:
            return jump_moves
        else:
            return moves

    def moves(self, counter):
        """
        moves calculates all non jump moves a counter may take
        :param counter: counter being checked for movement
        :return: list of moves
        """
        moves = []
        if counter is not None:
            left = counter.col - 1
            right = counter.col + 1
            row = counter.row
            row_mods = self.get_row_mods(counter)
            for row_mod in row_mods:
                if (
                    ROW_COL > left >= 0
                    and ROW_COL > row + row_mod >= 0
                    and self.board[row + row_mod][left] is None
                ):
                    moves.append((row + row_mod, left))
                if (
                    ROW_COL > right >= 0
                    and ROW_COL > row + row_mod >= 0
                    and self.board[row + row_mod][right] is None
                ):
                    moves.append((row + row_mod, right))
        return moves

    def jump_moves(self, counter):
        """
        jump_moves all jump moves a counter may take
        :param counter: counter being checked for movement
        :return: list of moves
        """
        moves = []
        if counter is not None:
            left = counter.col - 1
            right = counter.col + 1
            row = counter.row
            row_mods = self.get_row_mods(counter)

            for row_mod in row_mods:
                if (
                    ROW_COL > left >= 0
                    and ROW_COL > row + row_mod >= 0
                    and self.board[row + row_mod][left] is not None
                ):
                    check_counter = self.board[row + row_mod][left]
                    if (
                        ROW_COL > check_counter.col - 1 >= 0
                        and ROW_COL > check_counter.row + row_mod >= 0
                        and check_counter.player != counter.player
                        and self.board[check_counter.row + row_mod][
                            check_counter.col - 1
                        ]
                        is None
                    ):
                        moves.append(
                            (check_counter.row + row_mod, check_counter.col - 1)
                        )
                if (
                    ROW_COL > right >= 0
                    and ROW_COL > row + row_mod >= 0
                    and self.board[row + row_mod][right] is not None
                ):
                    check_counter = self.board[row + row_mod][right]
                    if (
                        ROW_COL > check_counter.col + 1 >= 0
                        and ROW_COL > check_counter.row + row_mod >= 0
                        and check_counter.player != counter.player
                        and self.board[check_counter.row + row_mod][
                            check_counter.col + 1
                        ]
                        is None
                    ):
                        moves.append(
                            (check_counter.row + row_mod, check_counter.col + 1)
                        )
        return moves

    def move_counter(self, counter, row, col):
        """
        move_counter validates and moves a counter while checking for other game states that may change such as becoming
        king.
        :param counter: counter being moved
        :param row: new row
        :param col: new col
        :return: if the counter has jumped or just became king
        """
        jump = False
        new_king = False
        if (row > counter.row + 1 or row < counter.row - 1) and (
            col > counter.col + 1 or col < counter.col - 1
        ):
            jumped_counter = self.get_counter(
                counter.row + ((row - counter.row) // 2),
                counter.col + ((col - counter.col) // 2),
            )
            if not counter.king:
                if jumped_counter.king:
                    counter.make_king()
                    new_king = True
                    if counter.player:
                        self.player_kings += 1
                    else:
                        self.comp_kings += 1
            self.remove_counter(jumped_counter)
            jump = True

        self.board[counter.row][counter.col], self.board[row][col] = (
            self.board[row][col],
            self.board[counter.row][counter.col],
        )
        counter.move(row, col)

        if not counter.king:
            if row == ROW_COL - 1 or row == 0:
                counter.make_king()
                new_king = True
                if counter.player:
                    self.player_kings += 1
                else:
                    self.comp_kings += 1
        return jump, new_king

    def remove_counter(self, counter):
        if counter is not None:
            self.board[counter.row][counter.col] = None
            if counter.player:
                self.player_remaining -= 1
                if counter.king:
                    self.player_kings -= 1
            else:
                self.comp_remaining -= 1
                if counter.king:
                    self.player_kings -= 1

    # GETTERS
    def get_counter(self, row, col):
        """
        get_counter returns the counters held at the value of row and col
        :param row: row of the grid
        :param col: col of the grid
        :return: counters
        """
        return self.board[row][col]

    def player_win(self):
        """
        player_win returns true or false if a player or the computer has won
        in the case neihter has won, "None" shall be returned.

        :return: a bool value if there is a player_win otherwise return None
        """
        if self.player_remaining <= 0 or len(self.get_valid_counters(True)) <= 0:
            return False
        elif self.comp_remaining <= 0 or len(self.get_valid_counters(False)) <= 0:
            return True
        return None

    def get_row_mods(self, counter):
        """
        get_row_mods calculates which directions a counter can move
        :param counter: counter being checked
        :return: directions a counter may move
        """
        if counter.king:
            return [-1, 1]
        elif counter.player:
            return [-1]
        else:
            return [1]
