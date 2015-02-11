# -*- coding: utf-8 -*-
from PyQt4 import QtCore, QtGui
import mathManip
import constGlobal


class CalcPeakWindow(QtGui.QWidget):
    #Show dialog window for calc peaks area
    parent = 0
    #count_cal = []
    def __init__(self, parent=None):
        self.parent = parent
        QtGui.QWidget.__init__(self, None)
        self.setWindowTitle(u"Выбор пиков")
        self.move(0, 0)
        self.vl_main = QtGui.QVBoxLayout(self)
        self.cb_peak_select = QtGui.QCheckBox(u"Выбор пика", self)
        self.vl_main.addWidget(self.cb_peak_select)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.label = QtGui.QLabel(self)
        self.label.setText(u"Название пика: ")
        self.horizontalLayout.addWidget(self.label)
        self.le_name = QtGui.QLineEdit(self)
        self.horizontalLayout.addWidget(self.le_name)
        self.vl_main.addLayout(self.horizontalLayout)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.label_2 = QtGui.QLabel(self)
        self.label_2.setText(u"Левая граница:")
        self.horizontalLayout_2.addWidget(self.label_2)
        self.le_left_bound = QtGui.QLineEdit(self)
        self.le_left_bound.setValidator(QtGui.QDoubleValidator(0.0, 500.0, 3, self))
        self.horizontalLayout_2.addWidget(self.le_left_bound)
        self.vl_main.addLayout(self.horizontalLayout_2)
        self.horizontalLayout_3 = QtGui.QHBoxLayout()
        self.label_3 = QtGui.QLabel(self)
        self.label_3.setText(u"Правая граница:")
        self.horizontalLayout_3.addWidget(self.label_3)
        self.le_right_bound = QtGui.QLineEdit(self)
        self.le_right_bound.setValidator(QtGui.QDoubleValidator(0.0, 500.0, 3, self))
        self.horizontalLayout_3.addWidget(self.le_right_bound)
        self.vl_main.addLayout(self.horizontalLayout_3)
        self.te_peaks = QtGui.QTextEdit(self)
        self.vl_main.addWidget(self.te_peaks)
        self.label_4 = QtGui.QLabel(self)
        self.label_4.setText(u"Тип расчета: ")
        self.vl_main.addWidget(self.label_4)
        self.comboBox = QtGui.QComboBox(self)

        comboBoxList = [u'По трапеции', u'По Симпсону', u'По Гаусу']
        self.comboBox.addItems(comboBoxList)

        self.vl_main.addWidget(self.comboBox)
        self.lCalc = QtGui.QLabel(self)
        self.vl_main.addWidget(self.lCalc)
        self.pbView = QtGui.QPushButton(self)
        self.vl_main.addWidget(self.pbView)
        self.pbCancel = QtGui.QPushButton(self)
        self.vl_main.addWidget(self.pbCancel)
        self.pbAssept = QtGui.QPushButton(self)
        self.vl_main.addWidget(self.pbAssept)
        self.pbView.setText(u"Просмотр")
        self.pbCancel.setText(u"Отмена")
        self.pbAssept.setText(u"Принять")

        QtCore.QObject.connect(self.pbView,
            QtCore.SIGNAL('clicked()'), lambda: self.viewPeakInt(parent))
        QtCore.QObject.connect(self.pbCancel,
            QtCore.SIGNAL('clicked()'), self.cancelPeak)
        QtCore.QObject.connect(self.pbAssept,
            QtCore.SIGNAL('clicked()'), lambda: self.asseptPeak(parent))
        QtCore.QObject.connect(self.cb_peak_select,
            QtCore.SIGNAL("stateChanged(int)"), lambda x: self.toggleZoom(x, parent))

    def closeEvent(self, event):
        # Set plot widget to normal state
        map(lambda z: z.setEnabled(True), self.parent.spec_plot.zoomers)
        event.accept()

    def viewPeakInt(self, parent=None):
        # Call when user push button view
        spec_index = parent.tab_index
        if constGlobal.list_spec[spec_index] == []:
            constGlobal.error_mes('Нет ни одного файла со спектром', 'M: CalcPeakWindows, str: 81')
        else:
            name = self.le_name.text()
            x_left = float(self.le_left_bound.text())
            x_right = float(self.le_right_bound.text())
            type_int = self.comboBox.currentIndex()
            mathManip.peakIntegr(name, x_left, x_right, type_int, spec_index)
            self.te_peaks.clear()
            for spec in constGlobal.list_spec[spec_index]:
                self.te_peaks.append(spec.spec_name + ': ')
                text = ''
                for peak in spec.peaks:
                    text += '  ' + peak['name'] + '\n  ' + str(peak['data_i']) + '\n  ' + str(peak['data_S']) + '\n'
                self.te_peaks.append(text)
            if type_int == 2:
                constGlobal.plot_spec(parent, transform=True, name=u'Gauss ')

    def toggleZoom(self, state, parent):
        # Disable or enable zoomers for plot
        #self.count_cal = []
        if state == 0:
            map(lambda z: z.setEnabled(True), parent.spec_plot.zoomers)
            #self.count_cal.append(parent.spec_plot.zoomers)
        elif state == 2:
            map(lambda z: z.setEnabled(False), parent.spec_plot.zoomers)
            #self.count_cal.append(parent.spec_plot.zoomers)

    def cancelPeak(self, parent):
        # Cancel peak calculate
        spec_index = parent.tab_index
        if constGlobal.list_spec[spec_index] == []:
            constGlobal.error_mes('Нет ни одного файла со спектром', 'M: CalcPeakWindows, str: 111')
        else:
            self.te_peaks.clear()
            for spec in constGlobal.list_spec[spec_index]:
                spec.peaks.pop()
            self.te_peaks.clear()
            for spec in constGlobal.list_spec[spec_index]:
                self.te_peaks.append(spec.spec_name + ': ')
                text = ''
                for peak in spec.peaks:
                    text += '  ' + peak['name'] + '\n  ' + str(peak['data_i']) + '\n  ' + str(peak['data_S'] + '\n')
                self.te_peaks.append(text)
            self.le_left_bound.setText('')
            self.le_right_bound.setText('')

    def asseptPeak(self, parent):
        #Assep peaks and put it into table
        spec_index = parent.tab_index
        if constGlobal.list_spec[spec_index] == []:
            constGlobal.error_mes('Нет ни одного файла со спектром', 'M: CalcPeakWindows, str: 129')
        else:
            parent.tv_spec.setColumnCount(len(constGlobal.list_spec[spec_index]))
            parent.tv_spec.setRowCount(len(constGlobal.list_spec[spec_index][0].peaks)*2)

            j = 0
            for spec in constGlobal.list_spec[spec_index]:
                #Set name to table headers
                parent.tv_spec.setHorizontalHeaderItem(j, QtGui.QTableWidgetItem(spec.spec_name))

                #Set name to cell and vertical headers
                c = 0
                for peak in spec.peaks:
                    parent.tv_spec.setVerticalHeaderItem(c, QtGui.QTableWidgetItem(peak['name']+'_I'))
                    parent.tv_spec.setItem(c, j, QtGui.QTableWidgetItem(str(peak['data_i'])))
                    parent.tv_spec.setVerticalHeaderItem(c+1, QtGui.QTableWidgetItem(peak['name']+'_S'))
                    parent.tv_spec.setItem(c+1, j, QtGui.QTableWidgetItem(str(peak['data_S'])))
                    c += 2
                j += 1