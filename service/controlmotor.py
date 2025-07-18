
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