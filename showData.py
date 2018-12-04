import pathlib
import numpy as np
import matplotlib.pyplot as pl

import config

def showData(exportPath, expID, fps, gui=False):


    # Import data
    ind, beta, = importMesures(exportPath, expID)

    # Plot data
    if gui:
        return ind, beta, pathlib.Path(exportPath, expID, expID + ".avi")
    else:
        plotGraphs(ind, beta)

def importMesures(dataPath, expID):

    # Import all the data in npy files
    ind = np.load(pathlib.Path(dataPath,expID,"data", expID + "_ind.npy"))
    beta = np.load(pathlib.Path(dataPath,expID, "data", expID + "_beta.npy"))

    return ind, beta

def plotGraphs(ind, beta):


    # Plot the Tail-Angle beta
    pl.figure(1)
    #x = np.arange(0, np.size(beta, 0))
    pl.plot(ind, beta, "r", linewidth=0.5)
    pl.plot(np.zeros(np.size(ind)), 'b--', linewidth=0.5)
    pl.suptitle("Angle between the tail and the head perpendicular (beta)")
    pl.ylabel("Tail angle (rad)")
    pl.xlabel("Frame")

    # Show Plots
    pl.show()

if (__name__ == "__main__"):

    exportPath = "./export/"
    expID = "TestFish"
    fps = 1000

    showData(exportPath, expID, fps)
    
    print("DONE.")
