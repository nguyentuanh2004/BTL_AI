from .glob_misc import SQR_DIM, GOLD, GREY, WHITE, BLACK, LINE_WIDTH
import pygame


class Counter:
    def __init__(self, row, col, player, firstPlayerTurn):
        self.row = row
        self.col = col
        self.player = player
        self.king = False
        self.x = 0
        self.y = 0
        self.set_coords()
        self.firstPlayerTurn = firstPlayerTurn

    def __repr__(self):
        if self.player:
            return "player"
        return "comp"

    def set_coords(self):
        """
        set_coords calculates the coordinates of the center of a square and sets the x, y values to this
        :param self:
        """
        self.x = (SQR_DIM * self.col) + (SQR_DIM // 2)
        self.y = (SQR_DIM * self.row) + (SQR_DIM // 2)

    def make_king(self):
        """
        make_king sets a counters to be king
        :param self:
        """
        self.king = True

    def draw(self, surface):
        """
        draw draws the counters on the game game_board
        :param surface: the surface to draw the counters on
        :return:
        """
        radius = (SQR_DIM // 2) - (LINE_WIDTH + 5)
        if self.king:
            pygame.draw.circle(surface, GOLD, (self.x, self.y), radius + LINE_WIDTH)
        else:
            pygame.draw.circle(surface, GREY, (self.x, self.y), radius + LINE_WIDTH)
        pygame.draw.circle(surface, self.get_colour(), (self.x, self.y), radius)

    def move(self, row, col):
        """
        move takes a row and col and updates counter's values for these.
        :param row: row location
        :param col: col location
        """
        self.row = row
        self.col = col
        self.set_coords()

    # GETTERS
    def get_colour(self):
        """
        get_colour sets the colour of the tile to the correct colour so the first to play is always playing the darker
        colour.
        :return: Counter Colour (as an (R,G,B) value)
        """
        if self.player == self.firstPlayerTurn:
            return BLACK
        else:
            return WHITE
