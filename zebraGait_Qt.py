# General libs
import pathlib
import logging
import numpy as np
import cv2 as cv
from PyQt5 import QtCore, QtWidgets, QtGui

# Import matplotlib Agg buffer prepared to threading/embedding on tkinter
import matplotlib
matplotlib.use("Agg") 
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT

# Import project libs
from swimTunnel import swimTunnel
from treatData import treatData
from showData import showData
from models import zebraGait_ui, showWindow_ui, resources_rc

class MainWindow(QtWidgets.QMainWindow, zebraGait_ui.Ui_zebraGait):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        self.setupUi(self)

        # Select video file
        self.iniPath = str(pathlib.Path.home())
        self.vidPathTButton.clicked.connect(self.selectVidPath)
        
        # Select video file
        self.iniSavePath = str(pathlib.Path.home()) 
        self.savePathTButton.clicked.connect(self.selectSavePath)
        
        # Run the process
        self.RunButton.clicked.connect(self.run)

        # Check/Done message
        self.checkDialog = QtWidgets.QMessageBox(self)
        self.checkDialog.setWindowTitle("Info")
        self.checkDialog.setIcon(QtWidgets.QMessageBox.Information)
        self.checkDialog.setText("The video has been processed. Continue or check the results.")
        self.checkDialog.setStandardButtons(QtWidgets.QMessageBox.Ok)
        self.checkButton = self.checkDialog.addButton("Check", QtWidgets.QMessageBox.AcceptRole)
        self.checkButton.clicked.connect(self.check)
   
    def selectVidPath(self):
        vidPath, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Select a file",  self.iniPath ,"Video files (*.avi *.mpg)")
        self.vidPathLineEdit.setText(vidPath)
        self.expIDLineEdit.setText(pathlib.Path(vidPath).stem)
        self.iniPath = str(pathlib.Path(vidPath).parent) # remember the last opened path

    def selectSavePath(self):
        savePath = QtWidgets.QFileDialog.getExistingDirectory(self, "Select a path", self.iniSavePath, QtWidgets.QFileDialog.ShowDirsOnly)
        self.savePathLineEdit.setText(savePath)
        self.iniSavePath = str(pathlib.Path(savePath)) # remember the last opened path

    def run(self):

        try:
            # Block Controls
            self.enabledControls(False)
            
            # Obtain the GUI data
            self.videoPath = self.vidPathLineEdit.text()
            self.exportPath = self.savePathLineEdit.text()
            self.expID = self.expIDLineEdit.text()
            self.fps = int(self.fpsSpinBox.text())

            # Init. logs
            self.initLogs(self.exportPath, self.expID)
            
        except Exception as err:
            self.aborted(err)

        # # Run the process without threads
        # try:
        #     self.progressLabel.setText("Extracting the data...")
        #     failedFrames, contrast = swimTunnel(self.videoPath, self.exportPath, self.expID, self.fps)
        #     self.progressLabel.setText("Treating the data...")
        #     treatData(self.exportPath, self.expID, self.fps, contrast , failedFrames)
        #     self.done()
        # except Exception as err:
        #     self.aborted(err) 

        try:
            # Run the process in a thread
            self.sendmsg("Select the ROI...")
            self.roi = self.getRoi(self.videoPath)
            self.runProc = RunProcessThread(self.videoPath, self.exportPath, self.expID, self.fps, self.roi)
            self.runProc.done.connect(self.done)
            self.runProc.msg.connect(self.sendmsg)
            self.runProc.aborted.connect(self.aborted)
            self.runProc.start()
        except Exception as err:
            self.aborted(err)
   
    def aborted(self, err):
        self.progressLabel.setText("An error occurred, try again.")
        QtWidgets.QMessageBox.critical(self, "Error", str(err))
        self.enabledControls(True)

    def done(self):
        self.progressLabel.setText("Done.")
        self.checkDialog.setInformativeText("Find the results in "+ str(self.exportPath) +" folder.")
        self.checkDialog.exec_()
        self.enabledControls(True)
    
    def sendmsg(self, msg):
        self.progressLabel.setText(msg)
    
    def check(self):
        importPath = self.savePathLineEdit.text()
        expID = self.expIDLineEdit.text()
        time, beta, showVid = showData(importPath, expID, gui=True)
        self.cwindow = ShowWindow(time, beta, showVid)
        self.cwindow.show()

    def enabledControls(self, status):
        if status == True:
            self.progressBar.setMaximum(10)
            self.progressLabel.setText("Ready")
        elif status == False:
            self.progressBar.setMaximum(0)
        self.RunButton.setEnabled(status)
        self.vidPathTButton.setEnabled(status)
        self.vidPathLineEdit.setEnabled(status)
        self.savePathTButton.setEnabled(status)
        self.savePathLineEdit.setEnabled(status)
        self.expIDLineEdit.setEnabled(status)
        self.fpsSpinBox.setEnabled(status)
    
    def getRoi(self, videoPath):
        # Open the video and select a ROI
        vid = cv.VideoCapture(videoPath)
        if not vid.isOpened():
            vid.release()
            raise Exception("Could not open the video reference: " + videoPath)
        
        _ret, backFrame = vid.read()
        (rx, ry, rw, rh) = cv.selectROI("Crop the region of interest", backFrame)
        cv.destroyAllWindows()
        vid.release()

        return (rx, ry, rw, rh)

    def initLogs(self, exportPath, expID):
        # Check/Create paths
        pathlib.Path(exportPath, expID, "logs").mkdir(parents=True, exist_ok=True)
        # Logs configuration in console/file
        logging.basicConfig(
            level=logging.INFO,
            format="[%(asctime)s] %(levelname)s: %(message)s (%(funcName)s:%(lineno)d)",
            datefmt="%m/%d/%Y %H:%M:%S",
            handlers=[logging.FileHandler(pathlib.Path(exportPath, expID, "logs", "log_file.log")),
                    logging.StreamHandler()]
        )

