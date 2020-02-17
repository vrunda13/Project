
import datetime
import sqlite3
import sys
sys.path=['', '/home/pi/.virtualenvs/cv/lib/python37.zip', '/home/pi/.virtualenvs/cv/lib/python3.7', '/home/pi/.virtualenvs/cv/lib/python3.7/lib-dynload', '/usr/lib/python3.7', '/home/pi/.virtualenvs/cv/lib/python3.7/site-packages']

import cv2
import imutils
import numpy as np
import pytesseract
from PIL import Image
import re
import time
conn=sqlite3.connect("Database.db")
cur=conn.cursor()

'''def getfilename():
        return datetime.datetime.now().strftime("%Y-%m-%d_%H.%M.%S.jpg")'''
        


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
        '''if data is None:
                #visitor_entry_writer()
                #visitor_entry_reader()
        else :
                print("updating")
                l=getdatetime().split("_")
                conn.execute("UPDATE userdata SET date =?,intime=? WHERE lastdigit=?",(l[0],l[1],m))
                conn.commit()
                print("updated")
                curr=conn.execute("SELECT * FROM userdata")
                for row in curr:
                        print(str(row[0]).ljust(10),row[1].ljust(10),str(row[2]).ljust(10),str(row[3]).ljust(10),str(row[4]).ljust(10),str(row[5]).ljust(10),str(row[6]).ljust(10))'''
        cv2.imshow('image',img)
        cv2.imshow('Cropped',Cropped)
        cv2.waitKey(0)
        cv2.destroyAllWindows()





carnumberrecognition()
                        
