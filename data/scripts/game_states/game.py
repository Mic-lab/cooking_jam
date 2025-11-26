import pygame
from pygame import Vector2 as Vec2
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
from .. import ingredient
from ..transition import Transition
from .. import sfx


class Customer(Entity):

    ORDERS = (
        {
            'want': ((2, ingredient.Bread()), ),
            'points': 30,
        },
        {
            'want': ((2, ingredient.Bread()), (2, ingredient.Bagel()), ),
            'points': 40,
        },
        {
            'want': ((2, ingredient.Bagel()),
                     (2, ingredient.Tomato()),
                     (2, ingredient.Cucumber())),
            'points': 40,
        },
        {
            'want': (
                (3, ingredient.Bread()),
                (3, ingredient.Cucumber()),
                (3, ingredient.Tomato()),
            ),
            'points': 125,
        },
        {
            'want': ((3, ingredient.Bagel()), ),
            'points': 65,
        },

        {
            'want': ((1, ingredient.Chicken()), ),
            'points': 25,
        },
        {
            'want': (
                (2, ingredient.Bagel()),
                (2, ingredient.Bread()),
                (1, ingredient.Chicken()),
            ),
            'points': 110,
        },
        {
            'want': (
                (1, ingredient.Chicken()),
                (1, ingredient.Sauce())),
            'points': 50,
        },

        {
            'want': (
                (1, ingredient.Sauce()),
                (1, ingredient.Chicken()),
                (2, ingredient.Cucumber()),
                (1, ingredient.Tomato()),
            ),
            'points': 45,
        },
        {
            'want': (
                (3, ingredient.Sauce()),
                (2, ingredient.Chicken()),
            ),
            'points': 195,
        },
        {
            'want': (
                (2, ingredient.Bagel()),
                (1, ingredient.Chicken()),
                (1, ingredient.Sauce()),
            ),
            'points': 55,
        },
        {
            'want': (
                (2, ingredient.Sauce()),
                (2, ingredient.Chicken()),
            ),
            'points': 140,
        },
        {
            'want': (
                (1, ingredient.Sauce()),
                (4, ingredient.Bagel()),
                (4, ingredient.Chicken()),
                (4, ingredient.Bagel()),
            ),
            'points': 340,
        },
        # {
        #     'want': (),
        #     'points': -1,
        # },




    )
        

    def __init__(self, username, *args, **kwargs):

        self.DIALOGUES = (
            ('John Smith', 'Hello. May I please have a sandwhich, but without the filling? Also, don\'t forget to hover your mouse over the ingredients to view their description.',
             'Exactly as I asked for. Thanks!'),
            ('Bob', 'Hi, I\'d like a sandwhich bagel (not to be confused with a bagel sandwhich)',
             'Oh yeah, that\'s the stuff'),
            ('Bob', 'I\'m feeling a bit spicy today. I\'ll have vegetable bagel.',
             'It\'s overflowing... but that\'s ok'),
            ('Bob', 'Now take everything you\'ve learnt to make me the ultimate sandwhich.',
             'Alternating the tomato\'s and cucumbers I see. I like it.'),
            ('Bob', 'I\'ll have a Double Triple Bossy Deluxe on a raft, 4x4 animal style, extra shingles with a shimmy and a squeeze, light axle grease, make it cry, burn it, and let it swim',
             'Acceptable.'),
            ('Bob', 'I\'ll try a caesar salad now',
             'I\'m so healthy B)'),
            ('Bob', 'I didn\'t know you had chicken. In that case, I\'ll take a chicken bagel sandwhich.',
             'Wow. Beautiful assortment.'),
            ('Bob', 'Now I\'m *actually* feeling spicy. So give me hawwt sauce! And pair that with chicken.',
             'This one\'s on on the house ;)\nOh wait you\'re supposed to say that.'),
            ('Bob', 'Maybe sprinkle some vegetables in there.\nSorry, I should\'ve told you in advance hihi',
             'Mmmm, just like how my mom\'s son used to make it.'),
            ('Bob', 'Now make me a chicken sandwhich. Please.',
             'It\'s a bit too spicy, but thanks I guess. *tsundere hmph*'),
            ('Bob', 'Make a chicken bagel, but please don\'t make don\'t make the bagel soggy.',
             'You made half of the bagel float. How sophisticated :O'),
            ('Bob', 'I\'m starting to get kind of stuffed, I\'ll just have a small bowl of stir-fry',
             'I wouldn\'t consider that a small bowl, but not gonna gonna complain about free food.'),
            ('Bob', 'I finally finished the stir-fry. Oh, how did I eat it so fast? Oh, you know... I just put it in my belly. Anyways, I\'m super stuffed now. So I won\'t be having anything. Wait why does it say "Ingredients" underneath? *gulp*',
             f'>_< That\'s way too much. It will take me some time to finish this. But I will always be your number 1 customer, {username}.'),
            ('Bob', 'Place holder',
             'Thanks'),
            ('Bob', 'Place holder',
             'Thanks'),
            ('Bob', 'Place holder',
             'Thanks'),
            ('Bob', 'Place holder',
             'Thanks'),
        )








        name = kwargs['name']
        n = int(name.split('_')[-1])
        kwargs['name'] = 'customer_0'
        super().__init__(*args, **kwargs)
        self.order = self.ORDERS[n]
        print(f'{n=}')
        self.dialogue = self.DIALOGUES[n]
        self.dialogue_img = self.get_dialogue_img()
        self.dialogue_img_2 = self.get_dialogue_img_2()
        self.showing_dialogue = False

        self.username = username

        name_surf = FONTS['basic'].get_surf(f'{self.username}\'s #1 customer', COLORS['white2'])
        self.name_surf = pygame.Surface(name_surf.get_size(), pygame.SRCALPHA)
        self.name_surf.fill((0, 0, 0, 100))
        self.name_surf.blit(name_surf)



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

    def get_dialogue_img_2(self):
        txt_1 = f'{self.dialogue[2]}'
        font_surf_1 = FONTS['basic'].get_surf(txt_1, wraplength=150, color=COLORS['black1'])

        h = font_surf_1.get_height()
        s = pygame.Surface((154, h+4))
        s.fill(COLORS['white1'])
        s.blit(font_surf_1, (2, 2))
        return s

    def show_dialogue(self, done=False):
        self.done = done
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
            og_img = self.dialogue_img_2 if self.done else self.dialogue_img
            dialogue_img = pygame.transform.scale(
                og_img,
                (
                    og_img.get_width() * (0.5 + 0.5 * ratio),
                    og_img.get_height(),

                )
            )
            dialogue_pos = (CANVAS_SIZE[0] - 200, CANVAS_SIZE[1]*0.5 - 30)
            dialogue_pos = (self.rect.topleft + Vec2(80, 0))
            surf.blit(dialogue_img, dialogue_pos)

        super().render(surf)
        surf.blit(self.name_surf,
                  (self.rect.centerx - self.name_surf.get_width()*0.5,
                   self.rect.top - 14))


