import pygame

IMAGES_ADDRESSES = "C:/Networks/Final_Project/graphics/"
PLAYER_PIXEL_WIDTH = 27
PLAYER_PIXEL_HEIGHT = 27
PLAYERS_LOCATION_LIST = [(567, 324), (54, 297), (81, 297), (54, 324), (81, 324), (54, 351), (81, 351)]
#                         runner     catcher1   catcher2   catcher3   catcher4   catcher5   catcher6


class Player:
    def __init__(self, p, is_runner, catcher_number, username):
        self.p_index = p  # players' index in the players list at the server
        self.is_runner = is_runner  # If the player is the runner or not
        self.catcher_number = catcher_number  # If the player is the runner the value is -1
        self.username = username  # The username of the client that plays as this player
        self.x, self.y = self.__get_x_and_y()  # Players location
        self.img_address = self.__get_skin()  # the players' image address
        self.steps = 0  # The number of steps the player did

    def __get_x_and_y(self):
        """
        :return: starting player location
        """
        if self.is_runner:
            return PLAYERS_LOCATION_LIST[0]
        return PLAYERS_LOCATION_LIST[self.catcher_number]

    def set_x_y(self, loc):
        """
        This function updates the players location
        :param loc: New players' location
        """
        self.x, self.y = loc

    def __get_skin(self):
        """
        :return: The players "skin" according to its job (catcher or runner)
        """
        if self.is_runner:
            return IMAGES_ADDRESSES + "runner.png"
        return IMAGES_ADDRESSES + "catcher_" + str(self.catcher_number) + ".png"

    def draw(self, window):
        """
        This function draws on "window" the player
        :param window: The game window (screen)
        """
        img = pygame.image.load(self.img_address)
        img = pygame.transform.scale(img, (PLAYER_PIXEL_HEIGHT, PLAYER_PIXEL_HEIGHT))
        window.blit(img, (self.x, self.y))

    def __str__(self):
        return f"p= {self.p_index} x= {self.x} y= {self.y} is_runner: {self.is_runner}  catcher number {self.catcher_number} steps = {self.steps} username = {self.username}"
