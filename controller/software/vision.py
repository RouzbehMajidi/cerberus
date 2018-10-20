import numpy as np
import argparse
import cv2
import os
import imutils
from imutils.video import videostream
from collections import deque
import matplotlib.pyplot as plt
import serial

CMD_TRIGGERED = b'T'
CMD_ACTIVE = b'A'
CMD_OFF = b'O'

alarm_active = False
alarm_triggered = False
system_available = False

dataset_path_prefix = os.getcwd() + '/controller/software/datasets/'

CLASSES = ["background", "aeroplane", "bicycle", "bird", "boat","bottle", "bus", "car", "cat", "chair", "cow", "diningtable","dog", "horse", "motorbike", "person", "pottedplant", "sheep", "sofa", "train", "tvmonitor"]
FILTERED_CLASSES = ["background", "bicycle", "bird","bottle", "bus", "car", "cat","dog","motorbike","person"]
COLORS = np.random.uniform(0, 255, size=(len(CLASSES), 3))
net = cv2.dnn.readNetFromCaffe(dataset_path_prefix + 'MobileNetSSD_deploy.prototxt', dataset_path_prefix + 'MobileNetSSD_deploy.caffemodel')

video_capture = cv2.VideoCapture(0)

count = 0

try:
    ser = serial.Serial("/dev/cu.usbmodem141240", 9600)
    system_available = True
    ser.write(CMD_ACTIVE)
except:
    print("Warning: Alarm alert system not available")

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
        confidence = detections[0, 0, i, 2]

        if confidence > 0.75:
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

    if "person" in objects and alarm_active and not alarm_triggered:
        if system_available:
            ser.write(CMD_TRIGGERED)
        alarm_triggered = True
    elif "person" not in objects and alarm_active and alarm_triggered:
        if system_available:
            ser.write(CMD_ACTIVE)
        alarm_triggered = False

    if alarm_triggered:
        cv2.putText(frame, "Alarm triggered", (5, 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,255), 2)
    elif alarm_active:
        cv2.putText(frame, "Alarm active", (5, 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 2)
    else:
        cv2.putText(frame, "Alarm off", (5, 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,0,0), 2)

    cv2.imshow("Output", frame)

    keypress = cv2.waitKey(1)
    if keypress == ord(" ") & 0xFF:
        alarm_active = not alarm_active
        if system_available and alarm_active:
            ser.write(CMD_ACTIVE)
        elif system_available and not alarm_active:
            ser.write(CMD_OFF)
    elif keypress ==  ord("q") & 0xFF:
        break


if system_available:
    ser.write(CMD_OFF)

video_capture.release()
cv2.destroyAllWindows()