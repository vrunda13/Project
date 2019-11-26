
import RPi.GPIO as GPIO
import time
from picamera import PiCamera
from mfrc522 import SimpleMFRC522
import datetime
import sqlite3
import sys
sys.path=['', '/home/pi/.virtualenvs/cv/lib/python37.zip', '/home/pi/.virtualenvs/cv/lib/python3.7', '/home/pi/.virtualenvs/cv/lib/python3.7/lib-dynload', '/usr/lib/python3.7', '/home/pi/.virtualenvs/cv/lib/python3.7/site-packages']


import numpy as np
import pytesseract
from PIL import Image
import cv2
import imutils
import re

count
GPIO.setmode(GPIO.BOARD)
pir=11
serv=13
led1=10
led2=12
led3=16
irsensor1=8
irsensor2=3
irsensor3=5

GPIO.setup(pir,GPIO.IN)
GPIO.setup(serv,GPIO.OUT)
GPIO.setup(irsensor1,GPIO.IN)
GPIO.setup(irsensor2,GPIO.IN)
GPIO.setup(irsensor3,GPIO.IN)
GPIO.setup(led1,GPIO.OUT)
GPIO.setup(led2,GPIO.OUT)
GPIO.setup(led3,GPIO.OUT)

GPIO.output(led1,GPIO.LOW)
GPIO.output(led2,GPIO.LOW)
GPIO.output(led3,GPIO.LOW)
GPIO.setwarnings(False)

camera = PiCamera()

avaliable=['A','B','C']
occupied=[]

l1=[0,90,0]
conn=sqlite3.connect("Database.db")
cur=conn.cursor()
def getdatetime():
        return datetime.datetime.now().strftime("%Y-%m-%d_%H.%M.%S")

        
def visitor_entry_writer():
        reader = SimpleMFRC522()
        try:
                text = input('New data:')
                print("Now place your tag to write")
                reader.write(text)
                print("Written")
        finally:
                GPIO.cleanup()
def visitor_entry_reader():
        reader = SimpleMFRC522()
        try:
                print("Place Card to read")
                id1, text = reader.read()
                print(id1)
                text=text.split()
                k=getdatetime.split("_")
                conn.execute("INSERT INTO visitor(id,Name,carnumber,date,intime,outtime) VALUES(?,?,?,?,?,'0')",(id1,text[0],text[1],k[0],k[1]))
                cur=conn.execute("SELECT * FROM userdata")
                for row in cur:
                        print(str(row[0]).ljust(10),row[1].ljust(10),str(row[2]).ljust(10),str(row[3]).ljust(10),str(row[4]).ljust(10),str(row[5]).ljust(10))
                conn.commit()

        finally:
                GPIO.cleanup()

def irsensor():
        if GPIO.input(irsensor1):
                time.sleep(5)
                print("Object Detected at A")
                print("Parked")
                GPIO.output(led1,GPIO.HIGH) 
                time.sleep(5)
        elif GPIO.input(irsensor2):
                time.sleep(5)
                print("Object Detected at B")
                GPIO.output(led2,GPIO.HIGH)
                print("parked")
                time.sleep(100)
        elif GPIO.input(irsensor3):
                time.sleep(5)
                print("Object Detected at C")
                GPIO.output(led3,GPIO.HIGH)
                print("parked")
                time.sleep(100)
        
                
        

def carnumberrecognition():
        img = cv2.imread('/home/pi/Downloads/3.jpg',cv2.IMREAD_COLOR)
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
                m=match.group(0)
        cur.execute('SELECT carnumber FROM userdata WHERE lastdigit=?',(m,))
        data=cur.fetchone()
        if data is None:
                visitor_entry_writer()
                visitor_entry_reader()
        else :
                print("updating")
                l=getdatetime().split("_")
                conn.execute("UPDATE userdata SET date =?,intime=? WHERE lastdigit=?",(l[0],l[1],m))
                conn.commit()
                print("updated")
                curr=conn.execute("SELECT * FROM userdata")
                for row in curr:
                        print(str(row[0]).ljust(10),row[1].ljust(10),str(row[2]).ljust(10),str(row[3]).ljust(10),str(row[4]).ljust(10),str(row[5]).ljust(10),str(row[6]).ljust(10))
        #cv2.imshow('image',img)
        #cv2.imshow('Cropped',Cropped)
        #cv2.waitKey(0)
        #cv2.destroyAllWindows()


        
def getfilename():
        return datetime.datetime.now().strftime("%Y-%m-%d_%H.%M.%S.jpg")
        

    
def entry():
        global count
        while True:
                ini=GPIO.input(pir)
                if ini==1:
                        filename="/home/pi/Desktop/"+getfilename()
                        time.sleep(3)
                        camera.start_preview()
                        time.sleep(5)
                        camera.capture(filename)
                        camera.stop_preview()
                        time.sleep(2)
                        carnumberrecognition()
                        count+=1
                        if count<=3:
                                pwm=GPIO.PWM(13,50)
                                pwm.start(7)
                                for i in range(0,len(l1)):
                                        input("enter")
                                        dc=(1./18.)*l1[i]+2
                                        pwm.ChangeDutyCycle(dc)
                                 pwm.stop()
                        else :
                                print("Parking lot is full")
                        if(len(avaliable)>0):
                                occupied.append(avaliable[0])
                                print("Go to parking lot ",avaliable[0])
                        irsensor()
                                
                        break;
entry()
GPIO.cleanup()
conn.close()
            
