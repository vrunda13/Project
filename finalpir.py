import RPi.GPIO as GPIO
import time
from picamera import PiCamera
import datetime
import sqlite3
GPIO.setmode(GPIO.BOARD)
i=0
pir=11
serv=13

GPIO.setup(pir, GPIO.IN)
GPIO.setup(serv,GPIO.OUT)
GPIO.setwarnings(False)

camera = PiCamera()

pwm=GPIO.PWM(13,50)

l1=[0,90,0]
conn=sqlite3.connect("database.db")
cur=conn.cursor()
def getdatetime():
        return datetime.datetime.now().strftime("%Y-%m-%d_%H.%M.%S")

while True:
    ini=GPIO.input(pir)
    if ini==1:
        time.sleep(3)
        camera.start_preview()
        time.sleep(4)
        camera.capture("/home/pi/Desktop/image%s.jpg"%i)
        i+=1
        camera.stop_preview()
        time.sleep(2)
        l=getdatetime().split("_")
        print(l)
        print("updating")
        conn.execute("UPDATE project_1 SET date =?,intime=? WHERE carnumber='CG04HF 2250'",(l[0],l[1]))
        conn.commit()
        print("updated")
        cur=conn.execute("SELECT * FROM project_1")
        for row in cur:
            print(str(row[0]).ljust(10),row[1].ljust(10),str(row[2]).ljust(10),str(row[3]).ljust(10),str(row[4]).ljust(10),str(row[5]).ljust(10))
            break;
        conn.close()
        pwm.start(7)
        for i in range(0,len(l1)):
            input("enter")
            dc=(1./18.)*l1[i]+2
            pwm.ChangeDutyCycle(dc)
        pwm.stop()
        GPIO.cleanup()
