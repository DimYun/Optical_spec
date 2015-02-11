#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import time
from PyQt4 import QtCore, QtGui, Qt
from PyQt4.Qwt5.qplt import *
from PyQt4.Qwt5 import Qwt, QwtPlot
import constGlobal
import takePict
import SmoothZ
import CalcPeakWindow
import Spectrum
import import_peak


class SelectionRectangle(QwtPlotItem):
    def __init__(self, interval, title="Selection"):
        QwtPlotItem.__init__(self, QwtText(title))
        self.pen = QPen(Black, 2)
        self.brush = QBrush(White)
        self.interval = interval

    def draw(self, painter, xMap, yMap, canvas):
        painter.setPen(self.pen)
        painter.setBrush(self.brush)
        painter.drawRect(self.interval[0], 0, self.interval[1] - self.interval[0], canvas.height())


class ManipulationEventFilterBuilder(QObject):
    def __init__(self, parent):
        QObject.__init__(self, parent)
        self.parent = parent
        self.parent.selectionStart = None
        self.parent.selectedRectangle = None

    def eventFilter(self, source, event):
        # New event filter for objects
        if event.type() == QtCore.QEvent.MouseMove and source is self.parent.plotCanvas:
            pos = event.pos()
            x = round(float(self.parent.spec_plot.invTransform(self.parent.spec_plot.xBottom, pos.x())), 3)
            y = round(float(self.parent.spec_plot.invTransform(self.parent.spec_plot.yLeft, pos.y())), 3)
            self.parent.spec_plot.setToolTip('x = %.6g, \ny = %.6g' % (x, y))

        if (event.type() == QtCore.QEvent.MouseButtonPress and source is self.parent.plotCanvas) \
            and not self.parent.spec_plot.zoomers[0].isEnabled():
            self.parent.selectionStart = event.pos().x()

        if event.type() == QtCore.QEvent.MouseMove and (source is self.parent.plotCanvas and
            self.parent.selectionStart is not None) and not self.parent.spec_plot.zoomers[0].isEnabled():
            pos = event.pos()
            xpos = pos.x()
            self.parent.selectedArea = (min(xpos, self.parent.selectionStart), max(xpos, self.parent.selectionStart))

            if self.parent.selectedRectangle is not None:
                self.parent.selectedRectangle.detach()

            self.parent.selectedRectangle = SelectionRectangle(self.parent.selectedArea)
            self.parent.selectedRectangle.attach(self.parent.spec_plot)
            self.parent.spec_plot.replot()

        if (event.type() == QtCore.QEvent.MouseButtonRelease and
            source is self.parent.plotCanvas and self.parent.selectionStart is
            not None) and not self.parent.spec_plot.zoomers[0].isEnabled():
            pos = event.pos()
            x1 = self.parent.spec_plot.invTransform(Qwt.QwtPlot.xBottom, min(self.parent.selectionStart, pos.x()))
            x1 = round(float(x1), 3)
            x2 = self.parent.spec_plot.invTransform(Qwt.QwtPlot.xBottom, max(self.parent.selectionStart, pos.x()))
            x2 = round(float(x2), 3)
            if self.parent.selectedRectangle is not None:
                self.parent.selectedRectangle.detach()

            self.parent.spec_plot.replot()
            self.parent.selectionStart = None
            try:
                self.parent.CalcPeaks.le_right_bound.setText(str(x2))
                self.parent.CalcPeaks.le_left_bound.setText(str(x1))
            except AttributeError, var:
                print var
                pass
        return QtGui.QWidget.eventFilter(self, source, event)


