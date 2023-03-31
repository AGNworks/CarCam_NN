from tensorflow.keras.models import Model , load_model
from tensorflow.keras.preprocessing import image 
import numpy as np 
import os

way = (255,255,255)
backg = (0,0,0)
class_labels = (way, backg)

#loading model
my_model = load_model('/home/agn/CarCam_NN/model_unet_light_new_better.h5', compile = False)
print("Ready to make segmanted pictures")

height = 60
width = 80

def labels_to_rgb(image_list):
    result = []

    for y in image_list:
        temp = np.zeros((height, width, 3), dtype='uint8')

        for i, cl in enumerate(class_labels):
            temp[np.where(np.all(y==i, axis=-1))] = class_labels[i]

        result.append(temp)
  
    return np.array(result)


def segmentpics(img):
    #x = image.img_to_array(img)
    #x = np.array(img)

    x = np.expand_dims(img, axis=0)
    predict = np.argmax(my_model.predict(x, verbose = 0), axis=-1)     #getting results as array
    return labels_to_rgb(predict[..., None])      #returning the result as array of rgb images


