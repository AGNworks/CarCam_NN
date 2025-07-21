"""
Camera
"""

import asyncio
import cv2
import numpy as np

from app.params import IMG_SIZE
from app.segmentation import segmentation_model
from app.robot import robot


class Camera:
    """
    Class to control the camera object.
    """

    def __init__(self):
        # Webcam setup
        self.camera_object = cv2.VideoCapture(0)
        self.camera_object.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
        self.camera_object.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)

    def shutdown(self):
        """
        Disconnect.
        """
        self.camera_object.release()

    async def generate_frames(self):
        """
        Get frames from camera.
        """

        while True:
            success, frame = self.camera_object.read()
            if not success:
                break
            ret, buffer = cv2.imencode('.jpg', frame)
            frame_bytes = buffer.tobytes()
            yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
            await asyncio.sleep(0.03)  # Control frame rate

    def gen_nn_frames(self):
        """
        Generates the video content from frames of nn-model.
        """

        while True:
            if robot.nn_on:
                success, frame = self.camera_object.read()  # read the camera frame
                if not success:
                    break
                else:
                    simg = cv2.resize(frame, (IMG_SIZE[1],IMG_SIZE[0])) #the resized capture image from webcam
                    imgseg = cv2.cvtColor(simg, cv2.COLOR_BGR2RGB) #change channel order pefore giving it to NN
                    predict_segments = segmentation_model.segment_frame(imgseg) #get prediction from model
                    predicted = predict_segments[0]
                    if robot.smart_moving:
                        # Move the robot
                        robot.smart_robot_control(predicted)

                    overlayed = cv2.addWeighted(simg, 1, predicted, 1,0) #combine the original and the predicted image
                    ret, buffer = cv2.imencode('.jpg', overlayed)
                    frame = buffer.tobytes()
                    yield (b'--frame\r\n'
                        b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # concat frame one by one and show result
            else:
                simg = np.empty(shape = (IMG_SIZE[0],IMG_SIZE[1], 3))
                # Stream empty
                ret, buffer = cv2.imencode('.jpg', simg)
                frame = buffer.tobytes()
                yield (b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # concat frame one by one and show result


camera = Camera()
