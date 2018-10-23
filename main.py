import tkinter as tk
import numpy as np
import cv2 as cv
import matplotlib.pyplot as pl
import matplotlib.figure as figure

from tkinter import filedialog, ttk
from threading import Thread
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

from swimTunnel import swimTunnel
from treatData import treatData
from showData import showData


### FUNCTIONS ###

# Main functions

def runProcess():
    # The selected video will be processed and the resultant data will be treated.
    # It saves the skeletons in "./data/" and the resultant video in "./export" using swimTunnel function.
    # It saves a cvs file in a "./export/" and treated data in "./data/" using treatData function.
    try:
        videoPath = txtPath.get()
        expID = txtVidId.get()
        fps = int(txtVidFps.get())
        if ((fps > 0) and (fps < 1001)):
            swimTunnel(videoPath, expID, fps)
            treatData(expID,fps)
        else:
            raise Exception("The fps value must be in [1,1000].")
    except Exception as err:
        tk.messagebox.showerror("Error", err)
    else:
        tk.messagebox.showinfo(
            "Info", "The video has been processed. Check the results in './export' folder.")


def showResults():    
    
     # It shows the data in the "./export" folder.
    try:
        expID = txtVidId.get()
        fps = int(txtVidFps.get())
        beta, gamma, videoPathR = showData(expID, fps, gui=True)
        plotWin(beta, gamma, videoPathR)
    except Exception as err:
        tk.messagebox.showerror("Error", err)


def plotWin(beta, gamma, videoPathR):
    # Open the video in a VideoCapture object
    vid = cv.VideoCapture(videoPathR)
    
    # PLOT WIN PROPERTIES

    # Show window
    showWin = tk.Toplevel(mainWin)
    showWin.title("Plots and data")
    showWin.resizable(width=False, height=False)
    # Icon
    img = tk.PhotoImage(file='gar-fish.png')
    showWin.tk.call('wm', 'iconphoto', showWin._w, img)
    
    # FIGS
    x = np.arange(0, np.size(beta, 0))

    # Fig beta
    fig2 = figure.Figure(figsize=(6, 4), dpi=100)
    ax2 = fig2.add_subplot(111, title="Angle between the tail and the head perpendicular (beta)",xlabel="Frame", ylabel="Tail angle (rad)")
    ax2.plot(x, beta, "r", linewidth=0.5)
    canvas2 = FigureCanvasTkAgg(fig2, master=showWin)
    canvas_plot2 = canvas2.get_tk_widget()  # Draw figures
    canvas_plot2.grid(row=0, column=0,sticky=tk.W+tk.E+tk.N+tk.S)
    toolbarFrame2 = tk.Frame(master=showWin)
    toolbarFrame2.grid(row=1, column=0, sticky=tk.W+tk.S)
    toolbar2 = NavigationToolbar2Tk(canvas2, toolbarFrame2)
    toolbar2.update()

    # Fig gamma
    fig3 = figure.Figure(figsize=(6, 4), dpi=100)
    ax3 = fig3.add_subplot(111, title="Angle between the tail and the head (gamma)",xlabel="Frame", ylabel="Tail-Head angle (rad)")
    ax3.plot(x, gamma, "r", linewidth=0.5)
    canvas3 = FigureCanvasTkAgg(fig3, master=showWin)
    canvas_plot3 = canvas3.get_tk_widget()  # Draw figures
    canvas_plot3.grid(row=0, column=1, sticky=tk.W+tk.E+tk.N+tk.S)
    toolbarFrame3 = tk.Frame(master=showWin)
    toolbarFrame3.grid(row=1, column=1, sticky=tk.W+tk.S)
    toolbar3 = NavigationToolbar2Tk(canvas3, toolbarFrame3)
    toolbar3.update()

    # RESULTANT VIDEO

    return 0

# Click functions

def clickPath():
    filePath = tk.filedialog.askopenfilename(
        initialdir="/home/", title="Select file", filetypes=(("avi files", "*.avi"), ("all files", "*.*")))
    txtPath.delete(0, tk.END)
    txtPath.insert(0, filePath)


def clickRun():
    run_thread('run', runProcess)


def clickShow():
    run_thread('show', showResults)

# Threading functions to run the progressbar


def run_thread(name, func):
    Thread(target=run_function, args=(name, func)).start()


def run_function(name, func):
    # Disable all buttons
    for btn in buttons:
        btn['state'] = 'disabled'

    progressbar.start(interval=10)
    func()
    progressbar.stop()

    # Enable all buttons
    for btn in buttons:
        btn['state'] = 'normal'

### GUI ###

# WINDOW PROPERTIES

# Main window
mainWin = tk.Tk()

mainWin.title("Swim Tunnel")
mainWin.resizable(width=False, height=False)

# Icon
img = tk.PhotoImage(file='gar-fish.png')
mainWin.tk.call('wm', 'iconphoto', mainWin._w, img)

# FIELDS FRAME

# Main frame
mainFrame = tk.Frame(mainWin, padx=5, pady=5)
mainFrame.grid(column=0, row=0, sticky=(tk.N, tk.W, tk.E, tk.S))

# Video open path
lblPath = tk.Label(mainFrame, text="Video path:")
lblPath.grid(column=0, row=0, sticky=tk.W, padx=10, pady=10)

defaultPath = tk.StringVar(mainFrame, value='./video/water_tunnel.avi')
txtPath = tk.Entry(mainFrame, width=35, textvariable=defaultPath)
txtPath.grid(column=1, row=0, sticky=(
    tk.W, tk.E), padx=5, pady=5, columnspan=3)

btnPath = tk.Button(mainFrame, text="Open", command=clickPath)
btnPath.grid(column=4, row=0, sticky=tk.W, padx=5, pady=5)

# Export string name
lblVidId = tk.Label(mainFrame, text="ExperimentID:")
lblVidId.grid(column=0, row=1, sticky=tk.W, padx=5, pady=5)

defaultID = tk.StringVar(mainFrame, value="ExpID")
txtVidId = tk.Entry(mainFrame, textvariable=defaultID)
txtVidId.grid(column=1, row=1, sticky=(tk.W, tk.E), padx=5, pady=5)

# Export fps integer
lblVidFps = tk.Label(mainFrame, text="Video Fps:")
lblVidFps.grid(column=2, row=1, sticky=tk.W, padx=5, pady=5)

defaultFps = tk.StringVar(mainFrame, value='1000')
txtVidFps = tk.Entry(mainFrame, width=5, textvariable=defaultFps)
txtVidFps.grid(column=3, row=1, sticky=(tk.W, tk.E), padx=5, pady=5)

# RUN FRAME

# Buttons frame
btnFrame = tk.Frame(mainWin, padx=10, pady=10)
btnFrame.grid(column=0, row=1, sticky=(tk.N, tk.E, tk.S))

# Progress bar
progressbar = ttk.Progressbar(btnFrame, mode="indeterminate")
progressbar.grid(column=0, row=0, sticky=tk.W, padx=5, pady=5)

# Spacer
spacer = tk.Label(btnFrame, text=" ")
spacer.grid(column=1, row=0, sticky=tk.W, padx=110, pady=5)

# Run button
btnRun = tk.Button(btnFrame, text="Run", width=5, command=clickRun)
btnRun.grid(column=3, row=0, sticky=tk.E, padx=5, pady=5)

# Show button.
btnShow = tk.Button(btnFrame, text="Show", width=5, command=clickShow)
btnShow.grid(column=2, row=0, sticky=tk.E, padx=5, pady=5)

buttons = [btnRun, btnShow]

mainWin.mainloop()

