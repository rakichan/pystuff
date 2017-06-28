# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'myForm.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName(_fromUtf8("Dialog"))
        Dialog.resize(452, 198)
        self.label = QtGui.QLabel(Dialog)
        self.label.setGeometry(QtCore.QRect(30, 30, 46, 13))
        self.label.setObjectName(_fromUtf8("label"))
        self.label_2 = QtGui.QLabel(Dialog)
        self.label_2.setGeometry(QtCore.QRect(30, 70, 46, 13))
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.label_3 = QtGui.QLabel(Dialog)
        self.label_3.setGeometry(QtCore.QRect(30, 110, 46, 13))
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.label_4 = QtGui.QLabel(Dialog)
        self.label_4.setGeometry(QtCore.QRect(30, 150, 46, 13))
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.cityComboBox = QtGui.QComboBox(Dialog)
        self.cityComboBox.setGeometry(QtCore.QRect(100, 20, 321, 26))
        self.cityComboBox.setObjectName(_fromUtf8("cityComboBox"))
        self.countyTextBrowser = QtGui.QTextBrowser(Dialog)
        self.countyTextBrowser.setGeometry(QtCore.QRect(100, 60, 321, 26))
        self.countyTextBrowser.setObjectName(_fromUtf8("countyTextBrowser"))
        self.latitudeTextBrowser = QtGui.QTextBrowser(Dialog)
        self.latitudeTextBrowser.setGeometry(QtCore.QRect(100, 100, 321, 26))
        self.latitudeTextBrowser.setObjectName(_fromUtf8("latitudeTextBrowser"))
        self.longitudeTextBrowser = QtGui.QTextBrowser(Dialog)
        self.longitudeTextBrowser.setGeometry(QtCore.QRect(100, 140, 321, 26))
        self.longitudeTextBrowser.setObjectName(_fromUtf8("longitudeTextBrowser"))

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(_translate("Dialog", "Dialog", None))
        self.label.setText(_translate("Dialog", "City", None))
        self.label_2.setText(_translate("Dialog", "County", None))
        self.label_3.setText(_translate("Dialog", "Latitude", None))
        self.label_4.setText(_translate("Dialog", "Longitude", None))

