import pygame
from checkers.glob_misc import (
    SQR_DIM,
    WIDTH_HEIGHT,
    XL_FONT,
    S_FONT,
    XS_FONT,
    WHITE,
    BLACK,
    GREEN,
    RED,
)


class GUI:
    def __init__(self, surface):
        self.surface = surface
        self.play = True
        self.help = False
        self.difficulty = 1
        self.verbose = False

    def get_square_from_mouse(self, pos):
        """
        get_square_from_mouse takes the pos of the mouse and calculates the
        loction of the square in the grid.

        :param pos: tuple of the x and y coordinates of the square
        :return: a tuple with the location of the square as rol and col
        """

        x, y = pos
        row = y // SQR_DIM
        col = x // SQR_DIM

        return row, col

    def output_message(self, output_str, font=XL_FONT, alpha=128):
        """
        output_message creates a transparent surface to be output contianing a message

        :param output_str: a string containing the output message
        :param font: the font for the output to use
        """

        output_surface = pygame.Surface((WIDTH_HEIGHT, WIDTH_HEIGHT))
        output_surface.set_alpha(alpha)
        output_surface.fill(WHITE)
        self.render_text(
            output_str,
            font,
            (WIDTH_HEIGHT // 2),
            (WIDTH_HEIGHT // 2),
            output_surface,
            BLACK,
        )
        self.surface.blit(output_surface, (0, 0))
        pygame.display.update()

    def output_help(self):
        """
        output_help creates a transparent surface to be output with the help text
        """
        self.help = True
        output_surface = pygame.Surface((WIDTH_HEIGHT, WIDTH_HEIGHT))
        output_surface.set_alpha(255)
        output_surface.fill(WHITE)
        self.render_text(
            "In checkers, regular counters can only move forwards, while",
            S_FONT,
            (WIDTH_HEIGHT // 2),
            100,
            output_surface,
            BLACK,
        )
        self.render_text(
            "kings can move in any direction. When clicking on a counter,",
            S_FONT,
            (WIDTH_HEIGHT // 2),
            200,
            output_surface,
            BLACK,
        )
        self.render_text(
            "the legal moves will be shown highlighted in green. To",
            S_FONT,
            (WIDTH_HEIGHT // 2),
            300,
            output_surface,
            BLACK,
        )
        self.render_text(
            "proceed to this position, the player must click on this green",
            S_FONT,
            (WIDTH_HEIGHT // 2),
            400,
            output_surface,
            BLACK,
        )
        self.render_text(
            "square. To become a king, the player must get to the other ",
            S_FONT,
            (WIDTH_HEIGHT // 2),
            500,
            output_surface,
            BLACK,
        )
        self.render_text(
            "side of the board to take an opponents king. To pause the",
            S_FONT,
            (WIDTH_HEIGHT // 2),
            600,
            output_surface,
            BLACK,
        )
        self.render_text(
            "the game during gameplay press (p), to get a hint press (h).",
            S_FONT,
            (WIDTH_HEIGHT // 2),
            700,
            output_surface,
            BLACK,
        )
        while self.help:
            for event in pygame.event.get():

                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
            button_width = 100
            button_height = 50
            self.render_button(
                "Go Back",
                (WIDTH_HEIGHT) - (button_width),
                (WIDTH_HEIGHT) - (button_height),
                button_width,
                button_height,
                GREEN,
                WHITE,
                output_surface,
                self.stop_help,
            )
            self.surface.blit(output_surface, (0, 0))
            pygame.display.update()

    def pause_menu(self):
        """
        pause_menu pauses the game and renders he pause menu
        """
        self.play = False

        output_surface = pygame.Surface(
            (WIDTH_HEIGHT, WIDTH_HEIGHT)
        )
        output_surface.set_alpha(128)
        output_surface.fill(WHITE)
        self.render_text(
            "Paused", XL_FONT, (WIDTH_HEIGHT // 2), (WIDTH_HEIGHT // 2), output_surface
        )

        while not self.play:
            for event in pygame.event.get():

                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
            button_width = 100
            button_height = 50
            self.render_button(
                "Continue",
                (WIDTH_HEIGHT // 3) - (button_width // 2),
                ((WIDTH_HEIGHT // 3) * 2) - (button_height // 2),
                button_width,
                button_height,
                GREEN,
                WHITE,
                output_surface,
                self.resume,
            )
            self.render_button(
                "Help",
                ((WIDTH_HEIGHT // 3) * 2) - (button_width // 2),
                ((WIDTH_HEIGHT // 3) * 2) - (button_height // 2),
                button_width,
                button_height,
                RED,
                WHITE,
                output_surface,
                self.output_help,
            )

            self.surface.blit(output_surface, (0, 0))
            pygame.display.update()

    def render_text(self, text, font, x, y, surface, COLOUR=BLACK):
        """
        render_text renders the text onto the given surface
        :param text: text string to be rendered
        :param font: font to render text with
        :param x: location of the center in the x axis
        :param y: location of the center in the y axis
        :param surface: surface to render output on
        :param COLOUR: colour of the text
        """
        text = font.render(text, True, COLOUR)
        textRect = text.get_rect()
        textRect.center = (x, y)
        surface.blit(text, textRect)

    def render_button(
        self, text, x, y, width, height, colour, alt_colour, surface, action=None
    ):
        """
        render_text renders a button onto the given surface
        :param text: text to render on button
        :param x: location of the center in the x axis
        :param y: location of the center in the y axis
        :param width: width of the button
        :param height: height of the button
        :param colour: colour of the button before highlighitng
        :param alt_colour: colour of the button during highlighting
        :param surface: surface to render output on
        :param action: buttons behaviour when clicked
        :return:
        """
        pressed = pygame.mouse.get_pressed()
        mouse_x, mouse_y = pygame.mouse.get_pos()
        if x + width > mouse_x > x and y + height > mouse_y > y:
            pygame.draw.rect(surface, alt_colour, (x, y, width, height))

            if pressed[0] == 1 and action is not None:
                action()
        else:
            pygame.draw.rect(surface, colour, (x, y, width, height))

        self.render_text(text, XS_FONT, (x + (width / 2)), (y + (height / 2)), surface)

    def resume(self):
        """
        resume resumes game play
        """
        self.play = True

    def stop_help(self):
        """
        sets the value of self.help to False informing the game loop to return to the previous menu / screen
        """
        self.help = False
