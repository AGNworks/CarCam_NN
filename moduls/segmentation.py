from tensorflow.keras.models import Model , load_model
from tensorflow.keras.preprocessing import image 
import numpy as np 
import os

way = (255,255,255)
backg = (0,0,0)
class_labels = (way, backg)

#loading model
my_model = load_model('model_unet_light.h5')
print("Ready to make segmanted pictures")



def labels_to_rgb(image_list):
    result = []

    for y in image_list:
        temp = np.zeros((240, 320, 3), dtype='uint8')

        for i, cl in enumerate(class_labels):
            temp[np.where(np.all(y==i, axis=-1))] = class_labels[i]

        result.append(temp)
  
    return np.array(result)


def segmentpics(img):
    x = image.img_to_array(img)
    x = np.array(x)
    #print(x.shape)
    
    x = np.expand_dims(x, axis=0)
    #print(x.shape)

    predict = np.argmax(my_model.predict(x), axis=-1)     #getting results as array
    return labels_to_rgb(predict[..., None])      #returning the result as array of rgb images