class ShowWindow(QtWidgets.QMainWindow, showWindow_ui.Ui_showWindow):
    def __init__(self, time, beta, videoPathR, parent=None):
        QtWidgets.QMainWindow.__init__(self)
        self.setupUi(self)

        # VID

        # Open the video object
        self.videoPathR = videoPathR
        self.vid = cv.VideoCapture(str(self.videoPathR))
        
        if not self.vid.isOpened():
            raise Exception("Could not open the video reference: " + videoPathR)
        
        # Get the number of video frames
        self.numFrames = self.vid.get(cv.CAP_PROP_FRAME_COUNT)

        # Set slider
        self.slider.setMaximum(self.numFrames -1)
        self.slider.valueChanged.connect(self.valueChange)
        
        # Load the first frame
        self.vid.set(cv.CAP_PROP_POS_FRAMES, 0)
        _, self.frame = self.vid.read()
        # Convert image to qt format
        image = cv.cvtColor(self.frame, cv.COLOR_BGR2RGB)
        image = QtGui.QImage(image.data, image.shape[1], image.shape[0], 3*image.shape[1], QtGui.QImage.Format_RGB888)
        image = QtGui.QPixmap.fromImage(image)
        pixmap = QtGui.QPixmap(image)
        # Draw the first frame
        self.labelVid.setPixmap(pixmap.scaled(self.labelVid.size(), QtCore.Qt.KeepAspectRatio))

        # FIG

        # Figure
        self.beta = beta
        self.x = time
        self.fig = plt.figure(figsize=(6, 4), dpi=100)
        plt.title("Angle between the tail and the head perpendicular (beta)")
        plt.xlabel("Time (ms)")
        plt.ylabel("beta (dg)")
        self.betaFig, = plt.plot(self.x, self.beta, "r", linewidth=0.5)
        self.lineFig, = plt.plot(np.zeros(np.size(self.x)), 'b--', linewidth=0.5)
        self.pointDraw, = plt.plot(self.x[0], self.beta[0], "bo")
        # Canvas object for plot
        self.canvasPlot = FigureCanvasQTAgg(self.fig)
        # Toolbar for plot
        self.toolbar = NavigationToolbar2QT(self.canvasPlot, self)
    
        # Show in the layout
        self.plotLayout.addWidget(self.toolbar)
        self.plotLayout.addWidget(self.canvasPlot)

    def valueChange(self):
        self.updateFrame(self.slider.value())
        self.updatePoint(self.slider.value())
        
    def updatePoint(self, value):
        self.pointDraw.set_xdata(self.x[value])
        self.pointDraw.set_ydata(self.beta[value])
        self.canvasPlot.draw_idle()
   
    def updateFrame(self, value):
        # Set a frame
        self.vid.set(cv.CAP_PROP_POS_FRAMES, value)
        _, self.frame = self.vid.read()
        # Convert image to qt format
        image = cv.cvtColor(self.frame, cv.COLOR_BGR2RGB)
        image = QtGui.QImage(image.data, image.shape[1], image.shape[0], 3*image.shape[1], QtGui.QImage.Format_RGB888)
        image = QtGui.QPixmap.fromImage(image)
        pixmap = QtGui.QPixmap(image)
        # Draw the frame
        self.labelVid.setPixmap(pixmap.scaled(self.labelVid.size(), QtCore.Qt.KeepAspectRatio))
        

class RunProcessThread(QtCore.QThread):

    aborted = QtCore.pyqtSignal(str)
    done = QtCore.pyqtSignal()
    msg = QtCore.pyqtSignal(str)

    def __init__(self, videoPath, exportPath, expID, fps, roi):
        QtCore.QThread.__init__(self)
        self.videoPath = videoPath
        self.exportPath = exportPath
        self.expID = expID
        self.fps = fps
        self.roi = roi

    def __del__(self):
        self.wait()

    def run(self):
        # Run the swimtunnel and the treat data
        try:
            self.msg.emit("Extracting the data...")
            self.failedFrames, self.contrast = swimTunnel(self.videoPath, self.exportPath, self.expID, self.fps, self.roi)
            self.msg.emit("Treating data...")
            treatData(self.exportPath, self.expID, self.fps, self.contrast , self.failedFrames)
            self.done.emit()
        except Exception as err:
            self.aborted.emit(str(err))


if __name__ == "__main__":

    app = QtWidgets.QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()
