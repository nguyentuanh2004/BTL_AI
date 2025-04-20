import pygame

pygame.init()

# WINDOW BEHAVIOURS
WIDTH_HEIGHT = 800
ROW_COL = 8
SQR_DIM = WIDTH_HEIGHT // ROW_COL

# TIME BEHAVIOURS
FRAMES = 30
TIME_DELAY = 1000

# COLOURS
RED = (255, 0, 0)
WHITE = (219, 112, 147) # Tú Anh thích màu hồng nhưng lười đổi tên biến hihi
BLACK = (175, 238, 238) # vẫn thế nhưng lần này là màu xanh dương :>
GREEN = (0, 255, 0)
BLUE = (181, 126, 220) #TuAnh thích màu tím nhưng lười đổi tên biến hehe
GREY = (128, 128, 128)
GOLD = (212, 175, 55)
BROWN = (53, 53, 53) #màu đen vì TA ghét màu nâu
CREAM = (220, 189, 194) #màu hồng nhạt nhưng lỡ đặt tên biến roi lười đổi lắmmmmm
TILE_BACKGROUND = BROWN
TILE_ALTERNATE = CREAM

# SHAPE BEHAVIOURS
LINE_WIDTH = 10

# FONTS
FONT_PATH = "font/LexendDeca.ttf"
XL_FONT = pygame.font.Font(FONT_PATH, 100)
L_FONT = pygame.font.Font(FONT_PATH, 75)
M_FONT = pygame.font.Font(FONT_PATH, 50)
S_FONT = pygame.font.Font(FONT_PATH, 25)
XS_FONT = pygame.font.Font(FONT_PATH, 15)
