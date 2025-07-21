"""
Module to work with frames from webcam.
"""

import time

import numpy as np
from tensorflow.keras.models import Model , load_model
from tensorflow.keras.preprocessing import image

from app.params import MODEL_PATH


class SegmentationModel:
    """
    Model to get segmanted frame for controling the robot.
    """

    way = (255,255,255)
    backg = (0,0,0)
    class_labels = (way, backg)
    height = 60
    width = 80

    def __init__(self):
        # Load pretrained model
        self.model = load_model(MODEL_PATH, compile = False)
        print("Ready to make segmanted pictures")

    def labels_to_rgb(self, image_list):
        """
        Postprocess the result of the U-net model to work with.
        """

        result = []

        for y in image_list:
            temp = np.zeros((self.height, self.width, 3), dtype='uint8')

            for i, cl in enumerate(self.class_labels):
                temp[np.where(np.all(y==i, axis=-1))] = self.class_labels[i]

            result.append(temp)

        return np.array(result)


    def segment_frame(self, img):
        """
        Get result from U-net model.
        """

        # x = image.img_to_array(img)
        # x = np.array(img)

        start = time.time()

        x = np.expand_dims(img, axis=0)

        # Get results as array
        predict = np.argmax(self.model.predict(x, verbose = 0), axis=-1)

        print(time.time()-start)

        # Return the result as array of rgb images
        return self.labels_to_rgb(predict[..., None])


segmentation_model = SegmentationModel()
