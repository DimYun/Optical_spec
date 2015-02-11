# -*- coding: utf-8 -*-

from PyQt4 import QtCore, QtGui
import constGlobal
import mathManip


class AbstractTab(QtGui.QWidget):
    # Class for common elements in all tab
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.tab = QtGui.QWidget()
        self.verticalLayout = QtGui.QVBoxLayout(self.tab)
        self.label = QtGui.QLabel()
        self.verticalLayout.addWidget(self.label)


class TabSW(AbstractTab):
    # Tab for simple weight smoothing
    def __init__(self, parent=None):
        AbstractTab.__init__(self, parent)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.label2 = QtGui.QLabel()
        self.label2.setText('p = ')
        self.dsbParam = QtGui.QDoubleSpinBox()
        self.dsbParam.setDecimals(3)
        self.dsbParam.setProperty("value", 0.5)
        self.dsbParam.setRange(0.0, 1.0)
        self.dsbParam.setSingleStep(0.001)
        self.horizontalLayout.addWidget(self.label2)
        self.horizontalLayout.addWidget(self.dsbParam)
        self.verticalLayout.addLayout(self.horizontalLayout)
        parent.ind_tab += 1


class TabSG(AbstractTab):
    # Tab for SavGol smoothing
    def __init__(self, parent=None):
        AbstractTab.__init__(self, parent)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.label2 = QtGui.QLabel()
        self.label2.setText(u'Полуширина окна (целое, нечетное)')
        self.spWindow = QtGui.QSpinBox()
        self.spWindow.setProperty("value", 5)
        self.horizontalLayout.addWidget(self.label2)
        self.horizontalLayout.addWidget(self.spWindow)
        self.horizontalLayout2 = QtGui.QHBoxLayout()
        self.label3 = QtGui.QLabel()
        self.label3.setText(u'Степень полинома')
        self.spOrder = QtGui.QSpinBox()
        self.spOrder.setProperty("value", 3)
        self.horizontalLayout2.addWidget(self.label3)
        self.horizontalLayout2.addWidget(self.spOrder)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.verticalLayout.addLayout(self.horizontalLayout2)
        parent.ind_tab += 1


class TabOther(AbstractTab):
    # Tab for other methods
    def __init__(self, parent = None):
        AbstractTab.__init__(self, parent)
        parent.ind_tab += 1


class SmoothZWindow(QtGui.QWidget):
    # Show dialog window for smooth spec
    list_tab = [{'obj': TabSW,
                 'name': u"Простой весовой",
                 'label': u'Сглаживает спектр по весовому алгоритму'},
                {'obj': TabSG,
                 'name': u"Савицкого-Голея",
                 'label': u'Сглаживание алгоритмом Савицкого-Голея'},
                {'obj': TabOther,
                 'name': u'Логарифмический масштаб',
                 'label': u'Представляет ось интенсивностей в логарифмическом масштабе'},
                {'obj': TabOther,
                 'name': u"Нормировать на дисперсию",
                 'label': u"Представляет спектр нормированный на стандартное отклонение"},
                {'obj': TabOther,
                 'name': u"Расчитать дисперсию",
                 'label': u"Представляет спектр по дисперсии"},
                {'obj': TabOther,
                 'name': u'Преобразование Фурье',
                 'label': u"Прямое и обратное Фурье-преобразование"},
                {'obj': TabOther,
                 'name': u'2-ая Производная',
                 'label': u"Представляет спектр по второй производной"}]
    ind_tab = 0

    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, None)
        self.move(0, 0)
        self.setWindowTitle(u'Преобразования спектра')
        self.main_layout = QtGui.QVBoxLayout(self)
        self.tabWidget = QtGui.QTabWidget(self)
        for i in self.list_tab:
            i['obj'] = i['obj'](self)
            self.tabWidget.addTab(i['obj'].tab, i['name'])
            i['obj'].label.setText(i['label'])
        self.tabWidget.setCurrentIndex(0)
        self.main_layout.addWidget(self.tabWidget)
        self.button_layout = QtGui.QHBoxLayout()
        self.pb_view = QtGui.QPushButton()
        self.pb_cancel = QtGui.QPushButton()
        self.pb_apply = QtGui.QPushButton()
        self.pb_view.setText(u'Просмотр')
        self.pb_cancel.setText(u'Отмена')
        self.pb_apply.setText(u'Применить')
        self.button_layout.addWidget(self.pb_view)
        self.button_layout.addWidget(self.pb_cancel)
        self.button_layout.addWidget(self.pb_apply)
        self.main_layout.addLayout(self.button_layout)

        QtCore.QObject.connect(self.pb_apply,
            QtCore.SIGNAL('clicked()'), lambda: self.apply_plot(parent))
        QtCore.QObject.connect(self.pb_cancel,
            QtCore.SIGNAL('clicked()'), lambda: constGlobal.plot_spec(parent))
        QtCore.QObject.connect(self.pb_view,
            QtCore.SIGNAL('clicked()'), lambda: self.view_plot(parent))

    def view_plot(self, parent):
        # Calculate manipulation and plot it near the original file
        if self.tabWidget.currentIndex() == 0:
            p = float(self.list_tab[0]['obj'].dsbParam.value())
            for spec in constGlobal.list_spec[parent.tab_index]:
                mathManip.calc_smooth_sm(p, spec)
            constGlobal.plot_spec(parent, transform=True, name='Smooth (p=' + str(p) + ') ')
        elif self.tabWidget.currentIndex() == 1:
            window_sg = float(self.list_tab[1]['obj'].spWindow.value())
            order = float(self.list_tab[1]['obj'].spOrder.value())
            for spec in constGlobal.list_spec[parent.tab_index]:
                mathManip.calc_smooth_sg(spec.list_i, window_sg, order, spec, self)
                lendelta = len(spec.list_transform) - len(spec.list_i)
                if lendelta > 0:
                    spec.list_transform = spec.list_transform[lendelta / 2:]
            constGlobal.plot_spec(parent, transform=True, name='Smooth (win, ord=' + str(window_sg) + ', ' +
                                                               str(order) + ') ')
        elif self.tabWidget.currentIndex() == 2:
            for spec in constGlobal.list_spec[parent.tab_index]:
                mathManip.calculate_log_scale(spec, self)
            constGlobal.plot_spec(parent, transform=True, name='Log conversion of ')
        elif self.tabWidget.currentIndex() == 4:
            for spec in constGlobal.list_spec[parent.tab_index]:
                mathManip.sigma_z(spec, self)
            constGlobal.plot_spec(parent, transform=True, name='sigma Z conversion of ')
        elif self.tabWidget.currentIndex() == 5:
            for spec in constGlobal.list_spec[parent.tab_index]:
                mathManip.sigma(spec, self)
            constGlobal.plot_spec(parent, transform=True, name='sigma conversion of ')
        elif self.tabWidget.currentIndex() == 6:
            for spec in constGlobal.list_spec[parent.tab_index]:
                mathManip.furie(spec, self)
            constGlobal.plot_spec(parent, transform=True, name='FFT-iFFT conversion of ')
        elif self.tabWidget.currentIndex() == 7:
            for spec in constGlobal.list_spec[parent.tab_index]:
                mathManip.deriv(spec, self)
            constGlobal.plot_spec(parent, transform=True, name='2nd derivative conversion of ')
        else:
            pass

    def apply_plot(self, parent):
        # Apply the transformation
        for spec in constGlobal.list_spec[parent.tab_index]:
            spec.list_i = spec.list_transform[:]
            spec.list_transform = []
        constGlobal.plot_spec(parent)