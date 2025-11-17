import pygame
from pygame import Vector2 as Vec2
from .state import State
from ..button import Button
from ..animation import Animation
from .. import ingredient
from ..ingredient import Ingredient
from ..font import FONTS
from ..config import COLORS
from ..timer import Timer

class Grid:

    PAN = Vec2(1, 1)
    CELL_SIZE = 24
    CENTER_POS = Vec2(415, 110)

    cell_img = Animation.img_db['cell']

    def __init__(self, size):
        self.size = size
        self.data = [[None]*size[0] for _ in range(size[1])]
        self.gen_img()
        self.pos = Grid.CENTER_POS - 0.5*Vec2(self.bg_surf.get_size())
        self.points = 0

    def get_rect(self, col, row):
        return pygame.Rect(*(self.pos + 2*self.PAN + self.CELL_SIZE*Vec2(col, row)), self.CELL_SIZE, self.CELL_SIZE)

    def add_ingredient(self, ingredient, col, row):
        self.data[row][col] = ingredient
        self.calculate_points()

    def remove_ingredient(self, ingredient):
        if ingredient.grid_pos is None:
            return
        ingredient.set_points(0)
        col, row = ingredient.grid_pos
        self.data[row][col] = None
        ingredient.grid_pos = None
        self.calculate_points()
    
    def gen_img(self):
        surf = pygame.Surface(self.CELL_SIZE * Vec2(self.size) + 4*self.PAN)  # idk didnt think about the pan too much
        surf.set_colorkey((0, 0, 0))
        for row in range(self.size[1]):
            for col in range(self.size[0]):
                pos = self.CELL_SIZE * Vec2(col, row) + self.PAN
                surf.blit(self.cell_img, pos)
        self.bg_surf = surf

    def calculate_points(self):
        print('Calculating points')
        points = 0
        for row in self.data:
            for ing in row:
                if ing:
                    ing.set_points(ing.calculate_points(self))
                    points += ing.points
        self.points = points
        print(f'{points=}')

    def render(self, surf):
        surf.blit(self.bg_surf, self.pos)

class Kitchen(State):

    GRID_SIZES = (
        (3, 3),
    )

    INGREDIENTS = (
        (ingredient.Bread(), ingredient.Bread()),
        # (Ingredient('bread'), Ingredient('bread'), Ingredient('tomato')),

    )

    INGREDIENT_BASE_POS = Vec2(200, 50)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bg = Animation.img_db['kitchen_bg']
       
        rects = [pygame.Rect(300, 150+i*30, 80, 20) for i in range(4)]
        self.btn_rect = pygame.Rect(400, 200, 80, 20)
        self.buttons = {
        }
        self.lvl = self.handler.lvl
        self.order = self.handler.order
        self.needed_points = self.order['points']
        self.get_order_img()

        self.win = False
        self.win_timer = Timer(20)
        self.points = 0
        self.generate_point_surf()
        self.grid = Grid(self.GRID_SIZES[self.lvl])

        self.selected_ingredient = None
        self.saved_hovered_ingredient = None

        self.hover_timer = Timer(duration=10)

        # Generate ingredient data ---------------
        self.ingredient_dict = {}
        for lvl in range(self.lvl + 1):
            for ing in self.INGREDIENTS[lvl]:
                name = ing.name
                self.ingredient_dict[name] = self.ingredient_dict.get(name, 0) + 1

        self.ingredients = []
        for row, (ingredient_name, quantity) in enumerate(self.ingredient_dict.items()):
            for i in range(quantity):
                pos = self.INGREDIENT_BASE_POS + Vec2(0, 25) * row + Vec2(25, 0) * i
                ing = ingredient.init_from_name(ingredient_name)
                ing.real_pos = pos
                self.ingredients.append(
                    ing
                )

    def get_order_img(self):
        self.order_img = Ingredient.get_order_img(self.order)

    def sub_update(self):
        canvas = self.handler.canvas
        self.handler.canvas.blit(self.bg)
        canvas.blit(self.order_img, (10, 50))

        self.grid.render(canvas)

        # for row in range(self.grid.size[1]):
        #     for col in range(self.grid.size[0]):
        #         r = self.grid.get_rect(col, row)
        #         from random import randint
        #         pygame.draw.rect(canvas, (30, 30, randint(1, 255)), r)

        hovered_ingredient = None
        for ing in self.ingredients:
            ing.update(self.handler.inputs, self.grid, self.selected_ingredient)
            if ing.selected:
                self.selected_ingredient = ing
                if ing.hovered_cell:
                    hovered_cell = ing.hovered_cell
                    rect = hovered_cell[2]
                    color = COLORS['blue4'] if hovered_cell[3] else (100, 0, 0, 100)
                    s = pygame.Surface(rect.size)
                    s.fill(color)
                    s.set_alpha(70)
                    canvas.blit(s, rect.topleft)
            elif ing is self.selected_ingredient:
                self.selected_ingredient = None

            if ing.rect.collidepoint(self.handler.inputs['mouse pos']):
                hovered_ingredient = ing
                self.saved_hovered_ingredient = ing

            ing.render(canvas)

        if self.saved_hovered_ingredient:
            if hovered_ingredient and hovered_ingredient is not self.selected_ingredient:
                self.hover_timer.frame += 1
            else:
                self.hover_timer.frame -= 1
            self.hover_timer.frame = max(min(self.hover_timer.frame, self.hover_timer.duration), 0)
            self.hover_timer.done = self.hover_timer.duration == 1
            self.saved_hovered_ingredient.description_surf.set_alpha(self.hover_timer.ratio * 255)
            canvas.blit(
                self.saved_hovered_ingredient.description_surf,
                self.handler.inputs['mouse pos'] - 1*Vec2(Ingredient.DESCRIPTION_SURF_W, 0)
            )

        
        if self.points != self.grid.points:
            self.points = self.grid.points
            self.win = self.points >= self.needed_points
            if self.win:
                self.buttons['back'] = Button(self.btn_rect, 'Finish', 'basic')
            self.generate_point_surf()
        canvas.blit(self.point_surf, (408, 34))

        alpha = self.win_timer.ratio * 255
        if self.win:
            self.buttons['back'].alpha = alpha
            if alpha != 255:
                self.win_timer.frame += 1
        else:
            if alpha != 0:
                self.win_timer.frame -= 1
                self.buttons['back'].alpha = alpha
            else:
                if 'back' in self.buttons:
                    del self.buttons['back']

        # Update Buttons
        for key, btn in self.buttons.items():
            btn.update(self.handler.inputs)
            btn.render(self.handler.canvas)

            if btn.clicked:
                if key == 'back':
                    self.handler.transition_to(self.handler.states.Game)
                    self.handler.lvl += 1

    def generate_point_surf(self):
        color = COLORS['blue1'] if self.win else COLORS['red2']
        surf = FONTS['basic'].get_surf(f'Score : {self.points} / {self.needed_points}', color)
        self.point_surf = surf
