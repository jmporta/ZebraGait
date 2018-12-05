import logging
import pathlib
import os

import numpy as np
from scipy import interpolate

# # Debug Only: draw approx
# import matplotlib.pyplot as plt
# import matplotlib.animation as animation

import config


def treatData(exportPath, expID, fps):

    # Init. data
    partJoint = config.PARTITION_JOINT

    # Check/Create paths
    pathlib.Path(exportPath, expID, "data").mkdir(parents=True, exist_ok=True)

    # Number of files
    nFiles = len(list(pathlib.Path(exportPath,expID,"skeleton").glob("*.npy")))

    # Obtain data
    logging.info("Computing Data...")
    ind, tailP, headP, jointP, nValidFrames, gamma, torsionP = importData(exportPath, expID, partJoint, nFiles)
    beta, ampl = computeBeta(tailP, headP, jointP, nValidFrames)
    ind[:nValidFrames] = (nFiles/fps)*ind[:nValidFrames]

    # Export data
    exportData(ind, tailP, headP, jointP, beta, ampl, gamma, torsionP, exportPath, expID, nValidFrames)

    logging.info("Computation DONE.")

def importData(filePath, expID, partJoint, nFiles):

    # Init. the main arrays
    ind = np.zeros((nFiles), int)
    gamma = np.zeros((nFiles),float)
    torsionP = np.zeros((nFiles, 2), int)
    tailP = np.zeros((nFiles, 2), int)
    headP = np.zeros((nFiles, 2), int)
    jointP = np.zeros((nFiles, 2), int)

    # # Debug Only: Start interactive fig
    # plt.ion()
    # fig = plt.figure()

    # Export/Extract the data from the files
    validInd = 0 # valid frames index
    for i in range(nFiles):

        # Load skeleton from a numpy binary array file *.npy
        skeleton = np.load(pathlib.Path(filePath,expID,"skeleton",expID + "_" + str(i+1) + ".npy"))
        
        if not np.array_equal(skeleton, 0):
            # Data pre-treatment
            skeleton = np.reshape(skeleton, (np.size(skeleton, 0), 2)) # convert the array-points to a matrix
            skeleton = skeleton[np.argsort(skeleton[:, 0])] # sort points by x
            skeleton = np.unique(skeleton, axis=0) # delete repeated points
            skeleton = uniqueMean(skeleton) # delete repeated points_x and get the mean_y
            skeleton[:, 1] = -skeleton[:, 1] # convert coords. to R^2 (original ones are image matrix indicies)

            # Skeleton pretreatmeant
            _skeletonLen, joint = lenPartSK(skeleton, partJoint)
            gamma[validInd], torsionP[validInd,:], _PART = computeGamma(skeleton, joint)

            # Save points- Fish direction swimming: left
            ind[validInd] = i
            tailP[validInd, :] = skeleton[-1, :]
            headP[validInd, :] = skeleton[0, :]
            jointP[validInd, :] = skeleton[joint, :]
            # Update the valid index
            validInd += 1
            
            
            # # Debug Only: draw approx
            # x = skeleton[:, 0]
            # y = skeleton[:, 1]
            # plot1 = plt.figure(1)
            # plt.plot(x, y, 'b-')
            # plt.plot(x[joint],y[joint],'go')
            # plt.plot(torsionP[validInd-1,0],torsionP[validInd-1,1],'r*')  
            # plt.plot(PART[:,0],PART[:,1],'y+')
            # plt.axis((0, 426.7, -154, -50))
            # # Update canvas
            # fig.canvas.draw()
            # plot1.clf()
            

    return ind, tailP, headP, jointP, validInd, gamma, torsionP

def uniqueMean(skeleton):

    skmean = np.array([], int).reshape(0,2)

    _sk, skind, skcounts = np.unique(skeleton[:,0],return_index=True,return_counts=True)

    for i,ind in enumerate(skind):
        ymean = 0
        for j in range(skcounts[i]):
            ymean = ymean + skeleton[ind+j, 1]
        skmean = np.vstack([skmean,[skeleton[i,0], int(ymean/skcounts[i])]])

    return skmean

