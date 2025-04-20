import pygame
import sys
from Board import Board
from Game import Game
import os

pygame.init()

WIDTH, HEIGHT = 700, 700
BOARD_SIZE = 8
SQUARE_SIZE = 63
BOARD_OFFSET_X = (WIDTH - BOARD_SIZE * SQUARE_SIZE) // 2
BOARD_OFFSET_Y = (HEIGHT - BOARD_SIZE * SQUARE_SIZE) // 2
FPS = 60

# Màu sắc
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
LIGHT_GRAY = (200, 200, 200)
DARK_GRAY = (50, 50, 50)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
LIGHT_BLUE = (173, 216, 230)
HIGHLIGHT = (255, 255, 0)

LIGHT_PINK = (255, 182, 193)  # LightPink
PINK = (255, 192, 203)  # Pink
HOT_PINK = (255, 105, 180)  # HotPink
DEEP_PINK = (255, 20, 147)  # DeepPink
PALE_VIOLET_RED = (219, 112, 147)  # PaleVioletRed
MEDIUM_VIOLET_RED = (199, 21, 133)  # MediumVioletRed
PASTEL_PINK = (255, 209, 220)  # Màu hồng pastel
COTTON_CANDY = (255, 188, 217)  # Màu hồng kẹo bông
BABY_PINK = (244, 194, 194)  # Màu hồng baby
BLUSH = (222, 93, 131)  # Màu hồng blush

screen = pygame.display.set_mode((WIDTH, HEIGHT))
icon = pygame.image.load('img/icon.png')
pygame.display.set_icon(icon)
pygame.display.set_caption("CHECKERS from AAP girls")
clock = pygame.time.Clock()

# Load fonts
title_font = pygame.font.SysFont("Cooper Black", 48, bold=True)
button_font = pygame.font.SysFont("Cooper Black", 24)
info_font = pygame.font.SysFont("Cooper Black", 20)
player_font = pygame.font.SysFont("Cooper Black", 28, bold=True)


class TextInputBox:
    def __init__(self, x, y, w, h, text='', color_active=(255, 255, 255), color_inactive=(180, 180, 180)):
        self.rect = pygame.Rect(x, y, w, h)
        self.color_active = color_active
        self.color_inactive = color_inactive
        self.color = self.color_inactive
        self.text = text
        self.font = pygame.font.SysFont("Cooper Black", 32)
        self.txt_surface = self.font.render(text, True, (0, 0, 0))
        self.active = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Click để chọn input
            if self.rect.collidepoint(event.pos):
                self.active = not self.active
            else:
                self.active = False
            self.color = self.color_active if self.active else self.color_inactive

        if event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_RETURN:
                    name = self.text
                    self.text = ''
                    return name  # Trả về khi nhấn Enter
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    if len(self.text) < 15:
                        self.text += event.unicode
                self.txt_surface = self.font.render(self.text, True, (0, 0, 0))
        return None

    def draw(self, screen):
        # Vẽ chữ
        screen.blit(self.txt_surface, (self.rect.x + 10, self.rect.y + 10))
        # Vẽ khung
        pygame.draw.rect(screen, self.color, self.rect, 3)


