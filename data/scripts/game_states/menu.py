from .state import State
from ..mgl import shader_handler
from ..import utils
from ..button import Button
from ..font import FONTS
from ..import animation
from ..entity import Entity, PhysicsEntity
from ..timer import Timer
from ..particle import Particle, ParticleGenerator
from .. import sfx
from .. import screen, config
import pygame

class TextBox:

    ACCEPTED_KEYS = set('1234567890qwertyuiopasdfghjklzxcvbnm') | {'space'}

    def __init__(self, pos, text='', max_size=16):
        self.pos = pos
        self.text = text
        self.max_size = max_size

    def update(self, inputs):
        if inputs['pressed'].get('backspace'):
            self.text = self.text[:-1]

        if len(self.text) <= self.max_size:
            for key, pressed in inputs['pressed'].items():
                if pressed and key in TextBox.ACCEPTED_KEYS:
                    if key == 'space': key = ' '
                    elif inputs['held'].get('left shift'): key = key.upper()
                    self.text += key
                    break  # NOTE: cant press multiple keys in the same frame

    def update_surf(self):
        font_surf = FONTS['basic'].get_surf(self.text, color=config.COLORS['blue4'])
        self.surf = pygame.Surface(font_surf.get_size(), pygame.SRCALPHA)
        # self.surf.fill((0, 0, 0, 100))
        self.surf.blit(font_surf)

    def render(self, surf):
        surf.blit(self.surf, self.pos)

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, new_text):
        self._text = new_text
        self.update_surf()

class Menu(State):

    NAME_POS = pygame.Vector2(292, 90)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        rects = [pygame.Rect(30, 30+i*30, 110, 20) for i in range(6)]
        self.buttons = {
            'game': Button(rects[0], 'harloo', 'basic'),
            'scale': Button(rects[1], f'Window Scale ({config.scale}x)', 'basic'),
        }
        self.name_surf = FONTS['basic'].get_surf('Enter your name > ')
        self.text_box = TextBox(Menu.NAME_POS + (90, 0))
        self.particle_gens = [ParticleGenerator.from_template((200, 200), 'angle test'),
                              ParticleGenerator.from_template((300, 200), 'color test')]
        self.particle_gens = []

    def sub_update(self):
        self.handler.canvas.blit(
            animation.Animation.img_db['menu']
        )
        self.handler.canvas.blit(self.name_surf, Menu.NAME_POS)
        self.text_box.update(self.handler.inputs)
        self.text_box.render(self.handler.canvas)


        if self.handler.inputs['pressed'].get('mouse1'):
            self.particle_gens.append(ParticleGenerator.from_template(self.handler.inputs['mouse pos'], 'smoke'))

        self.particle_gens = ParticleGenerator.update_generators(self.particle_gens)
        for particle_gen in self.particle_gens:
            particle_gen.render(self.handler.canvas)

        self.handler.canvas.set_at(self.handler.inputs['mouse pos'], (255, 0, 0))

        # Update Buttons
        for key, btn in self.buttons.items():
            btn.update(self.handler.inputs)
            btn.render(self.handler.canvas)

            if btn.clicked:
                if key == 'game':
                    name = self.text_box.text.strip()
                    if not name: name = 'Bob'
                    self.handler.name = name
                    # self.handler.transition_to(self.handler.states.Game)
                    if config.DEBUG:
                        self.handler.transition_to(self.handler.states.Game)
                    else:
                        self.handler.transition_to(self.handler.states.Intro)
                    # pygame.mixer.music.set_volume(0.2)
                    # sfx.play_music('song_1.wav', -1)
                elif key == 'scale':
                    config.scale = (config.scale + 1) % 5
                    if config.scale == 0: config.scale = 1
                    config.SCREEN_SIZE = config.scale*config.CANVAS_SIZE[0], config.scale*config.CANVAS_SIZE[1]
                    screen.screen = screen.create_screen()
                    shader_handler.ctx.viewport = (0, 0, config.SCREEN_SIZE[0], config.SCREEN_SIZE[1])
                    btn.text = f'Window Scale ({config.scale}x)'
                    shader_handler.vars['scale'] = config.scale

        text = [f'{round(self.handler.clock.get_fps())} fps',
                ]
        self.handler.canvas.blit(FONTS['basic'].get_surf('\n'.join(text)), (0, 0))
