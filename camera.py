import pygame as pg
import numpy as np

from global_params import FULL_SCREEN, BLACK, WHITE, FPS, CAM_DAMPING_FACTOR
from rectangle import Rectangle


class Camera:
    def __init__(self):
        if FULL_SCREEN:
            self._screen = pg.display.set_mode((0, 0), pg.FULLSCREEN)
        else:
            self._screen = pg.display.set_mode((800, 600))
        self._clock = pg.time.Clock()
        self._font = pg.font.SysFont(pg.font.get_default_font(), 24)

        self.w_pos = np.array([0.0, 0.0])
        self.pix_size = np.array(self._screen.get_size())

    @property
    def w_view(self):
        return np.array([
            self.w_pos - self.pix_size / 2,
            self.w_pos + self.pix_size / 2,
            ])

    def _w_pos_to_pix_shift(self, w_pos):
        return np.floor((w_pos - self.w_pos) * np.array((1, -1)) + self.pix_size / 2).astype(int)

    def empty_screen(self):
        self._screen.fill(BLACK)

    def flip_display_and_tick(self):
        pg.display.flip()
        self._clock.tick(FPS)

    def req_move(self, w_pos):
        self.w_pos += (w_pos - self.w_pos) * (CAM_DAMPING_FACTOR / FPS) * np.array((1, 0))

    def draw(self, obj):
        pix_shift = self._w_pos_to_pix_shift(obj.w_pos)
        obj.draw(self._screen, pix_shift)

    def draw_debug_info(self):
        fps_surf = self._font.render(f"{self._clock.get_fps():.1f}", True, WHITE)
        self._screen.blit(fps_surf, (20, 20))
