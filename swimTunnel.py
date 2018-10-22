import cv2 as cv
import numpy as np
import os


def swimTunnel(filePath,expID):

    # Global vars
    exportFilePath = "./data/"

    # Open the video in a VideoCapture object
    vid = cv.VideoCapture(filePath)

    # Check if the video object has opened the reference
    if (not vid.isOpened()):
        raise Exception("Could not open the video reference: " + filePath)

    # Define main objects
    fishContoursPrev = np.zeros((1,2), int)
    numFrame = 0
    failFrames = 0
    matchContour = 1.0

    # First walk. Define a smaller image movement subset and crop.
    # The crop region is bigger than the main box. The main box is only to verify the location of the correct blob
    totalFrames, (rx,ry,rw,rh), (mbx,mby,mbw,mbh) = getMainBox(filePath)

    # Read the first frame for second video walk
    _, frame = vid.read()

    # Second video walk to find the skeleton and its data
    print("Extracting data...")
    while(frame is not None):

        numFrame += 1

        # Step1 -- Crop the region of interest
        frame = frame[ry:(ry+rh), rx:(rx+rw)]
        frame = frame[mby:(mby+mbh), mbx:(mbx+mbw)]
        originalFrame = frame

        # Step2 -- PreProcess the image
        frame = preprocess(frame, True, True)

        # Step3 -- Fish contour and skeleton detection
        fishContours = getFishContours(frame)
        fishSkeleton = getFishSkeleton(frame)

        # Step4 -- Validate and Show/Save the results

        # First frame condition
        if (numFrame == 1):
            fishContoursPrev = fishContours

        # Check the previous countour shape
        skeletonBelong = True
        matchContour = cv.matchShapes(fishContours, fishContoursPrev, 3, 0.0)
        
        # Check if the fish boundary contains the fish skeleton
        (fx, fy, fw, fh) = cv.boundingRect(fishContours)
        for i in range(np.size(fishSkeleton,0)):
            if (not ((fx<fishSkeleton[i][0,0]<(fx+fw)) and (fy<fishSkeleton[i][0,1]<(fy+fh)))):
                skeletonBelong = False
                break

        # Check the frame and save the results
        if ((matchContour < 0.1) and (skeletonBelong)):
            # Export Results
            exportResults(exportFilePath, expID, fishSkeleton, numFrame, True)

            # DebugOnly: Show results
            cv.polylines(originalFrame, fishContours, True,(0, 255, 0), 1)
            cv.polylines(originalFrame, fishSkeleton, True, (0, 0, 255), 1)
            cv.rectangle(originalFrame, (fx,fy),(fw+fx,fy+fh), (255, 255, 255), 1, 8, 0)
            cv.imshow('Video', originalFrame)
            cv.waitKey(1)
        else:
            failFrames += 1

            # Export Results
            exportResults(exportFilePath, expID, fishSkeleton, numFrame, False)

            # Check the fail proportion
            if (failFrames >= 10 * totalFrames /100):
                raise Exception("Too much failed frames! The computation do not proceed, it could be wrong.")

            # DebugOnly: Show results
            cv.polylines(originalFrame, fishContours, True,(0, 255, 0), 1,8)
            cv.polylines(originalFrame, fishSkeleton, True, (0, 0, 255), 1,8)
            cv.rectangle(originalFrame, (fx,fy),(fw+fx,fy+fh), (255, 255, 255), 1, 8, 0)
            cv.imshow('Video', originalFrame)
            cv.waitKey(0)

        # Step5 -- Update the next frame
        fishContoursPrev = fishContours
        _, frame = vid.read()

    # Clean
    vid.release()
    cv.destroyAllWindows()

    print("Failed frames: " + str(failFrames) + "/" + str(totalFrames))
    print("Extraction DONE.")

    return failFrames

def getMovementBox(frame):

    # Dilate one time the image for a better edges detection
    morphSize = 2
    element = cv.getStructuringElement(cv.MORPH_ELLIPSE, (2*morphSize+1, 2*morphSize+1), (morphSize, morphSize))
    frame = cv.morphologyEx(frame, cv.MORPH_DILATE, element)

    # Canny Edge-Detection
    frame = cv.Canny(frame, 100, 200)

    # Find countours
    _, contours, _ = cv.findContours(frame, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)

    # Join the contours in one
    if (np.size(contours) == 0):
        (mx, my, mw, mh) = (0, 0, 0, 0)
    else:
        joinedContours = contours[0]
        for i in range(1,np.size(contours,0)):
            joinedContours = np.concatenate((joinedContours,contours[i]),0) # faster than an insert
        (mx, my, mw, mh) = cv.boundingRect(joinedContours)

    return np.array([mx, my, mw, mh], int)

