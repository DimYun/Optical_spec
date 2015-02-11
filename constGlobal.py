#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'dmitry'

from PyQt4.Qwt5.qplt import *
from PyQt4 import Qt, QtGui, QtCore

list_color = [DarkGreen,
        Blue,
        DarkRed,
        Magenta,
        Cyan,
        DarkBlue,
        DarkCyan,
        DarkGray,
        Green,
        DarkMagenta,
        Red,
        DarkYellow,
        Gray,
        Yellow]
ind_color = 0
list_spec = []

ind_spec = -1


def plot_spec(parent, transform=False, name=''):
    tab_index = parent.tab_index
    parent.spec_plot.clear()
    if transform:
        for spec in list_spec[tab_index]:
            parent.spec_plot.plot(Curve(spec.list_l, spec.list_i, spec.spec_name, Pen(spec.spec_color)))
            parent.spec_plot.plot(Curve(spec.list_l, spec.list_transform,
                                        name + spec.spec_name, Pen(spec.spec_color, Qt.Qt.DashDotLine)))
    else:
        for spec in list_spec[tab_index]:
            parent.spec_plot.plot(Curve(spec.list_l, spec.list_i, spec.spec_name, Pen(spec.spec_color)))
    parent.spec_plot.replot()


def error_mes(var, string_error=u'undefined'):
    # Show error dialog
    variable_err = str(var)
    warn_box = QtGui.QMessageBox.warning(QtGui.QMessageBox(), u'Ошибка',
                                         QtCore.QString.fromLocal8Bit(string_error + ' ' + variable_err))
    return None