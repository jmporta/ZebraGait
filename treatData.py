import logging
import pathlib
import os

import numpy as np

import config


def treatData(expID, fps):

    # Init. data
    axisLon = config.AXIS_LON  
    dataPath = config.DATA_PATH
    exportPath = config.EXPORT_PATH

    # Clean previous data
    cleanData(dataPath,expID)

    # Number of files
    nFiles = len(list(pathlib.Path(dataPath).glob("*.npy")))

    # Obtain data
    logging.info("Computing Data...")
    tailP, headP, headPe, nValidFrames = importData(dataPath, expID, axisLon, nFiles)
    print("import done")
    ampl, beta, gamma = computeData(tailP, headP, headPe, nValidFrames)

    # Export data
    exportData(tailP, headP, headPe, ampl, beta, gamma, dataPath, exportPath, expID, nValidFrames)

    logging.info("Computation DONE.")

    return 0


def importData(filePath, expID, axisLon, nFiles):

    # Init. the main arrays
    A = np.zeros((1, 2), int)
    tailP = np.zeros((nFiles, 2), int)
    headP = np.zeros((nFiles, 2), int)
    headPe = np.zeros((nFiles, 2), int)

    # Export/Extract the data from the files
    k = 0 # valid frames index
    for i in range(nFiles):

        # Load skeleton from a numpy binary array file *.npy
        A = np.load(pathlib.Path(filePath,expID + "_" + str(i+1) + ".npy"))
        
        if not np.array_equal(A, 0):
            # Data pre-treatment
            A = np.reshape(A, (np.size(A, 0), 2)) # convert the array-points to a matrix
            A = A[np.argsort(A[:, 0])]  # sort points by x
            A = np.unique(A, axis=0)  # delete repeated points
            A[:, 1] = -A[:, 1]# convert coords. to R^2 (original ones are image matrix indicies)
            # Save data
            tailP[k, :] = A[0, :]
            headP[k, :] = A[-1, :]
            headPe[k, :] = A[-axisLon, :]
            # Update the valid index
            k += 1

    return tailP, headP, headPe, k


def computeData(tailP, headP, headPe, nValidFrames):

    # Amplitude between the tail and the head perpendicular(sin(alpha)=(vxu)/||v||·||u||)
    sinAlpha = np.zeros(nValidFrames, float)
    h = np.zeros(nValidFrames, float)
    ampl = np.zeros(nValidFrames, float)

    for i in range(nValidFrames):
        h[i] = np.sqrt(np.abs(tailP[i, 0]-headP[i, 0])**2 + np.abs(tailP[i, 1]-headP[i, 1])**2)
        sinAlpha[i] = ((tailP[i, 0]-headP[i, 0])*(headPe[i, 1]-headP[i, 1]) - (headPe[i, 0]-headP[i, 0])*(tailP[i, 1]-headP[i, 1])) / (np.sqrt(
            (tailP[i, 0]-headP[i, 0])**2 + (tailP[i, 1]-headP[i, 1])**2) * np.sqrt((headPe[i, 0]-headP[i, 0])**2 + (headPe[i, 1]-headP[i, 1])**2))
        ampl[i] = h[i] * sinAlpha[i]

    # Tail angle from the axis headP/headPe
    beta = np.zeros(nValidFrames, float)

    for i in range(nValidFrames):
        beta[i] = np.arcsin(ampl[i]/np.sqrt(np.abs(tailP[i, 0] -
                                                   headPe[i, 0])**2 + np.abs(tailP[i, 1]-headPe[i, 1])**2))

    # Tail-Head angle
    gamma = np.zeros(nValidFrames, float)
    gamma[:] = np.pi - beta[:]

    return ampl, beta, gamma


def exportData(tailP, headP, headPe, ampl, beta, gamma, dataPath, exportPath, expID, nValidFrames):

    # Export all the data in a cvs file
    dataHeader = "x_TailP,y_TailP,x_HeadP,y_HeadP,x_HeadPe,y_HeadPe,Amplitude,TailAngle(beta),TailHeadAngle(Gamma)"
    data = np.transpose([tailP[:nValidFrames, 0], tailP[:nValidFrames, 1], headP[:nValidFrames, 0],
                         headP[:nValidFrames, 1], headPe[:nValidFrames, 0], headPe[:nValidFrames, 1], ampl, beta, gamma])
    np.savetxt(pathlib.Path(exportPath,expID + ".csv"), data, fmt="%10.5f",
               delimiter=',', header=dataHeader, comments="")

    # Export all the data in npy files to show faster in showData
    np.save(pathlib.Path(dataPath, expID + "_ampl"), ampl)
    np.save(pathlib.Path(dataPath, expID + "_beta"), beta)
    np.save(pathlib.Path(dataPath, expID + "_gamma"), gamma)

    return 0


def cleanData(dirPath,expID):
    if (pathlib.Path(dirPath,expID + "_ampl.npy").exists()):
        os.remove(pathlib.Path(dirPath, expID + "_ampl.npy"))
    if (pathlib.Path(dirPath, expID + "_beta.npy").exists()):
        os.remove(pathlib.Path(dirPath, expID + "_beta.npy"))
    if (pathlib.Path(dirPath, expID + "_gamma.npy").exists()):
        os.remove(pathlib.Path(dirPath, expID + "_gamma.npy"))


if (__name__ == "__main__"):

    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s: %(message)s"
    )

    expID = "ExpID"
    fps = 1000

    try:
        treatData(expID, fps)
    except Exception as err:
        logging.error(err)
    
    logging.info("DONE.")
