import logging
import pathlib
import os

import numpy as np

# # Debug Only: draw approx
# import matplotlib.pyplot as plt
# import matplotlib.animation as animation

import config


def treatData(exportPath, expID, fps):

    # Init. data
    proportionJoint = config.PROPORTION_JOINT
    proportionTorsion = config.PROPORTION_TORSION 

    # Check/Create paths 
    pathlib.Path(exportPath, expID, "data").mkdir(parents=True, exist_ok=True)
 
    # Number of files
    nFiles = len(list(pathlib.Path(exportPath,expID,"skeleton").glob("*.npy")))

    # Obtain data
    logging.info("Importing Data...")
    ind, tailP, headP, jointP, nValidFrames, torsionP = importData(exportPath, expID, proportionJoint, proportionTorsion, nFiles)

    # Compute data
    logging.info("Computing Data...")
    beta, ampl = computeAngle(headP, jointP, tailP, nValidFrames)
    gamma, _amplgamma = computeAngle(jointP, torsionP, tailP, nValidFrames)
    
    ind[:nValidFrames] = (nFiles/fps)*ind[:nValidFrames] # time in ms

    # Export data
    logging.info("Exporting Data...")
    exportData(ind, tailP, headP, jointP, beta, ampl, gamma, torsionP, exportPath, expID, nValidFrames)

    logging.info("Treatment DONE.")

def importData(filePath, expID, proportionJoint, proportionTorsion, nFiles):

    # Init. the main arrays
    ind = np.zeros((nFiles), int)
    tailP = np.zeros((nFiles, 2), int)
    headP = np.zeros((nFiles, 2), int)
    jointP = np.zeros((nFiles, 2), int)
    torsionP = np.zeros((nFiles, 2), int)

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
            skeleton = uniqueMean(skeleton) # delete repeated points_x and get they mean_y
            skeleton[:, 1] = -skeleton[:, 1] # convert coords. to R^2. Original ones are image matrix indicies

            # Save points- Fish direction swimming: left
            ind[validInd] = i
            tailP[validInd, :] = skeleton[-1, :]
            headP[validInd, :] = skeleton[0, :]
            _skeletonLen, joint = lenSK(skeleton, proportionJoint)
            jointP[validInd, :] = skeleton[joint, :]
            _skeletonLen, torsion = lenSK(skeleton[joint:, :], proportionTorsion)
            torsionP[validInd, :] = skeleton[torsion+joint, :]

            # Update the valid index
            validInd += 1

            # # Debug Only: draw approx
            # x = skeleton[:, 0]
            # y = skeleton[:, 1]
            # plot1 = plt.figure(1)
            # plt.plot(x, y, 'b-')
            # plt.plot(x[joint],y[joint],'ro')
            # plt.plot(x[torsion+joint],y[torsion+joint],'g*')
            # plt.axis((0, 426.7, -154, -50))
            # # Update canvas
            # fig.canvas.draw()
            # plot1.clf()
            
    return ind, tailP, headP, jointP, validInd, torsionP

def uniqueMean(skeleton):

    skmean = np.array([], int).reshape(0,2)

    # Count the repeated coords. x and get they index
    _sk, skind, skcounts = np.unique(skeleton[:,0], return_index=True, return_counts=True)

    # Copy unique x coords. and assign the y coords mean
    for i,ind in enumerate(skind):
        if skcounts[i] > 1: 
            ymean = 0
            for j in range(skcounts[i]):
                ymean = ymean + skeleton[ind+j, 1]
            skmean = np.vstack([skmean,[skeleton[i,0], int(ymean/skcounts[i])]])
        else:  # if not repeated x
            skmean = np.vstack([skmean,[skeleton[i,0], skeleton[i,1]]])

    return skmean

