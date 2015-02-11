#!/usr/bin/env python

from PyQt4 import Qt
import PyQt4.Qwt5 as Qwt
from PyQt4.Qwt5.anynumpy import asarray, Float


# Usage:
# curve = errbars.ErrorBarYPlotCurve(x=x, y=y, dy=dy, name='2')
# a = Plot()
# curve.attach(a)
# a.clearZoomStack()

class ErrorBarYPlotCurve(Qwt.QwtPlotCurve):
    def __init__(self, name='',
                 x=[], y=[], dy=None,
                 curvePen=Qt.QPen(Qt.Qt.black, 2),
                 curveStyle=Qwt.QwtPlotCurve.Lines,
                 curveSymbol=Qwt.QwtSymbol(Qwt.QwtSymbol.Ellipse,
                                           Qt.QBrush(Qt.Qt.red),
                                           Qt.QPen(Qt.Qt.black, 2),
                                           Qt.QSize(9, 9)),
                 errorPen=Qt.QPen(Qt.Qt.red, 2),
                 errorCap=10,
                 errorOnTop=False,
                 ):

        Qwt.QwtPlotCurve.__init__(self)
        self.setTitle(Qt.QString(name))
        self.setData(x, y, dy)
        self.setPen(curvePen)
        self.setStyle(curveStyle)
        self.setSymbol(curveSymbol)
        self.errorPen = errorPen
        self.errorCap = errorCap
        self.errorOnTop = errorOnTop

    def setData(self, x, y, dy=None):
        self.__x = asarray(x, Float)
        if len(self.__x.shape) != 1:
            raise RuntimeError('len(asarray(x).shape) != 1')

        self.__y = asarray(y, Float)
        if len(self.__y.shape) != 1:
            raise RuntimeError('len(asarray(y).shape) != 1')
        if len(self.__x) != len(self.__y):
            raise RuntimeError('len(asarray(x)) != len(asarray(y))')

        if dy is None:
            self.__dy = dy
        else:
            self.__dy = asarray(dy, Float)
        if len(self.__dy.shape) not in [0, 1, 2]:
            raise RuntimeError('len(asarray(dy).shape) not in [0, 1, 2]')

        Qwt.QwtPlotCurve.setData(self, self.__x, self.__y)

    def boundingRect(self):
        xmin = min(self.__x)
        xmax = max(self.__x)

        if self.__dy is None:
            ymin = min(self.__y)
            ymax = max(self.__y)
        elif len(self.__dy.shape) in [0, 1]:
            ymin = min(self.__y - self.__dy)
            ymax = max(self.__y + self.__dy)
        else:
            ymin = min(self.__y - self.__dy[0])
            ymax = max(self.__y + self.__dy[1])

        return Qt.QRectF(xmin, ymin, xmax-xmin, ymax-ymin)

    def drawFromTo(self, painter, xMap, yMap, first, last=-1):
        if last < 0:
            last = self.dataSize() - 1

        if self.errorOnTop:
            Qwt.QwtPlotCurve.drawFromTo(self, painter, xMap, yMap, first, last)

        painter.save()
        painter.setPen(self.errorPen)

        if self.__dy is not None:
            if len(self.__dy.shape) in [0, 1]:
                ymin = (self.__y - self.__dy)
                ymax = (self.__y + self.__dy)
            else:
                ymin = (self.__y - self.__dy[0])
                ymax = (self.__y + self.__dy[1])
            x = self.__x
            n, i, = len(x), 0
            lines = []
            while i < n:
                xi = xMap.transform(x[i])
                lines.append(
                    Qt.QLine(xi, yMap.transform(ymin[i]),
                             xi, yMap.transform(ymax[i])))
                i += 1
            painter.drawLines(lines)
            if self.errorCap > 0:
                cap = self.errorCap/2
                n, i = len(x), 0
                lines = []
                while i < n:
                    xi = xMap.transform(x[i])
                    lines.append(
                        Qt.QLine(xi - cap, yMap.transform(ymin[i]),
                                 xi + cap, yMap.transform(ymin[i])))
                    lines.append(
                        Qt.QLine(xi - cap, yMap.transform(ymax[i]),
                                 xi + cap, yMap.transform(ymax[i])))
                    i += 1
            painter.drawLines(lines)

        painter.restore()

        if not self.errorOnTop:
            Qwt.QwtPlotCurve.drawFromTo(self, painter, xMap, yMap, first, last)
