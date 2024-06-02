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
        instructions_catchers = pygame.image.load(IMAGE_ADDRESS + "multiple_catchers_instructions.png")
        self.instructions_catchers_scaled = pygame.transform.scale(instructions_catchers, (55, 55))
        instructions_runner = pygame.image.load(IMAGE_ADDRESS + "runner.png")
        self.instructions_runner_scaled = pygame.transform.scale(instructions_runner, (40, 40))
        players_pic = pygame.image.load(IMAGE_ADDRESS + "players_picture.png")
        self.players_pic_scaled = pygame.transform.scale(players_pic, (SCREEN_WIDTH, SCREEN_HEIGHT / 2))
        background = pygame.image.load(IMAGE_ADDRESS + "back.png")
        self.background_scaled = pygame.transform.scale(background, (GAME_SCREEN_WIDTH, GAME_SCREEN_HEIGHT))
        block = pygame.image.load(IMAGE_ADDRESS + "block_tex.png")
        self.block_scaled = pygame.transform.scale(block, (BLOCK_PIXEL_WIDTH, BLOCK_PIXEL_HEIGHT))
