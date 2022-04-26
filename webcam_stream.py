import numpy as np
import cv2
import face_recognition
import pickle
import time


class Webcam(object):
    def __init__(self):
        self.video = cv2.VideoCapture(0)

    def framing(self):
        success, data = self.video.read()

        cv2.imwrite('./static/client_img/client.jpg', data)

        ret, jpeg = cv2.imencode('.jpg', data)
        return jpeg.tobytes()
