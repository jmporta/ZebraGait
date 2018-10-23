import fnmatch
import os
import numpy as np


def treatData(expID, fps):

    # Init. data
    axisLon = 50  # length of the headP-HeadPe
    dataPath = "./data/"
    exportPath = "./export/"

    # Check the paths
    if not os.path.exists(dataPath):
        os.makedirs(dataPath)  # create the folder if it does not exisist
    if not os.path.exists(exportPath):
        os.makedirs(exportPath)  # create the folder if it does not exisist

    # Number of files
    nFiles = len(fnmatch.filter(os.listdir(dataPath), "*.npy"))

    # Obtain data
    print("Computing Data...")
    tailP, headP, headPe = importData(dataPath, expID, axisLon, nFiles)
    ampl, beta, gamma = computeData(tailP, headP, headPe, nFiles)

    # Export data
    exportData(tailP, headP, headPe, ampl, beta, gamma, dataPath, exportPath, expID)

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
        # Convert the array-points to a matrix
        A = np.reshape(A, (np.size(A, 0), 2))
        A = A[np.argsort(A[:, 0])]  # sort points by x
        A = np.unique(A, axis=0)  # delete repeated points
        # convert coords. to R^2 (original ones are image matrix indicies)
        A[:, 1] = -A[:, 1]

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


def exportData(tailP, headP, headPe, ampl, beta, gamma, dataPath, exportPath, expID):

    # Export all the data in a cvs file
    dataHeader = "x_TailP, y_TailP, x_HeadP, y_HeadP, x_HeadPe, y_HeadPe, Amplitude, TailAngle(beta), TailHeadAngle(Gamma)"
    data = np.transpose([tailP[:, 0], tailP[:, 1], headP[:, 0],
                         headP[:, 1], headPe[:, 0], headPe[:, 1], ampl, beta, gamma])
    np.savetxt(exportPath + expID + ".csv", data,
               delimiter=',', header=dataHeader, comments="")

    # Export all the data in npy files
    np.save(dataPath + expID + "_ampl", ampl)
    np.save(dataPath + expID + "_beta", beta)
    np.save(dataPath + expID + "_gamma", gamma)

    return 0


if (__name__ == "__main__"):
    # DebugOnly: MAIN
    treatData(1000, "ExpTEST")
    print("DONE.")
