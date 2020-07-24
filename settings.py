from classes import DifficultyPreset, Action


class Settings:
    def __init__(self, *, difficulty_preset=None, fps):
        self.FPS = fps

        # Difficulty
        self.DIFFICULTY_PRESET = difficulty_preset

        self.INPUT_DERIVATIVE = 1
        self.LATENCY_FACTOR = 1000

        self.BALL_RADIUS = 20
        self.BALL_ACTION_FORCE = 1000
        self.BALL_RESTITUTION = 0.75
        self.BALL_FRICTION = 10

        self.ENEMY_WAIT = 1024
        self.ENEMY_SPEED = 256 / self.FPS
        self.ENEMY_LOGADD_SPEED = 16 / self.FPS
        self.ENEMY_PROX_POW = 0.1
        self.ENEMY_PROX_BIAS = self.BALL_RADIUS / 4
        self.ENEMY_PROX_COMPENSATION_FACTOR = 2

        self.BOUND_OBST_WIDTH = (32, 256)
        self.BOUND_OBST_HEIGHT = (self.BALL_RADIUS * 4, self.BALL_RADIUS * 16)
        self.BOUND_OBST_DIST = (self.BOUND_OBST_WIDTH[1] + self.BALL_RADIUS * 4, 1024)

        self.set_difficulty(self.DIFFICULTY_PRESET)

    def set_difficulty(self, difficulty_preset: int):
        self.DIFFICULTY_PRESET = difficulty_preset

        if difficulty_preset is None:
            pass

        elif difficulty_preset == DifficultyPreset.der_1_lag:
            self.INPUT_DERIVATIVE = 1
            self.LATENCY_FACTOR = 1000

            self.BALL_ACTION_FORCE = 1000
            self.BALL_FRICTION = 10

            self.ENEMY_WAIT = 1024
            self.ENEMY_SPEED = 320 / self.FPS
            self.ENEMY_LOGADD_SPEED = 32 / self.FPS

        elif difficulty_preset == DifficultyPreset.der_2:
            self.INPUT_DERIVATIVE = 2
            self.LATENCY_FACTOR = 0

            self.BALL_ACTION_FORCE = 1000
            self.BALL_RESTITUTION = 0.75
            self.BALL_FRICTION = 10

            self.ENEMY_WAIT = 2048
            self.ENEMY_SPEED = 32 / self.FPS
            self.ENEMY_LOGADD_SPEED = 16 / self.FPS

        elif difficulty_preset == DifficultyPreset.der_2_high_restitution:
            self.INPUT_DERIVATIVE = 2
            self.LATENCY_FACTOR = 0

            self.BALL_ACTION_FORCE = 2000
            self.BALL_RESTITUTION = 1.05
            self.BALL_FRICTION = 12

            self.ENEMY_WAIT = 2048
            self.ENEMY_SPEED = 32 / self.FPS
            self.ENEMY_LOGADD_SPEED = 12 / self.FPS

        elif difficulty_preset == DifficultyPreset.der_2_high_friction:
            self.INPUT_DERIVATIVE = 2
            self.LATENCY_FACTOR = 1

            self.BALL_ACTION_FORCE = 8000
            self.BALL_FRICTION = 40

            self.ENEMY_WAIT = 2048
            self.ENEMY_SPEED = 32 / self.FPS
            self.ENEMY_LOGADD_SPEED = 16 / self.FPS

        elif difficulty_preset == DifficultyPreset.der_3:
            self.INPUT_DERIVATIVE = 3
            self.LATENCY_FACTOR = 0

            self.BALL_ACTION_FORCE = 1000
            self.BALL_FRICTION = 0

            self.ENEMY_WAIT = 2048
            self.ENEMY_SPEED = 32 / self.FPS
            self.ENEMY_LOGADD_SPEED = 16 / self.FPS

        elif difficulty_preset == DifficultyPreset.test:
            self.INPUT_DERIVATIVE = 2
            self.LATENCY_FACTOR = 0

            self.BALL_ACTION_FORCE = 1000
            self.BALL_FRICTION = 10

            self.ENEMY_WAIT = 2048
            self.ENEMY_SPEED = 32 / self.FPS
            self.ENEMY_LOGADD_SPEED = 16 / self.FPS

            self.BOUND_OBST_WIDTH = (128, 128)
            self.BOUND_OBST_HEIGHT = (self.BALL_RADIUS * 64, self.BALL_RADIUS * 64)
            self.BOUND_OBST_DIST = (4096, 4096)

        else:
            raise Exception(f"{difficulty_preset} is not a valid difficulty preset. ")
