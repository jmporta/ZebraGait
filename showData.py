import pathlib
import numpy as np
import matplotlib.pyplot as plt

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
    plt.figure(1)
    plt.plot(ind, beta, "r", linewidth=0.5)
    plt.plot(np.zeros(np.size(ind)), 'b--', linewidth=0.5)
    plt.suptitle("Angle between the tail and the head perpendicular (beta)")
    plt.ylabel("Tail angle (deg)")
    plt.xlabel("ms")

    # Show Plots
    plt.show()

if (__name__ == "__main__"):

    exportPath = "./export/"
    expID = "TestFish"
    fps = 1000

    showData(exportPath, expID, fps)
    
    print("DONE.")
