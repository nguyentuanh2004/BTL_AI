import pygame
import pygame_menu
from checkers.glob_misc import (
    WIDTH_HEIGHT,
    SQR_DIM,
    FRAMES,
    TIME_DELAY,
    LINE_WIDTH,
    BLUE,
    M_FONT,
)
from checkers.gui import GUI
from checkers.game import Game
from ai.minimax import Minimax


class Main:
    # SETTERS
    def set_difficulty(self, value, dif):
        """
        set_difficulty sets difficulty
        :param value: name on slider (ignored)
        :param dif: new difficulty
        """
        self.difficulty = dif

    def set_verbose(self, value, ver):
        """
        set_verbose sets verbose
        :param value: name on slider (ignored)
        :param ver: new verbose
        """
        self.verbose = ver

    def set_playerTurn(self, value, turn):
        """
        set_playerTurn sets the player playing first
        :param value: name on slider (ignored)
        :param turn: player plaing first
        """
        self.playerTurn = turn

    # GAME LOGIC
    def start_the_game(self):
        """
        start_the_game starts the game loop and handles inputs
        """
        self.game_over = False
        self.play = True
        self.menu.disable()
        clock = pygame.time.Clock()
        gui = GUI(self.window_surface)
        minimax = Minimax()
        game = Game(
            self.window_surface, gui, self.difficulty, self.verbose, self.playerTurn
        )
        while not self.game_over:
            clock.tick(FRAMES)
            if not game.playerTurn:
                if not self.verbose:
                    gui.output_message("THINKING...")
                value, new_board, multi_leg = minimax.maxAB(
                    game.get_board(),
                    self.difficulty,
                    float("-inf"),
                    float("inf"),
                    game,
                    False,
                    self.verbose,
                )
                game.ai_move(new_board, multi_leg)

            if game.player_win() is not None:
                if game.player_win():
                    gui.output_message("YOU HAVE WON!", font=M_FONT, alpha=255)
                else:
                    gui.output_message("You Have Lost!", font=M_FONT, alpha=255)
                pygame.time.delay(2 * TIME_DELAY)
                self.game_over = True

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.game_over = True

                if gui.play and event.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    row, col = gui.get_square_from_mouse(pos)
                    game.click_on_square(row, col)

                if event.type == pygame.locals.KEYDOWN:
                    if event.key == pygame.K_p:
                        gui.pause_menu()
                    if event.key == pygame.K_i:
                        gui.play = False
                        gui.output_help()
                        gui.play = True
                    if event.key == pygame.K_h:
                        gui.play = False
                        gui.output_message("Thinking...")
                        value, new_board, multi_leg = minimax.maxAB(
                            game.get_board(),
                            3,
                            float("-inf"),
                            float("inf"),
                            game,
                            True,
                            False,
                        )
                        proposed_counters = new_board.get_sides_counters(True)
                        current_counters = game.get_board().get_sides_counters(True)
                        proposed_counters_cords = []
                        current_counters_cords = []
                        for counter in proposed_counters:
                            proposed_counters_cords.append((counter.col, counter.row))
                        for counter in current_counters:
                            current_counters_cords.append((counter.col, counter.row))
                        current = list(
                            set(current_counters_cords) - set(proposed_counters_cords)
                        )
                        new = list(
                            set(proposed_counters_cords) - set(current_counters_cords)
                        )
                        game.update()

                        current_x = SQR_DIM * current[0][0] + SQR_DIM // 2
                        current_y = SQR_DIM * current[0][1] + SQR_DIM // 2
                        new_x = SQR_DIM * new[0][0] + SQR_DIM // 2
                        new_y = SQR_DIM * new[0][1] + SQR_DIM // 2

                        pygame.draw.circle(
                            self.window_surface,
                            BLUE,
                            (current_x, current_y),
                            LINE_WIDTH,
                        )
                        pygame.draw.circle(
                            self.window_surface, BLUE, (new_x, new_y), LINE_WIDTH
                        )
                        pygame.display.update()
                        pygame.time.delay(2 * TIME_DELAY)
                        gui.play = True

            game.update()
        self.menu.enable()

    def __init__(self):
        pygame.init()
        self.difficulty = 1
        self.verbose = False
        self.playerTurn = False
        self.window_surface = pygame.display.set_mode((WIDTH_HEIGHT, WIDTH_HEIGHT))
        pygame.display.set_caption("Checkers Game")
        self.menu = pygame_menu.Menu(
            "Checkers Game - Selection",
            WIDTH_HEIGHT,
            WIDTH_HEIGHT,
            theme=pygame_menu.themes.THEME_DARK,
        )
        self.menu.add.selector(
            "Difficulty :",
            [
                ("Easy", 1),
                ("Medium", 3),
                ("Hard", 5),
                ("Skynet", 7),
                ("HAL (Requires Fast Computer)", 9),
            ],
            onchange=self.set_difficulty,
        )
        self.menu.add.selector(
            "Verbose AI (Not Advised on Harder AIs) :",
            [("Off", False), ("On", True)],
            onchange=self.set_verbose,
        )
        self.menu.add.selector(
            "Who Starts? :",
            [("Computer", False), ("You", True)],
            onchange=self.set_playerTurn,
        )
        self.menu.add.button("Play", self.start_the_game)
        self.menu.add.button("Quit", pygame_menu.events.EXIT)

        while True:
            events = pygame.event.get()

            if self.menu.is_enabled():
                self.menu.update(events)
                self.menu.draw(self.window_surface)

            pygame.display.update()


main = Main()
