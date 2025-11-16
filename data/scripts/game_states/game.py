import pygame
from .state import State
# from .menu import Menu
from ..button import Button
from ..animation import Animation
from ..entity import Entity
from ..config import CANVAS_SIZE
from .. import config
from ..config import COLORS
from ..font import FONTS
from ..timer import Timer
from ..utils import lerp
from ..ingredient import Ingredient


class Customer(Entity):

    ORDERS = (
        {
            'want': ((2, Ingredient('bread'), ), )
        },
    )
        
    DIALOGUES = (
        ('kid', 'Hello. May I please have a sandwhich, but without the filling'),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        n = int(self.name[-1])
        self.order = self.ORDERS[n]
        self.dialogue = self.DIALOGUES[n]
        self.dialogue_img = self.get_dialogue_img()
        self.showing_dialogue = False

    def get_dialogue_img(self):
        # s.fill((80, 80, 150))
        # s.fill(COLORS['dark gray'])
        # r = pygame.Rect(0, 0, *s.get_size())
        # r.x += 1
        # r.y += 1
        # r.w -= 2
        # r.h -= 2
        # pygame.draw.rect(s, COLORS['ground'], r, width=1)
        #
        txt_1 = f'{self.dialogue[1]}\n\nIngredients :'
        font_surf_1 = FONTS['basic'].get_surf(txt_1, wraplength=150, color=COLORS['black1'])

        txt_2 = 'Ingredients:'
        for quantity, ingredient in self.order['want']:
            txt_2 += f'\n{quantity}x {ingredient}'
        font_surf_2 = FONTS['basic'].get_surf(txt_2, wraplength=150, color=COLORS['blue1'])

        font_surf_2 = Ingredient.get_order_img(self.order)

        h = font_surf_1.get_height() + font_surf_2.get_height()
        s = pygame.Surface((154, h))
        s.fill(COLORS['white1'])
        s.blit(font_surf_1, (2, 2))
        s.blit(font_surf_2, (2, font_surf_1.get_height()))
        # pygame.draw.aaline(s, COLORS['white'], (0+4, 15), (150-4, 15))
        return s

    def show_dialogue(self):
        if self.showing_dialogue is False:
            self.showing_dialogue = True
            self.dialogue_timer = Timer(30)

    def update(self, *args, **kwargs):
        super().update(*args, **kwargs)
        if self.showing_dialogue:
            self.dialogue_timer.update()

    def render(self, surf):
        if self.showing_dialogue:
            ratio = self.dialogue_timer.easeOutElastic()
            dialogue_img = pygame.transform.scale(
                self.dialogue_img,
                (
                    self.dialogue_img.get_width() * (0.5 + 0.5 * ratio),
                    self.dialogue_img.get_height(),

                )
            )
            dialogue_pos = (CANVAS_SIZE[0] - 200, CANVAS_SIZE[1]*0.5 - 30)
            surf.blit(dialogue_img, dialogue_pos)
        return super().render(surf)


class Game(State):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        w, h = 100, 20
        self.btn_rect_center = pygame.Rect(CANVAS_SIZE[0]*0.5 - w * 0.5, 20, w, h)
        self.btn_rect = pygame.Rect(CANVAS_SIZE[0] - 200, 80, w, h)
        self.buttons = {
        }

        self.bg = Animation.img_db['bg']
        self.lvl = 0
        self.start_level()

    def start_level(self):
        self.lvl_start_timer = Timer(duration=30)
        self.customer = Customer(pos=(0, 0), name=f'customer_{self.lvl}', action='idle')
        self.customer.real_pos = [CANVAS_SIZE[0] * 0.5 - self.customer.img.get_width() * 0.5, CANVAS_SIZE[1]-self.customer.rect.h]
        self.START_POS = self.customer.real_pos.copy()


    def sub_update(self):
        canvas = self.handler.canvas
        self.handler.canvas.blit(self.bg, (0, 0))

        if self.lvl_start_timer.done:
            self.customer.show_dialogue()
            if self.customer.dialogue_timer.frame == 0:
                self.buttons['kitchen'] = Button(self.btn_rect, 'Go to kitchen', 'basic')
                self.buttons['kitchen'].alpha = 0

        else:
            # self.customer.real_pos[1] = lerp(self.customer.real_pos[1],
            #                                  CANVAS_SIZE[1]*0.5 - self.customer.rect.h*0.5,
            #                                  self.lvl_start_timer.get_ease_squared())

            self.customer.real_pos[1] = lerp(self.START_POS[1],
                                             CANVAS_SIZE[1]*0.5 - self.customer.rect.h*0.5,
                                             self.lvl_start_timer.get_ease_squared())

        self.customer.update()
        self.customer.render(canvas)



        # Update Buttons
        for key, btn in self.buttons.items():
            btn.update(self.handler.inputs)
            btn.render(self.handler.canvas)

            if key == 'kitchen':
                btn.alpha += 5

            if btn.clicked:
                if key == 'kitchen':
                    self.handler.transition_to(self.handler.states.Kitchen)
                    self.handler.lvl = self.lvl
                    self.handler.order = self.customer.order

        self.lvl_start_timer.update()
