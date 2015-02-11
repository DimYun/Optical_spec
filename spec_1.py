#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'dmitry'

from PyQt4 import QtCore, QtGui, Qt
from PyQt4.Qwt5.qplt import *
from PyQt4.Qwt5 import Qwt, QwtPlot
from SimpleCV import Camera, Display, Image

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
        self.spec_plot = Plot()
        self.spec_plot.setAxisTitle(QwtPlot.xBottom, u'wawelenght, nm')
        self.spec_plot.setAxisTitle(QwtPlot.yLeft, u'I')
        self.plotCanvas = self.spec_plot.canvas()
        self.plotCanvas.setMouseTracking(True)
        #self.plotCanvas.installEventFilter(ManipulationEventFilterBuilder(self))
        self.vl_spec.addWidget(self.spec_plot)

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
    def take_image(self):
        # Drow image from camera
        # self.my_camera = Camera(prop_set={'width': 320, 'height': 240})
        if self.count_call_camera == 0:
            n_cam = self.select_cam_cb.currentIndex()
            try:
                self.my_camera = Camera(1)
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


reload(sys)
sys.setdefaultencoding('utf8')
app = QtGui.QApplication(sys.argv)
sw = TakePict()
desktop = QtGui.QApplication.desktop()
x = desktop.width() / 2
y = desktop.height() / 2
sw.move(x, y)
sw.show()
sys.exit(app.exec_())