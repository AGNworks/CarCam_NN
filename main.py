from flask import Flask, render_template, Response, make_response, redirect, request, url_for, jsonify, send_file
from subprocess import check_output
from moduls.segmentation import *


import threading
import RPi.GPIO as GPIO
import time
import os
import numpy as np
import cv2


mode = GPIO.getmode()
GPIO.setmode(GPIO.BCM)

GPIO.setup(21, GPIO.IN, pull_up_down = GPIO.PUD_UP)
def shutdownrpi(channel):  #function for turning off raspberry pi safely with the help of a button on GPIO pin 21
    print("Shutting down")
    time.sleep(5)
    os.system("sudo shutdown -h now")
    
GPIO.add_event_detect(21, GPIO.FALLING, callback=shutdownrpi, bouncetime=2000)

speed = 50 #Starting PWM % value for wheels, this determinates the speed of the motors 
sleepturn = 0.3
sleeprun = 0.5

imgcount = 0
imgname = "norec.jpg"
rec_img = False

NN_on = False
img_w = 60
img_h = 80


overlay = cv2.imread('static/overlay.png')
print(type(overlay))

#Controlling pins for motors
Apin1 = 15
Apin2 = 14
Bpin1 = 26
Bpin2 = 19
Aen = 18   #PWM pin
Ben = 13   #PWM pin
stateLED = 25

#Set up the mode of the GPIO pins 
GPIO.setup(Apin1, GPIO.OUT)
GPIO.setup(Apin2, GPIO.OUT)
GPIO.setup(Bpin1, GPIO.OUT)
GPIO.setup(Bpin2, GPIO.OUT)
GPIO.setup(Aen, GPIO.OUT)
GPIO.setup(Ben, GPIO.OUT)

GPIO.setup(stateLED, GPIO.OUT)

#flash ones with the LED pins
GPIO.output(stateLED, GPIO.HIGH)
time.sleep(0.5)
GPIO.output(stateLED, GPIO.LOW)

#GPIO.output(Aen, GPIO.HIGH)
#GPIO.output(Ben, GPIO.HIGH)
Ap = GPIO.PWM(Aen, 1000)
Bp = GPIO.PWM(Ben, 1000)
Ap.start(35)   #speed of the left side
Bp.start(50)   #speed of the right side

#functions to control DC motors
def forward():
    GPIO.output(Apin1, GPIO.LOW)
    GPIO.output(Apin2, GPIO.HIGH)
    GPIO.output(Bpin1, GPIO.LOW)
    GPIO.output(Bpin2, GPIO.HIGH)
    print("MF")
       
def backward():
    GPIO.output(Bpin1, GPIO.HIGH)
    GPIO.output(Bpin2, GPIO.LOW)
    GPIO.output(Apin1, GPIO.HIGH)
    GPIO.output(Apin2, GPIO.LOW)
    print("MB")
    
def stop():
    GPIO.output(Apin1, GPIO.HIGH)
    GPIO.output(Apin2, GPIO.HIGH)
    GPIO.output(Bpin1, GPIO.HIGH)
    GPIO.output(Bpin2, GPIO.HIGH)
    print("S")
    
def turnleft():
    GPIO.output(Bpin1, GPIO.LOW)
    GPIO.output(Bpin2, GPIO.HIGH)
    GPIO.output(Apin1, GPIO.HIGH)
    GPIO.output(Apin2, GPIO.LOW)
    print("ML")

    
def turnright():
    GPIO.output(Apin1, GPIO.LOW)
    GPIO.output(Apin2, GPIO.HIGH)
    GPIO.output(Bpin1, GPIO.HIGH)
    GPIO.output(Bpin2, GPIO.LOW)
    print("MR")


def turn_NN_on():
    global NN_on
    if NN_on == False:
        try:
            NN_on = True
            print("NN - ON")
            GPIO.output(stateLED, GPIO.HIGH)
        except:
            print("can't start NN")
    elif NN_on == True:
        try:
            NN_on = False
            print("NN - OFF")
            GPIO.output(stateLED, GPIO.LOW)
        except:
            print("can't stop NN")

check_xy = [45, 45]
def control_NN(img): #function to control the robot accoding to the predicted image
    white = [255,255,255]
    if NN_on == True:
        if img[check_xy[0]][check_xy[1]][0] <= 5 and img[check_xy[0]][check_xy[1]][1] <= 5 and img[check_xy[0]][check_xy[1]][2] <= 5 :
            ind_left = np.where(np.all(img[check_xy[0]][0 : check_xy[1]] == white, axis = -1))[0]
            ind_right = np.where(np.all(img[check_xy[0]][check_xy[1] : ] == white, axis = -1))[0]
            
            if len(ind_left) != 0:
                turnleft()
            else:
                turnright()
                
        else:
            forward()


def check_wifi(): #function to check wifi connection
    wifi_ip = check_output(['hostname', '-I'])
    wifi_str = str(wifi_ip.decode())
    if len(wifi_ip) > 4:
        wifi_str = wifi_str[:-2]
        print(len(wifi_str))
        print('connected')
        return wifi_str
    print("not connected")
    return None

ip_adr = check_wifi()
print(ip_adr)
print(type(ip_adr))



img_size = (60,80)
if ip_adr is not None:
    app = Flask(__name__)
    
    simg = np.empty(shape = (img_size[0],img_size[1],3))
    
    def gen_frames(): #this generates the video content for visualization
        camera = cv2.VideoCapture(0)
        while True:
            success, frame = camera.read()  # read the camera frame
            if not success:
                break
            else:
                #w = int(frame.shape[1]/2)
                #h = int(frame.shape[0]/2)
                global simg
                simg = cv2.resize(frame, (img_size[1],img_size[0])) #the resized capture image from webcam
                imgseg = cv2.cvtColor(simg, cv2.COLOR_BGR2RGB) #change channel order pefore giving it to NN
                predict_segments = segmentpics(imgseg) #get prediction from model
                predicted = predict_segments[0]
                control_NN(predicted) #controling function
                
                overlayed = cv2.addWeighted(simg, 1, predicted, 1,0) #combine the original and the predicted image
                ret, buffer = cv2.imencode('.jpg', overlayed) 
                frame = buffer.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # concat frame one by one and show result
    
            

    @app.route("/")
    def main_page():
        print("Page is working")
        return render_template("index.html")

    @app.route('/video_feed')
    def video_feed():
        return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')
    
    @app.route('/status')
    def status():
        global imgname
        return send_file('static/{}'.format(imgname), mimetype='image/gif')

    @app.route('/process', methods=["GET", "POST"])
    def background_process_test():
        if request.method == "POST":
            data = request.get_json()
            if data == "S" : 
                print("the robot stops")
                stop()
            elif data == "C" : 
                print("NN processing -- ON/OFF")
                turn_NN_on()
        
        return ("nothing")

    if __name__ == "__main__":
        app.run(debug=True, host = ip_adr, port=8030, threaded = True)

