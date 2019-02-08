# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'showWindow.ui'
#
# Created by: PyQt5 UI code generator 5.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_showWindow(object):
    def setupUi(self, showWindow):
        showWindow.setObjectName("showWindow")
        showWindow.resize(664, 781)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/icon/icons/gar-fish.ico"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        showWindow.setWindowIcon(icon)
        self.centralwidget = QtWidgets.QWidget(showWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.slider = QtWidgets.QSlider(self.centralwidget)
        self.slider.setGeometry(QtCore.QRect(20, 500, 621, 16))
        self.slider.setTracking(True)
        self.slider.setOrientation(QtCore.Qt.Horizontal)
        self.slider.setTickPosition(QtWidgets.QSlider.TicksBelow)
        self.slider.setObjectName("slider")
        self.labelVid = QtWidgets.QLabel(self.centralwidget)
        self.labelVid.setGeometry(QtCore.QRect(20, 520, 621, 251))
        self.labelVid.setObjectName("labelVid")
        self.verticalLayoutWidget = QtWidgets.QWidget(self.centralwidget)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(30, 0, 611, 491))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.plotLayout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.plotLayout.setContentsMargins(0, 0, 0, 0)
        self.plotLayout.setObjectName("plotLayout")
        showWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(showWindow)
        QtCore.QMetaObject.connectSlotsByName(showWindow)

    def retranslateUi(self, showWindow):
        _translate = QtCore.QCoreApplication.translate
        showWindow.setWindowTitle(_translate("showWindow", "Check Results"))
        self.labelVid.setText(_translate("showWindow", "TextLabel"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    showWindow = QtWidgets.QMainWindow()
    ui = Ui_showWindow()
    ui.setupUi(showWindow)
    showWindow.show()
    sys.exit(app.exec_())

