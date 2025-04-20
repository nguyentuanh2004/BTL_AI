import pygame
import os
from Board import Board
from Game import Game
from AI import Minimax
from checkers.glob_misc import WIDTH_HEIGHT, SQR_DIM, FRAMES, TIME_DELAY, LINE_WIDTH
from checkers.gui import GUI
from checkers.game import Game as CheckersGame
from ai.minimax import Minimax as CheckersMinimax

pygame.init()
pygame.mixer.init()  # Khởi tạo mixer để phát âm thanh

# Define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
LIGHT_GRAY = (200, 200, 200)
DARK_GRAY = (50, 50, 50)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
LIGHT_BLUE = (173, 216, 230)
PINK = (255, 192, 203)
DARK_RED = (180, 0, 0)
DARK_BLACK = (20, 20, 20)
YELLOW = (255, 255, 0)  # Color for highlighting the active player

# Define button colors
BUTTON_COLOR = (255, 188, 217)
BUTTON_HOVER_COLOR = (222, 93, 131)
TEXT_COLOR = WHITE

LIGHT_PINK = (255, 182, 193)  # LightPink
HOT_PINK = (255, 105, 180)  # HotPink
DEEP_PINK = (255, 20, 147)  # DeepPink
PALE_VIOLET_RED = (219, 112, 147)  # PaleVioletRed
MEDIUM_VIOLET_RED = (199, 21, 133)  # MediumVioletRed
PASTEL_PINK = (255, 209, 220)  # Màu hồng pastel
COTTON_CANDY = (255, 188, 217)  # Màu hồng kẹo bông
BABY_PINK = (244, 194, 194)  # Màu hồng baby
BLUSH = (222, 93, 131)  # Màu hồng blush

# Board configuration
BOARD_SIZE = 8
ORIGINAL_BOARD_WIDTH = 640  # The original board width
TOTAL_PIECES = 12  # Each player starts with 12 pieces


icon = pygame.image.load('img/icon.png')
pygame.display.set_icon(icon)
pygame.display.set_caption("CHECKERS from AAP girls")