class Game(State):

    def __init__(self, *args, **kwargs):
        pygame.mixer.music.set_volume(0.2)

        super().__init__(*args, **kwargs)

        self.username = self.handler.name

        w, h = 100, 20
        self.btn_rect_center = pygame.Rect(CANVAS_SIZE[0]*0.5 - w * 0.5, 20, w, h)
        self.btn_rect = pygame.Rect(CANVAS_SIZE[0] - 200, 80, w, h)
        self.buttons = {
        }

        self.bg = Animation.img_db['bg']
        self.lvl = self.handler.lvl
        self.lvl_start_timer = Timer(60, done=True)
        self.stall_timer = Timer(60, done=True)
        
        if self.lvl is None:
            self.lvl_surf = FONTS['basic'].get_surf(f'')
        else:
            self.lvl_surf = FONTS['basic'].get_surf(f'Level {self.lvl+1} / {len(Customer.ORDERS)}')

        if config.DEBUG and 0:
            self.lvl_start_timer = Timer(5, done=True)
            self.lvl_end_timer = Timer(5, done=True)

        if self.lvl == self.handler.start_lvl:
            self.start_level()
            pygame.mixer.music.set_volume(0.2)
            sfx.play_music('song_1.wav', -1)
        else:
            self.end_level()


        self.handler.set_transition_duration(None)

    def get_start_pos(self):
        return [CANVAS_SIZE[0] * 0.5 - self.customer.img.get_width() * 0.5, CANVAS_SIZE[1]]
        # return [CANVAS_SIZE[0] * 0.5 - self.customer.img.get_width() * 0.5, CANVAS_SIZE[1]-self.customer.rect.h]

    def get_end_pos_y(self):
        return CANVAS_SIZE[1]*0.5 - self.customer.rect.h*0.5

    def end_level(self):
        self.leaving = True
        if self.lvl is None:
            self.customer = None
            self.done_timer = Timer(120)
            self.done_img = Animation.img_db['done']
            pygame.mixer.music.set_volume(0.3)
            sfx.play_music('ggs.wav')
            return
        else:
            name = f'customer_{self.lvl - 1}'
        self.customer = Customer(username=self.username, pos=(0, 0), name=name, action='idle')
        self.customer.real_pos = self.get_start_pos()
        self.customer.real_pos[1] = self.get_end_pos_y()
        self.start_pos = self.customer.real_pos.copy()

        self.customer.show_dialogue(done=True)

        words = len(self.customer.dialogue[2].split())
        print(f'{words=}')
        self.lvl_end_timer = Timer(30 + 15 * words, done=True)
        self.lvl_end_timer.reset()

    def start_level(self):
        print(f'start_level {self.lvl}')
        if self.lvl == len(Customer.ORDERS):
            self.handler.lvl = None
            self.handler.transition_to(self.handler.states.Intro)
            return
        self.leaving = False
        self.lvl_start_timer.reset()
        name = f'customer_{self.lvl}'
        print(f'{name=}')
        self.customer = Customer(username=self.username, pos=(0, 0), name=name, action='idle')
        self.customer.real_pos = self.get_start_pos()
        self.start_pos = self.customer.real_pos.copy()


    def sub_update(self):
        canvas = self.handler.canvas
        self.handler.canvas.blit(self.bg, (0, 0))

        if self.customer is None:
            pass
        elif self.leaving:
            if not self.lvl_end_timer.done:
                self.customer.real_pos[1] = lerp(self.start_pos[1],
                                                 self.get_start_pos()[1],
                                                 self.lvl_end_timer.weird_ease() * self.lvl_end_timer.ratio**10)
                                                 # self.lvl_end_timer.get_ease_in_out_sin() * self.lvl_end_timer.ratio**10)
            else:
                self.stall_timer.reset()
                self.start_level()
            self.lvl_end_timer.update()
        else:

            if self.lvl_start_timer.done:
                self.customer.show_dialogue()
                if self.customer.dialogue_timer.frame == 0:
                    self.buttons['kitchen'] = Button(self.btn_rect, 'Go to kitchen', 'basic')
                    self.buttons['kitchen'].alpha = 0

            else:
                # self.customer.real_pos[1] = lerp(self.customer.real_pos[1],
                #                                  CANVAS_SIZE[1]*0.5 - self.customer.rect.h*0.5,
                #                                  self.lvl_start_timer.get_ease_squared())

                self.customer.real_pos[1] = lerp(self.start_pos[1],
                                                 self.get_end_pos_y(),
                                                 self.lvl_start_timer.get_ease_in_out_sin())

        if self.customer:
            self.customer.update()
            self.customer.render(canvas)
        else:
            self.done_img.set_alpha(self.done_timer.ratio*255)
            self.handler.canvas.blit(self.done_img, (200, 60))
            self.done_timer.update()

        canvas.blit(self.lvl_surf, (CANVAS_SIZE[0]*0.5-self.lvl_surf.get_width()*0.5, 5))

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
