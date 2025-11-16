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

class Menu(State):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        rects = [pygame.Rect(30, 30+i*30, 110, 20) for i in range(6)]
        self.buttons = {
            'game': Button(rects[0], 'harloo', 'basic'),
            'scale': Button(rects[1], f'Window Scale ({config.scale}x)', 'basic'),
        }
        self.surf = Entity((0, 0), 'test')
        self.entity = PhysicsEntity(pos=(150, 30), name='side', action='idle')
        self.e_speed = 1.5
        self.timer = None
        self.particle_gens = [ParticleGenerator.from_template((200, 200), 'angle test'),
                              ParticleGenerator.from_template((300, 200), 'color test')]

    def sub_update(self):

        if self.timer:
            if self.timer.done:
                self.timer = None
            else:
                self.timer.update()

        if self.handler.inputs['pressed'].get('mouse3'):
            self.timer = Timer(60)

        self.handler.canvas.fill((20, 20, 20))

        self.surf.real_pos = self.handler.inputs['mouse pos']
        self.surf.render(self.handler.canvas)
        # self.handler.canvas.blit(self.surf, self.handler.inputs['mouse pos'])

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
                    self.handler.transition_to(self.handler.states.Game)
                elif key == 'music 1':
                    sfx.play_music('song_1.wav', -1)
                elif key == 'music 2':
                    sfx.play_music('song_2.wav')
                elif key == 'stop':
                    pygame.mixer.music.fadeout(1000)
                elif key == 'scale':
                    config.scale = (config.scale + 1) % 5
                    if config.scale == 0: config.scale = 1
                    config.SCREEN_SIZE = config.scale*config.CANVAS_SIZE[0], config.scale*config.CANVAS_SIZE[1]
                    screen.screen = screen.create_screen()
                    shader_handler.ctx.viewport = (0, 0, config.SCREEN_SIZE[0], config.SCREEN_SIZE[1])
                    btn.text = f'Window Scale ({config.scale}x)'
                    shader_handler.vars['scale'] = config.scale

        self.entity.vel = [0, 0]
        if self.handler.inputs['held'].get('a'):
            self.entity.vel[0] -= self.e_speed
            self.entity.animation.flip[0] = True
        elif self.handler.inputs['held'].get('d'):
            self.entity.vel[0] += self.e_speed
            self.entity.animation.flip[0] = False
        if self.handler.inputs['held'].get('w'):
            self.entity.vel[1] -= self.e_speed
        elif self.handler.inputs['held'].get('s'):
            self.entity.vel[1] += self.e_speed

        if any(self.entity.vel):
            self.entity.animation.set_action('run')
        else:
            self.entity.animation.set_action('idle')

        self.entity.update([btn.rect for btn in self.buttons.values()])
        self.entity.render(self.handler.canvas)

        text = [f'{round(self.handler.clock.get_fps())} fps',
                f'vel = {self.entity.vel}',
                # pprint.pformat(Particle.cache)
                ]
        self.handler.canvas.blit(FONTS['basic'].get_surf('\n'.join(text)), (0, 0))

        # shader_handler.vars['shakeTimer'] = -1 if not self.timer else self.timer.ratio ** 2
        shader_handler.vars['caTimer'] = -1 if not self.timer else self.timer.ratio ** 2
