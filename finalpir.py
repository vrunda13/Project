
import RPi.GPIO as GPIO
import time
from picamera import PiCamera
import datetime
import sqlite3
import sys
sys.path=['', '/home/pi/.virtualenvs/cv/lib/python37.zip', '/home/pi/.virtualenvs/cv/lib/python3.7', '/home/pi/.virtualenvs/cv/lib/python3.7/lib-dynload', '/usr/lib/python3.7', '/home/pi/.virtualenvs/cv/lib/python3.7/site-packages']


import numpy as np
import pytesseract
from PIL import Image
import cv2
import imutils


GPIO.setmode(GPIO.BOARD)
pir=11
serv=13
irsensor=8 

GPIO.setup(pir,GPIO.IN)
GPIO.setup(serv,GPIO.OUT)
GPIO.setup(irsensor,GPIO.IN)
GPIO.setwarnings(False)

camera = PiCamera()

l1=[0,90,0]
conn=sqlite3.connect("Database.db")
cur=conn.cursor()

def visitor_entry():
        
        

def carnumberrecognition(filename):
        img = cv2.imread(filename,cv2.IMREAD_COLOR)
        img = cv2.resize(img, (620,480) )
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray = cv2.bilateralFilter(gray, 11, 17, 17)
        edged = cv2.Canny(gray, 30, 200)
        cnts = cv2.findContours(edged.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)
        cnts = sorted(cnts, key = cv2.contourArea, reverse = True)[:10]
        screenCnt = None
        for c in cnts:
                peri = cv2.arcLength(c, True)
                approx = cv2.approxPolyDP(c, 0.018 * peri, True)
                if len(approx) == 4:
                        screenCnt = approx
                        break
        if screenCnt is None:
                detected = 0
                print("No contour detected")
        else:
                detected = 1
        if detected == 1:
                cv2.drawContours(img, [screenCnt], -1, (0, 255, 0), 3)
        mask = np.zeros(gray.shape,np.uint8)
        new_image = cv2.drawContours(mask,[screenCnt],0,255,-1,)
        new_image = cv2.bitwise_and(img,img,mask=mask)
        (x, y) = np.where(mask == 255)
        (topx, topy) = (np.min(x), np.min(y))
        (bottomx, bottomy) = (np.max(x), np.max(y))
        Cropped = gray[topx:bottomx+1, topy:bottomy+1]
        text = pytesseract.image_to_string(Cropped, config='--psm 11')
        print("Detected Number is:",text)
        regex=r'\d{3,}'
        match=re.search(regex,text)
        if match != None:
                print(match.group(0))
        conn.execute("SELECT carnumber FROM userdata WHERE lastdigit=?", (match.group(0)))
        data=cursor.fetchone()
        if(len(data) == 0):
                visitor_entry()
        '''print("updating")
        conn.execute("UPDATE project_1 SET date =?,intime=? WHERE carnumber='CG04HF 2250'",(l[0],l[1]))
        conn.commit()
        print("updated")
        cur=conn.execute("SELECT * FROM project_1")
        for row in cur:
                print(str(row[0]).ljust(10),row[1].ljust(10),str(row[2]).ljust(10),str(row[3]).ljust(10),str(row[4]).ljust(10),str(row[5]).ljust(10))
        conn.close()
        #cv2.imshow('image',img)
        #cv2.imshow('Cropped',Cropped)
        #cv2.waitKey(0)
        #cv2.destroyAllWindows()'''


        
def getfilename():
        return datetime.datetime.now().strftime("%Y-%m-%d_%H.%M.%S.jpg")
        
def getdatetime():
        return datetime.datetime.now().strftime("%Y-%m-%d_%H.%M.%S")

def irsen():
    while True:
        if GPIO.input(irsensor):
                time.sleep(5)
                print("Object Detected")
                time.sleep(10)
    
    
while True:
    ini=GPIO.input(pir)
    if ini==1:
            filename="/home/pi/Desktop/"+getfilename()
            time.sleep(3)
            camera.start_preview()
            time.sleep(4)
            camera.capture(filename)
            camera.stop_preview()
            time.sleep(2)
            l=getdatetime().split("_")
            carnumberrecognition(filename)
            pwm=GPIO.PWM(13,50)
            pwm.start(7)
            for i in range(0,len(l1)):
                    input("enter")
                    dc=(1./18.)*l1[i]+2
                    pwm.ChangeDutyCycle(dc)
            pwm.stop()
            #text=carnumberrecognition(filename)
            GPIO.cleanup()
            
            #irsen()