def getMainBox(filePath):

    totalFrames = 0

    # Open the video in a VideoCapture object
    backVid = cv.VideoCapture(filePath)

    # Check if the video object has opened the reference
    if (not backVid.isOpened()):
        raise Exception("Could not open the video reference: " + filePath)

    # Create Background Subtractor object
    pMOG2 = cv.createBackgroundSubtractorMOG2(0, 10, False)

    # Read the first frame to select the area to track
    _, backFrame = backVid.read()

    # Select the region of interest
    (rx, ry, rw, rh) = cv.selectROI(backFrame)
    cv.destroyAllWindows()

    # Init. main box to the union
    #(mbx, mby, mbw, mbh) = (-np.size(backFrame,0), -np.size(backFrame,1), 0 , 0)
    (mbx, mby, mbw, mbh) = (np.size(backFrame, 0), np.size(backFrame, 1),-np.size(backFrame, 0), -np.size(backFrame, 1))

    # First walk to detect the movement domain and the total number of frames
    print("Detecting the movement domain...")
    while(backFrame is not None):
        
        totalFrames += 1

        # Step1 -- Crop the region of interest
        backFrame = backFrame[ry:(ry+rh), rx:(rx+rw)]

        # Step2 -- Update of the background model and the movement domain
        backFrame = preprocess(backFrame, True, False)
        backFrame = pMOG2.apply(backFrame)
        
        (mx, my, mw, mh) = getMovementBox(backFrame)
        
        # # DebugOnly: Show the boxes union
        # drawing2 = np.zeros((np.size(backFrame, 0), np.size(backFrame, 1)), np.uint8)
        # cv.rectangle(backFrame, (mx, my), (mw+mx, my+mh),(255, 255, 255), 1, 8, 0)
        # cv.imshow("movement box", drawing2)
        # cv.waitKey(1)

        # Step3 -- Join the boxes ommiting the limit ones
        if ((mw*mh > 10000) and (mw*mh < 28000)):
            # Horizontal coords
            if (mx < mbx):
                if ( mx+mw < mbx+mbw):
                    mbw = mw
                mbx=mx
            else:
                if (mx+mw > mbx+mbw):
                    mbw = mw + (mx-mbx)
            # Vertical coords
            if (my < mby):
                if ( my+mh < mby+mbh):
                    mbh = mh
                mby=my
            else:
                if (my+mh > mby+mbh):
                    mbh = mh + (my-mby)

        # # DebugOnly: Show the boxes union
        # print(mbx, mby, mbw, mbh)
        # drawing = np.zeros((np.size(backFrame, 0), np.size(backFrame, 1)), np.uint8)
        # cv.rectangle(backFrame, (mbx, mby), (mbw+mbx, mby+mbh),(255, 255, 255), 1, 8, 0)
        # cv.imshow("Main box", drawing)
        # cv.waitKey(1)

        # Update the frame
        _, backFrame = backVid.read()

    print("Movement domain defined.")
    return totalFrames, np.array([rx,ry,rw,rh], int), np.array([mbx,mby,mbw,mbh], int) # [crop region] and [main box coords]

def preprocess(frame, blur, threshold):

    # Force B&W
    frame = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)

    # Apply gamma correction using the lookup table
    invGamma = 1.0/2
    table = np.array([((i / 255.0) ** invGamma) * 255 for i in np.arange(0, 256)]).astype("uint8")
    frame = cv.LUT(frame, table)

    if (blur):
        # Clean Noise
        frame = cv.GaussianBlur(frame, (3, 3), 0, 0)
        frame = cv.medianBlur(frame, 9)

    if (threshold):
        # Threshold by color
        frame = cv.inRange(frame, 0, 110)

    # # DebugOnly: Show preprocess image
    # cv.imshow("PreProcess",frame)
    # cv.waitKey(1)

    return frame

def getFishContours(frame):

    # Canny Edge-Detection
    frame = cv.Canny(frame, 100, 200)

    # Find and draw Contours
    _, contours, _ = cv.findContours(frame, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)

    # Delete unnecessary blobs TODO: No absolute values!
    iFishContour = 0
    for i in range(np.size(contours, 0)):

        area = cv.contourArea(contours[i], False)

        if (area > 5500 and area < 6500):
            iFishContour = i
    
    # # DebugOnly: Draw all contours
    # drawing = np.zeros((np.size(frame, 0), np.size(frame, 1)), np.uint8)
    # cv.drawContours(drawing, contours, iFishContour, (255, 255, 255), 2)
    # cv.imshow("Fish Contours", drawing)
    # cv.waitKey(1)

    # # DebugOnly: Draw all contours
    # drawing2 = np.zeros((np.size(frame, 0), np.size(frame, 1)), np.uint8)
    # cv.drawContours(drawing2,contours,-1,(0,0,255),2)#-1 to print all contours
    # cv.imshow("All Contours",drawing2)
    # cv.waitKey(1)

    return contours[iFishContour]

def getFishSkeleton(frame):

    # Create the skeleton through Zhang-Suen thinning 
    frame = cv.ximgproc.thinning(frame, 0)

    # Find the Skeleton
    _, contours, _ = cv.findContours(frame, cv.RETR_CCOMP, cv.CHAIN_APPROX_NONE)

    # Delete unnecessary lines
    maxLen = 0
    for i in range(np.size(contours,0)):
        length = cv.arcLength(contours[i], False)
        if (length > maxLen):
            maxLen = length
            iFishSkeleton = i

    return contours[iFishSkeleton]

def exportResults(exportFilePath, expID, fishSkeleton, step, validFrame):

    # Check if path exists, if not create it
    if not os.path.exists(exportFilePath):
        os.makedirs(exportFilePath)

    # Save skeleton to a numpy binary array file *.npy
    if (validFrame):
        np.save(exportFilePath + expID + "_" + str(step), fishSkeleton)
    else:
        # Write an ampty file if the frame is failed
        np.save(exportFilePath + expID + "_" + str(step),0)

    return 0


# # DebugOnly: MAIN
# swimTunnel("./video/water_tunnel.avi","ExpTEST")
# print("DONE.")