def computeAngle(A, B, C, nValidFrames):

    # Amplitude between the tail and the head perpendicular
    # sin(alpha)=(vXu)/||v||·||u||  (permits to obtain the sign of angle)
    sinAlpha = np.zeros(nValidFrames, float)
    h = np.zeros(nValidFrames, float)
    ampl = np.zeros(nValidFrames, float)

    for i in range(nValidFrames):
        h[i] = np.sqrt(np.abs(C[i, 0]-A[i, 0])**2 + np.abs(C[i, 1]-A[i, 1])**2)
        sinAlpha[i] = ((C[i, 0]-A[i, 0])*(B[i, 1]-A[i, 1]) - (B[i, 0]-A[i, 0])*(C[i, 1]-A[i, 1])) / (np.sqrt((C[i, 0]-A[i, 0])**2 + (C[i, 1]-A[i, 1])**2) * np.sqrt((B[i, 0]-A[i, 0])**2 + (B[i, 1]-A[i, 1])**2))
        if (np.sqrt((C[i, 0]-A[i, 0])**2 + (C[i, 1]-A[i, 1])**2) * np.sqrt((B[i, 0]-A[i, 0])**2 + (B[i, 1]-A[i, 1])**2)) == 0:
            print(i)
        ampl[i] = h[i] * sinAlpha[i]

    # Tail angle from the axis headP/jointP
    alpha = np.zeros(nValidFrames, float)

    for i in range(nValidFrames):
        alpha[i] = np.rad2deg( np.arcsin(ampl[i]/np.sqrt(np.abs(C[i, 0] - B[i, 0])**2 + np.abs(C[i, 1]-B[i, 1])**2)) )

    return alpha, ampl

def lenSK(skeleton, proportion):
    # Compute the length of the skeleton
    skeletonLen = 0
    for i in range(1,len(skeleton)):
        skeletonLen += ((skeleton[i-1][0] - skeleton[i][0])**2 + (skeleton[i-1][1] - skeleton[i][1])**2)**(1/2)

    # Compute the desired index point on proportion measure
    measure = 0
    for i in range(1,len(skeleton)):
        measure += ((skeleton[i-1][0] - skeleton[i][0])**2 + (skeleton[i-1][1] - skeleton[i][1])**2)**(1/2)
        if measure > skeletonLen*proportion:
            point = i
            break

    return skeletonLen, point

def exportData(ind, tailP, headP, jointP, beta, ampl, gamma, torsionP, exportPath, expID, nValidFrames):

    # Export all the data in a cvs file
    dataHeader = "Time(ms), x_Head, y_Head, x_Joint, y_Joint, x_Torsion, y_Torsion, x_Tail, y_Tail, Amplitude(px), TailAngleBeta(dg), TorsionAngleGamma(dg)"
    data = np.transpose([ind[:nValidFrames], headP[:nValidFrames, 0], headP[:nValidFrames, 1], jointP[:nValidFrames, 0], jointP[:nValidFrames, 1], torsionP[:nValidFrames, 0], torsionP[:nValidFrames, 1], tailP[:nValidFrames, 0], tailP[:nValidFrames, 1], ampl, beta, gamma])
    np.savetxt(pathlib.Path(exportPath,expID,expID + ".csv"), data, fmt="%10.5f", delimiter=',', header=dataHeader, comments="")
    # Export all the data in npy files to show faster in showData
    np.save(pathlib.Path(exportPath,expID,"data", expID + "_ind"), ind[:nValidFrames])
    np.save(pathlib.Path(exportPath, expID, "data", expID + "_amp"), ampl)
    np.save(pathlib.Path(exportPath,expID, "data", expID + "_beta"), beta)
    np.save(pathlib.Path(exportPath, expID, "data", expID + "_gamma"), gamma)


if (__name__ == "__main__"):

    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s: %(message)s"
    )

    exportPath = "./export/"
    expID = "TestFish"
    fps = 1000

    # try:
    treatData(exportPath, expID, fps)
    # except Exception as err:
    #     logging.error(err)
    
    logging.info("DONE.")
