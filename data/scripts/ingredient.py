from .entity import Entity
from .config import COLORS
from .font import FONTS
import pygame

class Ingredient(Entity):

    @staticmethod
    def get_order_img(order):
        txt_1 = 'Ingredients:'
        txt_2 = ''
        w = 150
        font_surf_1 = FONTS['basic'].get_surf(txt_1, wraplength=w, color=COLORS['black1'])
        for quantity, ingredient in order['want']:
            txt_2 += f'    {quantity}x {ingredient}\n'
        font_surf_2 = FONTS['basic'].get_surf(txt_2, wraplength=w, color=COLORS['blue1'])

        h = font_surf_1.get_height() + font_surf_2.get_height()
        s = pygame.Surface((w, h))
        # s.fill(COLORS['white1'])
        s.set_colorkey((0, 0, 0))
        # s.blit(font_surf_1, (0, 2))
        y = font_surf_1.get_height()
        # pygame.draw.aaline(s, COLORS['black3'], (0, y+2), (w, y+2))
        # s.blit(font_surf_2, (0, y+3))
        s.blit(font_surf_2, (0, 0))
        return s


    def __init__(self, name):
        super().__init__((0, 0), name, 'idle')
