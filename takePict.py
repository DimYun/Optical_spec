#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'dmitry'

import time
import sip
from PyQt4 import QtCore, QtGui
from SimpleCV import Camera, Display, Image
import cv
import Spectrum
import constGlobal


class TakePict(QtGui.QWidget):
    list_cb = [u'Управление',
               u'Открыть изображение',
               u'Получить изображение',
               u'Сохранить изображение',
               u'Рассчитать спектр',
               u'Протестировать выбранную камеру']
    my_image = ''
    count_call_camera = 0
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self)
        self.resize(400, 400)
        self.move(0, 0)
        self.setWindowTitle(u"Получить спектр")
        self.vl_spec = QtGui.QVBoxLayout(self)
        self.select_cam_hl = QtGui.QHBoxLayout()
        self.select_cam_label = QtGui.QLabel(u'Выберите камеру: ')
        self.select_cam_cb = QtGui.QComboBox()
        self.select_cam_cb.addItems(['0', '1', '2', '3', '4'])
        self.select_cam_hl.addWidget(self.select_cam_label)
        self.select_cam_hl.addWidget(self.select_cam_cb)
        self.vl_spec.addLayout(self.select_cam_hl)
        self.cb_manip = QtGui.QComboBox()
        self.cb_manip.addItems(self.list_cb)
        self.vl_spec.addWidget(self.cb_manip)
        self.hl_spec = QtGui.QHBoxLayout()
        self.l_name = QtGui.QLabel()
        self.l_name.setText(u'Имя спектра: ')
        self.hl_spec.addWidget(self.l_name)
        self.le_name = QtGui.QLineEdit()
        self.hl_spec.addWidget(self.le_name)
        self.vl_spec.addLayout(self.hl_spec)
        self.label = QtGui.QLabel()
        self.vl_spec.addWidget(self.label)

        QtCore.QObject.connect(self.cb_manip, QtCore.SIGNAL('activated(int)'),
                               lambda x: self.cb_main(x, parent))

    def cb_main(self, ind=0, parent=None):
        if ind == 0:
            pass
        elif ind == 1:
            self.open_image()
        elif ind == 2:
            self.take_image()
        elif ind == 3:
            self.save_pict()
        elif ind == 4:
            self.calculate_spec(parent)
        elif ind == 5:
            self.test_cam()

    def open_image(self):
        filename_spec = QtGui.QFileDialog.getOpenFileName(self, u'Открыть изображение')
        image_filename = filename_spec.toLocal8Bit().data()
        self.my_image = Image(image_filename)
        self.my_image = self.my_image[100:420, 50:260]
        #self.my_image.show()
        self.simpleCvImageToQtPixMap(self.my_image)
        pixmap = self.simpleCvImageToQtPixMap(self.my_image)
        self.label.setPixmap(pixmap)

    def take_image2(self):
        n_cam = self.select_cam_cb.currentIndex()
        capture = cv.CaptureFromCAM(n_cam)
        self.my_image = cv.QueryFrame(capture)
        #print self.my_image.height
        #print self.my_image.width
        pixmap = self.simpleCvImageToQtPixMap(self.my_image, is_cv=True)
        self.label.setPixmap(pixmap)
        #[50:290, 100:420]

    def take_image(self):
        # Drow image from camera
        # self.my_camera = Camera(prop_set={'width': 320, 'height': 240})
        if self.count_call_camera == 0:
            n_cam = self.select_cam_cb.currentIndex()
            try:
                self.my_camera = Camera(n_cam)
            except:
                constGlobal.error_mes(var=u'Выбранной камеры не существует')
                return
        self.my_image = self.my_camera.getImage()
        #[100:470, 50:170]
        #self.my_image = self.my_image.crop(120,50,350,120)
        pixmap = self.simpleCvImageToQtPixMap(self.my_image)
        self.label.setPixmap(pixmap)
        self.count_call_camera += 1
        # return my_image

    def simpleCvImageToQtPixMap (self, img, is_cv=False):
        #scvImg = self.cam.getImage()
        if is_cv:
            data = img.tostring()
        else:
            data = img.getBitmap().tostring()
        #qtImg = QtGui.QImage(data, img.width, img.height, 3 * img.width, QtGui.QImage.Format_RGB888)
        qtImg = QtGui.QImage(data, img.width, img.height, QtGui.QImage.Format_RGB888)
        pixmap = QtGui.QPixmap()
        pixmap.convertFromImage(qtImg.rgbSwapped())
        return pixmap

    def save_pict(self):
        name_pict = self.le_name.text()
        filename = QtGui.QFileDialog.getSaveFileName(self, u'Сохранить изображение', name_pict + '.png')
        if filename == '':
            return
        else:
            filename = str(filename.toLocal8Bit())
            ind_in = filename.rfind('/')
            ind_out = filename.rfind('.')
            if ind_in == -1:
                ind_in = 0
            if ind_out == -1:
                ind_out = len(filename)
            self.le_name.setText(filename[ind_in:ind_out])
            self.my_image.save(filename)

    def calculate_spec(self, parent):
        lines = []
        for i in range(self.my_image.width):
            summ = 0
            for j in range(self.my_image.height):
                rgb = self.my_image.getPixel(i, j)
                summ = rgb[0]+rgb[1]+rgb[2]
            lines.append(summ)
        name = self.le_name.text()
        if name == '':
            name = 'John Smith_'+time.asctime()
        Spectrum.Spectrum(range(len(lines)), lines, name)
        constGlobal.plot_spec(parent)

    def test_cam(self):
        if self.count_call_camera == 0:
            n_cam = self.select_cam_cb.currentIndex()
            try:
                self.my_camera = Camera(n_cam)
            except:
                constGlobal.error_mes(var=u'Выбранной камеры не существует')
                return
        disp = Display()
        while disp.isNotDone():
            img = self.my_camera.getImage()
            txt = 'Test spectrometer'
            img.drawText(txt, x=0, y=0, fontsize=48)
            if disp.mouseLeft:
                    break
            img.save(disp)
        self.count_call_camera += 1