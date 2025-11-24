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
from ..transition import Transition
import pygame
from pygame import Vector2 as Vec2

class Intro(State):


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        rects = [pygame.Rect(30, 30+i*30, 110, 20) for i in range(6)]
        self.buttons = {
        }
        self.particle_gens = []
        self.txt_surf = FONTS['basic'].get_surf('You only have 1 customer.')
        self.timer = Timer(60)
        self.done = False
        self.handler.set_transition_duration(90)

    def sub_update(self):
        self.handler.canvas.fill(config.COLORS['super black'])
        pos = Vec2(config.CANVAS_SIZE) * 0.5 - Vec2(self.txt_surf.get_size()) * 0.5
        self.handler.canvas.blit(self.txt_surf, pos)

        self.particle_gens = ParticleGenerator.update_generators(self.particle_gens)
        for particle_gen in self.particle_gens:
            particle_gen.render(self.handler.canvas)

        # Update Buttons
        for key, btn in self.buttons.items():
            btn.update(self.handler.inputs)
            btn.render(self.handler.canvas)

            if btn.clicked:
                if key == 'game':
                    self.handler.transition_to(self.handler.states.Game)

        if self.timer.done and not self.done:
            self.done = True
            self.handler.transition_to(self.handler.states.Game)
        self.timer.update()
