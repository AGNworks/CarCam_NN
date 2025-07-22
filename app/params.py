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

# Pixel coordinates where to check the values of predicted images from camera
FOCUS_POINT = [40, 40]
CHECK_ZONE_HEIGHT = 5
ZONE_THRESHOLD = 10  # If the difference of the white px qty is less then this threshold then it is the same
SPEED_STEP = 2
ZONE_K = 3
MAX_NULL_ZONES = 10