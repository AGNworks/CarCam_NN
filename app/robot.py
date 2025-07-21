"""
Module to control pins of the raspberry pi.
"""

import os
import time
import numpy as np

import RPi.GPIO as GPIO

from app.camera import camera
from app.params import SPEED


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

    def control_by_nn(self, img):
        """
        Method to control the robot according to the predicted image.
        """

        white = [255,255,255]
        if img[self.FOCUS_POINT[0]][self.FOCUS_POINT[1]][0] <= 5 and img[self.FOCUS_POINT[0]][self.FOCUS_POINT[1]][1] <= 5 and img[self.FOCUS_POINT[0]][self.FOCUS_POINT[1]][2] <= 5 :
            ind_left = np.where(np.all(img[self.FOCUS_POINT[0]][0 : self.FOCUS_POINT[1]] == white, axis = -1))[0]
            ind_right = np.where(np.all(img[self.FOCUS_POINT[0]][self.FOCUS_POINT[1] : ] == white, axis = -1))[0]

            if len(ind_left) != 0:
                self.turn_left()
            else:
                self.turn_right()

        else:
            self.forward()

    def turn_nn_on(self):
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
        camera.shutdown()

robot = RobotCar()
