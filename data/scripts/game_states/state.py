from abc import abstractmethod
from ..animation import Animation
from pygame import Vector2 as Vec2

class State:

    def __init__(self, game_handler):
        self.handler = game_handler
        self.mouse_img = (Animation.img_db['mouse_1'], Animation.img_db['mouse_2'])

    def update(self):
        self.sub_update()

        i = 1 if self.handler.inputs['held'].get('mouse1') else 0
        self.handler.canvas.blit(self.mouse_img[i], self.handler.inputs['mouse pos'] - Vec2(4, 0))

    @abstractmethod
    def sub_update(self):
        pass
