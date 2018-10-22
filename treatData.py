import fnmatch
import os
import numpy as np
import matplotlib.pyplot as plt


def treatData(fps,expID):

    # Init. data
    axisLon = 200  # length of the headP-HeadPe
    importPath = "./data/"
    exportPath = "./export/"
    
    # Number of files
    nFiles = len(fnmatch.filter(os.listdir(importPath), "*.npy"))

    # Obtain data
    print("Computing Data...")
    tailP, headP, headPe = importData(importPath, expID, axisLon, nFiles)
    ampl, beta, gamma = computeData(tailP, headP, headPe, nFiles)

    # Export data
    if (not os.path.isdir(exportPath)): # create the folder if it does not exisist
        os.makedirs(exportPath)

    exportData(tailP, headP, headPe, ampl, beta, gamma,
               nFiles, exportPath, expID)

    #plotGraphs(ampl, beta, gamma)

    print("Computation DONE.")

    return 0


def importData(filePath, expID, axisLon, nFiles):

    # Init. the main arrays
    A = np.zeros((1, 2), int)
    tailP = np.zeros((nFiles, 2), int)
    headP = np.zeros((nFiles, 2), int)
    headPe = np.zeros((nFiles, 2), int)

    # Export/Extract the data from the files
    for i in range(nFiles):

        # Load skeleton from a numpy binary array file *.npy
        A = np.load(filePath + expID + "_" + str(i+1) + ".npy")
        
        # Data pre-treatment
        A = np.reshape(A, (np.size(A, 0), 2)) # Convert the array-points to a matrix
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

    dataHeader = "x_TailP, y_TailP, x_HeadP, y_HeadP, x_HeadPe, y_HeadPe, Amplitude, TailAngle(beta), TailHeadAngle(Gamma)"
    data = np.transpose([tailP[:, 0], tailP[:, 1], headP[:, 0], headP[:, 1], headPe[:, 0], headPe[:, 1], ampl, beta, gamma])
    np.savetxt(filePath + expID + ".csv",data, delimiter=',', header=dataHeader, comments="")

    return 0


# DebugOnly: MAIN
treatData(1000, "ExpTEST")
print("DONE.")
