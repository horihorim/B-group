#!/usr/bin/python
# -*- coding: utf-8 -*-

# import
import cv2
from datetime import datetime
import json

# read data file
face_cascade_path = '/usr/share/opencv/haarcascades/'\
                    'haarcascade_frontalface_default.xml'
eye_cascade_path = '/usr/share/opencv/haarcascades/'\
                   'haarcascade_eye.xml'

face_cascade = cv2.CascadeClassifier(face_cascade_path)
eye_cascade = cv2.CascadeClassifier(eye_cascade_path)

# open VideoCapture
cap = cv2.VideoCapture(0)

# definition
path_w = '/home/pi/Desktop/cloud/log/log.json'
room_Name = 'C201'

def out_res(in_room_no, in_timestamp, in_occupied):
    #print in_timestamp.isoformat()
    out_list = {"room-no": in_room_no, "timestamp": in_timestamp, "occupied": in_occupied}
    
    with open(path_w, mode='a') as f:
        json.dump(out_list,f,indent=4)

def main():
    while True:
        # get image
        ret, img = cap.read()    
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
        # face detect
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5)
        human_num = len(faces)
    
        # if face detect
        if(human_num > 0):
            #time = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
            time = datetime.now().isoformat()
            #time.microsecond = 0
            #time = time.isoformat()
            print time , ' human_num : ', human_num
            out_res(room_Name, time, human_num)
        
        # draw rect  
        for x, y, w, h in faces:
            cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)
            #face = img[y: y + h, x: x + w]
            #face_gray = gray[y: y + h, x: x + w]
            #eyes = eye_cascade.detectMultiScale(face_gray)
            #for (ex, ey, ew, eh) in eyes:
            #    cv2.rectangle(face, (ex, ey), (ex + ew, ey + eh), (0, 255, 0), 2)
        
        # show img
        cv2.imshow('video image', img)
    
        # wait key
        key = cv2.waitKey(10)
    
        # quit
        if key == 27:  # ESCキーで終了
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()