class Button:
    def __init__(self, x, y, width, height, text, color, hover_color, text_color=BLACK):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.hovered = False

    def draw(self, surface):
        color = self.hover_color if self.hovered else self.color
        pygame.draw.rect(surface, color, self.rect, border_radius=5)
        pygame.draw.rect(surface, WHITE, self.rect, 2, border_radius=5)

        text_surf = button_font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def check_hover(self, pos):
        self.hovered = self.rect.collidepoint(pos)

    def is_clicked(self, pos, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self.rect.collidepoint(pos)
        return False


class Checker:
    def __init__(self, row, col, color):
        self.row = row
        self.col = col
        self.color = color
        self.king = False
        self.x = 0
        self.y = 0
        self.calc_pos()

    def calc_pos(self):
        self.x = SQUARE_SIZE * self.col + SQUARE_SIZE // 2 + BOARD_OFFSET_X
        self.y = SQUARE_SIZE * self.row + SQUARE_SIZE // 2 + BOARD_OFFSET_Y

    def make_king(self):
        self.king = True

    def draw(self, win):
        radius = SQUARE_SIZE // 2 - 10
        pygame.draw.circle(win, self.color, (self.x, self.y), radius)
        if self.king:
            # Draw a crown for king
            crown_color = WHITE if self.color == BLUE or self.color == PINK else BLACK
            pygame.draw.circle(win, crown_color, (self.x, self.y), radius // 2)

    def move(self, row, col):
        self.row = row
        self.col = col
        self.calc_pos()


class Board:
    def __init__(self):
        self.board = []
        self.selected_piece = None
        self.blue_left = self.pink_left = 12
        self.blue_kings = self.pink_kings = 0
        self.create_board()

    def create_board(self):
        self.board = [[None for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        self.place_pieces()

    def place_pieces(self):
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                if col % 2 == ((row % 2) ^ 1):  # ^ is XOR
                    if row < 3:
                        self.board[row][col] = Checker(row, col, PINK)
                    elif row > 4:
                        self.board[row][col] = Checker(row, col, BLUE)

    def draw(self, win, valid_moves=None, hint=None):
        if valid_moves is None:
            valid_moves = {}

        self.draw_squares(win)

        # Draw hints if enabled
        if hint is not None:
            pygame.draw.rect(win, GREEN, (
                BOARD_OFFSET_X + hint[1] * SQUARE_SIZE,
                BOARD_OFFSET_Y + hint[0] * SQUARE_SIZE,
                SQUARE_SIZE, SQUARE_SIZE
            ), 4)

        # Draw pieces
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                piece = self.board[row][col]
                if piece:
                    piece.draw(win)

        # Draw valid moves
        for move in valid_moves.values():
            row, col = move
            pygame.draw.circle(win, GREEN, (
                BOARD_OFFSET_X + col * SQUARE_SIZE + SQUARE_SIZE // 2,
                BOARD_OFFSET_Y + row * SQUARE_SIZE + SQUARE_SIZE // 2
            ), 15)

    def draw_squares(self, win):
        win.fill(PASTEL_PINK)
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                if (row + col) % 2 == 0:
                    color = WHITE
                else:
                    color = BLACK
                pygame.draw.rect(win, color, (
                    BOARD_OFFSET_X + col * SQUARE_SIZE,
                    BOARD_OFFSET_Y + row * SQUARE_SIZE,
                    SQUARE_SIZE, SQUARE_SIZE
                ))

    def get_piece(self, row, col):
        if 0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE:
            return self.board[row][col]
        return None

    def move(self, piece, row, col):
        # Swap positions in board
        self.board[piece.row][piece.col], self.board[row][col] = None, piece

        # Check if piece becomes king
        if row == 0 and piece.color == BLUE:
            piece.make_king()
            self.blue_kings += 1
        elif row == BOARD_SIZE - 1 and piece.color == PINK:
            piece.make_king()
            self.pink_kings += 1

        # Move the piece
        piece.move(row, col)

    def get_valid_moves(self, piece):
        moves = {}
        left = piece.col - 1
        right = piece.col + 1
        row = piece.row

        if piece.color == BLUE or piece.king:
            # Moving up
            moves.update(self._traverse_left(row - 1, max(row - 3, -1), -1, piece.color, left))
            moves.update(self._traverse_right(row - 1, max(row - 3, -1), -1, piece.color, right))

        if piece.color == PINK or piece.king:
            # Moving down
            moves.update(self._traverse_left(row + 1, min(row + 3, BOARD_SIZE), 1, piece.color, left))
            moves.update(self._traverse_right(row + 1, min(row + 3, BOARD_SIZE), 1, piece.color, right))

        return moves

    def _traverse_left(self, start, stop, step, color, left, skipped=None):
        if skipped is None:
            skipped = []

        moves = {}
        last = []

        for r in range(start, stop, step):
            if left < 0:
                break

            current = self.board[r][left]

            # If square is empty
            if current is None:
                if skipped and not last:
                    break
                elif skipped:
                    moves[(r, left)] = last + skipped
                else:
                    moves[(r, left)] = last

                if last:
                    if step == -1:
                        row = max(r - 3, -1)
                    else:
                        row = min(r + 3, BOARD_SIZE)

                    moves.update(self._traverse_left(r + step, row, step, color, left - 1, skipped=last))
                    moves.update(self._traverse_right(r + step, row, step, color, left + 1, skipped=last))
                break
            # If piece is of same color
            elif current.color == color:
                break
            # If piece is of different color
            else:
                last = [current]

            left -= 1

        return moves

    def _traverse_right(self, start, stop, step, color, right, skipped=None):
        if skipped is None:
            skipped = []

        moves = {}
        last = []

        for r in range(start, stop, step):
            if right >= BOARD_SIZE:
                break

            current = self.board[r][right]

            # If square is empty
            if current is None:
                if skipped and not last:
                    break
                elif skipped:
                    moves[(r, right)] = last + skipped
                else:
                    moves[(r, right)] = last

                if last:
                    if step == -1:
                        row = max(r - 3, -1)
                    else:
                        row = min(r + 3, BOARD_SIZE)

                    moves.update(self._traverse_left(r + step, row, step, color, right - 1, skipped=last))
                    moves.update(self._traverse_right(r + step, row, step, color, right + 1, skipped=last))
                break
            # If piece is of same color
            elif current.color == color:
                break
            # If piece is of different color
            else:
                last = [current]

            right += 1

        return moves

    def remove(self, pieces):
        for piece in pieces:
            self.board[piece.row][piece.col] = None
            if piece.color == BLUE:
                self.blue_left -= 1
            else:
                self.pink_left -= 1


class Game:
    def __init__(self):
        self.init_game()

    def init_game(self):
        # Save current player names before reset
        current_blue_name = self.player_blue_name if hasattr(self, 'player_blue_name') else "Player 1"
        current_pink_name = self.player_pink_name if hasattr(self, 'player_pink_name') else "Player 2"
        current_turn = self.turn if hasattr(self, 'turn') else BLUE

        self.board = Board()
        self.turn = current_turn
        self.valid_moves = {}
        self.selected = None
        self.game_over = False
        self.winner = None
        self.moves_history = []
        self.show_hints = False
        self.sound_enabled = True
        self.playing_against_ai = False
        self.ai_difficulty = "Easy"

        # Restore player names
        self.player_blue_name = current_blue_name
        self.player_pink_name = current_pink_name

    def update(self):
        self.board.draw(screen, self.valid_moves, self.get_hint() if self.show_hints else None)
        self.draw_game_info()
        pygame.display.update()

    def select(self, row, col):
        if self.selected:
            result = self._move(row, col)
            if not result:
                self.selected = None
                self.select(row, col)

        piece = self.board.get_piece(row, col)
        if piece and piece.color == self.turn:
            self.selected = piece
            self.valid_moves = self.board.get_valid_moves(piece)
            return True

        return False

    def _move(self, row, col):
        piece = self.board.get_piece(row, col)

        if self.selected and not piece and (row, col) in self.valid_moves:
            self.board.move(self.selected, row, col)
            skipped = self.valid_moves[(row, col)]
            if skipped:
                self.board.remove(skipped)

            # Save move for undo function
            self.moves_history.append({
                'piece': self.selected,
                'from': (self.selected.row, self.selected.col),
                'to': (row, col),
                'skipped': skipped,
                'was_king': self.selected.king
            })

            self.change_turn()
            return True

        return False

    def change_turn(self):
        self.valid_moves = {}
        self.selected = None

        if self.turn == BLUE:
            self.turn = PINK
        else:
            self.turn = BLUE

        # Check for winner
        if self.board.blue_left == 0:
            self.winner = PINK
            self.game_over = True
        elif self.board.pink_left == 0:
            self.winner = BLUE
            self.game_over = True

    def draw_game_info(self):
        # Draw player info at bottom corners
        blue_text = player_font.render(f"{self.player_blue_name}", True, BLUE)
        pink_text = player_font.render(f"{self.player_pink_name}", True, PINK)

        # Position text at bottom corners with padding
        padding = 20
        blue_rect = blue_text.get_rect(bottomleft=(padding, HEIGHT - padding))
        pink_rect = pink_text.get_rect(bottomright=(WIDTH - padding, HEIGHT - padding))

        # Draw piece count circles
        circle_radius = 25
        circle_padding = 15

        # Blue player circle
        blue_circle_pos = (blue_rect.centerx, blue_rect.top - circle_radius - circle_padding)
        pygame.draw.circle(screen, BLUE, blue_circle_pos, circle_radius)
        pygame.draw.circle(screen, WHITE, blue_circle_pos, circle_radius, 2)

        # Blue player piece count
        blue_count = player_font.render(str(12 - self.board.pink_left), True, WHITE)
        blue_count_rect = blue_count.get_rect(center=blue_circle_pos)
        screen.blit(blue_count, blue_count_rect)

        # Pink player circle
        pink_circle_pos = (pink_rect.centerx, pink_rect.top - circle_radius - circle_padding)
        pygame.draw.circle(screen, PINK, pink_circle_pos, circle_radius)
        pygame.draw.circle(screen, WHITE, pink_circle_pos, circle_radius, 2)

        # Pink player piece count
        pink_count = player_font.render(str(12 - self.board.blue_left), True, WHITE)
        pink_count_rect = pink_count.get_rect(center=pink_circle_pos)
        screen.blit(pink_count, pink_count_rect)

        # Highlight active player
        if self.turn == BLUE:
            pygame.draw.rect(screen, LIGHT_BLUE,
                             (blue_rect.left - 10, blue_rect.top - 5, blue_rect.width + 20, blue_rect.height + 10),
                             border_radius=5)
        else:
            pygame.draw.rect(screen, LIGHT_BLUE,
                             (pink_rect.left - 10, pink_rect.top - 5, pink_rect.width + 20, pink_rect.height + 10),
                             border_radius=5)

        screen.blit(blue_text, blue_rect)
        screen.blit(pink_text, pink_rect)

        # Draw buttons
        undo_button = Button(WIDTH - 120, 20, 100, 30, "Undo", COTTON_CANDY, BLUSH)
        menu_button = Button(20, 20, 100, 30, "Menu", COTTON_CANDY, BLUSH)
        undo_button.draw(screen)
        menu_button.draw(screen)

        # Check for game over
        if self.game_over:
            winner_name = self.player_blue_name if self.winner == BLUE else self.player_pink_name
            game_over_text = title_font.render(f"{winner_name} Wins!", True, self.winner)
            screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, 20))

    def undo_move(self):
        if not self.moves_history:
            return

        last_move = self.moves_history.pop()
        piece = last_move['piece']
        from_pos = last_move['from']
        to_pos = last_move['to']
        skipped = last_move['skipped']
        was_king = last_move['was_king']

        # Move the piece back
        self.board.board[to_pos[0]][to_pos[1]] = None
        self.board.board[from_pos[0]][from_pos[1]] = piece
        piece.row, piece.col = from_pos
        piece.calc_pos()

        # Restore king status
        if piece.king and not was_king:
            piece.king = False
            if piece.color == BLUE:
                self.board.blue_kings -= 1
            else:
                self.board.pink_kings -= 1

        # Restore skipped pieces
        for skipped_piece in skipped:
            self.board.board[skipped_piece.row][skipped_piece.col] = skipped_piece
            if skipped_piece.color == BLUE:
                self.board.blue_left += 1
            else:
                self.board.pink_left += 1

        # Change turn back
        self.change_turn()

    def get_hint(self):
        # Simple hint: find a piece that can capture
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                piece = self.board.get_piece(row, col)
                if piece and piece.color == self.turn:
                    moves = self.board.get_valid_moves(piece)
                    for move, skipped in moves.items():
                        if skipped:  # If this move captures a piece
                            return (row, col)  # Return the position of the piece that can capture

        # If no capture available, just return the first piece with valid moves
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                piece = self.board.get_piece(row, col)
                if piece and piece.color == self.turn:
                    moves = self.board.get_valid_moves(piece)
                    if moves:
                        return (row, col)

        return None


class Menu:
    def __init__(self):
        self.state = "main"  # main, options, game, instructions, single_player, two_player
        self.buttons = {}
        self.name_input_boxes = {}
        self.init_main_menu()

    def init_main_menu(self):
        button_width = 200
        button_height = 50
        button_x = WIDTH // 2 - button_width // 2

        self.buttons["main"] = [
            Button(button_x, 340, button_width, button_height, "ONE PLAYER", COTTON_CANDY, BLUSH),
            Button(button_x, 410, button_width, button_height, "TWO PLAYER", COTTON_CANDY, BLUSH),
            Button(button_x, 480, button_width, button_height, "HOW TO PLAY", COTTON_CANDY, BLUSH),
            Button(button_x, 550, button_width, button_height, "OPTION", COTTON_CANDY, BLUSH),
            Button(button_x, 620, button_width, button_height, "EXIT", COTTON_CANDY, BLUSH)
        ]

        self.buttons["options"] = [
            Button(button_x, 340, button_width, button_height, "SOUND: ON", COTTON_CANDY, BLUSH),
            Button(button_x, 410, button_width, button_height, "PLAY TIPS: OFF", COTTON_CANDY, BLUSH),
            Button(button_x, 550, button_width, button_height, "BACK", COTTON_CANDY, BLUSH)
        ]

        self.buttons["instructions"] = [
            Button(button_x, 630, button_width, button_height, "BACK", COTTON_CANDY, BLUSH)
        ]

        self.buttons["single_player"] = [
            Button(button_x - 100, 270, button_width, button_height, "Difficulty: Easy", COTTON_CANDY, BLUSH),
            Button(button_x - 100, 340, button_width, button_height, "Color: Blue", COTTON_CANDY, BLUSH),
            Button(button_x - 100, 410, button_width, button_height, "BACK", COTTON_CANDY, BLUSH),
            Button(button_x + 120, 410, button_width, button_height, "START GAME", BABY_PINK, BLUSH)
        ]

        self.buttons["two_player"] = [
            Button(button_x - 100, 340, button_width, button_height, "BACK", COTTON_CANDY, BLUSH),
            Button(button_x + 120, 340, button_width, button_height, "START GAME", BABY_PINK, BLUSH)
        ]

        # Add text input boxes for player names - moved right to avoid overlap
        self.name_input_boxes["two_player"] = [
            TextInputBox(WIDTH // 2, 200, button_width + 100, 50, ""),
            TextInputBox(WIDTH // 2, 270, button_width + 100, 50, "")
        ]

        self.buttons["game_over"] = [
            Button(WIDTH // 2 - 100, HEIGHT // 2, 200, 50, "PLAY AGAIN", COTTON_CANDY, BLUSH),
            Button(WIDTH // 2 - 100, HEIGHT // 2 + 70, 200, 50, "MAIN MENU", COTTON_CANDY, BLUSH)
        ]

        # Add text input box for single player name
        self.name_input_boxes["single_player"] = [
            TextInputBox(WIDTH // 2, 200, button_width + 100, 50, "")
        ]

        self.buttons["game"] = [
            Button(WIDTH - 120, 20, 100, 30, "Undo", COTTON_CANDY, BLUSH),
            Button(20, 20, 100, 30, "Menu", COTTON_CANDY, BLUSH)
        ]

    def draw(self, game):
        screen.fill(PASTEL_PINK)

        if self.state == "main":
            self.draw_main_menu()
        elif self.state == "options":
            self.draw_options_menu(game)
        elif self.state == "instructions":
            self.draw_instructions()
        elif self.state == "single_player":
            self.draw_single_player_menu(game)
        elif self.state == "two_player":
            self.draw_two_player_menu(game)
        elif self.state == "game":
            game.update()
        elif self.state == "game_over":
            self.draw_game_over(game)

    def draw_main_menu(self):
        title_image = pygame.image.load("img/title_image.png")

        title_rect = title_image.get_rect(center=(WIDTH // 2, HEIGHT // 4))
        screen.blit(title_image, title_rect)

        for button in self.buttons["main"]:
            button.draw(screen)

    def draw_options_menu(self, game):
        title_image = pygame.image.load("img/title_image.png")

        title_rect = title_image.get_rect(center=(WIDTH // 2, HEIGHT // 4))
        screen.blit(title_image, title_rect)

        title = title_font.render("OPTIONS", True, WHITE)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 280))

        # Update button texts based on settings
        self.buttons["options"][0].text = f"SOUND: {'ON' if game.sound_enabled else 'OFF'}"
        self.buttons["options"][1].text = f"PLAY TIPS: {'ON' if game.show_hints else 'OFF'}"

        for button in self.buttons["options"]:
            button.draw(screen)

    def draw_instructions(self):
        title = title_font.render("HOW TO PLAY", True, WHITE)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 20))

        title_image = pygame.image.load("img/howtoplay.png")
        title_image = pygame.transform.scale(title_image, (600, 600))
        title_rect = title_image.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        screen.blit(title_image, title_rect)

        for button in self.buttons["instructions"]:
            button.draw(screen)

    def draw_single_player_menu(self, game):
        title = title_font.render("PLAY WITH AI", True, WHITE)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 100))

        # Draw player label
        player_label = player_font.render("Player name:", True, WHITE)
        screen.blit(player_label, (WIDTH // 2 - 300, 210))

        # Draw text input box
        for input_box in self.name_input_boxes["single_player"]:
            input_box.draw(screen)

        # Update button texts based on settings
        self.buttons["single_player"][0].text = f"Difficulty: {game.ai_difficulty}"
        self.buttons["single_player"][1].text = f"Color: {'Blue' if game.turn == BLUE else 'Pink'}"

        # Draw buttons
        for button in self.buttons["single_player"]:
            button.draw(screen)

    def draw_two_player_menu(self, game):
        title = title_font.render("TWO PLAYERS", True, WHITE)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 100))

        # Draw player labels - moved left
        player1_label = player_font.render("Player 1:", True, WHITE)
        player2_label = player_font.render("Player 2:", True, WHITE)
        screen.blit(player1_label, (WIDTH // 2 - 300, 210))
        screen.blit(player2_label, (WIDTH // 2 - 300, 280))

        # Draw text input boxes
        for input_box in self.name_input_boxes["two_player"]:
            input_box.draw(screen)

        # Draw buttons
        for button in self.buttons["two_player"]:
            button.draw(screen)

    def draw_game_over(self, game):
        # Draw the board in the background
        game.board.draw(screen)

        # Semi-transparent overlay
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))  # Black with alpha
        screen.blit(overlay, (0, 0))

        # Game over message
        winner_name = game.player_blue_name if game.winner == BLUE else game.player_pink_name
        game_over_text = title_font.render(f"{winner_name} Win!", True, game.winner)
        screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2 - 100))

        # Draw buttons
        for button in self.buttons["game_over"]:
            button.draw(screen)

    def handle_event(self, event, game, pos):
        if self.state == "main":
            self.handle_main_menu(event, game, pos)
        elif self.state == "options":
            self.handle_options_menu(event, game, pos)
        elif self.state == "instructions":
            self.handle_instructions(event, pos)
        elif self.state == "single_player":
            self.handle_single_player_menu(event, game, pos)
        elif self.state == "two_player":
            self.handle_two_player_menu(event, game, pos)
        elif self.state == "game":
            self.handle_game(event, game, pos)
        elif self.state == "game_over":
            self.handle_game_over(event, game, pos)

    def handle_main_menu(self, event, game, pos):
        for i, button in enumerate(self.buttons["main"]):
            button.check_hover(pos)
            if button.is_clicked(pos, event):
                if i == 0:  # 1 Player
                    self.state = "single_player"
                    game.playing_against_ai = True
                elif i == 1:  # 2 Players
                    self.state = "two_player"
                    game.playing_against_ai = False
                elif i == 2:  # Instructions
                    self.state = "instructions"
                elif i == 3:  # Options
                    self.state = "options"
                elif i == 4:  # Exit
                    pygame.quit()
                    sys.exit()

    def handle_options_menu(self, event, game, pos):
        for i, button in enumerate(self.buttons["options"]):
            button.check_hover(pos)
            if button.is_clicked(pos, event):
                if i == 0:  # Sound toggle
                    game.sound_enabled = not game.sound_enabled
                elif i == 1:  # Hints toggle
                    game.show_hints = not game.show_hints
                elif i == 2:  # Back
                    self.state = "main"

    def handle_instructions(self, event, pos):
        for button in self.buttons["instructions"]:
            button.check_hover(pos)
            if button.is_clicked(pos, event):
                self.state = "main"

    def handle_single_player_menu(self, event, game, pos):
        # Handle text input box
        for input_box in self.name_input_boxes["single_player"]:
            name = input_box.handle_event(event)
            if name:  # If Enter was pressed and name was submitted
                game.player_blue_name = name

        # Handle buttons
        for i, button in enumerate(self.buttons["single_player"]):
            button.check_hover(pos)
            if button.is_clicked(pos, event):
                if i == 0:  # Change difficulty
                    difficulties = ["Easy", "Normal", "Hard"]
                    current_index = difficulties.index(game.ai_difficulty)
                    game.ai_difficulty = difficulties[(current_index + 1) % len(difficulties)]
                elif i == 1:  # Change color
                    if game.turn == BLUE:
                        game.turn = PINK
                        game.player_blue_name, game.player_pink_name = game.player_pink_name, game.player_blue_name
                    else:
                        game.turn = BLUE
                        game.player_blue_name, game.player_pink_name = game.player_pink_name, game.player_blue_name
                elif i == 2:  # Back
                    self.state = "main"
                elif i == 3:  # Start
                    # Get final name from input box
                    game.player_blue_name = self.name_input_boxes["single_player"][0].text or "Player 1"
                    self.state = "game"
                    game.init_game()

    def handle_two_player_menu(self, event, game, pos):
        # Handle text input boxes
        for i, input_box in enumerate(self.name_input_boxes["two_player"]):
            name = input_box.handle_event(event)
            if name:  # If Enter was pressed and name was submitted
                if i == 0:
                    game.player_blue_name = name
                else:
                    game.player_pink_name = name

        # Handle buttons
        for i, button in enumerate(self.buttons["two_player"]):
            button.check_hover(pos)
            if button.is_clicked(pos, event):
                if i == 0:  # Back
                    self.state = "main"
                elif i == 1:  # Start
                    # Get final names from input boxes
                    game.player_blue_name = self.name_input_boxes["two_player"][0].text or "Player 1"
                    game.player_pink_name = self.name_input_boxes["two_player"][1].text or "Player 2"
                    self.state = "game"
                    game.init_game()

    def handle_game(self, event, game, pos):
        # Handle game events
        # Create buttons
        menu_button = Button(20, 20, 100, 30, "Menu", COTTON_CANDY, BLUSH)
        undo_button = Button(WIDTH - 120, 20, 100, 30, "Undo", COTTON_CANDY, BLUSH)

        # Check hover effects
        menu_button.check_hover(pos)
        undo_button.check_hover(pos)

        if event.type == pygame.MOUSEBUTTONDOWN:
            # Check if menu button was clicked
            if menu_button.rect.collidepoint(pos):
                game.init_game()
                self.state = "main"
                return

            # Check if undo button was clicked
            if undo_button.rect.collidepoint(pos):
                game.undo_move()
                return

            # Check board click
            if (BOARD_OFFSET_X <= pos[0] <= BOARD_OFFSET_X + BOARD_SIZE * SQUARE_SIZE and
                    BOARD_OFFSET_Y <= pos[1] <= BOARD_OFFSET_Y + BOARD_SIZE * SQUARE_SIZE):
                col = (pos[0] - BOARD_OFFSET_X) // SQUARE_SIZE
                row = (pos[1] - BOARD_OFFSET_Y) // SQUARE_SIZE

                if game.select(row, col):
                    # If selected valid piece
                    pass

        # Check for game over
        if game.game_over:
            self.state = "game_over"

    def handle_game_over(self, event, game, pos):
        for i, button in enumerate(self.buttons["game_over"]):
            button.check_hover(pos)
            if button.is_clicked(pos, event):
                if i == 0:  # Play again
                    game.init_game()
                    self.state = "game"
                elif i == 1:  # Main menu
                    game.init_game()
                    self.state = "main"


# AI Bot for single player mode
class AI:
    def __init__(self, difficulty="Easy"):
        self.difficulty = difficulty

    def make_move(self, game):
        if game.turn != PINK:  # Assume AI is always PINK
            return

        # Find all pieces that can move
        all_pieces = []
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                piece = game.board.get_piece(row, col)
                if piece and piece.color == PINK:
                    valid_moves = game.board.get_valid_moves(piece)
                    if valid_moves:
                        all_pieces.append((piece, valid_moves))

        if not all_pieces:
            return  # No valid moves

        # Strategy based on difficulty
        if self.difficulty == "Easy":
            # Pick a random piece and a random move
            import random
            piece, moves = random.choice(all_pieces)
            move = random.choice(list(moves.keys()))
            pygame.time.delay(500)  # Add a delay for AI thinking

        elif self.difficulty == "Normal":
            # Prioritize captures
            captures = []
            for piece, moves in all_pieces:
                for move, skipped in moves.items():
                    if skipped:  # If this move captures something
                        captures.append((piece, move))

            import random
            if captures:
                # Choose a random capture
                piece, move = random.choice(captures)
            else:
                # No captures available, choose a random move
                piece, moves = random.choice(all_pieces)
                move = random.choice(list(moves.keys()))

            pygame.time.delay(800)  # Slightly longer delay

        else:  # Difficult
            # Prioritize multiple captures, then single captures, then safe moves
            best_move = None
            best_score = -float('inf')

            for piece, moves in all_pieces:
                for move, skipped in moves.items():
                    score = len(skipped) * 10  # Heavily weight captures

                    # King pieces are more valuable
                    if piece.king:
                        score += 5

                    # Promote to king if possible
                    if move[0] == 0 and not piece.king:  # If moving to last row and not already a king
                        score += 8

                    # Avoid moving into a position where we can be captured
                    temp_game = self.simulate_move(game, piece, move)
                    if self.is_vulnerable(temp_game, move[0], move[1]):
                        score -= 15

                    if score > best_score:
                        best_score = score
                        best_move = (piece, move)

            if best_move:
                piece, move = best_move
            else:
                # Fallback to random if no good move found
                import random
                piece, moves = random.choice(all_pieces)
                move = random.choice(list(moves.keys()))

            pygame.time.delay(1000)  # Longest delay for difficult

        # Make the selected move
        game.select(piece.row, piece.col)  # Select the piece
        game.select(move[0], move[1])  # Select the destination

    def simulate_move(self, game, piece, move):
        # Create a deep copy of the game state to simulate a move
        import copy
        temp_game = copy.deepcopy(game)
        temp_piece = temp_game.board.get_piece(piece.row, piece.col)
        temp_game.select(piece.row, piece.col)
        temp_game.select(move[0], move[1])
        return temp_game

    def is_vulnerable(self, game, row, col):
        # Check if a piece at (row, col) can be captured in the next move
        piece = game.board.get_piece(row, col)
        if not piece:
            return False

        # Check if any opponent piece can capture this piece
        opponent_color = BLUE if piece.color == PINK else PINK

        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                opp_piece = game.board.get_piece(r, c)
                if opp_piece and opp_piece.color == opponent_color:
                    moves = game.board.get_valid_moves(opp_piece)
                    for move, skipped in moves.items():
                        if any(p.row == row and p.col == col for p in skipped):
                            return True

        return False


# Main loop
def main():
    game = Game()
    menu = Menu()
    ai = AI()
    running = True





    while running:
        clock.tick(FPS)
        pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            menu.handle_event(event, game, pos)

        menu.draw(game)

        # AI move if in single player mode
        if menu.state == "game" and game.playing_against_ai and game.turn == PINK and not game.game_over:
            ai.difficulty = game.ai_difficulty
            ai.make_move(game)

        pygame.display.update()

    pygame.quit()


if __name__ == "__main__":
    main()