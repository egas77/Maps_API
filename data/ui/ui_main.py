# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\main.ui'
#
# Created by: PyQt5 UI code generator 5.12.3
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(668, 596)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
        self.sat_btn = QtWidgets.QPushButton(self.centralwidget)
        self.sat_btn.setObjectName("sat_btn")
        self.gridLayout.addWidget(self.sat_btn, 3, 1, 1, 1)
        self.hybrid_btn = QtWidgets.QPushButton(self.centralwidget)
        self.hybrid_btn.setObjectName("hybrid_btn")
        self.gridLayout.addWidget(self.hybrid_btn, 3, 2, 1, 1)
        self.main_map = QtWidgets.QLabel(self.centralwidget)
        self.main_map.setText("")
        self.main_map.setObjectName("main_map")
        self.gridLayout.addWidget(self.main_map, 2, 0, 1, 3)
        self.map_btn = QtWidgets.QPushButton(self.centralwidget)
        self.map_btn.setObjectName("map_btn")
        self.gridLayout.addWidget(self.map_btn, 3, 0, 1, 1)
        self.search_btn = QtWidgets.QPushButton(self.centralwidget)
        self.search_btn.setObjectName("search_btn")
        self.gridLayout.addWidget(self.search_btn, 0, 2, 1, 1)
        self.search_line_edit = QtWidgets.QLineEdit(self.centralwidget)
        self.search_line_edit.setObjectName("search_line_edit")
        self.gridLayout.addWidget(self.search_line_edit, 0, 0, 1, 2)
        self.reset_search_btn = QtWidgets.QPushButton(self.centralwidget)
        self.reset_search_btn.setObjectName("reset_search_btn")
        self.gridLayout.addWidget(self.reset_search_btn, 1, 2, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 668, 21))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Maps"))
        self.sat_btn.setText(_translate("MainWindow", "Спутник"))
        self.hybrid_btn.setText(_translate("MainWindow", "Гибрид"))
        self.map_btn.setText(_translate("MainWindow", "Схема"))
        self.search_btn.setText(_translate("MainWindow", "Поиск"))
        self.reset_search_btn.setText(_translate("MainWindow", "Сбросить поиск"))
