# -*- coding: utf-8 -*-
from PyQt4 import QtCore, QtGui
import mathManip
import constGlobal


class ImportPeak(QtGui.QWidget):
    count_tab_list = []

    def __init__(self, parent=None, parent_main=None):
        self.parent = parent
        QtGui.QWidget.__init__(self, None)
        self.setWindowTitle(u"Выбор вкладки для импорта")
        self.move(0, 0)
        self.vl_main = QtGui.QVBoxLayout(self)
        self.l_main = QtGui.QLabel()
        self.l_main.setText(u'Введите номер вкладки для импорта данных')
        # self.l_main.setWordWrap(True)
        self.vl_main.addWidget(self.l_main)
        self.cb_tab_spec = QtGui.QComboBox()
        self.count_tab = parent_main.tabWidget.count()
        for i in range(self.count_tab-1):
            self.count_tab_list.append(str(i+1))
        self.cb_tab_spec.addItems(self.count_tab_list)
        self.vl_main.addWidget(self.cb_tab_spec)
        self.pb_ok = QtGui.QPushButton()
        self.pb_ok.setText(u'Ок')
        self.vl_main.addWidget(self.pb_ok)
        self.pb_close = QtGui.QPushButton()
        self.pb_close.setText(u'Закрыть')
        self.vl_main.addWidget(self.pb_close)

        QtCore.QObject.connect(self.pb_ok,
            QtCore.SIGNAL('clicked()'), lambda: self.push_ok(parent))
        QtCore.QObject.connect(self.pb_close,
            QtCore.SIGNAL('clicked()'), self.close)

    def push_ok(self, parent=None):
        # when push button ok
        number_spec = self.cb_tab_spec.currentText()
        parent.import_spec = number_spec
        # parent.emit(QtCore.SIGNAL('NumTab(int)'), number_spec)
        parent.import_spec_data()
        self.close()