import logging
import pathlib
import os

import numpy as np

import config


def treatData(exportPath, expID, fps):

    # Init. data
    axisLen = config.AXIS_LEN  
    dataPath = config.DATA_PATH

    # Clean previous data
    cleanData(dataPath,expID)

    # Number of files
    nFiles = len(list(pathlib.Path(dataPath).glob("*.npy")))

    # Obtain data
    logging.info("Computing Data...")
    ind, tailP, headP, headPe, nValidFrames = importData(dataPath, expID, axisLen, nFiles)
    beta = computeData(tailP, headP, headPe, nValidFrames)
    ind[:nValidFrames] = (nFiles/fps)*ind[:nValidFrames]

    # Export data
    exportData(ind, tailP, headP, headPe, beta, dataPath, exportPath, expID, nValidFrames)

    logging.info("Computation DONE.")

def importData(filePath, expID, axisLen, nFiles):

    # Init. the main arrays
    ind = np.zeros((nFiles), int)
    skeleton = np.zeros((1, 2), int)
    tailP = np.zeros((nFiles, 2), int)
    headP = np.zeros((nFiles, 2), int)
    headPe = np.zeros((nFiles, 2), int)

    # Export/Extract the data from the files
    k = 0 # valid frames index
    for i in range(nFiles):

        # Load skeleton from a numpy binary array file *.npy
        skeleton = np.load(pathlib.Path(filePath,expID + "_" + str(i+1) + ".npy"))
        
        if not np.array_equal(skeleton, 0):
            # Data pre-treatment
            skeleton = np.reshape(skeleton, (np.size(skeleton, 0), 2)) # convert the array-points to a matrix
            skeleton = skeleton[np.argsort(skeleton[:, 0])] # sort points by x
            skeleton = np.unique(skeleton, axis=0) # delete repeated points
            skeleton[:, 1] = -skeleton[:, 1] # convert coords. to R^2 (original ones are image matrix indicies)
            # Skeleton treatmeant
            skeletonLen = computeSK(skeleton)
            # # Save points
            ind[k] = i
            tailP[k, :] = skeleton[0, :]
            headP[k, :] = skeleton[-1, :]
            headPe[k, :] = skeleton[-int(skeletonLen*axisLen), :]
            # Update the valid index
            k += 1

    return ind, tailP, headP, headPe, k

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

    # # Tail-Head angle
    # gamma = np.zeros(nValidFrames, float)
    # gamma[:] = np.pi - beta[:]

    return beta

def computeSK(skeleton):
    skeletonLen = 0
    for i in range(1,len(skeleton)):
        skeletonLen += np.sqrt((skeleton[i-1][0] - skeleton[i][0])**2 + (skeleton[i-1][1] - skeleton[i][1])**2)

    return skeletonLen

def exportData(ind, tailP, headP, headPe, beta, dataPath, exportPath, expID, nValidFrames):

    # Export all the data in a cvs file
    dataHeader = "Time(ms), x_Tail,y_Tail,x_Head,y_Head,x_Joint,y_Joint,TailAngle(beta)"
    data = np.transpose([ind[:nValidFrames], tailP[:nValidFrames, 0], tailP[:nValidFrames, 1], headP[:nValidFrames, 0],
                         headP[:nValidFrames, 1], headPe[:nValidFrames, 0], headPe[:nValidFrames, 1], beta])
    np.savetxt(pathlib.Path(exportPath,expID + ".csv"), data, fmt="%10.5f",
               delimiter=',', header=dataHeader, comments="")

    # Export all the data in npy files to show faster in showData
    np.save(pathlib.Path(dataPath, expID + "_ind"), ind[:nValidFrames])
    np.save(pathlib.Path(dataPath, expID + "_beta"), beta)

    return 0

def cleanData(dirPath,expID):
    if (pathlib.Path(dirPath, expID + "_ind.npy").exists()):
        os.remove(pathlib.Path(dirPath, expID + "_ind.npy"))
    if (pathlib.Path(dirPath, expID + "_beta.npy").exists()):
        os.remove(pathlib.Path(dirPath, expID + "_beta.npy"))

if (__name__ == "__main__"):

    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s: %(message)s"
    )

    exportPath = "./export/"
    expID = "TestFish"
    fps = 1000

    try:
        treatData(exportPath, expID, fps)
    except Exception as err:
        logging.error(err)
    
    logging.info("DONE.")
