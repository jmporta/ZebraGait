# Python libs
import tkinter as tk
from tkinter import filedialog
from tkinter import ttk

# Local libs
from swimTunnel import swimTunnel
from treatData import treatData

# FUNCTIONS

def runProcess():
    try:
        filePath = txtPath.get()
        expID = txtVidId.get()
        Fps = int(txtVidFps.get())
        if ((Fps > 0) and (Fps < 1001)):
            swimTunnel(filePath,expID)
            treatData(Fps, expID)
        else:
            raise Exception("The fps value must be in [1,1000].")
    except Exception as err:
        tk.messagebox.showerror("Error",err)
    else:
        tk.messagebox.showinfo("Info", "The video has been processed. Check the results in './export' folder.")


def showResults():
    pass

# MAIN WIDGETS

# Main window
mainWin = tk.Tk()
mainWin.title("Swim Tunnel")
mainWin.resizable(width=False, height=False)

# Icon
img = tk.PhotoImage(file='gar-fish.png')
mainWin.tk.call('wm', 'iconphoto', mainWin._w, img)

# Main frame
mainFrame = tk.Frame(mainWin, padx=5, pady=5)
mainFrame.grid(column=0, row=0, sticky=(tk.N, tk.W, tk.E, tk.S))

# Buttons frame
btnFrame = tk.Frame(mainWin, padx=10, pady=10)
btnFrame.grid(column=0, row=1, sticky=(tk.N, tk.E, tk.S), columnspan=4)

# Video open path
lblPath = tk.Label(mainFrame, text="Video path:")
lblPath.grid(column=0,row=0, sticky=tk.W, padx=10,pady=10)

defaultPath = tk.StringVar(mainFrame, value='./video/water_tunnel.avi')
txtPath = tk.Entry(mainFrame, width=35,textvariable=defaultPath)
txtPath.grid(column=1, row=0, sticky=(tk.W, tk.E), padx=5, pady=5, columnspan=3)

def clickPath():
    filePath = tk.filedialog.askopenfilename(initialdir="/home/",title="Select file", filetypes=(("avi files", "*.avi"), ("all files", "*.*")))
    txtPath.delete(0, tk.END)
    txtPath.insert(0, filePath)

btnPath = tk.Button(mainFrame, text="Open", command=clickPath)
btnPath.grid(column=4, row=0, sticky=tk.W, padx=5, pady=5)

# Export string name
lblVidId = tk.Label(mainFrame, text="ExperimentID:")
lblVidId.grid(column=0, row=1, sticky=tk.W, padx=5, pady=5)

defaultID = tk.StringVar(mainFrame, value='ExpID_0')
txtVidId = tk.Entry(mainFrame,textvariable=defaultID)
txtVidId.grid(column=1, row=1, sticky=(tk.W, tk.E), padx=5, pady=5)

# Export fps integer
lblVidFps = tk.Label(mainFrame, text="Video Fps:")
lblVidFps.grid(column=2, row=1, sticky=tk.W, padx=5, pady=5)

defaultFps = tk.StringVar(mainFrame, value='1000')
txtVidFps = tk.Entry(mainFrame,width=5,textvariable=defaultFps)
txtVidFps.grid(column=3, row=1, sticky=(tk.W, tk.E), padx=5, pady=5)

# Progress bar
progressbar = ttk.Progressbar(btnFrame, mode="indeterminate")
progressbar.grid(column=0,row=0)
progressbar.start()

# BUTTONS

# Run button
# The selected video will be processed and the resultant data will be treated. 
# It saves the skeletons in a "./data/" and a video in "./export" using swimTunnel function. 
# It saves a cvs file with the treated data in a "./export" using treatData function.
def clickRun():
    runProcess()

btnVid = tk.Button(btnFrame, text="Run", width=5, command=clickRun)
btnVid.grid(column=1, row=0, sticky=tk.E, padx=5, pady=5)

# Show button.
# It shows the data in the "./export" folder.  TODO: save the data on the desired folder.
def clickShow():
    showResults()

btnVid = tk.Button(btnFrame, text="Show", width=5, command=clickShow)
btnVid.grid(column=0, row=0, sticky=tk.E, padx=5, pady=5)


mainWin.mainloop()







