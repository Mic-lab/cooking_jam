import sys
import pygame
from pygame import Vector2 as Vec2
from data.scripts import config
from data.scripts import utils
from data.scripts.mgl import shader_handler
from data.scripts import game_states
from data.scripts.transition import Transition, TransitionState
from data.scripts.animation import Animation

pygame.mouse.set_visible(False)

class GameHandler:

    def __init__(self):
        self.states = game_states
        self.canvas = pygame.Surface(config.CANVAS_SIZE)
        self.clock = pygame.time.Clock()
        self.inputs = {'pressed': {}, 'released': {}, 'held': {}}
        self.lvl = 0
        self.lvl = 4
        self.set_state(self.states.Menu)
        # self.set_state(self.states.Game)
        self.transition = Transition()
        shader_handler.vars['scale'] = config.scale

    def set_state(self, state):
        self.state = state(self)

    def transition_to(self, state):
        self.next_state = state
        self.transition.start()

    def handle_transition(self):
        switch = self.transition.update()
        if switch:
            self.set_state(self.next_state)
        shader_handler.vars['transitionTimer'] = self.transition.timer.get_ease_squared()
        shader_handler.vars['transitionState'] = self.transition.state

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

        self.mouse_img = (Animation.img_db['mouse_1'], Animation.img_db['mouse_2'])

        while self.running:
            self.handle_input()

            if self.transition.state != TransitionState.STARTING:
                self.state.update()

            i = 1 if self.inputs['held'].get('mouse1') else 0
            self.canvas.blit(self.mouse_img[i], self.inputs['mouse pos'] - Vec2(4, 0))


            self.handle_transition()

            shader_handler.surfs['canvasTex'] = self.canvas
            shader_handler.render()
            pygame.display.flip()
            shader_handler.release_textures()
            self.clock.tick(config.fps)

        pygame.quit()
        sys.exit()

GameHandler().run()
