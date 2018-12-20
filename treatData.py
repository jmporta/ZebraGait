import logging
import pathlib
import os
import csv

import numpy as np
from scipy.interpolate import CubicSpline

# # Debug Only: draw 
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
    alpha, _amplalpha = computeAngle(headP, jointP, torsionP, nValidFrames)
    beta, _amplbeta = computeAngle(headP, jointP, tailP, nValidFrames)
    gamma, _amplgamma = computeAngle(jointP, torsionP, tailP, nValidFrames)

    time = (nFiles/fps)*ind[:nValidFrames] # time in ms

    dataAlpha = angleData(time, alpha)
    dataBeta = angleData(time, beta)
    dataGamma =  angleData(time, gamma)

    aData = np.array([dataAlpha, dataBeta,dataGamma], float)

    # Export data
    logging.info("Exporting Data...")
    exportData(time, headP, jointP, torsionP, tailP, alpha, beta, gamma, aData, exportPath, expID, nValidFrames)

    logging.info("Treatment DONE.")

def importData(filePath, expID, proportionJoint, proportionTorsion, nFiles):

    # Init. the main arrays
    ind = np.zeros((nFiles), int)
    tailP = np.zeros((nFiles, 2), int)
    headP = np.zeros((nFiles, 2), int)
    jointP = np.zeros((nFiles, 2), int)
    torsionP = np.zeros((nFiles, 2), int)

    # # Debug Only: Start interactive fig to plot skeleton and partition
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

def angleData(time, angle):

    # Init. data
    interpPart = 15
    dist = 1.5
    kerPts = 9

    # Smooth angle data
    ker = np.ones(kerPts)/kerPts
    smoothAngle = np.convolve(angle, ker, mode='same')
    
    # Define interp. points
    x = time[0:-1:interpPart]
    x = np.append(x,[time[-1]])
    y = smoothAngle[0:-1:interpPart]
    y = np.append(y,[smoothAngle[-1]])

    # Compute the splines and its relative points
    cs = CubicSpline(x, y)
    rootsd = cs.derivative().roots() 

    # Filter roots
    noiseHDist = dist*interpPart
    noiseVDist = noiseHDist*time[-1]/np.abs(np.max(y)-np.min(y))
    relativeP = []
    noiseP = []

    if (rootsd[0] >= x[0]): # first root
        if (np.abs(rootsd[0]-rootsd[1]) > noiseHDist) or (np.abs(cs(rootsd[0])-cs(rootsd[1])) > noiseVDist):
            # Append valid root
            relativeP.append(rootsd[0])
        else:
            # Save noise
            noiseP.append(rootsd[0])

    for i in range(1,len(rootsd)-1): # mid roots
            if (np.abs(rootsd[i]-rootsd[i+1]) > noiseHDist) or (np.abs(cs(rootsd[0])-cs(rootsd[1])) > noiseVDist):
                if (len(noiseP) == 0 ): 
                    # Append valid root
                    relativeP.append(rootsd[i])
                elif (len(noiseP)%2 == 0):
                    # Append median of the noise roots
                    noiseP.append(rootsd[i])
                    relativeP.append(np.median(noiseP))
                # Restart noise points 
                noiseP = []
            else:
                # Save noise
                noiseP.append(rootsd[i])

    if (rootsd[-1] <= x[-1]) : # last root
        if (len(noiseP) == 0 ): 
            # Append valid root
            relativeP.append(rootsd[-1])
        else:
            # Append median of the noise roots
            noiseP.append(rootsd[-1])
            relativeP.append(np.median(noiseP))

    # Compute mean data
    amp = np.zeros(len(relativeP)-1, float)
    for i in range(1,len(relativeP)):
        amp[i-1] = np.abs(cs(relativeP[i])-cs(relativeP[i-1]))/2
    
    meanAmp = np.mean(amp)
    freq = (int((len(relativeP)-1)/2) * 1000)/time[-1]

    # # Debug Only: draw the approx.
    # plt.figure(1)
    # xs = np.linspace(x[0], x[-1], 1000, endpoint=True)
    # plt.plot(time, angle, "C7.", alpha=0.25, label="Raw Data")
    # plt.plot(time, smoothAngle, "C8.", alpha=0.25, label="Smooth Data")
    # plt.plot(x, y, "C1*", label="Inter. Pts")
    # plt.plot(xs, cs(xs), "C0", label="CS approx.")
    # plt.plot(relativeP, cs(relativeP), "C3o", alpha=0.5, label="Relative Pts")
    # plt.legend(loc="lower left", ncol=2)
    # plt.grid()
    # plt.show()

    return meanAmp, freq

def exportData(time, headP, jointP, torsionP, tailP, alpha, beta, gamma, aData, exportPath, expID, nValidFrames):

    # Export all the data in a cvs file
    dataHeader = "Time(ms), x_Head, y_Head, x_Joint, y_Joint, x_Torsion, y_Torsion, x_Tail, y_Tail, AngleAlpha(dg), AngleBeta(dg), AngleGamma(dg)"
    data = np.transpose([time, headP[:nValidFrames, 0], headP[:nValidFrames, 1], jointP[:nValidFrames, 0], jointP[:nValidFrames, 1],
                         torsionP[:nValidFrames, 0], torsionP[:nValidFrames, 1], tailP[:nValidFrames, 0], tailP[:nValidFrames, 1], alpha, beta, gamma])
    np.savetxt(pathlib.Path(exportPath,expID,expID + ".csv"), data, fmt="%10.5f", delimiter=',', header=dataHeader, comments="")
    
    # Append the global data to the csv file
    with open(pathlib.Path(exportPath, expID, expID + ".csv"), 'a') as f:
        w = csv.writer(f)
        w.writerow([None])
        w.writerow([None, "MeanAmp", "Freq(Hz)"])
        w.writerow(["Alpha", aData[0, 0], aData[0, 1]])
        w.writerow(["Beta", aData[1, 0], aData[1, 1]])
        w.writerow(["Gamma", aData[2, 0], aData[2, 1]])

    # Export the data in npy files to show faster in showData
    np.save(pathlib.Path(exportPath, expID, "data", expID + "_time"), time)
    np.save(pathlib.Path(exportPath, expID, "data", expID + "_alpha"), alpha)
    np.save(pathlib.Path(exportPath, expID, "data", expID + "_beta"), beta)
    np.save(pathlib.Path(exportPath, expID, "data", expID + "_gamma"), gamma)


if (__name__ == "__main__"):

    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s: %(message)s"
    )

    exportPath = "./export/"
    expID = "TestFast"
    fps = 1000

    treatData(exportPath, expID, fps)
    
    logging.info("DONE.")
