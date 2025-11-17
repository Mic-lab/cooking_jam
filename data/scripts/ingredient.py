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
        self.old_pos = self.real_pos.copy()

        if inputs['released']['mouse1']:
            self.selected = False
            if self.hovered_cell:
                if self.hovered_cell[3]:
                    self.real_pos = self.hovered_cell[2].center - 0.5*Vec2(self.rect.size)
                    self.grid_pos = self.hovered_cell[0], self.hovered_cell[1]
                    grid.add_ingredient(self, self.hovered_cell[0], self.hovered_cell[1])
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
                    rect = grid.get_rect(col, row)
                    if rect.collidepoint(self.rect.center):
                        empty = grid.data[row][col] is None
                        self.hovered_cell = (col, row, rect, empty)
                        break

        vel = self.real_pos - self.old_pos
        self.angle += vel.x * 0.8
        self.angle *= 0.6

    DESCRIPTION_SURF_W = 200
    def get_description_surf(self):
        point_info = '  Collectively' if self.group else ''
        name_surf = FONTS['basic'].get_surf(self.name.title() + f'    (+{self.points}{point_info})', COLORS['blue4'])
        font_surf = FONTS['basic'].get_surf(self.description,
                                            wraplength=self.DESCRIPTION_SURF_W,
                                            color=COLORS['white1'])

        h = font_surf.get_height() + name_surf.get_height()
        surf = pygame.Surface((self.DESCRIPTION_SURF_W, h + 4), pygame.SRCALPHA)
        surf.fill((*COLORS['black2'], 120))
        surf.blit(name_surf, (2, 2))
        surf.blit(font_surf, (2, name_surf.get_height()))
        pygame.draw.rect(surf, COLORS['white1'], (0, 0, *surf.get_size()), width=1)
        return surf

    def __init__(self, name, description, group=False):
        super().__init__((0, 0), name)
        Animation.animation_db[self.name]['rect'] = pygame.Rect(0, 0, 23, 23)
        self.description = description
        self.group = group
        self.selected = False
        self.hovered_cell = None
        self.grid_pos = None
        self.points = 0
        self.description_surf = self.get_description_surf()
        self.angle = 0

    def render(self, surf):
        img = self.img
        angle = round(self.angle)
        if angle != 0:
            img = pygame.transform.rotate(img, angle)
        offset = 0.5 * (Vec2(img.get_size()) - self.img.get_size())
        surf.blit(img, self.pos - offset)

    def set_points(self, new_points):
        self.points = new_points
        self.description_surf = self.get_description_surf()

    def calculate_points(self, grid):
        return 0

    def calculate_points_group(self, grid):
        return 0

class Bread(Ingredient):
    def __init__(self):
        description = '''+ 10 points if another bread is on the same line.'''
        super().__init__(name='bread', description=description)
        
    def calculate_points(self, grid):
        points = 0
        for row in range(grid.size[1]):
            if self.grid_pos == (self.grid_pos[0], row): continue
            if isinstance(grid.data[row][self.grid_pos[0]], Bread):
                points += 10
        for col in range(grid.size[0]):
            if self.grid_pos == (col, self.grid_pos[1]): continue
            if isinstance(grid.data[self.grid_pos[1]][col], Bread):
                points += 10
        return points

class Bagel(Ingredient):
    def __init__(self):
        description = '''+5 points for every ingredient in between bagels'''
        super().__init__(name='bagel', description=description, group=True)

    def calc_func(self, grid):
        score = 0
        first = False
        for row in grid:
            added_score = 0
            for cell in row:
                if cell is None: continue
                if isinstance(cell, Bagel):
                    if not first:
                        first = True
                        continue
                    score += added_score
                    added_score = 0
                else:
                    added_score += 5
        return score
        
    def calculate_points(self, grid):
        score = 0
        score += self.calc_func(grid.data)
        transposed_grid = list(zip(*grid.data))
        score += self.calc_func(transposed_grid)
        return score

class Tomato(Ingredient):
    def __init__(self):
        description = '''.'''
        super().__init__(name='tomato', description=description)

class Cucumber(Ingredient):
    def __init__(self):
        description = '''.'''
        super().__init__(name='cucumber', description=description)

name_map = {
    'bread': Bread,
    'bagel': Bagel,
    'tomato': Tomato,
    'cucumber': Cucumber,
}
def init_from_name(name):
    return name_map[name]()
