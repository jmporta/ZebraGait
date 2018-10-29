import logging
import pathlib
import csv
from threading import Thread
import tkinter as tk
from tkinter import filedialog, ttk
import matplotlib
import PIL.Image
import PIL.ImageTk

import numpy as np
import cv2 as cv

# Import matplotlib prepared to threading/embedding
matplotlib.use("Agg")
import matplotlib.pyplot as pl
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

# Import own libs
from swimTunnel import swimTunnel
from treatData import treatData
from showData import showData

import config


class mainWindow:
    
    # MASONRY

    def __init__(self, master):

        # WINDOW PROPERTIES

        defaultVid = "./video/water_tunnel.avi"
        defaultFrames = "1000"

        # Main window
        self.master=master
        self.master.title("Swim Tunnel")
        master.resizable(width=False, height=False)

        # Icon
        self.img = tk.PhotoImage(file=pathlib.Path("./icons/gar-fish.png"))
        self.master.tk.call("wm", "iconphoto", master._w, self.img)

        # FIELDS FRAME

        # Main frame
        self.mainFrame = tk.Frame(self.master, padx=5, pady=5)
        self.mainFrame.grid(column=0, row=0, sticky=(tk.N, tk.W, tk.E, tk.S))

        # Video open path
        self.lblPath =  tk.Label(self.mainFrame, text="Video path:")
        self.lblPath.grid(column=0, row=0, sticky=tk.W, padx=10, pady=10)

        self.defaultPath = tk.StringVar(self.mainFrame, value=defaultVid)
        self.txtPath =  tk.Entry(self.mainFrame, width=35, textvariable=self.defaultPath)
        self.txtPath.grid(column=1, row=0, sticky=(tk.W, tk.E), padx=5, pady=5, columnspan=3)

        self.btnPath =  tk.Button(self.mainFrame, text="Open", command=self.clickPath)
        self.btnPath.grid(column=4, row=0, sticky=tk.W, padx=5, pady=5)

        # Export string name
        self.lblVidId =  tk.Label(self.mainFrame, text="ExperimentID:")
        self.lblVidId.grid(column=0, row=1, sticky=tk.W, padx=5, pady=5)

        self.defaultID = tk.StringVar(self.mainFrame, value="ExpID")
        self.txtVidId =  tk.Entry(self.mainFrame, textvariable=self.defaultID)
        self.txtVidId.grid(column=1, row=1, sticky=(tk.W, tk.E), padx=5, pady=5)

        # Export fps integer
        self.lblVidFps =  tk.Label(self.mainFrame, text="Video Fps:")
        self.lblVidFps.grid(column=2, row=1, sticky=tk.W, padx=5, pady=5)

        self.defaultFps = tk.StringVar(self.mainFrame, value=defaultFrames)
        self.txtVidFps =  tk.Entry(self.mainFrame, width=5, textvariable=self.defaultFps)
        self.txtVidFps.grid(column=3, row=1, sticky=(tk.W, tk.E), padx=5, pady=5)

        # RUN FRAME

        # Buttons frame
        self.btnFrame = tk.Frame(self.master, padx=10, pady=10)
        self.btnFrame.grid(column=0, row=1, sticky=(tk.N, tk.E, tk.S))

        # Progress bar
        self.progressbar = ttk.Progressbar(self.btnFrame, mode="indeterminate")
        self.progressbar.grid(column=0, row=0, sticky=tk.W, padx=5, pady=5)

        # Spacer
        self.spacer =  tk.Label(self.btnFrame, text=" ")
        self.spacer.grid(column=1, row=0, sticky=tk.W, padx=110, pady=5)

        # Run button
        self.btnRun =  tk.Button(self.btnFrame, text="Run", width=5, command=self.clickRun)
        self.btnRun.grid(column=3, row=0, sticky=tk.E, padx=5, pady=5)

        # Show button.
        self.btnShow =  tk.Button(self.btnFrame, text="Show", width=5, command=self.clickShow)
        self.btnShow.grid(column=2, row=0, sticky=tk.E, padx=5, pady=5)

        # List of buttons to threading
        self.buttons = [self.btnRun, self.btnShow, self.btnPath]

    # FUNCS

    # Main functions
    def runProcess(self):
        # The selected video will be processed and the resultant data will be treated.
        # It saves the skeletons in "./data/" and the resultant video in "./export" using swimTunnel function.
        # It saves a cvs file in a "./export/" and treated data in "./data/" using treatData function.
        try:
            videoPath = self.txtPath.get()
            expID = self.txtVidId.get()
            fps = int(self.txtVidFps.get())
            if ((fps > 0) and (fps < 1001)):
                # Run computations
                swimTunnel(videoPath, expID, fps)
                treatData(expID, fps)
            else:
                raise Exception("The fps value must be in [1,1000].")
        except Exception as err:
            tk.messagebox.showerror("Error", err)
            logging.error(err)
        else:
            tk.messagebox.showinfo("Info", "The video has been processed. Check the results in './export' folder.")
            logging.info("The video has been processed.")

    def showResults(self):
        # It shows the data in the "./export" folder.
        try:
            expID = self.txtVidId.get()
            fps = int(self.txtVidFps.get())
            beta, gamma, videoPathR, csvPathR = showData(expID, fps, gui=True)

            # New Window
            showWin = tk.Toplevel(self.master)
            showWindow(showWin, beta, gamma, videoPathR, csvPathR)
        except Exception as err:
            tk.messagebox.showerror("Error", err)
            logging.error(err)

    # Click functions

    def clickPath(self):
        iniPath = "/home/"
        filePath = tk.filedialog.askopenfilename(initialdir=iniPath, title="Select file", filetypes=(("avi files", "*.avi"), ("all files", "*.*")))
        self.txtPath.delete(0, tk.END)
        self.txtPath.insert(0, filePath)

    def clickRun(self):
        self.run_thread("run", self.runProcess)

    def clickShow(self):
        self.run_thread("show", self.showResults)

    # Threading functions

    def run_thread(self, name, func):
        Thread(target=self.run_function, args=(name, func)).start()

    def run_function(self, name, func):
        # Disable all buttons
        for btn in self.buttons:
            btn["state"] = "disabled"

        self.progressbar.start(interval=10)
        func()
        self.progressbar.stop()

        # Enable all buttons
        for btn in self.buttons:
            btn["state"] = "normal"

