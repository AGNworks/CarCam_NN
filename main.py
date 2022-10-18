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
def shutdownrpi(channel):
    print("Shutting down")
    time.sleep(5)
    os.system("sudo shutdown -h now")
    
GPIO.add_event_detect(21, GPIO.FALLING, callback=shutdownrpi, bouncetime=2000)

speed = 50 #Starting PWM % value for wheels
sleepturn = 0.3
sleeprun = 0.5

imgcount = 0
imgname = "norec.jpg"
rec_img = False

NN_on = False
img_w = 240
img_h = 320


overlay = cv2.imread('static/overlay.png')

Apin1 = 15
Apin2 = 14
Bpin1 = 26
Bpin2 = 19
Aen = 18   #PWM pin
Ben = 13   #PWM pin
stateLED = 25

GPIO.setup(Apin1, GPIO.OUT)
GPIO.setup(Apin2, GPIO.OUT)
GPIO.setup(Bpin1, GPIO.OUT)
GPIO.setup(Bpin2, GPIO.OUT)
GPIO.setup(Aen, GPIO.OUT)
GPIO.setup(Ben, GPIO.OUT)

GPIO.setup(stateLED, GPIO.OUT)

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
    time.sleep(sleepturn)
    stop()
    
def turnright():
    GPIO.output(Apin1, GPIO.LOW)
    GPIO.output(Apin2, GPIO.HIGH)
    GPIO.output(Bpin1, GPIO.HIGH)
    GPIO.output(Bpin2, GPIO.LOW)
    print("MR")
    time.sleep(sleepturn)
    stop()

def create_imgs():
    global NN_on
    if NN_on == False:
        try:
            #t = threading.Timer(5.0, create_frame).start()
            NN_on = True
            print("ON")
            GPIO.output(stateLED, GPIO.HIGH)
        except:
            print("can't start recording")
    elif NN_on == True:
        try:
            #t.cancel()
            NN_on = False
            print("OFF")
            GPIO.output(stateLED, GPIO.LOW)
        except:
            print("can't stop recording")
    

def create_frame():  #function to save frames when button is pressed
    if rec_img == True:
        time.sleep(sleeprun)  #stopping the movement of the car before creating a picture
        stop()
        time.sleep(1) #needed to make less not clear image
        with open ("imgnumb.txt", "r") as numbfile:   #reading from file the current number of the frame
            imgnumb = int(numbfile.read())
        print(imgnumb)
        
        cv2.imwrite('/home/agn/Pictures/createdimgs_new/{}.png'.format(imgnumb), simg)
        imgnumb += 1
        
        with open ("imgnumb.txt", "w") as numbfile: #writing to the file the current number of the frame
            numbfile.write(str(imgnumb))
    

def check_wifi(): #function to chechk wifi connection
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

img_size = (240,320)
if ip_adr is not None:
    app = Flask(__name__)
    
    simg = np.empty(shape = (img_size[0],img_size[1],3))
    
    def gen_frames():
        camera = cv2.VideoCapture(0)
        while True:
            success, frame = camera.read()  # read the camera frame
            if not success:
                break
            else:
                #w = int(frame.shape[1]/2)
                #h = int(frame.shape[0]/2)
                global simg
                simg = cv2.resize(frame, (img_size[1],img_size[0]))
                overlayed = cv2.addWeighted(simg, 1, overlay, 1,0)
                ret, buffer = cv2.imencode('.jpg', overlayed)
                frame = buffer.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # concat frame one by one and show result
    
    def gen_seq(): 
        while True:
            cv2.imwrite('temp/0.png', simg)
            imgseg = image.load_img('temp/0.png', target_size=(img_w, img_h))
            predict_segments = segmentpics(imgseg)
            ret, buffer = cv2.imencode('.png', predict_segments[0])
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
    
    @app.route('/seq_feed')
    def seq_feed():
        return Response(gen_seq(), mimetype='multipart/x-mixed-replace; boundary=frame')
    
    @app.route('/status')
    def status():
        global imgname
        return send_file('static/{}'.format(imgname), mimetype='image/gif')

    @app.route('/process', methods=["GET", "POST"])
    def background_process_test():
        if request.method == "POST":
            data = request.get_json()
            print (type(data))
            if data == "F" : 
                print("the machine moves forward")
                forward()
                create_frame()
            elif data == "B" : 
                print("the machine moves back")
                backward()
                create_frame()
            elif data == "L" : 
                print("the machine moves left")
                turnleft()
                create_frame()
            elif data == "R" : 
                print("the machine moves right")
                turnright()
                create_frame()
            elif data == "S" : 
                print("the machine stops")
                stop()
            elif data == "C" : 
                print("recording frames turned ON/OFF")
                create_imgs()
        return ("nothing")

    if __name__ == "__main__":
        app.run(debug=True, host = ip_adr, port=8030, threaded = True)