class SpecTab(QtGui.QWidget):
    # Class for common elements in spec tab
    list_cb = [u'Управление',
               u'Открыть спектр',
               u'Открыть директорию',
               u'Сохранить спектры',
               u'Очистить полотно и спектры',
               u'Открыть вкладку',
               u'Закрыть вкладку']
    list_cb_spec = [u'Работа со спектром',
                    u'Получить спектр',
                    u'Удалить последний спектр',
                    u'Обработка спектра',
                    u'Выбор пиков']
    constGlobal.ind_spec += 1
    constGlobal.list_spec.append([])

    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.tab_index = constGlobal.ind_spec
        self.tab = QtGui.QWidget()
        self.vl_spec = QtGui.QVBoxLayout(self.tab)
        self.cb_manip = QtGui.QComboBox(self.tab)
        self.cb_manip.addItems(self.list_cb)
        self.vl_spec.addWidget(self.cb_manip)
        self.cb_spec = QtGui.QComboBox(self.tab)
        self.cb_spec.addItems(self.list_cb_spec)
        self.vl_spec.addWidget(self.cb_spec)
        self.tv_spec = QtGui.QTableWidget(self.tab)
        self.tv_spec.setToolTip(unicode('Для копирования данных \n\
выделите нужный диапазон и используйте Ctrl+c', 'utf-8'))
        QShortcut(QKeySequence('Ctrl+c'), self.tv_spec).activated.connect(self._handleTableCopy)
        self.vl_spec.addWidget(self.tv_spec)
        self.spec_plot = Plot(self.tab)
        self.spec_plot.setAxisTitle(QwtPlot.xBottom, u'wawelenght, nm')
        self.spec_plot.setAxisTitle(QwtPlot.yLeft, u'I')
        self.plotCanvas = self.spec_plot.canvas()
        self.plotCanvas.setMouseTracking(True)
        self.plotCanvas.installEventFilter(ManipulationEventFilterBuilder(self))
        self.vl_spec.addWidget(self.spec_plot)

        self.clip = QtGui.QApplication.clipboard()

        QtCore.QObject.connect(self.cb_manip, QtCore.SIGNAL('activated(int)'),
                               lambda x: self.cbMain(x, parent))
        QtCore.QObject.connect(self.cb_spec, QtCore.SIGNAL('activated(int)'),
                               lambda x: self.cbSpec(x, parent))

    def cbMain(self, ind=0, parent=None):
        if ind == 0:
            pass
        elif ind == 1:
            filename_spec = QtGui.QFileDialog.getOpenFileName(self, u'Открыть спектр')
            if filename_spec == '':
                return
            name_dir = str(filename_spec.toLocal8Bit())
            file_spec = open(name_dir, 'r')
            text_spec = file_spec.read()
            text_spec = text_spec.splitlines()
            list_i = []
            list_l = range(int(text_spec[0]), int(text_spec[1])+1)
            for i in text_spec[2:]:
                list_i.append(float(i))
            index = str(name_dir).rfind('/')
            name_spec = QtCore.QString.fromLocal8Bit(name_dir[index:])
            Spectrum.Spectrum(list_l, list_i, name_spec)
            constGlobal.plot_spec(self)
        elif ind == 2:
            directory_spec = QtGui.QFileDialog.getExistingDirectory(self, u"Выбор директории")
            if directory_spec == '':
                return
            try:
                for i in os.listdir(str(directory_spec.toLocal8Bit())):
                    name_dir = str(directory_spec.toLocal8Bit()) + '/' + i
                    text_spec = open(name_dir, 'r')
                    text_spec = text_spec.splitlines()
                    list_i = []
                    list_l = range(float(text_spec[0]), float(text_spec[1])+1)
                    for j in text_spec[2:]:
                        list_i.append(float(j))
                    constGlobal.list_spec[self.tab_index].append(Spectrum.Spectrum(list_l, list_i, i))
                constGlobal.plot_spec(self)
            except OSError as var:
                constGlobal.error_mes(var, 'm: main, str 150')
            except ValueError as var:
                constGlobal.error_mes(var, 'm: main, str 152')
        elif ind == 3:
            # constCOM.filename = ''
            # constCOM.filename = QtGui.QFileDialog.getSaveFileName(self, 'Save File', '.spe')
            if len(constGlobal.list_spec[self.tab_index]) == 0:
                return
            else:
                t = time.localtime()
                string_save = r'Save_spec/'+str(t[2])+'_'+str(t[1])+'_'+str(t[0])+'/'
                string_save = os.path.abspath(string_save)
                if os.path.exists('Save_spec/'):
                    if os.path.exists(string_save):
                        Spectrum.save_spec(self.tab_index, string_save)
                    else:
                        os.makedirs(string_save)
                        Spectrum.save_spec(self.tab_index, string_save)
                else:
                    os.makedirs(string_save)
                    Spectrum.save_spec(self.tab_index, string_save)
        elif ind == 4:
            constGlobal.list_spec[self.tab_index] = []
            self.spec_plot.clear()
            self.spec_plot.replot()
        elif ind == 5:
            obj = SpecTab(parent)
            parent.tabWidget.insertTab(len(parent.list_tab)-1, obj.tab,
                                       u'работа со спектром {0}'.format(len(parent.list_tab)-1))
            parent.list_tab.append({
                'obj': obj,
                'name': u'работа со спектром {0}'.format(len(parent.list_tab)-1)})
        elif ind == 6:
            self.close_tab(parent)

    def close_tab(self, parent):
        msg = QtGui.QMessageBox()
        msg.setButtonText(msg.Yes, QtCore.QString("Да"))
        msg.setButtonText(msg.No, QtCore.QString("Нет"))
        m = msg.question(msg, u'Предупреждение', u"Закрыть текущую вкладку?", msg.Yes, msg.No)
        if m == msg.Yes:
            currentIndex = parent.tabWidget.currentIndex()
            parent.tabWidget.removeTab(currentIndex)
            parent.list_tab.pop(currentIndex)
        else:
            pass

        # quit_msg = "Are you sure you want to close the tab?"
        # button = QtGui.QMessageBox.button(QtGui.QMessageBox.Yes)
        # button.setText(u"Да")
        # #QtGui.QMessageBox.setButtonText(QtGui.QMessageBox.No, u"Нет")
        # #QtGui.QMessageBox.button(QtGui.QMessageBox.No).setText(u"Нет")
        # reply = QtGui.QMessageBox.question(self, 'Message',
        #              quit_msg, QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
        # if reply == QtGui.QMessageBox.Yes:
        #     parent.tabWidget.removeTab(currentIndex)
        #     parent.list_tab.pop(currentIndex)
        # else:
        #     pass

    def cbSpec(self, ind=0, parent=None):
        if ind == 0:
            pass
        elif ind == 1:
            self.takePict = takePict.TakePict(self)
            self.takePict.show()
        elif ind == 2:
            constGlobal.list_spec[self.tab_index].pop()
            constGlobal.plot_spec(self)
        elif ind == 3:
            self.ZSmooth = SmoothZ.SmoothZWindow(self)
            self.ZSmooth.show()
        elif ind == 4:
            self.CalcPeaks = CalcPeakWindow.CalcPeakWindow(self)
            self.CalcPeaks.show()

    def _handleTableCopy(self):
        data = "<!--StartFragment-->\n<table>"

        for i in self.tv_spec.selectedRanges():
            for row in xrange(i.topRow(), i.topRow() + i.rowCount()):
                data += "<tr>"
                for column in xrange(i.leftColumn(), i.leftColumn() + i.columnCount()):
                    data += "<td>" + self.tv_spec.item(row, column).text() + "</td>"
                data += "</tr>\n"

        data += "</table><!--EndFragment-->\n"
        mimedata = QMimeData()
        mimedata.setHtml(QtCore.QString(data))
        self.clip.setMimeData(mimedata)


