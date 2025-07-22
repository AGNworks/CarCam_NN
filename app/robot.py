"""
Module to control pins of the raspberry pi.
"""

import os
import time

import numpy as np
import RPi.GPIO as GPIO

from app.params import (CHECK_ZONE_HEIGHT, FOCUS_POINT,
        MAX_NULL_ZONES, MAX_SPEED, MIN_SPEED, SPEED, SPEED_STEP, ZONE_THRESHOLD)


def shutdownrpi(channel):
    """
    Used to shutdown the system with a button, connected to the board.
    """

    print("Shutting down")
    time.sleep(5)
    os.system("sudo shutdown -h now")


class RobotCar:
    """
    Used to define the used pins
    """

    #Controlling pins for motors
    left_pin1 = 15
    left_pin2 = 14
    right_pin1 = 26
    right_pin2 = 19
    left_pwm_pin = 18   #PWM pin
    right_pwm_pin = 13   #PWM pin
    state_pin = 25

    def __init__(self):
        self.nn_on: bool = False  # The NN is working or not
        self.smart_moving: bool = False  # The NN is moving it or not

        self.left_speed: int = MAX_SPEED
        self.right_speed: int = MAX_SPEED

        self.null_zone_counter: int = 0

        # Set up the pins
        self.set_up_robot_pins()

    def set_up_robot_pins(self) -> None:
        """
        Set up the used pins.
        """

        # Initialize GPIO
        GPIO.setmode(GPIO.BCM)

        ## SHUTDOWN
        # Setup shutdown button
        GPIO.setup(21, GPIO.IN, pull_up_down=GPIO.PUD_UP)

        # Add Shutdown event
        GPIO.add_event_detect(21, GPIO.FALLING, callback=shutdownrpi, bouncetime=2000)

        # Setup GPIO pins
        GPIO.setup(self.left_pin1, GPIO.OUT)
        GPIO.setup(self.left_pin2, GPIO.OUT)
        GPIO.setup(self.right_pin1, GPIO.OUT)
        GPIO.setup(self.right_pin2, GPIO.OUT)
        GPIO.setup(self.left_pwm_pin, GPIO.OUT)
        GPIO.setup(self.right_pwm_pin, GPIO.OUT)
        GPIO.setup(self.state_pin, GPIO.OUT)

        # Initialize PWM
        self.left_pwm = GPIO.PWM(self.left_pwm_pin, 1000)  # Left side
        self.right_pwm = GPIO.PWM(self.right_pwm_pin, 1000)  # Right side
        self.left_pwm.start(SPEED)
        self.right_pwm.start(SPEED)

    def forward(self) -> None:
        """
        Move forward.
        """

        GPIO.output(self.left_pin1, GPIO.LOW)
        GPIO.output(self.left_pin2, GPIO.HIGH)
        GPIO.output(self.right_pin1, GPIO.LOW)
        GPIO.output(self.right_pin2, GPIO.HIGH)

    def backward(self) -> None:
        """
        Move backward.
        """

        GPIO.output(self.right_pin1, GPIO.HIGH)
        GPIO.output(self.right_pin2, GPIO.LOW)
        GPIO.output(self.left_pin1, GPIO.HIGH)
        GPIO.output(self.left_pin2, GPIO.LOW)

    def stop(self) -> None:
        """
        Stop movement.
        """

        GPIO.output(self.left_pin1, GPIO.HIGH)
        GPIO.output(self.left_pin2, GPIO.HIGH)
        GPIO.output(self.right_pin1, GPIO.HIGH)
        GPIO.output(self.right_pin2, GPIO.HIGH)

    def turn_left(self) -> None:
        """
        Turn left.
        """

        GPIO.output(self.right_pin1, GPIO.LOW)
        GPIO.output(self.right_pin2, GPIO.HIGH)
        GPIO.output(self.left_pin1, GPIO.HIGH)
        GPIO.output(self.left_pin2, GPIO.LOW)

    def turn_right(self) -> None:
        """
        Trun right
        """

        GPIO.output(self.left_pin1, GPIO.LOW)
        GPIO.output(self.left_pin2, GPIO.HIGH)
        GPIO.output(self.right_pin1, GPIO.HIGH)
        GPIO.output(self.right_pin2, GPIO.LOW)

    def set_motor_speeds(self, test_mode: bool = False) -> bool:
        """
        Set the motor speeds.
        """

        print(f"Left speed: {self.left_speed}, right speed: {self.right_speed}")

        if not test_mode:
            # Get the speed to set
            if abs(self.left_speed) > MAX_SPEED:
                v_left = MAX_SPEED
            elif abs(self.left_speed) < MIN_SPEED:
                v_left = MIN_SPEED
            else:
                v_left = abs(self.left_speed)

            if abs(self.right_speed) > MAX_SPEED:
                r_left = MAX_SPEED
            elif abs(self.right_speed) < MIN_SPEED:
                r_left = MIN_SPEED
            else:
                r_left = abs(self.right_speed)

            # Set the speed
            self.left_pwm.ChangeDutyCycle(v_left)
            self.right_pwm.ChangeDutyCycle(r_left)

            # Set the direction
            if self.left_speed < 0:
                GPIO.output(self.left_pin1, GPIO.HIGH)
                GPIO.output(self.left_pin2, GPIO.LOW)   # Left side backward
            else:
                GPIO.output(self.left_pin1, GPIO.LOW)
                GPIO.output(self.left_pin2, GPIO.HIGH)  # Left side forward

            if self.right_speed < 0:
                GPIO.output(self.right_pin1, GPIO.HIGH)
                GPIO.output(self.right_pin2, GPIO.LOW)   # Right side backward
            else:
                GPIO.output(self.right_pin1, GPIO.LOW)
                GPIO.output(self.right_pin2, GPIO.HIGH)  # Right side forward

            return True

    def control_by_nn(self, img: np.ndarray):
        """
        Method to control the robot according to the predicted image.
        """

        white = [255,255,255]
        if (img[FOCUS_POINT[0]][FOCUS_POINT[1]][0] <= 5 and
            img[FOCUS_POINT[0]][FOCUS_POINT[1]][1] <= 5 and
            img[FOCUS_POINT[0]][FOCUS_POINT[1]][2] <= 5) :

            # Check a five pixel height zone
            zone_left = img[FOCUS_POINT[0]:FOCUS_POINT[0]+5, 0:FOCUS_POINT[1]]
            white_pixels_left = np.sum(np.all(zone_left == white, axis=-1))

            zone_right = img[FOCUS_POINT[0]:FOCUS_POINT[0]+5, FOCUS_POINT[1]:]
            white_pixels_right = np.sum(np.all(zone_right == white, axis=-1))

            print(f"White pixels on the left: {white_pixels_left}, on the right: {white_pixels_right}")
            if white_pixels_left > white_pixels_right:
                self.turn_left()
            else:
                self.turn_right()
        else:
            self.forward()

    def smart_robot_control(self, img: np.ndarray) -> np.ndarray:
        """
        Improved method to control the robot according to the predicted image.
        Uses proportional control based on the track's center position relative to the image center.
        """

        # Create a copy of the original image to modify
        merged_img = img.copy()

        white = [255,255,255]

        # Check a five pixel height zone
        zone_left = img[FOCUS_POINT[0]:FOCUS_POINT[0]+CHECK_ZONE_HEIGHT, 0:FOCUS_POINT[1]]
        white_pixels_left = np.sum(np.all(zone_left == white, axis=-1))

        zone_right = img[FOCUS_POINT[0]:FOCUS_POINT[0]+CHECK_ZONE_HEIGHT, FOCUS_POINT[1]:]
        white_pixels_right = np.sum(np.all(zone_right == white, axis=-1))

        print(f"White pixels on the left: {white_pixels_left}, on the right: {white_pixels_right}")

        # Color the zones on the merged image
        # Left zone (green with 50% opacity)
        merged_img[FOCUS_POINT[0]:FOCUS_POINT[0]+CHECK_ZONE_HEIGHT, 0:FOCUS_POINT[1]] = (
            merged_img[FOCUS_POINT[0]:FOCUS_POINT[0]+CHECK_ZONE_HEIGHT, 0:FOCUS_POINT[1]] * 0.5 +
            np.array([0, 255, 0]) * 0.5
        )

        # Right zone (blue with 50% opacity)
        merged_img[FOCUS_POINT[0]:FOCUS_POINT[0]+CHECK_ZONE_HEIGHT, FOCUS_POINT[1]:] = (
            merged_img[FOCUS_POINT[0]:FOCUS_POINT[0]+CHECK_ZONE_HEIGHT, FOCUS_POINT[1]:] * 0.5 +
            np.array([255, 0, 0]) * 0.5
            )

        # Control the movement
        self.correct_direction(
            zone_left=white_pixels_left,
            zone_right=white_pixels_right,
            test_mode=False
        )

        return merged_img

    def switch_nn(self):
        """
        Acitvate the NN to work with.
        """

        if not self.nn_on:
            self.nn_on = True
            print("NN - ON")
            # GPIO.output(self.state_pin, GPIO.HIGH)
        else:
            self.nn_on = False
            print("NN - OFF")
            # GPIO.output(self.state_pin, GPIO.LOW)

    def cleanup(self):
        """
        Clean before finish session.
        """

        self.stop()
        GPIO.cleanup()

    def correct_direction(self, zone_left: int, zone_right: int, test_mode: bool = False):
        """
        Analyze the difference between qty of white pixels, and decide how to move.
        """

        if abs(zone_left-zone_right) <= ZONE_THRESHOLD:
            self.right_speed = MAX_SPEED
            self.left_speed = MAX_SPEED
            self.set_motor_speeds(test_mode=test_mode)

        if zone_left-ZONE_THRESHOLD > zone_right:
            self.left_speed -= SPEED_STEP
            self.set_motor_speeds(test_mode=test_mode)

        if zone_right-ZONE_THRESHOLD > zone_left:
            self.right_speed -= SPEED_STEP
            self.set_motor_speeds(test_mode=test_mode)

        if zone_right == 0 and zone_left != 0:
            self.right_speed = MAX_SPEED
            self.left_speed = MAX_SPEED
            if not test_mode:
                self.turn_left()

        if zone_left == 0 and zone_right != 0:
            self.right_speed = MAX_SPEED
            self.left_speed = MAX_SPEED
            if not test_mode:
                self.turn_right()

        if zone_left == 0 and zone_right == 0:
            self.null_zone_counter += 1
            if self.null_zone_counter == MAX_NULL_ZONES:
                if not test_mode:
                    self.stop()
                self.null_zone_counter = 0

robot = RobotCar()
