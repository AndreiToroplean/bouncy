import os

import pygame as pg

from settings import Settings
from classes import DifficultyPreset

DEBUG = True
FULL_SCREEN = True
WINDOWED_RES = 1280, 720

C_BLACK = pg.Color(0, 0, 0)
C_DARK_GREY = pg.Color(32, 32, 32)
C_WHITE = pg.Color(255, 255, 255)
C_RED = pg.Color(255, 0, 0)

C_LIME_GREEN = pg.Color(196, 255, 128)
C_YELLOW = pg.Color(255, 255, 64)

C_LIGHT_GREEN = pg.Color(128, 255, 128)
C_LIGHT_BLUE = pg.Color(128, 196, 255)

C_END = pg.Color(150, 50, 50)

FPS = 60
DELAY_BEFORE_QUITTING = 1000
N_PHYSICS_SUBSTEPS = 10
MAX_N_OBSTS = 10

BORDER_S_WIDTH = 1 / 4
CAM_DAMPING_FACTOR = 8

SCORE_ADD_FACTOR = 1.0
SCORE_EXPADD_FACTOR = 0.00002

N_PLAYERS = 1

SEED = 0
DIFFICULTY_PRESET = DifficultyPreset.der_2
SETTINGS = Settings(difficulty_preset=DIFFICULTY_PRESET, fps=FPS)

LOAD = True
SAVE = True

if DIFFICULTY_PRESET == DifficultyPreset.test:
    LOAD = False
    SAVE = False

SAVE_DIR = "saves"
SAVE_PROFILES = [
    f"p1_l{DIFFICULTY_PRESET.value}_s{SEED}",
    f"p2_l{DIFFICULTY_PRESET.value}_s{SEED}",
    f"p3_l{DIFFICULTY_PRESET.value}_s{SEED}",
    ]
SAVE_PATHS = [os.path.join(SAVE_DIR, f"{save_profile}.json") for save_profile in SAVE_PROFILES]

BALLS_COLORS = [
    (C_WHITE, ),
    (C_LIGHT_BLUE, C_LIGHT_GREEN),
    (C_LIGHT_BLUE, C_LIGHT_GREEN, C_YELLOW),
    ][N_PLAYERS-1]

BALLS_DISTANCE = 80
ENEMY_MIN_REMAP = -2000, 200, 50, 4
