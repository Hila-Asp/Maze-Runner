import pygame


class Button:
    def __init__(self, text, x, y, button_color, text_color, width, height, font, text_size):
        # The text that will be on the button
        self.text = text
        # The x value of the buttons' location
        self.x = x
        # The y value of the buttons' location
        self.y = y
        # The color of the button
        self.button_color = button_color
        # The color of the text on the button
        self.text_color = text_color
        # The width of the button
        self.width = width
        # The height of the button
        self.height = height
        # The font type that the text on the button will be
        self.font = font
        # The size of the text on the button
        self.text_size = text_size

    def draw(self, window):
        """"
        This functions draws on the screen the button
        :param window: The window that the button is Drawn on
        """
        pygame.font.init()
        pygame.draw.rect(window, self.button_color, (self.x, self.y, self.width, self.height))
        font = pygame.font.SysFont(self.font, self.text_size)
        text = font.render(self.text, True, self.text_color)
        window.blit(text, (self.x + round(self.width/2) - round(text.get_width()/2), self.y + round(self.height/2) - round(text.get_height()/2)))

    def click(self, pos):
        """
        This function checks if the mouse clicked on the button.
        :param pos: The position of the mouse
        :return: True if the mouse pressed on the button.
                 False if the mouse didn't press on the button
        """
        x1 = pos[0]
        y1 = pos[1]
        if self.x <= x1 <= self.x + self.width and self.y <= y1 <= self.y + self.height:
            # If pressed the button
            return True
        else:
            return False
