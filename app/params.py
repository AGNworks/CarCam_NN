"""
Module to define all the parameters used in controlling.
"""

MODEL_PATH = 'assets/models/model_unet_light_new_better.h5'

# Motor control parameters
SPEED = 10  # Starting PWM % value for wheels
SLEEPTURN = 0.3
SLEEPRUN = 0.5

TURN_FACTOR = 0.7
MIN_SPEED = 15
MAX_SPEED = 100

IMG_SIZE = (60,80)
