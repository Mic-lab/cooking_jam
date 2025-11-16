from .entity import Entity
from .config import COLORS
from .font import FONTS
from .animation import Animation
from pygame import Vector2 as Vec2
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

    def update(self, inputs, grid, selected_ingredient):
        if inputs['released']['mouse1']:
            self.selected = False
            if self.hovered_cell:
                if self.hovered_cell[3]:
                    self.real_pos = self.hovered_cell[2].center - 0.5*Vec2(self.rect.size)
                    grid.add_ingredient(self, self.hovered_cell[0], self.hovered_cell[1])
                    self.grid_pos = self.hovered_cell[0], self.hovered_cell[1]
                    self.hovered_cell = None
        elif inputs['pressed']['mouse1']:
            if self.rect.collidepoint(inputs['mouse pos']) and not selected_ingredient:
                grid.remove_ingredient(self)
                self.selected = True

        if self.selected:
            self.real_pos = inputs['mouse pos'] - Vec2(self.rect.size) * 0.5

            self.hovered_cell = None
            for row in range(grid.size[1]):
                for col in range(grid.size[0]):
                    rect = grid.get_rect(row, col)
                    if rect.collidepoint(self.rect.center):
                        empty = grid.data[row][col] is None
                        self.hovered_cell = (col, row, rect, empty)
                        break

    def __init__(self, name):
        super().__init__((0, 0), name)
        Animation.animation_db[self.name]['rect'] = pygame.Rect(0, 0, 23, 23)
        self.selected = False
        self.hovered_cell = None
        self.grid_pos = None
