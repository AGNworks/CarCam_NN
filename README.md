# Control system for remote car with computer vision

**I created this little project to connect to connect the physical world with a neural network which I created to recognize the red road (because I had that color of tape) in real time in front the robot and in this way control it.**

## The actual version of my robot
![Actual version](https://github.com/AGNworks/CarCam_NN/blob/main/pictures/1.png)

**The design idea I got from Tim Clark's model, which I found on [thingiverse](https://www.thingiverse.com/thing:700835). After the first version it became more controlable and more solid. The first version looked like this:**

![Old version](https://github.com/AGNworks/CarCam_NN/blob/main/pictures/2.png)

## Dataset collecting
** For first I wrote a program which can control the robot step by step, and after every step (which is choosen from [forward, backward, left, right]) it is saving a picture. After collecting in this way enough pics, I prepared them for further work. The code for the collection you can find in [this](https://github.com/AGNworks/CarCam) repository. **
