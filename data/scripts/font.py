from . import utils
import pygame
import os
from .config import COLORS

pygame.init()

class Font:

    FONTS_DIR = 'data/imgs/fonts'

    def __init__(self, file, size, color, antialias=False):
        self.obj = pygame.font.Font(f'{Font.FONTS_DIR}/{file}.ttf', size)
        self.color = color
        self.antialias = antialias

    def get_surf(self, text, color=None, **kwargs):
        if not color:
            color = self.color

        surf = pygame.Font.render(self.obj, text, self.antialias, color, **kwargs)
        return surf

FONTS = {
    'regular': Font('ProggyClean', 16, (240, 240, 240)),
    'basic': Font('Minecraftia', 8, COLORS['white2']),
}