class TechniqueTab(QtGui.QWidget):
    # Tab for technique
    list_cb = [u'Управление',
               u'Импорт данных',
               u'Открыть данные',
               u'Сохранить результат',
               u'Выход']
    list_cb_tech = [u'Работа со методикой',
               u'Аппроксимация',
               u'Множественная регрессия']
    import_spec = 0

    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.tab = QtGui.QWidget()
        self.vl_tech = QtGui.QVBoxLayout(self.tab)
        self.cb_manip = QtGui.QComboBox(self.tab)
        self.cb_manip.addItems(self.list_cb)
        self.vl_tech.addWidget(self.cb_manip)
        self.cb_tech = QtGui.QComboBox(self.tab)
        self.cb_tech.addItems(self.list_cb_tech)
        self.vl_tech.addWidget(self.cb_tech)
        self.hl_tech = QtGui.QHBoxLayout()
        self.tv_tech = QtGui.QTableWidget(self.tab)
        self.hl_tech.addWidget(self.tv_tech)
        self.spec_plot = Plot(self.tab)
        self.spec_plot.setAxisTitle(QwtPlot.xBottom, u'концентрация, мас. %')
        self.spec_plot.setAxisTitle(QwtPlot.yLeft, u'I')
        self.plotCanvas = self.spec_plot.canvas()
        self.plotCanvas.setMouseTracking(True)
        self.plotCanvas.installEventFilter(ManipulationEventFilterBuilder(self))
        self.hl_tech.addWidget(self.spec_plot)
        self.vl_tech.addLayout(self.hl_tech)

        QtCore.QObject.connect(self.cb_manip, QtCore.SIGNAL('activated(int)'),
                               lambda x: self.cbMain(x, parent))
        QtCore.QObject.connect(self.cb_tech, QtCore.SIGNAL('activated(int)'),
                               lambda x: self.cbTech(x, parent))

    def import_spec_data(self):
        self.import_spec = int(self.import_spec)-1
        if not constGlobal.list_spec[self.import_spec]:
            constGlobal.error_mes('Нет ни одного файла со спектром', 'M: CalcPeakWindows, str: 129')
        else:
            self.tv_tech.setColumnCount(len(constGlobal.list_spec[self.import_spec]))
            self.tv_tech.setRowCount(len(constGlobal.list_spec[self.import_spec][0].peaks)*4)
            # print len(constGlobal.list_spec[self.import_spec][0].peaks)*4
            j = 0
            for spec in constGlobal.list_spec[self.import_spec]:
                # Set name to table headers
                self.tv_tech.setHorizontalHeaderItem(j, QtGui.QTableWidgetItem(spec.spec_name))

                # Set name to cell and vertical headers
                c = 0
                for peak in spec.peaks:
                    self.tv_tech.setVerticalHeaderItem(c, QtGui.QTableWidgetItem(peak['name']+'_I'))
                    self.tv_tech.setItem(c, j, QtGui.QTableWidgetItem(str(peak['data_i'])))
                    self.tv_tech.setVerticalHeaderItem(c+1, QtGui.QTableWidgetItem(peak['name']+'_S'))
                    self.tv_tech.setItem(c+1, j, QtGui.QTableWidgetItem(str(peak['data_S'])))
                    self.tv_tech.setVerticalHeaderItem(c+2, QtGui.QTableWidgetItem(peak['name']+'_Conc_I'))
                    self.tv_tech.setVerticalHeaderItem(c+3, QtGui.QTableWidgetItem(peak['name']+'_Conc_S'))
                    c += 4
                j += 1

    def cbMain(self, ind=0, parent=None):
        main_path = os.path.curdir
        if ind == 0:
            pass
        elif ind == 1:
            self.import_peak_window = import_peak.ImportPeak(parent=self, parent_main=parent)
            self.import_peak_window.show()
        elif ind == 2:
            filename = QtGui.QFileDialog.getOpenFileName(self, u'Открыть методику', main_path+'/Save_technique/',
                                                         selectedFilter='*.tech')
            if filename == '':
                return

            text = filename.readlines()
            self.tv_spec.setColumnCount(len(text[0]))
            self.tv_spec.setRowCount(len(text))
            self.tv_spec.setHorizontalHeaderItem(0, QtGui.QTableWidgetItem('I'))
            count = 0
            for i in text:
                i = i.split(':')
                self.tv_spec.setVerticalHeaderItem(count, QtGui.QTableWidgetItem(i[0]))
                self.tv_spec.setItem(count, 0, QtGui.QTableWidgetItem(str(i[1])))
        elif ind == 3:
            filename_tech = QtGui.QFileDialog.getSaveFileName(self, u'Сохранить методику', main_path+'/Save_technique/',
                                                              selectedFilter='*.tech')
            print filename_tech

            file_tech = open(filename_tech, 'w')
            data = ''
            count_col = self.tv_tech.columnCount()
            count_row = self.tv_tech.rowCount()
            i = 0
            while i <= count_col:
                spec_name = self.tv_tech.horizontalHeaderItem(i)
                data += str(spec_name)
                j = 0
                while j <= count_row:
                    row_name = self.tv_tech.verticalHeaderItem(j)
                    data_cell = self.tv_tech.item(j, i).text()
                    data += str(row_name) + ':' + str(data_cell) + '\t\n'
                    j += 1
                file_tech.write(data)


            for i in self.tv_tech.selectedRanges():
                print i
                for row in xrange(i.topRow(), i.topRow() + i.rowCount()):
                    data += "<tr>"
                    for column in xrange(i.leftColumn(), i.leftColumn() + i.columnCount()):
                        data += "<td>" + self.tvPeaks.item(row, column).text() + "</td>"
                    data += "</tr>\n"

            #for i in self.tvPeaksFP.selectedRanges():
            #    for row in xrange(i.topRow(), i.topRow() + i.rowCount()):
            #        data += "<tr>"
            #        for column in xrange(i.leftColumn(), i.leftColumn() + i.columnCount()):
            #            data += "<td>" + self.tvPeaksFP.item(row, column).text() + "</td>"
            #        data += "</tr>\n"

            data += "</table><!--EndFragment-->\n"
            mimedata = QMimeData()
            mimedata.setHtml(QtCore.QString(data))
            self.clip.setMimeData(mimedata)

            # self.filename = QtGui.QFileDialog.getSaveFileName(self, u'Сохранить методику')

    def approx(self):
        #Start apptoximation window
        self.approxWindow = Approx.Approx(self)
        self.approxWindow.show()
        if self.approxWindow is not None:
            tab_index = self.approxWindow
            print tab_index


