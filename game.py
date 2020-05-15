import pygame as pg
import numpy as np

from ball import Ball
from global_params import BLACK, WHITE, FPS, PHYSICS_SUBSTEPS, INPUT_DERIVATIVE, FULL_SCREEN, DEBUG


class Game:
    def __init__(self):
        pg.init()
        if FULL_SCREEN:
            self.screen = pg.display.set_mode((0, 0), pg.FULLSCREEN)
        else:
            self.screen = pg.display.set_mode((800, 600))
        self.screen_rect = self.screen.get_rect()
        self.clock = pg.time.Clock()
        self.font = pg.font.SysFont(pg.font.get_default_font(), 24)

        self.len_der = INPUT_DERIVATIVE
        self.input_action_value = 1000.0 / (FPS * PHYSICS_SUBSTEPS) ** self.len_der
        self.input_action = np.array((0.0, 0.0))

        self.ball = Ball(
            init_pos=np.array(self.screen_rect.center, dtype=np.float64),

            len_der=self.len_der,

            env_bbox=self.screen_rect,

            radius=20,
            restitution=0.95,

            color=WHITE
            )

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pg.quit()

    def main_loop(self):
        while True:
            # Inputs
            for event in pg.event.get():
                if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE or event.type == pg.QUIT:
                    return

                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_LEFT:
                        self.input_action[0] = -self.input_action_value
                    if event.key == pg.K_RIGHT:
                        self.input_action[0] = self.input_action_value
                    if event.key == pg.K_DOWN:
                        self.input_action[1] = self.input_action_value
                    if event.key == pg.K_UP:
                        self.input_action[1] = -self.input_action_value

                if event.type == pg.KEYUP:
                    if event.key == pg.K_LEFT or event.key == pg.K_RIGHT:
                        self.input_action[0] = 0.0
                    if event.key == pg.K_DOWN or event.key == pg.K_UP:
                        self.input_action[1] = 0.0

            # Logic
            for _ in range(PHYSICS_SUBSTEPS):
                self.ball.run_physics_step(self.input_action)

            # Graphics
            self.screen.fill(BLACK)

            self.ball.draw(self.screen)

            if DEBUG:
                fps_surf = self.font.render(f"{self.clock.get_fps():.1f}", True, WHITE)
                self.screen.blit(fps_surf, (20, 20))

            pg.display.flip()

            # Time
            self.clock.tick(FPS)
