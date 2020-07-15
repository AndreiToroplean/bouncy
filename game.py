import pygame as pg
import numpy as np

from ball import Ball
from camera import Camera
from global_params import WHITE, FPS, N_PHYSICS_SUBSTEPS, INPUT_DERIVATIVE, DEBUG


class Game:
    def __init__(self):
        pg.init()
        pg.mouse.set_visible(False)

        self.camera = Camera()

        self.len_der = INPUT_DERIVATIVE
        self.input_action_value = 1000.0 / (FPS * N_PHYSICS_SUBSTEPS) ** self.len_der
        self.input_action = np.array((0.0, 0.0))

        self.ball = Ball(
            init_w_pos=np.array((0.0, 0.0)),

            len_der=self.len_der,

            radius=20,
            restitution=0.75,

            color=WHITE
            )

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pg.quit()

    def main_loop(self):
        while True:
            # Inputs
            keys_pressed = pg.key.get_pressed()

            if keys_pressed[pg.K_ESCAPE] or pg.event.peek(pg.QUIT):
                return

            is_moving_horiz = False
            if keys_pressed[pg.K_LEFT]:
                self.input_action[0] = -self.input_action_value
                is_moving_horiz ^= True
            if keys_pressed[pg.K_RIGHT]:
                self.input_action[0] = self.input_action_value
                is_moving_horiz ^= True
            if not is_moving_horiz:
                self.input_action[0] = 0.0

            is_moving_vert = False
            if keys_pressed[pg.K_DOWN]:
                self.input_action[1] = -self.input_action_value
                is_moving_vert ^= True
            if keys_pressed[pg.K_UP]:
                self.input_action[1] = self.input_action_value
                is_moving_vert ^= True
            if not is_moving_vert:
                self.input_action[1] = 0.0

            # Logic
            self.ball.run_physics(self.input_action)
            self.camera.req_move(self.ball.w_pos)

            # Graphics
            self.camera.empty_screen()

            self.camera.draw(self.ball)

            if DEBUG:
                self.camera.draw_debug_info()

            self.camera.flip_display_and_tick()