class showWindow:

    # MASONRY

    def __init__(self, master, beta, gamma, videoPathR, csvPathR):

        # WINDOW PROPERTIES
        
        # Main window
        self.master = master
        self.master.title("Plots and data")
        self.master.resizable(width=False, height=False)
        # Icon
        self.img = tk.PhotoImage(file=pathlib.Path("./icons/gar-fish.png"))
        self.master.tk.call("wm", "iconphoto", self.master._w, self.img)

        # VID

        # Open the video object
        self.videoPathR = videoPathR
        self.vid = cv.VideoCapture(str(self.videoPathR))
        
        if (not self.vid.isOpened()):
            raise Exception("Could not open the video reference: " + videoPathR)
        
        # get the number of video frames
        self.numFrames = self.vid.get(cv.CAP_PROP_FRAME_COUNT)
        
        # Load the first frame
        self.vid.set(cv.CAP_PROP_POS_FRAMES, 0)
        _, self.frame = self.vid.read()

        # Create a canvas that can fit the above image
        self.canvasVid = tk.Canvas(self.master, width=self.vid.get(cv.CAP_PROP_FRAME_WIDTH), height=self.vid.get(cv.CAP_PROP_FRAME_HEIGHT))
        self.canvasVid.grid(row=0, column=1, sticky=(tk.W, tk.N))

        # Trackbar
        self.trackBarVid =  tk.Scale(self.master, from_=1, to=self.numFrames, orient=tk.HORIZONTAL, length=self.vid.get(cv.CAP_PROP_FRAME_WIDTH), command=self.onTrack)
        self.trackBarVid.grid(row=1, column=1, sticky=(tk.W, tk.S))

        # Draw the first frame
        self.frame = cv.cvtColor(self.frame, cv.COLOR_BGR2RGB) # exchange BGR(openCV) to RGB(tkinter)
        self.photo = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(self.frame)) # use PIL (Pillow) to convert the NumPy ndarray to a PhotoImage
        self.canvasVidArea = self.canvasVid.create_image(0, 0, image=self.photo, anchor=tk.NW) # add a PhotoImage to the Canvas
    
        # FIG

        # Figure
        self.beta = beta
        self.x = np.arange(0, np.size(self.beta, 0))
        self.fig = pl.figure(figsize=(6, 4), dpi=100)
        pl.title("Angle between the tail and the head perpendicular (beta)")
        pl.xlabel("Frame")
        pl.ylabel("beta (rad)")
        self.betaFig, = pl.plot(self.x, self.beta, "r", linewidth=0.5)
        self.lineFig, = pl.plot(np.zeros(np.size(self.x)), 'b--', linewidth=0.5)
        self.pointDraw, = pl.plot(self.x[0], self.beta[0], "bo")
        # Canvas object for plot
        self.canvasPlot = FigureCanvasTkAgg(self.fig, self.master)
        self.canvasPlotArea = self.canvasPlot.get_tk_widget()  # Draw figures
        self.canvasPlotArea.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        # Toolbar for plot
        self.toolbarFrame = tk.Frame(self.master)
        self.toolbarFrame.grid(row=1, column=0, sticky=(tk.W, tk.S))
        self.toolbar = NavigationToolbar2Tk(self.canvasPlot, self.toolbarFrame)
        self.toolbar.update()
        
    # FUNCS
    
    def onTrack(self, value):
        self.updateFrame(int(value))
        self.updatePoint(int(value))
        
    def updatePoint(self,val):
        self.pointDraw.set_xdata(self.x[val-1])
        self.pointDraw.set_ydata(self.beta[val-1])
        self.canvasPlot.draw_idle()
   
    def updateFrame(self,val):
        # Set a frame
        self.vid.set(cv.CAP_PROP_POS_FRAMES, val)
        _, self.frame = self.vid.read()
        # Draw the frame
        self.frame = cv.cvtColor(self.frame, cv.COLOR_BGR2RGB)
        self.photo = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(self.frame))
        self.canvasVid.itemconfig(self.canvasVidArea,image=self.photo)

if (__name__ == "__main__"):

    # Check/Create paths
    pathlib.Path(config.LOGS_PATH).mkdir(parents=True, exist_ok=True)

    logging.basicConfig(
        filename=pathlib.Path(config.LOGS_PATH,"log_file.log"),
        level=logging.INFO,
        format="%(asctime)s: %(levelname)s: %(message)s"
    )

    matplotlib.use("Agg")

    # Run gui and wait
    mainWin = tk.Tk()
    mainWindow(mainWin)
    mainWin.mainloop()
    