class Main(QtGui.QMainWindow):
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
    ind_tab = 0
    list_tab = [{'obj': SpecTab,
                'name': u'работа со спектром'},
                {'obj': TechniqueTab,
                'name': u'методика'}]
    list_menu = [{'name': u'Главное',
                  'type': 'menu',
                  'multiply': 0,
                  'split_line': 0},
                 {'name': u'Аппаратная часть',
                  'type': 'menu',
                  'multiply': 0,
                  'split_line': 0},
                 {'name': u'Работа со спектрами',
                  'type': 'menu',
                  'multiply': 0,
                  'split_line': 0},
                 {'name': u'Методическая часть',
                  'type': 'menu',
                  'multiply': 0,
                  'split_line': 0},
                 {'name': u'Помощь',
                  'type': 'menu',
                  'multiply': 0,
                  'split_line': 0},
                 {'name': u'Обработка спектра',
                  'type': 'menu',
                  'multiply': 1,
                  'split_line': 0},
                 {'name': u'Открыть спектр',
                  'type': 'action',
                  'menu': 0,
                  'multiply': 0,
                  'split_line': 0},
                 {'name': u'Открыть директорию',
                  'type': 'action',
                  'menu': 0,
                  'multiply': 0,
                  'split_line': 0},
                 {'name': u'Открыть изображение',
                  'type': 'action',
                  'menu': 0,
                  'multiply': 0,
                  'split_line': 1},
                 {'name': u'Сохранить спектр',
                  'type': 'action',
                  'menu': 0,
                  'multiply': 0,
                  'split_line': 0},
                 {'name': u'Сохранить все спектры',
                  'type': 'action',
                  'menu': 0,
                  'multiply': 0,
                  'split_line': 1},
                 {'name': u'Экспорт спектра',
                  'type': 'action',
                  'menu': 0,
                  'multiply': 0,
                  'split_line': 0},
                 {'name': u'Экспорт спектров',
                  'type': 'action',
                  'menu': 0,
                  'multiply': 0,
                  'split_line': 1},
                 {'name': u'Добавить вкладку',
                  'type': 'action',
                  'menu': 0,
                  'multiply': 0,
                  'split_line': 0},
                 {'name': u'Закрыть вкладку',
                  'type': 'action',
                  'menu': 0,
                  'multiply': 0,
                  'split_line': 1},
                 {'name': u'Выход',
                  'type': 'action',
                  'menu': 0,
                  'multiply': 0,
                  'split_line': 0},
                 {'name': u'Проверка системы',
                  'type': 'action',
                  'menu': 1,
                  'multiply': 0,
                  'split_line': 0},
                 {'name': u'Калибровка системы',
                  'type': 'action',
                  'menu': 1,
                  'multiply': 0,
                  'split_line': 0},
                 {'name': u'Получить спектр',
                  'type': 'action',
                  'menu': 2,
                  'multiply': 0,
                  'split_line': 1},
                 {'name': u'Расчет пиков',
                  'type': 'action',
                  'menu': 2,
                  'multiply': 0,
                  'split_line': 0},
                 {'name': u'Аппроксимация',
                  'type': 'action',
                  'menu': 3,
                  'multiply': 0,
                  'split_line': 0},
                 {'name': u'Множественная регрессия',
                  'type': 'action',
                  'menu': 3,
                  'multiply': 0,
                  'split_line': 0},
                 {'name': u'О программе',
                  'type': 'action',
                  'menu': 4,
                  'multiply': 0,
                  'split_line': 0},
                 {'name': u'Авторы и контакты',
                  'type': 'action',
                  'menu': 4,
                  'multiply': 0,
                  'split_line': 0},
                 {'name': u'Сглаживание',
                  'type': 'action',
                  'menu': 5,
                  'multiply': 0,
                  'split_line': 0},
                 {'name': u'Фурье преобразование',
                  'type': 'action',
                  'menu': 5,
                  'multiply': 0,
                  'split_line': 0},
                 {'name': u'Дисперсия',
                  'type': 'action',
                  'menu': 5,
                  'multiply': 0,
                  'split_line': 0},
                 {'name': u'Интегральный вид',
                  'type': 'action',
                  'menu': 5,
                  'multiply': 0,
                  'split_line': 0}]
    spec_error = False

    def __init__(self, parent=None):
        QtGui.QMainWindow.__init__(self, parent=None)
        #self.installEventFilter(ManipulationEventFilterBuilder(self))
        self.resize(800, 600)
        self.setWindowTitle("Spectra")
        self.centralwidget = QtGui.QWidget(self)
        self.vl_main = QtGui.QVBoxLayout(self.centralwidget)
        self.tabWidget = QtGui.QTabWidget(self.centralwidget)
        for i in self.list_tab:
            i['obj'] = i['obj'](self)
            self.tabWidget.addTab(i['obj'].tab, i['name'])
        self.tabWidget.setTabsClosable(True)
        self.tabWidget.tabCloseRequested.connect(self.close_tab)

        self.setCentralWidget(self.centralwidget)
        self.menubar = self.menuBar()
        self.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(self)
        self.setStatusBar(self.statusbar)
        self.statusBar().showMessage('Ready')
        for i in self.list_menu:
            if i['type'] == 'menu':
                if i['name'] == u'Обработка спектра':
                    self.menu = QtGui.QMenu(i['name'], self.list_menu[2]['type'])
                    i['type'] = self.menu
                    self.list_menu[2]['type'].addMenu(self.menu)

                else:
                    self.menu = QtGui.QMenu(i['name'], self.menubar)
                    i['type'] = self.menu
                    self.menubar.addMenu(self.menu)
            elif i['type'] == 'action':
                self.action = QtGui.QAction(i['name'], self.menubar)
                #self.action.triggered.connect(QtGui.qApp.quit)
                i['type'] = self.action
                self.list_menu[i['menu']]['type'].addAction(self.action)
                if i['split_line']:
                    self.list_menu[i['menu']]['type'].addSeparator()

        self.tabWidget.setCurrentIndex(0)
        self.vl_main.addWidget(self.tabWidget)

        #QtCore.QObject.connect(self.pushButton, QtCore.SIGNAL("clicked()"), self.statusbar.clearMessage)
        #QtCore.QObject.connect(self.qwtPlot, QtCore.SIGNAL("legendChecked(QwtPlotItem*,bool)"), self.statusbar.clearMessage)

    def close_tab(self, cur_ind):
        msg = QtGui.QMessageBox()
        msg.setButtonText(msg.Yes, QtCore.QString("Да"))
        msg.setButtonText(msg.No, QtCore.QString("Нет"))
        m = msg.question(msg, u'Предупреждение', u"Закрыть вкладку?", msg.Yes, msg.No)
        if m == msg.Yes:
            if len(self.list_tab) == 1:
                self.close()
            else:
                #cur_ind = self.tabWidget.currentIndex()
                self.tabWidget.removeTab(cur_ind)
                self.list_tab.pop(cur_ind)
        else:
            pass


reload(sys)
sys.setdefaultencoding('utf8')
app = QtGui.QApplication(sys.argv)
sw = Main()
desktop = QtGui.QApplication.desktop()
x = desktop.width() / 2
y = desktop.height() / 2
sw.move(x, y)
sw.show()
sys.exit(app.exec_())