class TextInputBox:
    def __init__(self, x, y, w, h, text='', color_active=(255, 255, 255), color_inactive=(180, 180, 180)):
        self.rect = pygame.Rect(x, y, w, h)
        self.color_active = color_active
        self.color_inactive = color_inactive
        self.color = self.color_inactive
        self.text = text
        self.font = pygame.font.SysFont("Arial", 24)
        self.txt_surface = self.font.render(text, True, BLACK)
        self.active = False
        self.max_length = 15

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Click to select input
            if self.rect.collidepoint(event.pos):
                self.active = not self.active
            else:
                self.active = False
            self.color = self.color_active if self.active else self.color_inactive

        if event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_RETURN:
                    return self.text
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    if len(self.text) < self.max_length:
                        self.text += event.unicode
                # Re-render the text
                self.txt_surface = self.font.render(self.text, True, BLACK)
        return None

    def draw(self, screen):
        # Draw the text
        screen.blit(self.txt_surface,
                    (self.rect.x + 10, self.rect.y + (self.rect.height - self.txt_surface.get_height()) // 2))
        # Draw the rect
        pygame.draw.rect(screen, self.color, self.rect, 2)


class Button:
    def __init__(self, x, y, width, height, text, color, hover_color, text_color=WHITE):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.hovered = False

    def draw(self, surface, font):
        color = self.hover_color if self.hovered else self.color
        pygame.draw.rect(surface, color, self.rect, border_radius=5)
        pygame.draw.rect(surface, WHITE, self.rect, 2, border_radius=5)

        text_surf = font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def check_hover(self, pos):
        self.hovered = self.rect.collidepoint(pos)

    def is_clicked(self, pos, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self.rect.collidepoint(pos)
        return False


class Menu:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.state = "menu"  # Can be "menu", "game", "game_over", "options", "one_player", "two_player"
        self.buttons = {}
        self.input_boxes = {}
        self.sound_enabled = True
        self.show_hints = False
        self.ai_difficulty = "Easy"  # Easy, Medium, Hard
        self.depth = 1  # Default depth for Easy difficulty
        self.player_names = {"player1": "Player 1", "player2": "Player 2", "ai": "AI"}
        self.first_color = "pink"  # Default first color is pink
        
        # Tải âm thanh nền
        self.background_music = pygame.mixer.Sound('gamesound.wav')
        self.background_music.set_volume(0.5)  # Đặt âm lượng ở mức 50%
        
        # Bắt đầu phát nhạc nếu âm thanh được bật
        if self.sound_enabled:
            self.background_music.play(-1)  # -1 nghĩa là lặp vô hạn
        
        # Load title image
        original_title_image = pygame.image.load("img/title_image.png")
        # Nhân đôi kích thước ảnh
        original_width = original_title_image.get_width()
        original_height = original_title_image.get_height()
        self.title_image = pygame.transform.scale(original_title_image, (original_width * 2, original_height * 2))
        
        # Load how to play image
        original_howtoplay_image = pygame.image.load("img/howtoplay.png")
        # Thu nhỏ hình ảnh (làm cho kích thước bằng 60% so với ban đầu)
        original_width = original_howtoplay_image.get_width()
        original_height = original_howtoplay_image.get_height()
        self.howtoplay_image = pygame.transform.scale(original_howtoplay_image, 
                                                       (int(original_width * 0.6), 
                                                        int(original_height * 0.6)))
        
        self.init_menu()

        # Fonts
        self.title_font = pygame.font.SysFont("Arial", 48, bold=True)
        self.button_font = pygame.font.SysFont("Arial", 24)
        self.label_font = pygame.font.SysFont("Arial", 20)

    def init_menu(self):
        button_width = 200
        button_height = 50
        center_x = self.screen_width // 2 - button_width // 2

        # Main menu buttons
        self.buttons["menu"] = [
            Button(center_x, 390, button_width, button_height, "ONE PLAYER", BUTTON_COLOR, BUTTON_HOVER_COLOR),
            Button(center_x, 460, button_width, button_height, "TWO PLAYER", BUTTON_COLOR, BUTTON_HOVER_COLOR),
            Button(center_x, 530, button_width, button_height, "HOW TO PLAY", BUTTON_COLOR, BUTTON_HOVER_COLOR),
            Button(center_x, 600, button_width, button_height, "OPTIONS", BUTTON_COLOR, BUTTON_HOVER_COLOR),
            Button(center_x, 670, button_width, button_height, "EXIT", BUTTON_COLOR, BUTTON_HOVER_COLOR)
        ]

        # Options menu buttons
        self.buttons["options"] = [
            Button(center_x, 530, button_width, button_height, "SOUND: ON", BUTTON_COLOR, BUTTON_HOVER_COLOR),
            Button(center_x, 600, button_width, button_height, "HINTS: OFF", BUTTON_COLOR, BUTTON_HOVER_COLOR),
            Button(center_x, 670, button_width, button_height, "BACK", BUTTON_COLOR, BUTTON_HOVER_COLOR)
        ]

        # One player menu buttons
        self.buttons["one_player"] = [
            Button(center_x, 460, button_width, button_height, "FIRST MOVE: YOU", BUTTON_COLOR, BUTTON_HOVER_COLOR),
            Button(center_x, 530, button_width, button_height, "DIFFICULTY: EASY", BUTTON_COLOR, BUTTON_HOVER_COLOR),
            Button(center_x, 600, button_width, button_height, "START GAME", BUTTON_COLOR, BUTTON_HOVER_COLOR),
            Button(center_x, 670, button_width, button_height, "BACK", BUTTON_COLOR, BUTTON_HOVER_COLOR)
        ]

        # Two player menu buttons
        self.buttons["two_player"] = [
            Button(center_x, 530, button_width, button_height, "STARTS: PINK", BUTTON_COLOR, BUTTON_HOVER_COLOR),
            Button(center_x, 600, button_width, button_height, "START GAME", BUTTON_COLOR, BUTTON_HOVER_COLOR),
            Button(center_x, 670, button_width, button_height, "BACK", BUTTON_COLOR, BUTTON_HOVER_COLOR)
        ]

        # Game-over menu buttons
        self.buttons["game_over"] = [
            Button(center_x, 300, button_width, button_height, "PLAY AGAIN", BUTTON_COLOR, BUTTON_HOVER_COLOR),
            Button(center_x, 400, button_width, button_height, "MAIN MENU", BUTTON_COLOR, BUTTON_HOVER_COLOR)
        ]

        # In-game menu buttons
        self.buttons["game"] = [
            Button(10, 10, 100, 30, "Menu", BUTTON_COLOR, BUTTON_HOVER_COLOR),
            Button(self.screen_width - 110, 10, 100, 30, "Hint", BUTTON_COLOR, BUTTON_HOVER_COLOR)
        ]

        # How to play menu buttons
        self.buttons["how_to_play"] = [
            Button(center_x, 670, button_width, button_height, "BACK", BUTTON_COLOR, BUTTON_HOVER_COLOR)
        ]

        # Text input boxes for player names
        input_width = 250
        input_height = 40
        input_x = self.screen_width // 2 - input_width // 2

        # One player input boxes
        self.input_boxes["one_player"] = [
            TextInputBox(input_x, 390, input_width, input_height, self.player_names["player1"])
        ]

        # Two player input boxes
        self.input_boxes["two_player"] = [
            TextInputBox(input_x, 390, input_width, input_height, self.player_names["player1"]),
            TextInputBox(input_x, 460, input_width, input_height, self.player_names["player2"])
        ]

    def draw_menu(self, screen):
        screen.fill(PASTEL_PINK)

        # Draw title image - dịch xuống thấp hơn
        title_rect = self.title_image.get_rect(center=(self.screen_width // 2, 180))
        screen.blit(self.title_image, title_rect)

        # Draw buttons
        for button in self.buttons["menu"]:
            button.draw(screen, self.button_font)

    def draw_options(self, screen):
        screen.fill(PASTEL_PINK)

        # Draw title image - dịch xuống thấp hơn
        title_rect = self.title_image.get_rect(center=(self.screen_width // 2, 180))
        screen.blit(self.title_image, title_rect)

        # Update button texts based on settings
        self.buttons["options"][0].text = f"SOUND: {'ON' if self.sound_enabled else 'OFF'}"
        self.buttons["options"][1].text = f"HINTS: {'ON' if self.show_hints else 'OFF'}"

        # Draw buttons
        for button in self.buttons["options"]:
            button.draw(screen, self.button_font)

    def draw_one_player(self, screen):
        screen.fill(PASTEL_PINK)

        # Draw title image - dịch xuống thấp hơn
        title_rect = self.title_image.get_rect(center=(self.screen_width // 2, 180))
        screen.blit(self.title_image, title_rect)

        # Draw player name label bên trái input box thay vì phía trên
        input_box = self.input_boxes["one_player"][0]
        name_label = self.label_font.render("Your Name:", True, WHITE)
        label_width = name_label.get_width()
        # Hiển thị nhãn bên trái, căn giữa theo chiều cao của input box
        screen.blit(name_label, 
                   (input_box.rect.x - label_width - 10, 
                    input_box.rect.y + (input_box.rect.height - name_label.get_height()) // 2))

        # Draw input box
        for input_box in self.input_boxes["one_player"]:
            input_box.draw(screen)

        # Update starting player and difficulty button text
        self.buttons["one_player"][0].text = f"FIRST MOVE: {'YOU' if self.first_color == 'pink' else 'AI'}"
        self.buttons["one_player"][1].text = f"DIFFICULTY: {self.ai_difficulty.upper()}"

        # Draw buttons
        for button in self.buttons["one_player"]:
            button.draw(screen, self.button_font)

    def draw_two_player(self, screen):
        screen.fill(PASTEL_PINK)

        # Draw title image - dịch xuống thấp hơn
        title_rect = self.title_image.get_rect(center=(self.screen_width // 2, 180))
        screen.blit(self.title_image, title_rect)

        # Draw player name labels bên trái input box thay vì phía trên
        input_box1 = self.input_boxes["two_player"][0]
        input_box2 = self.input_boxes["two_player"][1]
        
        label1 = self.label_font.render("Player 1 Name:", True, WHITE)
        label2 = self.label_font.render("Player 2 Name:", True, WHITE)
        
        label_width1 = label1.get_width()
        label_width2 = label2.get_width()
        
        # Hiển thị nhãn bên trái, căn giữa theo chiều cao của input box
        screen.blit(label1, 
                   (input_box1.rect.x - label_width1 - 10, 
                    input_box1.rect.y + (input_box1.rect.height - label1.get_height()) // 2))
        screen.blit(label2, 
                   (input_box2.rect.x - label_width2 - 10, 
                    input_box2.rect.y + (input_box2.rect.height - label2.get_height()) // 2))

        # Draw input boxes
        for input_box in self.input_boxes["two_player"]:
            input_box.draw(screen)

        # Update starting color button text
        self.buttons["two_player"][0].text = f"STARTS: {self.first_color.upper()}"

        # Draw buttons
        for button in self.buttons["two_player"]:
            button.draw(screen, self.button_font)

    def draw_how_to_play(self, screen):
        screen.fill(PASTEL_PINK)

        # Hiển thị tiêu đề văn bản "HOW TO PLAY"
        title = self.title_font.render("HOW TO PLAY", True, WHITE)
        title_rect = title.get_rect(center=(self.screen_width // 2, 80))
        screen.blit(title, title_rect)

        # Hiển thị hình ảnh hướng dẫn thay vì văn bản
        # Căn giữa hình ảnh
        howtoplay_rect = self.howtoplay_image.get_rect(center=(self.screen_width // 2, self.screen_height // 2 + 40))
        screen.blit(self.howtoplay_image, howtoplay_rect)

        # Draw back button
        for button in self.buttons["how_to_play"]:
            button.draw(screen, self.button_font)

    def draw_game_over(self, screen, winner="Player", reason="capture", is_draw=False):
        # Create semi-transparent overlay
        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))  # Black with alpha for transparency
        screen.blit(overlay, (0, 0))

        # Draw title
        if is_draw:
            title = self.title_font.render("DRAW!", True, WHITE)
        else:
            title = self.title_font.render(f"{winner} WINS!", True, WHITE)

        title_rect = title.get_rect(center=(self.screen_width // 2, 150))
        screen.blit(title, title_rect)

        # Display reason for game end
        subtitle_font = pygame.font.SysFont("Arial", 24)

        if is_draw:
            subtitle = subtitle_font.render("Neither player has any valid moves left!", True, WHITE)
        elif reason == "no_moves":
            subtitle = subtitle_font.render("Opponent has no valid moves left!", True, WHITE)

        if is_draw or reason == "no_moves":
            subtitle_rect = subtitle.get_rect(center=(self.screen_width // 2, 200))
            screen.blit(subtitle, subtitle_rect)

        # Draw buttons
        for button in self.buttons["game_over"]:
            button.draw(screen, self.button_font)

    def handle_menu_events(self, event, pos):
        result = {"state": self.state, "action": None}

        if self.state == "menu":
            for i, button in enumerate(self.buttons["menu"]):
                button.check_hover(pos)
                if button.is_clicked(pos, event):
                    if i == 0:  # One Player
                        result["state"] = "one_player"
                    elif i == 1:  # Two Player
                        result["state"] = "two_player"
                    elif i == 2:  # How to Play
                        result["state"] = "how_to_play"
                    elif i == 3:  # Options
                        result["state"] = "options"
                    elif i == 4:  # Exit
                        result["action"] = "quit"

        elif self.state == "options":
            for i, button in enumerate(self.buttons["options"]):
                button.check_hover(pos)
                if button.is_clicked(pos, event):
                    if i == 0:  # Sound toggle
                        self.sound_enabled = not self.sound_enabled
                        # Bật/tắt âm thanh theo tùy chọn
                        if self.sound_enabled:
                            self.background_music.play(-1)  # Bật lại nhạc
                        else:
                            self.background_music.stop()  # Tắt nhạc
                    elif i == 1:  # Hints toggle
                        self.show_hints = not self.show_hints
                    elif i == 2:  # Back
                        result["state"] = "menu"

        elif self.state == "one_player":
            # Handle input boxes
            for input_box in self.input_boxes["one_player"]:
                name = input_box.handle_event(event)
                if name:
                    self.player_names["player1"] = name if name else "Player 1"

            # Handle buttons
            for i, button in enumerate(self.buttons["one_player"]):
                button.check_hover(pos)
                if button.is_clicked(pos, event):
                    if i == 0:  # Starting player toggle
                        # Toggle between player and AI starting
                        self.first_color = "blue" if self.first_color == "pink" else "pink"
                    elif i == 1:  # Difficulty
                        # Cycle through difficulties
                        if self.ai_difficulty == "Easy":
                            self.ai_difficulty = "Medium"
                            self.depth = 3
                        elif self.ai_difficulty == "Medium":
                            self.ai_difficulty = "Hard"
                            self.depth = 5
                        else:
                            self.ai_difficulty = "Easy"
                            self.depth = 1
                    elif i == 2:  # Start Game
                        # Save the current player name from input box
                        self.player_names["player1"] = self.input_boxes["one_player"][0].text if \
                        self.input_boxes["one_player"][0].text else "Player 1"
                        result["state"] = "game"
                        result["action"] = "start_ai_game"
                    elif i == 3:  # Back
                        result["state"] = "menu"

        elif self.state == "two_player":
            # Handle input boxes
            for i, input_box in enumerate(self.input_boxes["two_player"]):
                name = input_box.handle_event(event)
                if name:
                    if i == 0:
                        self.player_names["player1"] = name
                    else:
                        self.player_names["player2"] = name

            # Handle buttons
            for i, button in enumerate(self.buttons["two_player"]):
                button.check_hover(pos)
                if button.is_clicked(pos, event):
                    if i == 0:  # Starting color toggle
                        # Toggle between pink and blue
                        self.first_color = "blue" if self.first_color == "pink" else "pink"
                    elif i == 1:  # Start Game
                        # Save the current player names from input boxes
                        self.player_names["player1"] = self.input_boxes["two_player"][0].text if \
                        self.input_boxes["two_player"][0].text else "Player 1"
                        self.player_names["player2"] = self.input_boxes["two_player"][1].text if \
                        self.input_boxes["two_player"][1].text else "Player 2"
                        result["state"] = "game"
                        result["action"] = "start_two_player_game"
                    elif i == 2:  # Back
                        result["state"] = "menu"

        elif self.state == "how_to_play":
            for button in self.buttons["how_to_play"]:
                button.check_hover(pos)
                if button.is_clicked(pos, event):
                    result["state"] = "menu"

        elif self.state == "game":
            for i, button in enumerate(self.buttons["game"]):
                button.check_hover(pos)
                if button.is_clicked(pos, event):
                    if i == 0:  # Menu
                        result["state"] = "menu"
                    elif i == 1 and self.show_hints:  # Hint button
                        result["action"] = "show_hint"

        elif self.state == "game_over":
            for i, button in enumerate(self.buttons["game_over"]):
                button.check_hover(pos)
                if button.is_clicked(pos, event):
                    if i == 0:  # Play Again
                        result["state"] = "game"
                        result["action"] = "reset"
                    elif i == 1:  # Main Menu
                        result["state"] = "menu"

        self.state = result["state"]
        return result


class Checkers:
    def __init__(self, screen, width, height):
        self.screen = screen
        self.width = width
        self.height = height
        self.running = True
        self.clock = pygame.time.Clock()
        self.menu = Menu(width, height)
        self.playing_against_ai = False
        self.hint_move = None
        # Map player colors to board colors
        self.player_colors = {"player1": "pink", "player2": "blue"}
        # Track captured pieces
        self.captured_pieces = {"player1": 0, "player2": 0}
        self.reset_game()

    def reset_game(self):
        # Calculate board position to center it in the window
        board_size = BOARD_SIZE
        tile_width, tile_height = ORIGINAL_BOARD_WIDTH // board_size, ORIGINAL_BOARD_WIDTH // board_size

        # Calculate the offset to center the board
        board_offset_x = (self.width - (tile_width * board_size)) // 2
        board_offset_y = (self.height - (tile_height * board_size)) // 2

        # Initialize the board with the calculated values and starting color
        self.board = Board(tile_width, tile_height, board_size, board_offset_x, board_offset_y, self.menu.first_color)
        self.game = Game()
        # Initialize minimax
        self.minimax = Minimax()
        self.hint_move = None
        # Reset captured pieces count
        self.captured_pieces = {"player1": 0, "player2": 0}

        # Set up listeners for piece capture events
        self.last_red_pieces, self.last_black_pieces = self.game.check_piece(self.board)

    def update_captured_pieces(self):
        # Check current piece counts
        current_red_pieces, current_black_pieces = self.game.check_piece(self.board)

        # Calculate captured pieces
        if self.last_red_pieces > current_red_pieces:
            # player2 captured pieces from player1
            self.captured_pieces["player2"] += (self.last_red_pieces - current_red_pieces)

        if self.last_black_pieces > current_black_pieces:
            # player1 captured pieces from player2
            self.captured_pieces["player1"] += (self.last_black_pieces - current_black_pieces)

        # Update the last known piece counts
        self.last_red_pieces, self.last_black_pieces = current_red_pieces, current_black_pieces

    def draw_captured_indicator(self, player, x, y):
        # Draw a circle with the captured count
        circle_radius = 20
        count_font = pygame.font.SysFont("Arial", 18, bold=True)

        if player == "player1":
            circle_color = HOT_PINK  # For player 1 (red pieces)
        else:
            circle_color = BLUE  # For player 2 (black pieces)

        # Draw the circle
        pygame.draw.circle(self.screen, circle_color, (x, y), circle_radius)
        pygame.draw.circle(self.screen, WHITE, (x, y), circle_radius, 2)  # White border

        # Draw the count
        count_text = count_font.render(str(self.captured_pieces[player]), True, WHITE)
        count_rect = count_text.get_rect(center=(x, y))
        self.screen.blit(count_text, count_rect)

    def get_current_player(self):
        # Return which player's turn it is based on the board's turn state
        return "player1" if self.board.turn == "pink" else "player2"

    def _draw_game(self):
        # Fill the background
        self.screen.fill(PASTEL_PINK)

        # Draw the board
        self.board.draw(self.screen)

        # Draw in-game menu buttons
        for button in self.menu.buttons["game"]:
            button.draw(self.screen, self.menu.button_font)

        # Draw player names and captured indicators
        player1_name = self.menu.player_names["player1"]
        if self.playing_against_ai:
            player2_name = "AI"
        else:
            player2_name = self.menu.player_names["player2"]

        player_font = pygame.font.SysFont("Arial", 20)

        # Determine which player's turn it is
        current_player = self.get_current_player()

        # Draw player1 name with highlighting if it's their turn
        if current_player == "player1":
            # Highlighted name for player 1
            player1_text = player_font.render(f"{player1_name}", True, YELLOW)
            # Draw a yellow glow effect
            glow_font = pygame.font.SysFont("Arial", 20, bold=True)
            glow_text = glow_font.render(f"{player1_name}", True, YELLOW)
        else:
            player1_text = player_font.render(f"{player1_name}", True, WHITE)

        # Draw player2 name with highlighting if it's their turn
        if current_player == "player2":
            # Highlighted name for player 2
            player2_text = player_font.render(f"{player2_name}", True, YELLOW)
            # Draw a yellow glow effect
            glow_font = pygame.font.SysFont("Arial", 20, bold=True)
            glow_text = glow_font.render(f"{player2_name}", True, YELLOW)
        else:
            player2_text = player_font.render(f"{player2_name}", True, WHITE)

        # Position for player 1 (bottom left)
        player1_x = 20
        player1_y = self.height - 30

        # Draw highlighting effect if it's player 1's turn
        if current_player == "player1":
            # Draw a subtle highlight behind the name
            highlight_rect = player1_text.get_rect(topleft=(player1_x, player1_y))
            highlight_rect.inflate_ip(10, 6)  # Make the highlight slightly larger
            pygame.draw.rect(self.screen, (70, 70, 10), highlight_rect, border_radius=4)

        self.screen.blit(player1_text, (player1_x, player1_y))

        # Position for player 2 (bottom right)
        player2_x = self.width - player2_text.get_width() - 20
        player2_y = self.height - 30

        # Draw highlighting effect if it's player 2's turn
        if current_player == "player2":
            # Draw a subtle highlight behind the name
            highlight_rect = player2_text.get_rect(topleft=(player2_x, player2_y))
            highlight_rect.inflate_ip(10, 6)  # Make the highlight slightly larger
            pygame.draw.rect(self.screen, (70, 70, 10), highlight_rect, border_radius=4)

        self.screen.blit(player2_text, (player2_x, player2_y))

        # Draw captured piece indicators
        self.draw_captured_indicator("player1", player1_x + player1_text.get_width() // 2, player1_y - 30)
        self.draw_captured_indicator("player2", player2_x + player2_text.get_width() // 2, player2_y - 30)

        # Draw hint if available and hints are enabled
        if self.hint_move and self.menu.show_hints:
            # Highlight the suggested move
            row, col = self.hint_move
            rect = pygame.Rect(
                self.board.offset_x + col * self.board.tile_width,
                self.board.offset_y + row * self.board.tile_height,
                self.board.tile_width,
                self.board.tile_height
            )
            pygame.draw.rect(self.screen, GREEN, rect, 4)  # Draw a green rectangle to highlight the move

    def get_hint(self):
        # Tìm một nước đi hợp lệ bất kỳ cho người chơi hiện tại
        current_player_color = self.board.turn  # Lấy màu của người chơi hiện tại
        
        # Tìm tất cả các quân cờ của người chơi hiện tại có thể di chuyển
        valid_pieces = []
        for row in range(self.board.board_size):
            for col in range(self.board.board_size):
                tile = self.board.get_tile_from_pos((col, row))
                if tile.occupying_piece and tile.occupying_piece.color == current_player_color:
                    # Kiểm tra xem quân cờ này có nước đi hợp lệ không
                    valid_moves = tile.occupying_piece.valid_moves()
                    valid_jumps = tile.occupying_piece.valid_jumps()
                    
                    if valid_jumps:  # Ưu tiên các nước nhảy (bắt quân)
                        return (tile.occupying_piece, valid_jumps[0][0])
                    elif valid_moves:  # Nếu không có nước nhảy, xét các nước đi thường
                        valid_pieces.append((tile.occupying_piece, valid_moves[0]))
        
        # Nếu tìm thấy ít nhất một nước đi hợp lệ
        if valid_pieces:
            import random
            # Chọn ngẫu nhiên một trong các nước đi hợp lệ
            return random.choice(valid_pieces)
        
        return None  # Không tìm thấy nước đi hợp lệ nào

    def show_hint(self):
        # Màu tím nhạt để tô cho gợi ý
        LIGHT_PURPLE = (200, 162, 200)
        
        hint = self.get_hint()
        if hint:
            piece, move_tile = hint
            
            # Lưu màu ban đầu của ô di chuyển
            original_color = move_tile.draw_color
            
            # Tô màu ô gợi ý bằng màu tím nhạt
            move_tile.draw_color = LIGHT_PURPLE
            
            # Vẽ lại bàn cờ để hiển thị gợi ý
            self._draw_game()
            pygame.display.update()
            
            # Đợi 1 giây
            pygame.time.delay(1000)
            
            # Khôi phục màu ban đầu
            move_tile.draw_color = original_color
            
            # Vẽ lại bàn cờ với màu ban đầu
            self._draw_game()
            pygame.display.update()
            
            return True
        return False

    def get_winner_name(self):
        # The Game class sets winner to 'pink' or 'blue', so we need to map it to player names
        if self.game.is_draw:
            return "Draw"
        elif self.game.winner == "pink":
            return self.menu.player_names["player1"]  # Player 1 is pink
        else:
            if self.playing_against_ai:
                return "AI"
            else:
                return self.menu.player_names["player2"]  # Player 2 is blue

    def get_game_over_reason(self):
        # Check if it's a draw first
        if self.game.is_draw:
            return "draw"

        # Determine if game ended due to no valid moves
        current_color = self.board.turn
        if not self.game.player_has_valid_moves(self.board, current_color):
            return "no_moves"
        return "capture"  # Default reason - captured all pieces

    def main(self):
        while self.running:
            mouse_pos = pygame.mouse.get_pos()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    # Dừng âm thanh và thoát khỏi pygame trước khi đóng chương trình
                    pygame.mixer.quit()
                    pygame.quit()

                # Handle menu events
                menu_result = self.menu.handle_menu_events(event, mouse_pos)

                if menu_result["action"] == "quit":
                    self.running = False
                elif menu_result["action"] == "reset":
                    self.reset_game()
                elif menu_result["action"] == "start_ai_game":
                    self.start_one_player_game()
                elif menu_result["action"] == "start_two_player_game":
                    self.playing_against_ai = False
                    self.reset_game()
                elif menu_result["action"] == "show_hint":
                    self.show_hint()

                # Handle game clicks if in game state
                if self.menu.state == "game" and event.type == pygame.MOUSEBUTTONDOWN and not any(
                        button.rect.collidepoint(mouse_pos) for button in self.menu.buttons["game"]):
                    self.hint_move = None  # Clear hint when player makes a move

                    # Store piece count before the move
                    old_red, old_black = self.game.check_piece(self.board)

                    # Process the click
                    self.board.handle_click(event.pos)

                    # Update captured pieces after the move
                    self.update_captured_pieces()

                    # Check if game is over
                    if self.game.is_game_over(self.board):
                        winner_name = self.get_winner_name()
                        game_over_reason = self.get_game_over_reason()
                        self.game.message()
                        self.menu.state = "game_over"
                        # Draw the game over screen with the winner name and reason
                        self.menu.draw_game_over(self.screen, winner_name, game_over_reason, self.game.is_draw)

            # Draw current state
            if self.menu.state == "menu":
                self.menu.draw_menu(self.screen)
            elif self.menu.state == "options":
                self.menu.draw_options(self.screen)
            elif self.menu.state == "one_player":
                self.menu.draw_one_player(self.screen)
            elif self.menu.state == "two_player":
                self.menu.draw_two_player(self.screen)
            elif self.menu.state == "how_to_play":
                self.menu.draw_how_to_play(self.screen)
            elif self.menu.state == "game":
                self.game.check_jump(self.board)
                
                # Handle AI move in single player mode
                if self.playing_against_ai and self.board.turn != self.menu.first_color:
                    # Get the AI's color (opposite of the player's color)
                    ai_color = "blue" if self.menu.first_color == "pink" else "pink"
                    
                    # Get the depth from the menu's difficulty setting
                    depth = self.menu.depth  # This should be set from the difficulty selection
                    
                    # Use minimax to find the best move
                    _, best_board, multi_leg = self.minimax.maxAB(
                        self.board, 
                        depth, 
                        float("-inf"), 
                        float("inf"), 
                        ai_color
                    )
                    
                    # If a valid move is found, update the board
                    if best_board is not None:
                        self.board = best_board
                        # If not a multi-leg jump, switch turns back to player
                        if not multi_leg:
                            self.board.turn = self.menu.first_color
                    
                self._draw_game()
                pygame.display.update()  # Ensure the game is displayed properly

            elif self.menu.state == "game_over":
                self._draw_game()  # Draw game board in background
                winner_name = self.get_winner_name()
                game_over_reason = self.get_game_over_reason()
                self.menu.draw_game_over(self.screen, winner_name, game_over_reason, self.game.is_draw)

            pygame.display.update()
            self.clock.tick(60)

    def start_one_player_game(self):
        """
        Khởi động phiên bản game giống như main1player.py, sử dụng checkers module
        """
        # Lưu trạng thái running hiện tại
        running_state = self.running
        self.running = False
        
        # Tạo cửa sổ mới với kích thước đúng như main1player
        window_surface = pygame.display.set_mode((WIDTH_HEIGHT, WIDTH_HEIGHT))
        pygame.display.set_caption("Checkers Game - Single Player")
        
        # Khởi tạo các thành phần
        gui = GUI(window_surface)
        checkers_minimax = CheckersMinimax()
        
        # Tạo nút Menu để quay lại menu chính
        menu_button_font = pygame.font.SysFont("Arial", 20)
        menu_button_rect = pygame.Rect(10, 10, 80, 30)
        # Sử dụng cùng màu với các nút trong menu chính
        menu_button_color = BUTTON_COLOR  # Thay vì (100, 100, 100)
        menu_button_hover_color = BUTTON_HOVER_COLOR  # Thay vì (150, 150, 150)
        menu_button_text = menu_button_font.render("Menu", True, (255, 255, 255))
        menu_button_text_rect = menu_button_text.get_rect(center=menu_button_rect.center)
        menu_button_hover = False
        
        # Xác định lượt chơi đầu tiên
        player_turn = True  # Người chơi đi trước mặc định
        if self.menu.first_color == "blue":
            player_turn = False  # AI đi trước
        
        # Lấy tên người chơi từ menu
        player_name = self.menu.player_names["player1"]
        ai_name = "AI"
        
        # Biến đếm quân đã ăn
        player_captures = 0
        ai_captures = 0
        
        # Định nghĩa các font chữ và màu sắc
        name_font = pygame.font.SysFont("Arial", 22)
        count_font = pygame.font.SysFont("Arial", 24, bold=True)
        active_color = (255, 255, 0)  # Màu vàng cho người đang đi
        inactive_color = (255, 255, 255)  # Màu trắng cho người đang chờ
        
        # Tạo game
        game = CheckersGame(
            window_surface, 
            gui, 
            self.menu.depth,  # Độ khó từ menu (1, 3, hoặc 5)
            False,  # Verbose mode off
            player_turn  # Ai đi trước
        )
        
        # Theo dõi số quân cờ ban đầu
        initial_player_pieces = 12
        initial_ai_pieces = 12
        
        # Bắt đầu game loop
        game_over = False
        clock = pygame.time.Clock()
        
        # Hàm vẽ thông tin người chơi
        def draw_player_info():
            # Cập nhật số quân đã bắt
            board = game.get_board()
            current_player_pieces = board.player_remaining
            current_ai_pieces = board.comp_remaining
            
            nonlocal player_captures, ai_captures
            player_captures = initial_ai_pieces - current_ai_pieces
            ai_captures = initial_player_pieces - current_player_pieces
            
            # Vẽ tên người chơi ở góc dưới trái với màu trắng
            player_text = name_font.render(player_name, True, (255, 255, 255))  # Màu trắng
            player_x = 20
            player_y = WIDTH_HEIGHT - 30
            
            # Vẽ tên AI ở góc dưới phải với màu trắng
            ai_text = name_font.render(ai_name, True, (255, 255, 255))  # Màu trắng
            ai_x = WIDTH_HEIGHT - ai_text.get_width() - 20
            ai_y = WIDTH_HEIGHT - 30
            
            # Vẽ viền highlight màu vàng xung quanh tên
            # Tạo hình chữ nhật cho viền highlight
            player_rect = player_text.get_rect(topleft=(player_x, player_y))
            player_rect.inflate_ip(10, 6)  # Làm viền lớn hơn một chút
            pygame.draw.rect(window_surface, (255, 255, 0), player_rect, 2, border_radius=4)  # Viền màu vàng
            
            ai_rect = ai_text.get_rect(topleft=(ai_x, ai_y))
            ai_rect.inflate_ip(10, 6)  # Làm viền lớn hơn một chút
            pygame.draw.rect(window_surface, (255, 255, 0), ai_rect, 2, border_radius=4)  # Viền màu vàng
            
            # Vẽ số quân cờ đã ăn được phía trên tên
            player_capture_text = count_font.render(str(player_captures), True, (255, 192, 203))  # Màu hồng cho quân người chơi
            ai_capture_text = count_font.render(str(ai_captures), True, (0, 0, 255))  # Màu xanh cho quân AI
            
            # Đặt vị trí số quân đã ăn phía trên tên
            player_capture_x = player_x + player_text.get_width() // 2 - player_capture_text.get_width() // 2
            player_capture_y = player_y - 25
            
            ai_capture_x = ai_x + ai_text.get_width() // 2 - ai_capture_text.get_width() // 2
            ai_capture_y = ai_y - 25
            
            # Vẽ tên và số quân đã ăn
            window_surface.blit(player_text, (player_x, player_y))
            window_surface.blit(ai_text, (ai_x, ai_y))
            window_surface.blit(player_capture_text, (player_capture_x, player_capture_y))
            window_surface.blit(ai_capture_text, (ai_capture_x, ai_capture_y))
        
        while not game_over:
            clock.tick(FRAMES)
            
            # AI's turn
            if not game.playerTurn:
                gui.output_message("THINKING...")
                value, new_board, multi_leg = checkers_minimax.maxAB(
                    game.get_board(),
                    self.menu.depth,
                    float("-inf"),
                    float("inf"),
                    game,
                    False,
                    False  # verbose off
                )
                game.ai_move(new_board, multi_leg)
            
            # Kiểm tra kết thúc game
            if game.player_win() is not None:
                if game.player_win():
                    gui.output_message("YOU HAVE WON!", font=pygame.font.SysFont("Arial", 32), alpha=255)
                else:
                    gui.output_message("You Have Lost!", font=pygame.font.SysFont("Arial", 32), alpha=255)
                pygame.time.delay(2 * TIME_DELAY)
                game_over = True
            
            # Xử lý sự kiện
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    game_over = True
                    
                # Xử lý nút Menu
                mouse_pos = pygame.mouse.get_pos()
                menu_button_hover = menu_button_rect.collidepoint(mouse_pos)
                
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if menu_button_hover:
                        # Quay trở về menu chính
                        game_over = True
                        # Khôi phục kích thước màn hình ban đầu
                        screen = pygame.display.set_mode((int(ORIGINAL_BOARD_WIDTH * 1.25), int(ORIGINAL_BOARD_WIDTH * 1.25)))
                        pygame.display.set_caption("CHECKERS from AAP girls")
                        # Đặt lại trạng thái running để menu chính hoạt động
                        self.running = running_state
                        # Đảm bảo trạng thái là menu chính
                        self.menu.state = "menu"
                        # Không khởi động lại game từ đầu, chỉ trở về menu hiện tại
                
                if gui.play and event.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    row, col = gui.get_square_from_mouse(pos)
                    game.click_on_square(row, col)
                
                # Các phím chức năng
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_p:  # Pause
                        gui.pause_menu()
                    if event.key == pygame.K_i:  # Info/Help
                        gui.play = False
                        gui.output_help()
                        gui.play = True
                    if event.key == pygame.K_ESCAPE:  # Quay về menu chính
                        game_over = True
                    if event.key == pygame.K_h:  # Hint
                        gui.play = False
                        gui.output_message("Thinking...")
                        value, new_board, multi_leg = checkers_minimax.maxAB(
                            game.get_board(),
                            3,  # Độ sâu cố định cho hint
                            float("-inf"),
                            float("inf"),
                            game,
                            True,
                            False
                        )
                        # Hiển thị gợi ý
                        proposed_counters = new_board.get_sides_counters(True)
                        current_counters = game.get_board().get_sides_counters(True)
                        proposed_counters_cords = []
                        current_counters_cords = []
                        
                        for counter in proposed_counters:
                            proposed_counters_cords.append((counter.col, counter.row))
                        for counter in current_counters:
                            current_counters_cords.append((counter.col, counter.row))
                            
                        current = list(set(current_counters_cords) - set(proposed_counters_cords))
                        new = list(set(proposed_counters_cords) - set(current_counters_cords))
                        
                        if current and new:
                            game.update()
                            current_x = SQR_DIM * current[0][0] + SQR_DIM // 2
                            current_y = SQR_DIM * current[0][1] + SQR_DIM // 2
                            new_x = SQR_DIM * new[0][0] + SQR_DIM // 2
                            new_y = SQR_DIM * new[0][1] + SQR_DIM // 2
                            
                            pygame.draw.circle(window_surface, (0, 0, 255), (current_x, current_y), LINE_WIDTH)
                            pygame.draw.circle(window_surface, (0, 0, 255), (new_x, new_y), LINE_WIDTH)
                            pygame.display.update()
                            pygame.time.delay(2 * TIME_DELAY)
                        
                        gui.play = True
            
            # Cập nhật màn hình
            game.update()
            
            # Vẽ thông tin người chơi
            draw_player_info()
            
            # Vẽ nút Menu
            pygame.draw.rect(window_surface, 
                             menu_button_hover_color if menu_button_hover else menu_button_color, 
                             menu_button_rect, 
                             border_radius=5)
            pygame.draw.rect(window_surface, (255, 255, 255), menu_button_rect, 2, border_radius=5)  # Viền trắng
            window_surface.blit(menu_button_text, menu_button_text_rect)
            
            # Cập nhật màn hình
            pygame.display.update()
        
        # Sau khi kết thúc game, quay lại màn hình chính
        # Đặt lại trạng thái running để menu chính hoạt động
        self.running = running_state
        # Đảm bảo trạng thái là menu chính
        self.menu.state = "menu"


if __name__ == "__main__":
    # Original window size
    original_size = (640, 640)

    # New window size (25% larger)
    window_size = (int(original_size[0] * 1.25), int(original_size[1] * 1.25))

    screen = pygame.display.set_mode(window_size)
    pygame.display.set_caption("CHECKERS from AAP girls")

    checkers = Checkers(screen, window_size[0], window_size[1])
    checkers.main()