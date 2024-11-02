from dataclasses import dataclass
import pygame

IMAGE_ADDRESS = "C:/Networks/Final_Project/graphics/"
BLOCK_PIXEL_WIDTH = 27
BLOCK_PIXEL_HEIGHT = 27
SCREEN_WIDTH = 675
SCREEN_HEIGHT = 702
GAME_SCREEN_HEIGHT = 675
GAME_SCREEN_WIDTH = 675


@dataclass
class Pictures:
    def __init__(self):
        # The picture of the catchers that appears in the instructions screen
        instructions_catchers = pygame.image.load(IMAGE_ADDRESS + "multiple_catchers_instructions.png")
        self.instructions_catchers_scaled = pygame.transform.scale(instructions_catchers, (55, 55))
        # The picture of the runner that appears in the instructions screen
        instructions_runner = pygame.image.load(IMAGE_ADDRESS + "runner.png")
        self.instructions_runner_scaled = pygame.transform.scale(instructions_runner, (40, 40))
        # The picture of the players that appears in the home screen
        players_pic = pygame.image.load(IMAGE_ADDRESS + "players_picture.png")
        self.players_pic_scaled = pygame.transform.scale(players_pic, (SCREEN_WIDTH, SCREEN_HEIGHT / 2))
        # The game's background
        background = pygame.image.load(IMAGE_ADDRESS + "back.png")
        self.background_scaled = pygame.transform.scale(background, (GAME_SCREEN_WIDTH, GAME_SCREEN_HEIGHT))
        # The block's texture (the block)
        block = pygame.image.load(IMAGE_ADDRESS + "block_tex.png")
        self.block_scaled = pygame.transform.scale(block, (BLOCK_PIXEL_WIDTH, BLOCK_PIXEL_HEIGHT))

        apple = pygame.image.load(IMAGE_ADDRESS + "apple.png")
        apple.set_colorkey((128, 128, 255))
        self.apple_scaled = pygame.transform.scale(apple, (BLOCK_PIXEL_WIDTH, BLOCK_PIXEL_HEIGHT))
