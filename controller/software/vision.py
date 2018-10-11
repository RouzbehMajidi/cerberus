import numpy as np
import argparse
import cv2
import os
import imutils
from imutils.video import videostream
from collections import deque
import matplotlib.pyplot as plt
import serial

CMD_OFF = b'O'
CMD_ACTIVE = b'A'
CMD_TRIGGERED = b'T'

alarm_ready = True
alarm_active = False

dataset_path_prefix = os.getcwd() + '/controller/software/datasets/'

CLASSES = ["background", "aeroplane", "bicycle", "bird", "boat","bottle", "bus", "car", "cat", "chair", "cow", "diningtable","dog", "horse", "motorbike", "person", "pottedplant", "sheep", "sofa", "train", "tvmonitor"]
FILTERED_CLASSES = ["background", "bicycle", "bird","bottle", "bus", "car", "cat","dog","motorbike","person"]
COLORS = np.random.uniform(0, 255, size=(len(CLASSES), 3))
net = cv2.dnn.readNetFromCaffe(dataset_path_prefix + 'MobileNetSSD_deploy.prototxt', dataset_path_prefix + 'MobileNetSSD_deploy.caffemodel')

video_capture = cv2.VideoCapture(0)

count = 0
    
ser = serial.Serial("/dev/cu.usbmodem143220", 9600)

ser.write(CMD_ACTIVE)

while True:
    _, frame = video_capture.read()
    frame = cv2.flip(frame,90)
    frame = imutils.resize(frame, width=480)
    (h, w) = frame.shape[:2]

    blob = cv2.dnn.blobFromImage(cv2.resize(frame, (300, 300)), 0.007843, (300, 300), 127.5)
    net.setInput(blob)
    detections = net.forward()
    objects = []

    for i in np.arange(0, detections.shape[2]):
        # extract the confidence (i.e., probability) associated with the
        # prediction
        confidence = detections[0, 0, i, 2]

        # filter out weak detections by ensuring the `confidence` is
        # greater than the minimum confidence
        if confidence > 0.75:
            # extract the index of the class label from the `detections`,
            # then compute the (x, y)-coordinates of the bounding box for
            # the object
            index = int(detections[0, 0, i, 1])
            box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
            (startX, startY, endX, endY) = box.astype("int")

            # display the prediction
            label = "{}: {:.2f}%".format(CLASSES[index], confidence * 100)
            if CLASSES[index] in FILTERED_CLASSES:
                objects.append(CLASSES[index])

            y = startY - 15 if startY - 15 > 15 else startY + 15

            cv2.rectangle(frame, (startX, startY), (endX, endY),COLORS[index], 2)
            cv2.putText(frame, label, (startX, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, COLORS[index], 2)

    if "person" in objects and alarm_ready and not alarm_active:
        ser.write(CMD_TRIGGERED)
        alarm_active = True
    elif "person" not in objects and alarm_ready and alarm_active:
        ser.write(CMD_ACTIVE)
        alarm_active = False

        
    if alarm_active:
        cv2.putText(frame, "Alarm Triggered", (10, 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,255), 2)
    elif alarm_ready:
        cv2.putText(frame, "Alarm Ready", (10, 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 2)
    else:
        cv2.putText(frame, "Alarm Off", (10, 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,0,0), 2)

    cv2.imshow("Output", frame)

    if cv2.waitKey(1)== ord("q") & 0xFF:
        break

ser.write(CMD_OFF)
video_capture.release()
cv2.destroyAllWindows()