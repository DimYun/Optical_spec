#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'dmitry'

#from SimpleCV import Image, Display, DrawingLayer, Color
import SimpleCV
from time import sleep
import sys
from PyQt4.Qwt5.qplt import *
from PyQt4 import QtCore, QtGui

reload(sys)
sys.setdefaultencoding('utf8')

myDisplay = SimpleCV.Display()
my_image = SimpleCV.Image('capture.png')

lines = []
for i in range(my_image.width):
    summ = 0
    for j in range(my_image.height):
        rgb = my_image.getPixel(i, j)
        summ += rgb[0]+rgb[1]+rgb[2]
    lines.append(summ)

#print len(range(len(lines)))
#print lines

class GUI_Device(QtGui.QWidget):
    #Draw main window with controls
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.verticalLayout = QtGui.QVBoxLayout()
        qwtPlot = Plot()
        self.verticalLayout.addWidget(qwtPlot)
        qwtPlot.plot(Curve(list(xrange(len(lines))), lines))

app = QtGui.QApplication(sys.argv)
sw = GUI_Device()
sw.show()
sys.exit(app.exec_())
# my_Layer = DrawingLayer((my_image.width, my_image.height))
# my_Layer.rectangle((50, 20), (250, 60), filled=True, color=Color.GREEN)
# my_Layer.setFontSize(45)
# my_Layer.text(u'Химия', (50, 20), color=Color.WHITE)
# my_image.addDrawingLayer(my_Layer)
# my_image.applyLayers()
#
# my_image.save(u'Химия.png')
#
# my_image.save(myDisplay)
# while not myDisplay.isDone():
#     sleep(0.1)
