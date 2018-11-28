import pathlib
import numpy as np
import matplotlib.pyplot as pl

import config

def showData(exportPath, expID, fps, gui=False):

    # Init. data
    dataPath = config.DATA_PATH

    # Import data
    ind, ampl, beta, gamma = importMesures(dataPath, expID)

    # Plot data
    if gui:
        return ind, beta, gamma, pathlib.Path(exportPath, expID + ".avi")
    else:
        plotGraphs(ind, ampl, beta, gamma)

def importMesures(dataPath, expID):

    # Import all the data in npy files
    ind = np.load(pathlib.Path(dataPath, expID + "_ind.npy"))
    ampl = np.load(pathlib.Path(dataPath, expID + "_ampl.npy"))
    beta = np.load(pathlib.Path(dataPath, expID + "_beta.npy"))
    gamma = np.load(pathlib.Path(dataPath, expID + "_gamma.npy"))

    return ind, ampl, beta, gamma

def plotGraphs(ind, ampl, beta, gamma):

    # Plot the amplitude
    pl.figure(1)
    #x = np.arange(0, np.size(ampl, 0))
    pl.plot(ind, ampl, "r", linewidth=0.5)
    pl.plot(np.zeros(np.size(ind)), 'b--', linewidth=0.5)
    pl.suptitle("Amplitude of the tail to the head perpendicular")
    pl.ylabel("Amplitude(px)")
    pl.xlabel("Frame")

    # Plot the Tail-Angle beta
    pl.figure(2)
    #x = np.arange(0, np.size(beta, 0))
    pl.plot(ind, beta, "r", linewidth=0.5)
    pl.plot(np.zeros(np.size(ind)), 'b--', linewidth=0.5)
    pl.suptitle("Angle between the tail and the head perpendicular (beta)")
    pl.ylabel("Tail angle (rad)")
    pl.xlabel("Frame")

    # Plot Tail-Head angle gamma
    #x = np.arange(0, np.size(gamma, 0))
    pl.figure(3)
    pl.plot(ind, gamma, "r", linewidth=0.5)
    pl.plot(np.pi*np.ones(np.size(ind)), 'b--', linewidth=0.5)
    pl.suptitle("Angle between the tail and the head perpendicular(beta)")
    pl.ylabel("Tail-Head angle (rad)")
    pl.xlabel("Frame")

    # Show Plots
    pl.show()

if (__name__ == "__main__"):

    exportPath = "./export/"
    expID = "TestFish"
    fps = 1000

    showData(exportPath,expID, fps)
    
    print("DONE.")
