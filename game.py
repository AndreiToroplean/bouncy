import pygame as pg
import numpy as np

BLACK = pg.Color(0, 0, 0)
GREY = pg.Color(128, 128, 128)
WHITE = pg.Color(255, 255, 255)
FPS = 60
PHYSICS_SUBSTEPS = 2


class Game:
    def __init__(self):
        pg.init()

        # self.screen = pg.display.set_mode((0, 0), pg.FULLSCREEN)
        self.screen = pg.display.set_mode((800, 600))
        self.screen_rect = self.screen.get_rect()
        self.clock = pg.time.Clock()
        self.font = pg.font.SysFont(pg.font.get_default_font(), 12)

        self.ball_radius = 25
        self.ball_color = WHITE

        self.ball_rect = pg.draw.circle(self.screen, self.ball_color, self.screen_rect.center, self.ball_radius)
        self.ball_vel = np.array((0.0, 0.0))
        self.ball_acc = np.array((0.0, 1500 / (FPS*PHYSICS_SUBSTEPS)**2))
        self.ball_restitution = 0.75

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

            # Logic
            for _ in range(PHYSICS_SUBSTEPS):
                self.ball_vel += self.ball_acc
                new_ball_rect = self.ball_rect
                new_ball_rect.center += self.ball_vel
                if new_ball_rect.bottom > self.screen_rect.bottom:
                    self.ball_vel[1] *= -1 * self.ball_restitution
                    new_ball_rect.bottom -= (new_ball_rect.bottom - self.screen_rect.bottom) * (1 + self.ball_restitution)
                self.ball_rect = new_ball_rect

            # Graphics
            self.screen.fill(BLACK)

            self.ball_rect = pg.draw.circle(self.screen, self.ball_color, self.ball_rect.center, self.ball_radius)

            fps_surf = self.font.render(f"{self.clock.get_fps():.0f}", True, WHITE)
            self.screen.blit(fps_surf, (20, 20))
            pg.display.flip()

            # Time
            self.clock.tick(FPS)
