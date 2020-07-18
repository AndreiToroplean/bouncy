import os

import pygame as pg

from settings import Settings

DEBUG = False
FULL_SCREEN = True
DEBUG_RES = 1280, 720

if DEBUG:
    FULL_SCREEN = False

BLACK = pg.Color(0, 0, 0)
DARK_GREY = pg.Color(32, 32, 32)
WHITE = pg.Color(255, 255, 255)
RED = pg.Color(255, 0, 0)

FPS = 60
DELAY_BEFORE_QUITTING = 1500
N_PHYSICS_SUBSTEPS = 10
MAX_N_OBSTS = 16

BORDER_S_WIDTH = 1 / 4
CAM_DAMPING_FACTOR = 10

SEED = 1
DIFFICULTY_PRESET_NB = 2
SETTINGS = Settings(difficulty_preset_nb=DIFFICULTY_PRESET_NB, fps=FPS)

SAVES_DIR = "saves"
SAVE_PROFILE = "player"
SAVE_PATH = os.path.join(SAVES_DIR, f"{SAVE_PROFILE}.json")
