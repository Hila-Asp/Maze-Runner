import pygame
from models.button import Button
from models.pictures import Pictures

# A list of the locations of the blocks in the frame
FRAME_LOCATIONS = [(0, 0), (0, 27), (0, 81), (27, 0), (54, 0), (81, 0), (108, 0), (162, 0), (135, 0), (189, 0),
                   (216, 0), (243, 0), (270, 0), (297, 0), (324, 0), (351, 0), (378, 0), (405, 0), (432, 0), (459, 0),
                   (486, 0), (513, 0), (540, 0), (567, 0), (594, 0), (621, 0), (648, 0), (0, 54), (0, 108), (0, 135),
                   (0, 162), (0, 189), (0, 216), (0, 297), (0, 270), (0, 243), (0, 324), (0, 648), (0, 621), (0, 594),
                   (0, 567), (0, 540), (0, 513), (0, 486), (0, 459), (0, 405), (0, 378), (0, 351), (0, 432), (27, 648),
                   (54, 648), (108, 648), (81, 648), (135, 648), (162, 648), (216, 648), (189, 648), (243, 648),
                   (270, 648), (297, 648), (324, 648), (351, 648), (378, 648), (405, 648), (432, 648), (459, 648),
                   (486, 648), (513, 648), (540, 648), (594, 648), (621, 648), (648, 648), (567, 648), (648, 594),
                   (648, 567), (648, 540), (648, 513), (648, 486), (648, 459), (648, 405), (648, 378), (648, 351),
                   (648, 297), (648, 243), (648, 216), (648, 162), (648, 81), (648, 27), (648, 54), (648, 135),
                   (648, 108), (648, 189), (648, 270), (648, 324), (648, 432), (648, 621)]
# A list of the players start location
PLAYERS_LOCATION_LIST = [(567, 324), (54, 297), (81, 297), (54, 324), (81, 324), (54, 351), (81, 351)]
# There are 25 blocks in a row
ROW_LENGTH = 25
# There are 25 blocks in a column
COLUMN_LENGTH = 25
BLOCK_HEIGHT = 27
BLOCK_WIDTH = 27
GAME_SCREEN_HEIGHT = 675
GAME_SCREEN_WIDTH = 675
SCREEN_HEIGHT = 702
BLOCK_TEXTURE = Pictures().block_scaled
BUTTONS_LIST = [Button("Reset", 75, GAME_SCREEN_HEIGHT, (70, 70, 70), (255, 255, 255), 150, 27, "papyrus", 20),
                Button("Save", 263, GAME_SCREEN_HEIGHT, (0, 81, 0), (255, 255, 255), 150, 27, "papyrus", 20),
                Button("Return", 450, GAME_SCREEN_HEIGHT, (40, 40, 40), (255, 255, 255), 150, 27, "papyrus", 20)]


class Creator:
    def __init__(self):
        # A list of the locations of the blocks
        self.block_locations = FRAME_LOCATIONS.copy()
        # A list of the buttons that appear on the screen
        self.buttons_list = BUTTONS_LIST

    def draw(self, window):
        """
        This Function draws on the window the map creator screen- a empty map (only with frames) and 3 buttons (save, reset, return)
        :param window: The screen that is presented
        :return: If the map is saved the function returns the map
        """
        pygame.display.set_caption("Map Creator")
        window.fill((128, 128, 128))
        for b in self.block_locations:
            window.blit(BLOCK_TEXTURE, b)
        self.buttons_list[0].draw(window)
        self.buttons_list[1].draw(window)
        self.buttons_list[2].draw(window)
        pygame.display.update()
        finish = False
        while not finish:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                if event.type == pygame.MOUSEBUTTONDOWN:
                    # if pressed the mouse
                    pos = pygame.mouse.get_pos()
                    if pos[1] <= GAME_SCREEN_HEIGHT:
                        # If in game screen
                        x = pos[0] // BLOCK_WIDTH
                        y = pos[1] // BLOCK_HEIGHT
                        pos = (x * BLOCK_WIDTH, y * BLOCK_HEIGHT)
                        if pos in FRAME_LOCATIONS or pos in PLAYERS_LOCATION_LIST:
                            # If clicked on the frame or the players start location nothing changes
                            pass
                        elif pos in self.block_locations:
                            # If clicked on a existing block - removes the block
                            self.block_locations.remove(pos)
                        else:
                            self.block_locations.append(pos)
                    elif self.buttons_list[0].click(pos):
                        # Pressed reset button
                        self.block_locations = FRAME_LOCATIONS.copy()
                    elif self.buttons_list[2].click(pos):
                        return
                    elif self.buttons_list[1].click(pos):
                        # Presses save button
                        return self.block_locations
                    window.fill((128, 128, 128))

                    # Draws the blocks on the screen
                    for b in self.block_locations:
                        window.blit(BLOCK_TEXTURE, b)

                    # Draws the buttons on the screen
                    self.buttons_list[0].draw(window)
                    self.buttons_list[1].draw(window)
                    self.buttons_list[2].draw(window)
                    pygame.display.update()
