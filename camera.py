#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'dmitry'

from SimpleCV import Camera, Image, Display, DrawingLayer, Color
import cv
from PyQt4 import QtGui, QtCore
from time import sleep
import sys

reload(sys)
sys.setdefaultencoding('utf8')

class OpenCVQImage(QtGui.QImage):

    def __init__(self, opencvBgrImg):
        depth, nChannels = opencvBgrImg.depth, opencvBgrImg.nChannels
        if depth != cv.IPL_DEPTH_8U or nChannels != 3:
            raise ValueError("the input image must be 8-bit, 3-channel")
        w, h = cv.GetSize(opencvBgrImg)
        opencvRgbImg = cv.CreateImage((w, h), depth, nChannels)
        # it's assumed the image is in BGR format
        cv.CvtColor(opencvBgrImg, opencvRgbImg, cv.CV_BGR2RGB)
        self._imgData = opencvRgbImg.tostring()
        super(OpenCVQImage, self).__init__(self._imgData, w, h,
            QtGui.QImage.Format_RGB888)


class MainGUI(QtGui.QWidget):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        # self.my_camera = Camera(prop_set={'width': 320, 'height': 240})
        self.my_camera = Camera(0)
        self.my_camera2 = Camera(1)
        # self.my_display = Display(resolution=(320, 240))

        self.my_image = self.my_camera.getImage()
        self.my_image.save(u'Химия2.png')

        self.my_image = self.my_camera2.getImage(2)
        self.my_image.save(u'Химия3.png')

        self.vl_spec = QtGui.QVBoxLayout(self)
        self.cb_manip = QtGui.QComboBox()
        self.cb_manip.addItems(['1', '2', '3'])
        self.vl_spec.addWidget(self.cb_manip)

        self.pixmap = self.simpleCvImageToQtPixMap(self.my_image)
        self.label = QtGui.QLabel(self)
        self.label.setPixmap(self.pixmap)
        self.vl_spec.addWidget(self.label)

    def simpleCvImageToQtPixMap (self, img):
        #scvImg = self.cam.getImage()
        data = img.getBitmap().tostring()
        #qtImg = QtGui.QImage(data, img.width, img.height, 3 * img.width, QtGui.QImage.Format_RGB888)
        qtImg = QtGui.QImage(data,img.width,img.height, QtGui.QImage.Format_RGB888)
        pixmap = QtGui.QPixmap()
        pixmap.convertFromImage(qtImg.rgbSwapped())
        return pixmap

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    sw = MainGUI()
    sw.show()
    sys.exit(app.exec_())

# while not my_display.isDone():
#     my_camera.getImage().save(my_display)
#     sleep(.1)