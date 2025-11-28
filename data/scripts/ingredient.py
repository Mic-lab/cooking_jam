from .entity import Entity
from .config import COLORS
from .font import FONTS
from .animation import Animation
from .sfx import sounds
from .utils import swap_colors, lerp
from . import config
from .timer import Timer
from pygame import Vector2 as Vec2
import pygame
from random import randint


class Ingredient(Entity):

    SHADOW_CACHE = {}
    SHADOW_OFFSET = Vec2(1, 2)

    @staticmethod
    def get_order_img(order):
        txt_1 = 'Ingredients:'
        txt_2 = ''
        w = 150
        font_surf_1 = FONTS['basic'].get_surf(txt_1, wraplength=w-2, color=COLORS['black1'])
        for quantity, ingredient in order['want']:
            txt_2 += f'    {quantity}x {ingredient}\n'
        font_surf_2 = FONTS['basic'].get_surf(txt_2, wraplength=w-2, color=COLORS['blue1'])

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
            if self.selected:
                self.selected = False
                self.select_timer.frame = self.select_timer.duration
                self.select_timer.done = True
            if self.hovered_cell:
                if self.hovered_cell[3]:
                    self.real_pos = self.hovered_cell[2].center - 0.5*Vec2(self.rect.size) + Vec2(1, 1)
                    self.grid_pos = self.hovered_cell[0], self.hovered_cell[1]
                    grid.add_ingredient(self, self.hovered_cell[0], self.hovered_cell[1])
                    self.hovered_cell = None
                    sounds[f'place_{randint(1, 4)}.wav'].play()
        elif inputs['pressed']['mouse1']:
            if self.rect.collidepoint(inputs['mouse pos']) and not selected_ingredient:
                grid.remove_ingredient(self)
                self.selected = True
                self.select_timer.reset()
                sounds['pickup.wav'].play()

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

        self.vel = self.real_pos - self.old_pos
        vel = self.vel
        self.angle += vel.x * 0.85
        self.angle *= 0.68

        if self.real_pos[0] > config.CANVAS_SIZE[0] - 50:
            self.real_pos[0] = config.CANVAS_SIZE[0] - 50
        if self.real_pos[1] > config.CANVAS_SIZE[1] - 50:
            self.real_pos[1] = config.CANVAS_SIZE[1] - 50

        if self.real_pos[0] < 10:
            self.real_pos[0] = 10
        if self.real_pos[1] < 10:
            self.real_pos[1] = 10
            
        self.select_timer.update()
    @property
    def description_title(self):
        return self.name.title()

    DESCRIPTION_SURF_W = 200
    def get_description_surf(self):
        point_info = '  Collectively' if self.group else ''
        name_surf = FONTS['basic'].get_surf(self.description_title + f'    (+{self.points}{point_info})', COLORS['blue4'])
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
        self.select_timer = Timer(30, done=True)
        self.hovered_cell = None
        self.grid_pos = None
        self.points = 0
        self.description_surf = self.get_description_surf()
        self.angle = 0
        self.just_placed = False
        if self.name not in self.SHADOW_CACHE:
            shadow = pygame.mask.from_surface(self.img).to_surface()
            shadow = swap_colors(shadow, (255, 255, 255), COLORS['super black'])
            shadow.set_colorkey((0, 0, 0))
            self.SHADOW_CACHE[self.name] = shadow
        self.shadow = self.SHADOW_CACHE[self.name]

    def render(self, surf):
        img = self.img
        x_scale = lerp(0.5, 1, self.select_timer.easeOutElastic(a=2), clamp=False)
        y_scale = lerp(0.5, 1, -self.select_timer.easeOutElastic(a=2)+2, clamp=False)
        img = pygame.transform.scale(img, 
                                     (img.get_width() * x_scale,
                                      img.get_height() * y_scale)
                                     )
        # scale_offset = -0.5*(Vec2(self.img.get_size()) + img.get_size())
        # scale_offset = 0.5*(Vec2(self.img.get_size()) - img.get_size())
        scale_offset = Vec2(0, 0)

        shadow = self.shadow
        angle = round(self.angle)
        if angle != 0:
            img = pygame.transform.rotate(img, angle)
            shadow = pygame.transform.rotate(shadow, angle)
        offset = 0.5 * (Vec2(img.get_size()) - self.img.get_size())
        if not self.grid_pos:
            shadow = pygame.transform.scale(shadow, 
                                         (shadow.get_width() * x_scale,
                                          shadow.get_height() * y_scale)
                                         )
            surf.blit(shadow, self.pos - offset - scale_offset + self.SHADOW_OFFSET)
        surf.blit(img, self.pos - offset - scale_offset)

    def set_points(self, new_points):
        self.points = new_points
        self.description_surf = self.get_description_surf()

    def calculate_points(self, grid):
        return 0

    def calculate_points_group(self, grid):
        return 0

