# Control system for remote car with computer vision

**I created this little project to connect to connect the physical world with a neural network which I created to recognize the red road (because I had that color of tape) in real time in front the robot and in this way control it.**

## The actual version of my robot
<p align="center">
  <img src="https://github.com/AGNworks/CarCam_NN/blob/main/pictures/1.png" alt="Actual version"/>
</p>

**The design idea I got from Tim Clark's model, which I found on [thingiverse](https://www.thingiverse.com/thing:700835). After the first version it became more controlable and more solid. The first version looked like this:**

<p align="center">
  <img src="https://github.com/AGNworks/CarCam_NN/blob/main/pictures/2.png" alt="Old version"/>
</p>

## Dataset collecting

**For first I wrote a program which can control the robot step by step, and after every step (which is choosen from [forward, backward, left, right]) it is saving a picture. After collecting in this way enough pics, I prepared them for further work. The code, for the process of collection, you can find in [this](https://github.com/AGNworks/CarCam) repository.**

**I generated the train segmented pictures (for the teaching process of the neural network) with the help of GIMP. To turn the rest of the picture to black I wrote a simple code to do this for me (everything what is not white should be black), here is the [code](https://github.com/AGNworks/Image-segmentation-with-GIMP/blob/main/y_generator.py) for that. And the end of this process I cheched, if all went well (it should be just clean white and clean black pixels on the picture) the code for the test is [here](https://github.com/AGNworks/Image-segmentation-with-GIMP/blob/main/check_y_image.py)**

<p align="center">
  <img src="https://github.com/AGNworks/CarCam_NN/blob/main/pictures/3.png" alt="segmented picture"/>
</p>

## The architecture of the NN model

**I started with a simple linear model Conv2D layers and Normalization, but this model didn't give me good results with pictures, what it never seen, so I moved on and experimented with U-Net models. Now I have simple U-Net model with 3 downsampling Block - Bottleneck - 3 upsampling Block. Here you can see how it works:** 

<p align="center">
  <img src="https://github.com/AGNworks/CarCam_NN/blob/main/pictures/4.png" alt="Result"/>
</p>

## Set up -- Raspberry Pi
Before use, we need to set up the system to run the python code after boot. For this read the following [txt file](https://github.com/AGNworks/CarCam_NN/blob/main/bootraspi.txt) .




