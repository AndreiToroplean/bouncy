import pygame as pg
import numpy as np

from global_params import FULL_SCREEN, C_BLACK, C_WHITE, FPS, CAM_DAMPING_FACTOR, DEBUG_RES, C_RED, C_END
from rectangle import Rectangle


class Camera:
    def __init__(self):
        if FULL_SCREEN:
            self._screen = pg.display.set_mode((0, 0), pg.FULLSCREEN)
        else:
            self._screen = pg.display.set_mode(DEBUG_RES)
        self._clock = pg.time.Clock()
        self.time = 0

        self._small_font = pg.font.Font("resources/SourceCodePro-Regular.ttf", 16)
        self._medium_font = pg.font.Font("resources/SourceCodePro-Regular.ttf", 32)
        self._large_font = pg.font.Font("resources/SourceCodePro-Regular.ttf", 64)

        self.w_pos = np.array([0.0, 0.0])
        self.res = np.array(self._screen.get_size())

    @property
    def w_view(self):
        return np.array([
            self.w_pos - self.res / 2,
            self.w_pos + self.res / 2,
            ])

    def _w_pos_to_pix_shift(self, w_pos):
        return np.floor((w_pos - self.w_pos) * np.array((1, -1)) + self.res / 2).astype(int)

    def empty_screen(self):
        self._screen.fill(C_BLACK)

    def flip_display_and_tick(self):
        pg.display.flip()
        self._clock.tick(FPS)
        self.time = pg.time.get_ticks()

    def req_move(self, w_pos_x):
        self.w_pos[0] += (w_pos_x - self.w_pos[0]) * (CAM_DAMPING_FACTOR / FPS)

    def draw(self, obj):
        pix_shift = self._w_pos_to_pix_shift(obj.w_pos)
        obj.draw(self._screen, pix_shift)

    def draw_score(self, score, high_score):
        pix_pos = 32, 32

        score_surf = self._medium_font.render(f"SCORE: {score:,}", True, C_BLACK)
        score_pix_size = score_surf.get_size()
        self._screen.blit(score_surf, (
                pix_pos[0],
                self.res[1] - score_pix_size[1] - pix_pos[1]
                ))

        high_score_surf = self._medium_font.render(f"HIGH SCORE: {high_score:,}", True, C_BLACK)
        high_score_pix_size = high_score_surf.get_size()
        self._screen.blit(high_score_surf, (
                self.res[0] - high_score_pix_size[0] - pix_pos[0],
                self.res[1] - high_score_pix_size[1] - pix_pos[1],
                ))

    def draw_debug_info(self):
        debug_info = f"fps: {self._clock.get_fps():.1f}, time: {self.time/1000:.1f}"
        debug_info_surf = self._small_font.render(debug_info, True, C_BLACK)
        self._screen.blit(debug_info_surf, (8, 8))

    def draw_end_screen(self, score_text):
        self._screen.fill(C_END, special_flags=pg.BLEND_ADD)
        self._screen.fill(C_END, special_flags=pg.BLEND_MULT)

        score_text = self._large_font.render(f"SCORE: {score_text:,}", True, C_WHITE)
        score_text_pix_size = np.array(score_text.get_size())
        self._screen.blit(score_text, self.res / 2 - score_text_pix_size / 2)

        replay_text = self._medium_font.render("REPLAY?", True, C_WHITE)
        replay_text_pix_size = np.array(replay_text.get_size())
        self._screen.blit(replay_text, self.res / 2 - replay_text_pix_size / 2 + [0, 64])
