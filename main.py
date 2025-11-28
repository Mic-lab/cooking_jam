# If you're looking over the code, just know it was made in a rush
# so it's probably not a good reference

import sys
import pygame
from pygame import Vector2 as Vec2
from data.scripts import sfx
from data.scripts import config
from data.scripts import utils
from data.scripts.mgl import shader_handler
from data.scripts import game_states
from data.scripts.transition import Transition, TransitionState
from data.scripts.animation import Animation

pygame.mouse.set_visible(False)
pygame.display.set_caption('Mealcraft')

class GameHandler:

    def __init__(self):
        self.states = game_states
        self.canvas = pygame.Surface(config.CANVAS_SIZE)
        self.clock = pygame.time.Clock()
        self.inputs = {'pressed': {}, 'released': {}, 'held': {}}
        self.pending_transition_durations = []
        self.start_lvl = 0
        if config.DEBUG:
            self.lvl = self.start_lvl
            self.set_state(self.states.Menu)
            # self.set_state(self.states.Game)
        else:
            self.lvl = self.start_lvl
            self.set_state(self.states.Menu)
        self.transition = Transition()
        shader_handler.vars['scale'] = config.scale

    def set_state(self, state):
        self.state = state(self)

    def set_transition_duration(self, duration):
        self.pending_transition_durations.append(duration)


    def transition_to(self, state):
        self.next_state = state
        self.transition.start()

    def handle_transition(self):
        switch = self.transition.update()
        if switch:
            self.set_state(self.next_state)
        shader_handler.vars['transitionTimer'] = self.transition.timer.get_ease_squared()
        shader_handler.vars['transitionState'] = self.transition.state
        if self.transition.state in {0, 1}:
            if len(self.pending_transition_durations) > 0:
                print('pop')
                self.transition = Transition(self.pending_transition_durations.pop(0))

    def handle_input(self):
        for key in self.inputs['pressed']:
            self.inputs['pressed'][key] = self.inputs['released'][key] = False

        mx, my = pygame.mouse.get_pos()
        self.inputs['mouse pos'] = (mx // config.scale, my // config.scale)
        self.inputs['unscaled mouse pos'] = mx, my

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                self.running = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                self.inputs['pressed'][f'mouse{event.button}'] = True
                self.inputs['held'][f'mouse{event.button}'] = True

            if event.type == pygame.MOUSEBUTTONUP:
                self.inputs['released'][f'mouse{event.button}'] = True
                self.inputs['held'][f'mouse{event.button}'] = False

            if event.type == pygame.KEYDOWN:
                key_name = pygame.key.name(event.key)
                self.inputs['pressed'][key_name] = True
                self.inputs['held'][key_name] = True

            if event.type == pygame.KEYUP:
                key_name = pygame.key.name(event.key)
                self.inputs['released'][key_name] = True
                self.inputs['held'][key_name] = False

    def run(self):
        self.running = True


        while self.running:
            self.handle_input()

            if self.transition.state != TransitionState.STARTING:
                self.state.update()

            self.handle_transition()

            shader_handler.surfs['canvasTex'] = self.canvas
            shader_handler.render()
            pygame.display.flip()
            shader_handler.release_textures()
            self.clock.tick(config.fps)

        pygame.quit()
        sys.exit()

GameHandler().run()
