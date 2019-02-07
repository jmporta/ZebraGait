import pathlib
import logging

from PyQt5 import QtCore, QtWidgets, uic
from swimTunnel import swimTunnel 
from treatData import treatData

LOGS_PATH = "./export/logs"

# Load ui file
MainWindowForm, MainWindowBase = uic.loadUiType("KinematicsZebra.ui")

class MainWindow(MainWindowBase, MainWindowForm):
    def __init__(self, *args, **kwargs):
        QtWidgets.QMainWindow.__init__(self, *args, **kwargs)
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

    def check(self):
        pass
   
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
            self.progressBar.setMaximum(0)
            self.RunButton.setEnabled(False)
            self.vidPathTButton.setEnabled(False)
            self.savePathTButton.setEnabled(False)
            
            # Obtain the GUI data
            videoPath = self.vidPathLineEdit.text()
            exportPath = self.savePathLineEdit.text()
            expID = self.expIDLineEdit.text()
            fps = int(self.fpsSpinBox.text())
            
            # Run the swimtunnel
            self.progressLabel.setText("Processing the video...")
            #failedFrames, contrast = swimTunnel(videoPath, exportPath, expID, fps)
            self.progressLabel.setText("Computing the data...")
            #treatData(exportPath, expID, fps, contrast , failedFrames)
            self.checkDialog.setInformativeText("Find the results in "+ str(exportPath) +" folder.")
            self.checkDialog.exec_()
        except Exception as err:
            self.progressBar.setMaximum(10)
            self.progressLabel.setText("An error occurred, try again.")
            QtWidgets.QMessageBox.critical(self, "Error", str(err))
            self.progressLabel.setText("Ready")
            self.RunButton.setEnabled(True)
            self.vidPathTButton.setEnabled(True)
            self.savePathTButton.setEnabled(True)
            
        else:
            self.progressBar.setMaximum(10)
            self.RunButton.setEnabled(True)
            self.vidPathTButton.setEnabled(True)
            self.savePathTButton.setEnabled(True)
            self.progressLabel.setText("Ready")
   
   
if __name__ == "__main__":

    # Check/Create paths
    pathlib.Path(LOGS_PATH).mkdir(parents=True, exist_ok=True)

    # Logs configuration in console/file
    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s] %(levelname)s: %(message)s (%(funcName)s:%(lineno)d)",
        datefmt="%m/%d/%Y %H:%M:%S",
        handlers=[logging.FileHandler(pathlib.Path(LOGS_PATH, "log_file.log")),
                  logging.StreamHandler()]
    )

    app = QtWidgets.QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()
