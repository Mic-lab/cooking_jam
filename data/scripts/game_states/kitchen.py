import pygame
from pygame import Vector2 as Vec2
from .state import State
from ..button import Button
from ..animation import Animation
from ..ingredient import Ingredient

class Grid:

    PAN = Vec2(1, 1)
    CELL_SIZE = 24
    CENTER_POS = Vec2(400, 80)

    cell_img = Animation.img_db['cell']

    def __init__(self, size):
        self.size = size
        self.data = [[None]*size[0] for _ in range(size[1])]
        self.gen_img()
        self.pos = Grid.CENTER_POS
    
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

    def get_order_img(self):
        self.order_img = Ingredient.get_order_img(self.order)

    def sub_update(self):
        canvas = self.handler.canvas
        self.handler.canvas.blit(self.bg)
        canvas.blit(self.order_img, (10, 50))

        self.grid.render(canvas)

        # Update Buttons
        for key, btn in self.buttons.items():
            btn.update(self.handler.inputs)
            btn.render(self.handler.canvas)

            if btn.clicked:
                if key == 'back':
                    self.handler.transition_to(self.handler.states.Game)
