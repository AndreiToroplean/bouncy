from enum import Enum


class DifficultyPreset(Enum):
    der_1_lag = 1
    der_2 = 2
    der_2_high_friction = 3
    der_3 = 4


class Action(Enum):
    stay = -1

    go_right = 0
    go_left = 1

    go_up = 2
    go_down = 3
