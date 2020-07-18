import pygame as pg
import numpy as np

from global_params import FULL_SCREEN, BLACK, WHITE, FPS, CAM_DAMPING_FACTOR, DEBUG_RES
from rectangle import Rectangle


class Camera:
    def __init__(self):
        if FULL_SCREEN:
            self._screen = pg.display.set_mode((0, 0), pg.FULLSCREEN)
        else:
            self._screen = pg.display.set_mode(DEBUG_RES)
        self._clock = pg.time.Clock()
        self.time = 0

        self._debug_font = pg.font.Font("resources/SourceCodePro-Regular.ttf", 16)
        self._score_font = pg.font.Font("resources/SourceCodePro-Regular.ttf", 32)

        self.w_pos = np.array([0.0, 0.0])
        self.res = np.array(self._screen.get_size())

        self.high_score = 0

    @property
    def w_view(self):
        return np.array([
            self.w_pos - self.res / 2,
            self.w_pos + self.res / 2,
            ])

    def _w_pos_to_pix_shift(self, w_pos):
        return np.floor((w_pos - self.w_pos) * np.array((1, -1)) + self.res / 2).astype(int)

    def empty_screen(self):
        self._screen.fill(BLACK)

    def flip_display_and_tick(self):
        pg.display.flip()
        self._clock.tick(FPS)
        self.time = pg.time.get_ticks()

    def req_move(self, w_pos):
        self.w_pos += (w_pos - self.w_pos) * (CAM_DAMPING_FACTOR / FPS) * np.array((1, 0))

    def draw(self, obj):
        pix_shift = self._w_pos_to_pix_shift(obj.w_pos)
        obj.draw(self._screen, pix_shift)

    def draw_score(self, score):
        pix_pos = 10, 10

        score_surf = self._score_font.render(f"{score}", True, BLACK)
        score_pix_size = score_surf.get_size()
        self._screen.blit(score_surf, (
                self.res[0] - score_pix_size[0] - pix_pos[0],
                self.res[1] - score_pix_size[1] - pix_pos[1],
                ))

        high_score_surf = self._score_font.render(f"HIGH SCORE: {self.high_score:.0f}", True, BLACK)
        high_score_pix_size = high_score_surf.get_size()
        self._screen.blit(high_score_surf, (
                pix_pos[0],
                self.res[1] - high_score_pix_size[1] - pix_pos[1],
                ))

    def draw_debug_info(self):
        debug_info = f"fps: {self._clock.get_fps():.1f}, time: {self.time/1000:.1f}"
        debug_info_surf = self._debug_font.render(debug_info, True, BLACK)
        self._screen.blit(debug_info_surf, (8, 8))
