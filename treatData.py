import fnmatch
import os
import numpy as np
import matplotlib.pyplot as plt


def treatData(fps,expID):

    # Init. data
    axisLon = 200  # length of the headP-HeadPe
    
    # number of files
    nFiles = len(fnmatch.filter(os.listdir("./data"), "*.dat"))

    # Obtain data
    tailP, headP, headPe = importData(axisLon, nFiles)
    ampl, beta, gamma = computeData(tailP, headP, headPe, nFiles)

    # Export data
    exportPath = "./export/"
    if not os.path.isdir(exportPath): # create the folder if it does not exisist
        os.makedirs(exportPath)

    exportData(tailP, headP, headPe, ampl, beta, gamma,
               nFiles, exportPath, expID)

    #plotGraphs(ampl, beta, gamma)

    return 0


def importData(axisLon, nFiles):

    # Init. the main arrays
    A = np.empty((1, 2), int)
    tailP = np.zeros((nFiles, 2), int)
    headP = np.zeros((nFiles, 2), int)
    headPe = np.zeros((nFiles, 2), int)

    # Export/Extract the data from the files
    for i in range(0, nFiles-1):

        # Open/Load/Close data file
        myImport = "./data/SkeletonFrame" + str(i+1) + ".dat"
        myFile = open(myImport, "r")
        A = np.loadtxt(myFile, dtype=int, usecols=range(2))
        myFile.close()

        # Data pre-treatment
        A = A[np.argsort(A[:, 0])]  # sort points by x
        A = np.unique(A, axis=0)  # delete repeated points
        A[:, 1] = -A[:, 1] # convert coords. to R^2 (original ones are image matrix indicies)

        # Save data
        tailP[i, :] = A[0, :]
        headP[i, :] = A[-1, :]
        headPe[i, :] = A[-axisLon, :]

    return tailP, headP, headPe


def computeData(tailP, headP, headPe, nFiles):

    # Amplitude between the tail and the head perpendicular(sin(alpha)=(vxu)/||v||·|u|||)
    sinAlpha = np.zeros(nFiles, float)
    h = np.zeros(nFiles, float)
    ampl = np.zeros(nFiles, float)

    for i in range(0, nFiles-1):
        h[i] = np.sqrt(np.abs(tailP[i, 0]-headP[i, 0])**2 +
                       np.abs(tailP[i, 1]-headP[i, 1])**2)
        sinAlpha[i] = ((tailP[i, 0]-headP[i, 0])*(headPe[i, 1]-headP[i, 1]) - (headPe[i, 0]-headP[i, 0])*(tailP[i, 1]-headP[i, 1])) / (np.sqrt(
            (tailP[i, 0]-headP[i, 0])**2 + (tailP[i, 1]-headP[i, 1])**2) * np.sqrt((headPe[i, 0]-headP[i, 0])**2 + (headPe[i, 1]-headP[i, 1])**2))
        ampl[i] = h[i] * sinAlpha[i]

    # Tail angle from the axis headP/headPe
    beta = np.zeros(nFiles, float)

    for i in range(0, nFiles-1):
        beta[i] = np.arcsin(ampl[i]/np.sqrt(np.abs(tailP[i, 0] -
                                                   headPe[i, 0])**2 + np.abs(tailP[i, 1]-headPe[i, 1])**2))

    # Tail-Head angle
    gamma = np.zeros(nFiles, float)
    gamma[:] = np.pi - beta[:]

    return ampl, beta, gamma


def plotGraphs(ampl, beta, gamma):

    # Plot the amplitude
    plt.figure(1)
    x = np.arange(0, np.size(ampl, axis=0))
    plt.plot(x, ampl, "r", linewidth=0.5)
    plt.plot(np.zeros(np.size(x)), 'b--', linewidth=0.5)
    plt.suptitle("Amplitude of the tail to the head perpendicular")
    plt.ylabel("Amplitude(px)")
    plt.xlabel("Frame")
    plt.show()

    # Plot the Tail-Angle beta
    plt.figure(2)
    x = np.arange(0, np.size(beta, axis=0))
    plt.plot(x, beta, "r", linewidth=0.5)
    plt.plot(np.zeros(np.size(x)), 'b--', linewidth=0.5)
    plt.suptitle("Angle between the tail and the head perpendicular (beta)")
    plt.ylabel("Tail angle (rad)")
    plt.xlabel("Frame")
    plt.show()

    # Plot Tail-Head angle gamma
    x = np.arange(0, np.size(gamma, axis=0))
    plt.figure(3)
    plt.plot(x, gamma, "r", linewidth=0.5)
    plt.plot(np.pi*np.ones(np.size(x)), 'b--', linewidth=0.5)
    plt.suptitle("Angle between the tail and the head perpendicular(beta)")
    plt.ylabel("Tail-Head angle (rad)")
    plt.xlabel("Frame")
    plt.show()

    return 0


def exportData(tailP, headP, headPe, ampl, beta, gamma, nFiles, filePath, expID):

    if not os.path.exists(filePath):
        os.makedirs(filePath)

    myExport = filePath + expID + ".csv"

    myFile = open(myExport, "w")

    columnTitleRow = "TailP, HeadP, HeadPe, Amplitude, TailAngle(beta), TailHeadAngle(Gamma)\n"
    myFile.write(columnTitleRow)

    for i in range(0, nFiles-1):
        row = str(tailP[i]) + ", " + str(headP[i]) + ", " + str(headPe[i]) + \
            ", " + str(ampl[i]) + ", " + str(beta[i]) + \
            ", " + str(gamma[i]) + "\n"
        myFile.write(row)

    myFile.close()

    return 0
