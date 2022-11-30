from threading import Thread

import cv2
from PyQt5 import QtGui, Qt
from PyQt5.QtGui import QPixmap, QColor
import zmq
import base64
import numpy as np
from PyQt5.QtWidgets import QLabel


class CameraStream(QLabel):
    def __init__(self):
        super().__init__()
        self.CAMERA_WIDTH = 640
        self.CAMERA_HEIGHT = 480

        grey = QPixmap(self.CAMERA_WIDTH, self.CAMERA_HEIGHT)
        grey.fill(QColor('darkGray'))
        self.last_frame: QPixmap = grey

        self.context = zmq.Context()
        self.camera_socket = self.context.socket(zmq.SUB)
        self.camera_socket.connect('tcp://192.168.0.115:6666')
        self.camera_socket.setsockopt_string(zmq.SUBSCRIBE, np.compat.unicode(''))

        self.__updateThread: Thread = Thread(target=self.__update, args=(), daemon=True)
        self.__updateThread.start()

    def draw(self):
        self.setPixmap(self.last_frame)

    def __update(self):
        while True:
            frame = self.camera_socket.recv_string()
            img = base64.b64decode(frame)
            npimg = np.fromstring(img, dtype=np.uint8)
            source = cv2.imdecode(npimg, 1)
            self.last_frame = self.__convert_cv_qt(source)


    def __convert_cv_qt(self, cv_img):
        """Convert from an opencv image to QPixmap"""
        rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        h, w, ch = cv_img.shape
        bytes_per_line = ch * w
        convert_to_Qt_format = QtGui.QImage(rgb_image.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)
        p = convert_to_Qt_format.scaled(self.CAMERA_WIDTH, self.CAMERA_HEIGHT)
        return QPixmap.fromImage(p)

