"""
Module to control pins of the raspberry pi.
"""

import os
import time

import numpy as np
import RPi.GPIO as GPIO

from app.params import MAX_SPEED, MIN_SPEED, SPEED


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
    FOCUS_POINT = [45, 45]  # Pixel coordinates where to check the values of predicted images from camera

    def __init__(self):
        self.nn_on: bool = False  # The NN is working or not
        self.smart_moving: bool = False  # The NN is moving it or not

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

    def set_motor_speeds(self, left_speed: float, right_speed: float) -> bool:
        """
        Set the motor speeds.
        """

        if left_speed == 0 and right_speed == 0:
            self.stop()
            return False

        # Get the speed to set
        if abs(left_speed) > MAX_SPEED:
            v_left = MAX_SPEED
        elif abs(left_speed) < MIN_SPEED:
            v_left = MIN_SPEED
        else:
            v_left = abs(left_speed)

        if abs(right_speed) > MAX_SPEED:
            r_left = MAX_SPEED
        elif abs(right_speed) < MIN_SPEED:
            r_left = MIN_SPEED
        else:
            r_left = abs(right_speed)

        # Set the speed
        self.left_pwm.ChangeDutyCycle(v_left)
        self.right_pwm.ChangeDutyCycle(r_left)

        # Set the direction
        if left_speed < 0:
            GPIO.output(self.left_pin1, GPIO.HIGH)
            GPIO.output(self.left_pin2, GPIO.LOW)   # Left side backward
        else:
            GPIO.output(self.left_pin1, GPIO.LOW)
            GPIO.output(self.left_pin2, GPIO.HIGH)  # Left side forward

        if right_speed < 0:
            GPIO.output(self.right_pin1, GPIO.HIGH)
            GPIO.output(self.right_pin2, GPIO.LOW)   # Right side backward
        else:
            GPIO.output(self.right_pin1, GPIO.LOW)
            GPIO.output(self.right_pin2, GPIO.HIGH)  # Right side forward

        return True

    def control_by_nn(self, img):
        """
        Method to control the robot according to the predicted image.
        """

        white = [255,255,255]
        if (img[self.FOCUS_POINT[0]][self.FOCUS_POINT[1]][0] <= 5 and
            img[self.FOCUS_POINT[0]][self.FOCUS_POINT[1]][1] <= 5 and
            img[self.FOCUS_POINT[0]][self.FOCUS_POINT[1]][2] <= 5) :
            ind_left = np.where(np.all(img[self.FOCUS_POINT[0]][0 : self.FOCUS_POINT[1]] == white, axis = -1))[0]
            ind_right = np.where(np.all(img[self.FOCUS_POINT[0]][self.FOCUS_POINT[1] : ] == white, axis = -1))[0]

            if len(ind_left) != 0:
                self.turn_left()
            else:
                self.turn_right()

        else:
            self.forward()

    def smart_robot_control(self, img):
        """
        Improved method to control the robot according to the predicted image.
        Uses proportional control based on the track's center position relative to the image center.
        """

        # Convert image to grayscale if it isn't already
        if len(img.shape) == 3 and img.shape[2] == 3:
            gray_img = np.mean(img, axis=2)
        else:
            gray_img = img

        # Define white threshold (adjust as needed)
        white_threshold = 200

        # Get image dimensions
        height, width = gray_img.shape[:2]

        # Define region of interest (ROI) - middle horizontal strip
        roi_height = height // 3
        roi_top = (height - roi_height) // 2
        roi_bottom = roi_top + roi_height
        roi = gray_img[roi_top:roi_bottom, :]

        # Find white pixels in ROI
        white_pixels = np.where(roi > white_threshold)

        if len(white_pixels[0]) == 0:
            # No track detected - stop or search
            self.stop()
            return

        # Calculate track center in ROI
        track_center_x = np.mean(white_pixels[1])

        # Convert to image coordinates
        track_center_x_img = track_center_x
        image_center_x = width // 2

        # Calculate error (difference between track center and image center)
        error = track_center_x_img - image_center_x

        # Proportional control parameters
        Kp = 0.01  # Proportional gain (adjust as needed)
        base_speed = 50  # Base speed (0-100)

        # Calculate motor speeds
        left_speed = base_speed - Kp * error
        right_speed = base_speed + Kp * error

        # Ensure speeds are within bounds
        left_speed = np.clip(left_speed, -100, 100)
        right_speed = np.clip(right_speed, -100, 100)

        # Set motor speeds
        self.set_motor_speeds(left_speed, right_speed)

    def switch_nn(self):
        """
        Acitvate the NN to work with.
        """

        if not self.nn_on:
            self.nn_on = True
            print("NN - ON")
            GPIO.output(self.state_pin, GPIO.HIGH)
        else:
            self.nn_on = False
            print("NN - OFF")
            GPIO.output(self.state_pin, GPIO.LOW)

    def cleanup(self):
        """
        Clean before finish session.
        """

        self.stop()
        GPIO.cleanup()

robot = RobotCar()
