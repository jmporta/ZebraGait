import os
import numpy as np
import matplotlib.pyplot as pl


def showData(expID, fps, gui=False):

    # Init. data
    dataPath = "./data/"
    exportPath = "./export/"

    # Import data
    ampl, beta, gamma = importMesures(dataPath, expID)

    # Plot data
    if gui:
        return beta, gamma, exportPath + expID + ".avi"
    else:
        plotGraphs(ampl, beta, gamma)

    return 0

def importMesures(dataPath, expID):

    # Import all the data in npy files
    ampl = np.load(dataPath + expID + "_ampl.npy")
    beta = np.load(dataPath + expID + "_beta.npy")
    gamma = np.load(dataPath + expID + "_gamma.npy")

    return ampl, beta, gamma


def plotGraphs(ampl, beta, gamma):

    # Plot the amplitude
    pl.figure(1)
    x = np.arange(0, np.size(ampl, 0))
    pl.plot(x, ampl, "r", linewidth=0.5)
    pl.plot(np.zeros(np.size(x)), 'b--', linewidth=0.5)
    pl.suptitle("Amplitude of the tail to the head perpendicular")
    pl.ylabel("Amplitude(px)")
    pl.xlabel("Frame")

    # Plot the Tail-Angle beta
    pl.figure(2)
    x = np.arange(0, np.size(beta, 0))
    pl.plot(x, beta, "r", linewidth=0.5)
    pl.plot(np.zeros(np.size(x)), 'b--', linewidth=0.5)
    pl.suptitle("Angle between the tail and the head perpendicular (beta)")
    pl.ylabel("Tail angle (rad)")
    pl.xlabel("Frame")

    # Plot Tail-Head angle gamma
    x = np.arange(0, np.size(gamma, 0))
    pl.figure(3)
    pl.plot(x, gamma, "r", linewidth=0.5)
    pl.plot(np.pi*np.ones(np.size(x)), 'b--', linewidth=0.5)
    pl.suptitle("Angle between the tail and the head perpendicular(beta)")
    pl.ylabel("Tail-Head angle (rad)")
    pl.xlabel("Frame")


    # Show Plots
    pl.show()

    return 0


if (__name__ == "__main__"):
    showData("ExpTEST", 1000)
    print("DONE.")