class Bread(Ingredient):
    def __init__(self):
        description = '''+15 if another bread is on the same line.'''
        super().__init__(name='bread', description=description)
        
    def calculate_points(self, grid):
        points = 0
        flash_coords = []
        for row in range(grid.size[1]):
            if self.grid_pos == (self.grid_pos[0], row): continue
            if isinstance(grid.data[row][self.grid_pos[0]], Bread):
                points += 15
                flash_style = 1
            else:
                flash_style = 0
            flash_coords.append((self.grid_pos[0], row, flash_style))
        for col in range(grid.size[0]):
            if self.grid_pos == (col, self.grid_pos[1]): continue
            if isinstance(grid.data[self.grid_pos[1]][col], Bread):
                points += 15
                flash_style = 1
            else:
                flash_style = 0
            flash_coords.append((col, self.grid_pos[1], flash_style))
        return points, flash_coords

class Bagel(Ingredient):
    def __init__(self):
        description = '''+10 for every ingredient in between bagels (only horizontally and vertically)'''
        super().__init__(name='bagel', description=description, group=True)

    def calc_func(self, grid, switch=False):
        score = 0
        for row in grid:
            first = False
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
                    if first:
                        added_score += 10
        return score
        
    def calculate_points(self, grid):
        score = 0
        flash_coords = []

        for i, matrix in enumerate((grid.data, list(zip(*grid.data)))):
        # for i, matrix in enumerate((grid.data,)):
            switch = i == 1
            added_score = self.calc_func(matrix, switch)
            score += added_score


        # ---------------------------------------------------------
        flash_coords = []
        for row in range(grid.size[1]):
            if self.grid_pos == (self.grid_pos[0], row):
                continue
            if isinstance(grid.data[row][self.grid_pos[0]], Bagel):
                continue
            flash_style = 1
            flash_coords.append((self.grid_pos[0], row, flash_style))
        for col in range(grid.size[0]):
            if self.grid_pos == (col, self.grid_pos[1]):
                continue
            if isinstance(grid.data[self.grid_pos[1]][col], Bagel):
                continue
            flash_style = 1
            flash_coords.append((col, self.grid_pos[1], flash_style))

        return score, flash_coords

class Tomato(Ingredient):
    def __init__(self):
        description = '''+5 for every Cucumber directly on top or bottom'''
        super().__init__(name='tomato', description=description)

    def calculate_points(self, grid):
        flash_coords = []
        score = 0

        for rel_pos in (Vec2(0, -1), Vec2(0, 1)):
            pos = self.grid_pos + rel_pos
            item = grid.fetch_data(pos)
            if isinstance(item, Cucumber):
                score += 5
                i = 1
            else:
                i = 0
            flash_coords.append((pos[0], pos[1], i))
        return score, flash_coords

class Cucumber(Ingredient):
    def __init__(self):
        description = '''+5 for every Tomato directly on left or right'''
        super().__init__(name='cucumber', description=description)

    def calculate_points(self, grid):
        flash_coords = []
        score = 0
        for rel_pos in (Vec2(-1, 0), Vec2(1, 0)):
            pos = self.grid_pos + rel_pos
            item = grid.fetch_data(pos)
            if isinstance(item, Tomato):
                score += 5
                i = 1
            else:
                i = 0
            flash_coords.append((pos[0], pos[1], i))
        return score, flash_coords

class Chicken(Ingredient):
    def __init__(self):
        description = '''+5 for every adjacent and diagonal ingredient'''
        super().__init__(name='chicken', description=description)

    def calculate_points(self, grid):
        flash_coords = []
        score = 0
        for i in range(-1, 2):
            for j in range(-1, 2):
                if (i, j) == (0, 0): continue
                pos = self.grid_pos + Vec2(i, j)
                item = grid.fetch_data(pos)
                if item:
                    score += 5
                else:
                    pass
                flash_coords.append((pos[0], pos[1], i))
        return score, flash_coords

class Sauce(Ingredient):
    def __init__(self):
        description = '+15 For every adjacent chicken\n+0 For every adjacent Hot Sauce\n-15 For every adjacent other ingredient'
        super().__init__(name='sauce', description=description)

    @property
    def description_title(self):
        return 'Hot Sauce'

    def calculate_points(self, grid):
        flash_coords = []
        points = 0
        for offset in (
            (-1, 0),
            (1, 0),
            (0, -1),
            (0, 1),):
            adj_tile_coord = self.grid_pos + Vec2(offset)
            adj_tile = grid.fetch_data(adj_tile_coord)
            flash_coords.append((*adj_tile_coord, 1))
            if not adj_tile:
                continue
            elif isinstance(adj_tile, Sauce):
                pass
            elif isinstance(adj_tile, Chicken):
                points += 15
            else:
                points -= 15
        print(f'{flash_coords=}')
        return points, flash_coords

name_map = {
    'bread': Bread,
    'bagel': Bagel,
    'tomato': Tomato,
    'cucumber': Cucumber,
    'chicken': Chicken,
    'sauce': Sauce,
}
def init_from_name(name):
    return name_map[name]()
