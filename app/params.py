"""
Module to define all the parameters used in controlling.
"""

MODEL_PATH = 'assets/models/model_unet_light_new_better.h5'

# Motor control parameters
SPEED = 20  # Starting PWM % value for wheels
SLEEPTURN = 0.3
SLEEPRUN = 0.5

TURN_FACTOR = 0.7
MIN_SPEED = 12
MAX_SPEED = 20

IMG_SIZE = (60,80)