def computeBeta(tailP, headP, jointP, nValidFrames):

    # Amplitude between the tail and the head perpendicular
    # sin(alpha)=(vXu)/||v||·||u||  (permits to obtain the sign of angle)
    sinAlpha = np.zeros(nValidFrames, float)
    h = np.zeros(nValidFrames, float)
    ampl = np.zeros(nValidFrames, float)

    for i in range(nValidFrames):
        h[i] = np.sqrt(np.abs(tailP[i, 0]-headP[i, 0])**2 + np.abs(tailP[i, 1]-headP[i, 1])**2)
        sinAlpha[i] = ((tailP[i, 0]-headP[i, 0])*(jointP[i, 1]-headP[i, 1]) - (jointP[i, 0]-headP[i, 0])*(tailP[i, 1]-headP[i, 1])) / (np.sqrt(
            (tailP[i, 0]-headP[i, 0])**2 + (tailP[i, 1]-headP[i, 1])**2) * np.sqrt((jointP[i, 0]-headP[i, 0])**2 + (jointP[i, 1]-headP[i, 1])**2))
        ampl[i] = h[i] * sinAlpha[i]

    # Tail angle from the axis headP/jointP
    beta = np.zeros(nValidFrames, float)

    for i in range(nValidFrames):
        beta[i] = np.rad2deg( np.arcsin(ampl[i]/np.sqrt(np.abs(tailP[i, 0] - jointP[i, 0])**2 + np.abs(tailP[i, 1]-jointP[i, 1])**2)) )

    return beta, ampl

def lenPartSK(skeleton, partition):
    # Compute the length of the skeleton
    skeletonLen = 0
    for i in range(1,len(skeleton)):
        skeletonLen += ((skeleton[i-1][0] - skeleton[i][0])**2 + (skeleton[i-1][1] - skeleton[i][1])**2)**(1/2)

    # Compute the desired index point on partition measure
    measure = 0
    for i in range(1,len(skeleton)):
        measure += ((skeleton[i-1][0] - skeleton[i][0])**2 + (skeleton[i-1][1] - skeleton[i][1])**2)**(1/2)
        if measure > skeletonLen*partition:
            partP = i
            break

    return skeletonLen, partP

def computeGamma(skeleton, joint):
    
    # Partition of the skeleton
    partTorsion = 2
    partSK = np.zeros((partTorsion + 1,2), int)

    partSK[0, :] = skeleton[joint, :]
    for i in range(1, partTorsion):
        _skeletonJointLen, torsionP = lenPartSK(skeleton[joint:, :], i/partTorsion)
        j = joint+torsionP
        partSK[i,:] = skeleton[j,:]
    partSK[-1, :] = skeleton[-1, :]
    
    # Compute de minimum angle
    # cos(alpha)=(v·u)/||v||·||u|| 
    minT = np.pi
    k = 0
    for i in range(1,partTorsion):
        normProduct = ((partSK[i-1, 0]-partSK[i, 0])**2 + (partSK[i-1, 1]-partSK[i, 1])**2)**(1/2) * ((partSK[i+1, 0]-partSK[i, 0])**2 + (partSK[i+1, 1]-partSK[i, 1])**2)**(1/2)
        dotProduct = ((partSK[i-1, 0]-partSK[i, 0])*(partSK[i+1, 0]-partSK[i, 0]) + (partSK[i-1, 1]-partSK[i, 1])*(partSK[i+1, 1]-partSK[i, 1]))
        cosAlpha = dotProduct / normProduct
        if np.abs(cosAlpha) > 1:
            cosAlpha = int(cosAlpha) #np.mod(cosAlpha,1)
        alpha = np.arccos(cosAlpha)
        if alpha < minT:
            minT = alpha
            k = i

    return np.rad2deg(minT), partSK[k, :], partSK

def exportData(ind, tailP, headP, jointP, beta, ampl, gamma, torsionP, exportPath, expID, nValidFrames):

    # Export all the data in a cvs file
    dataHeader = "Time(ms), x_Head, y_Head, x_Joint, y_Joint, x_Torsion, y_Torsion, x_Tail, y_Tail, Amplitude(px), TailAngleBeta(dg), TorsionAngleGamma(dg)"
    data = np.transpose([ind[:nValidFrames], headP[:nValidFrames, 0], headP[:nValidFrames, 1], jointP[:nValidFrames, 0], jointP[:nValidFrames, 1], torsionP[:nValidFrames, 0], torsionP[:nValidFrames, 1], tailP[:nValidFrames, 0], tailP[:nValidFrames, 1], ampl, beta,  gamma[:nValidFrames]])
    np.savetxt(pathlib.Path(exportPath,expID,expID + ".csv"), data, fmt="%10.5f",
               delimiter=',', header=dataHeader, comments="")

    # Export all the data in npy files to show faster in showData
    np.save(pathlib.Path(exportPath,expID,"data", expID + "_ind"), ind[:nValidFrames])
    np.save(pathlib.Path(exportPath, expID, "data", expID + "_amp"), ampl)
    np.save(pathlib.Path(exportPath,expID, "data", expID + "_beta"), beta)
    np.save(pathlib.Path(exportPath, expID, "data", expID + "_gamma"), gamma[:nValidFrames])


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
