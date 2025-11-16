import pygame
from pygame import Vector2 as Vec2
from .state import State
from ..button import Button
from ..animation import Animation
from ..ingredient import Ingredient
from ..config import COLORS

class Grid:

    PAN = Vec2(1, 1)
    CELL_SIZE = 24
    CENTER_POS = Vec2(400, 80)

    cell_img = Animation.img_db['cell']

    def __init__(self, size):
        self.size = size
        self.data = [[None]*size[0] for _ in range(size[1])]
        self.gen_img()
        self.pos = Grid.CENTER_POS - 0.5*Vec2(self.bg_surf.get_size())

    def get_rect(self, col, row):
        return pygame.Rect(*(self.pos + 2*self.PAN + self.CELL_SIZE*Vec2(col, row)), self.CELL_SIZE, self.CELL_SIZE)

    def add_ingredient(self, ingredient, col, row):
        self.data[row][col] = ingredient

    def remove_ingredient(self, ingredient):
        if ingredient.grid_pos is None:
            return
        col, row = ingredient.grid_pos
        self.data[row][col] = None
        ingredient.grid_pos = None
    
    def gen_img(self):
        surf = pygame.Surface(self.CELL_SIZE * Vec2(self.size) + 4*self.PAN)  # idk didnt think about the pan too much
        surf.set_colorkey((0, 0, 0))
        for row in range(self.size[1]):
            for col in range(self.size[0]):
                pos = self.CELL_SIZE * Vec2(col, row) + self.PAN
                surf.blit(self.cell_img, pos)
        self.bg_surf = surf

    def render(self, surf):
        surf.blit(self.bg_surf, self.pos)

class Kitchen(State):

    GRID_SIZES = (
        (3, 3),
    )

    INGREDIENTS = (
        (Ingredient('bread'), Ingredient('bread'), Ingredient('tomato')),

    )

    INGREDIENT_BASE_POS = Vec2(200, 50)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bg = Animation.img_db['kitchen_bg']
       
        rects = [pygame.Rect(300, 150+i*30, 80, 20) for i in range(4)]
        self.buttons = {
            'back': Button(rects[0], 'Restaurant', 'basic'),
        }
        self.lvl = self.handler.lvl
        self.order = self.handler.order
        self.get_order_img()

        self.grid = Grid(self.GRID_SIZES[self.lvl])

        self.selected_ingredient = None

        # Generate ingredient data ---------------
        self.ingredient_dict = {}
        for lvl in range(self.lvl + 1):
            for ingredient in self.INGREDIENTS[lvl]:
                name = ingredient.name
                self.ingredient_dict[name] = self.ingredient_dict.get(name, 0) + 1

        print(f'{self.ingredient_dict=}')

        self.ingredients = []
        for row, (ingredient_name, quantity) in enumerate(self.ingredient_dict.items()):
            for i in range(quantity):
                pos = self.INGREDIENT_BASE_POS + Vec2(0, 25) * row + Vec2(25, 0) * i
                ingredient = Ingredient(ingredient_name)
                ingredient.real_pos = pos
                self.ingredients.append(
                    ingredient
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


        for ingredient in self.ingredients:
            ingredient.update(self.handler.inputs, self.grid, self.selected_ingredient)
            if ingredient.selected:
                self.selected_ingredient = ingredient
            elif ingredient is self.selected_ingredient:
                self.selected_ingredient = None

            if ingredient.hovered_cell:
                hovered_cell = ingredient.hovered_cell
                rect = hovered_cell[2]
                color = COLORS['blue4'] if hovered_cell[3] else (100, 0, 0, 100)
                s = pygame.Surface(rect.size)
                s.fill(color)
                s.set_alpha(70)
                canvas.blit(s, rect.topleft)

            ingredient.render(canvas)


        # Update Buttons
        for key, btn in self.buttons.items():
            btn.update(self.handler.inputs)
            btn.render(self.handler.canvas)

            if btn.clicked:
                if key == 'back':
                    self.handler.transition_to(self.handler.states.Game)
