import logging
import pathlib

import numpy as np
import cv2 as cv

import config

# Colors
WHITE = (255, 255, 255)
GREEN = (51, 153, 0)
RED = (0, 0, 255)
BLUE = (255, 153, 0)


def swimTunnel(videoPath, exportPath, expID, fps, roi=()):

    # Init. Data
    defaultContrast = config.DEFAULT_CONTRAST
    fAreaMin = config.FISH_AREA_MIN
    fAreaMax = config.FISH_AREA_MAX
    bAreaMin = config.BOX_AREA_MIN
    bAreaMax = config.BOX_AREA_MAX
    blankBorder = config.BLANK_BORDER

    videoPath = str(pathlib.Path(videoPath)) # OpenCV do not admit pathlib inside his functions

    # Check/Create paths
    pathlib.Path(exportPath, expID, "skeleton").mkdir(parents=True, exist_ok=True)

    # Open the video in a VideoCapture object
    vid = cv.VideoCapture(videoPath)
    
    # Check if the video object has opened the reference
    if not vid.isOpened():
        vid.release()
        raise Exception("Could not open the video reference: " + videoPath)

    # Define main objects
    numFrame = 0
    failFrames = 0
    consecFails = 0

    # First video loop. Define a smaller image movement subset and crop it. Choose the ROI and the contrast.
    # The crop region is bigger than the main box. The main box is only to verify the location of the correct blob and to save computations in each step.
    totalFrames, contrast, (mbx, mby, mbw, mbh) = getMainBox(videoPath, defaultContrast, bAreaMin, bAreaMax, roi)

    # Open the save video object
    codec = cv.VideoWriter_fourcc('M', 'J', 'P', 'G')
    out = cv.VideoWriter(str(pathlib.Path(exportPath,expID,expID + ".avi")), codec, fps, (mbw + 2*blankBorder, mbh + 2*blankBorder))

    # Read the first frame for second video walk
    _ret, frame = vid.read()

    # Second video loop to find the skeleton and its data
    logging.info("Extracting data...")

    while frame is not None:
        numFrame += 1

        # Step1 -- Initial crops/adds

        # Crop the main movement box
        frame = frame[mby:(mby+mbh), mbx:(mbx+mbw)]
        # Add a solid border to avoid blob border fusion
        frame = cv.copyMakeBorder(frame, blankBorder, blankBorder, blankBorder, blankBorder, cv.BORDER_CONSTANT, None, WHITE)
        # Hard copy of frame without changes
        originalFrame = frame.copy()

        # Step2 -- PreProcess the image

        frame = preprocess(frame, contrast, True, True)

        # Step3 -- Fish contour and fish skeleton detection

        fishContours = getFishContours(frame, fAreaMin, fAreaMax)
        fishSkeleton = getFishSkeleton(frame)

        # Step4 -- Validate and Show/Save the results

        # First frame condition
        if numFrame == 1:
            fishContoursPrev = fishContours
        
        # Check the the conditions and save the results
        if checkFrame(fishSkeleton, fishContours, fishContoursPrev):
            # Export and draw the Results
            exportResults(exportPath, expID, fishSkeleton, numFrame, validFrame=True)
            drawResults(originalFrame, fishContours, fishSkeleton, out, validFrame=True)

            # Reset consecutive failed frames counter
            consecFails = 0

            # DebugOnly: Show results
            cv.imshow("Zebra Gait", originalFrame)
            # Abort if ESC button is pressed
            if cv.waitKey(10) == 27:
                vid.release()
                cv.destroyAllWindows()
                raise Exception("Process aborted by the user.")
            
        else:
            consecFails += 1
            failFrames += 1

            # Export Results
            exportResults(exportPath, expID, fishSkeleton, numFrame, validFrame=False)

            # Check the fail proportion
            if (failFrames >= 10*totalFrames/100) or (consecFails >= 5*totalFrames/100):
                vid.release()
                cv.destroyAllWindows()
                raise Exception("Too much failed frames! The computation do not proceed, it could be wrong.")   

            drawResults(originalFrame, fishContours, fishSkeleton, out, validFrame=False)
            
            # DebugOnly: Show results
            cv.imshow("Zebra Gait", originalFrame)
            # Abort if ESC button is pressed
            if cv.waitKey(10) == 27:
                vid.release()
                cv.destroyAllWindows()
                raise Exception("Process aborted by the user.")

        # Step5 -- Update the next frame
        fishContoursPrev = fishContours
        _ret, frame = vid.read()

    # Clean
    vid.release()
    out.release()
    cv.destroyAllWindows()

    logging.info("Extraction DONE.")
    logging.info("Failed frames: " + str(failFrames) + "/" + str(totalFrames))

    return failFrames, contrast


def getMovementBox(frame):

    # Dilate one time the image for a better edges detection
    morphSize = 2
    element = cv.getStructuringElement(cv.MORPH_ELLIPSE, (2*morphSize+1, 2*morphSize+1), (morphSize, morphSize))
    frame = cv.morphologyEx(frame, cv.MORPH_DILATE, element)

    # Auto Canny Edge-Detection
    v = np.median(frame)
    sigma = 0.33
    lower = int(max(0, (1.0 - sigma) * v))
    upper = int(min(255, (1.0 + sigma) * v))
    frame = cv.Canny(frame, lower, upper)

    # Find countours
    contours, _hier= cv.findContours(frame, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)

    # Join the contours in one
    if np.size(contours) == 0:
        (mx, my, mw, mh) = (0, 0, 0, 0)
    else:
        joinedContours = contours[0]
        for i in range(1,np.size(contours,0)):
            joinedContours = np.concatenate((joinedContours,contours[i]),0) # faster than an insert
        (mx, my, mw, mh) = cv.boundingRect(joinedContours)

    return np.array([mx, my, mw, mh], int)


def getMainBox(videoPath, defaultContrast, bAreaMin, bAreaMax, roi):

    totalFrames = 0
    layer = 10 # secure layer/border in pixels

    # Open the video in a VideoCapture object
    backVid = cv.VideoCapture(videoPath)

    # Check if the video object has opened the reference
    if not backVid.isOpened():
        backVid.release()
        raise Exception("Could not open the video reference: " + videoPath)

    # Create Background Subtractor object
    pMOG2 = cv.createBackgroundSubtractorMOG2(history=0, detectShadows=False)

    # Read the first frame to select the area to track
    _ret, backFrame = backVid.read()

    # Select the region of interest and the contrast
    if roi == ():
        (rx, ry, rw, rh) = cv.selectROI("Crop the region of interest", backFrame)
        cv.destroyAllWindows()
    else:
        (rx, ry, rw, rh) = (roi[0], roi[1], roi[2], roi[3])

    if rh == 0 or rw == 0:
        raise Exception("The cropped region is empty.")
    contrast = getContrast(defaultContrast, backFrame[ry:(ry+rh), rx:(rx+rw)])

    # Init. main box of the union
    (mbx, mby, mbw, mbh) = (np.size(backFrame, 0), np.size(backFrame, 1), -np.size(backFrame, 0), -np.size(backFrame, 1))

    # First loop to detect the movement domain and the total number of frames
    logging.info("Detecting the movement domain...")
    while backFrame is not None:
        
        totalFrames += 1

        # Step1 -- Crop the region of interest
        backFrame = backFrame[ry:(ry+rh), rx:(rx+rw)]

        # Step2 -- Update of the background model and the movement domain
        backFrame = preprocess(backFrame, contrast, True, False)
        backFrame = pMOG2.apply(backFrame)

        (mx, my, mw, mh) = getMovementBox(backFrame)

        # Step3 -- Join the boxes omiting the limit ones
        if (mw*mh > bAreaMin) and (mw*mh < bAreaMax):
            x = min(mx, mbx)
            y = min(my, mby)
            w = max(mx+mw, mbx+mbw) - x
            h = max(my+mh, mby+mbh) - y

            (mbx, mby, mbw, mbh) = (x, y, w, h) 

        # # DebugOnly: Show the boxes union
        # cv.rectangle(backFrame, (mbx, mby), (mbx+mbw, mby+mbh), WHITE, 3, 8)
        # cv.rectangle(backFrame, (mx, my), (mw+mx, my+mh), WHITE, 1, 8)
        # cv.imshow("Main box", backFrame)
        # cv.waitKey(1)

        # Update the frame
        _ret, backFrame = backVid.read()

    logging.info("Movement domain defined.")
    backVid.release()
    
    # Add a secure border layer (smaller than ROI)
    if mbx-layer > 0:
        mbx = mbx-layer
        mbw = mbw+layer
    if mby-layer > 0:
        mby = mby-layer
        mbh = mbh+layer
    if mbx+mbw+layer < rw:
        mbw = mbw+layer
    if mby+mbh+layer < rh:
        mbh = mbh+layer

    # Change coords to original image basis (MB+ROI)
    mbx = mbx + rx
    mby = mby + ry

    return totalFrames, contrast, np.array([mbx,mby,mbw,mbh], int)


def getContrast(defaultContrast, frame):

    windowsName = "Choose Contrast"
    cv.namedWindow(windowsName)
    
    def ContrastBar(val):
        alpha = cv.getTrackbarPos("Contrast", windowsName)
        res = cv.convertScaleAbs(frame, alpha=(alpha/100))
        cv.imshow(windowsName, res)
        return alpha

    # Create Trackbar to choose contrast value
    cv.createTrackbar("Contrast", windowsName, int(defaultContrast*100), 300, ContrastBar)

    # Call the function to initialize
    ContrastBar(0)

    # Wait until user finishes the selection
    cv.waitKey(0)
    alpha = cv.getTrackbarPos("Contrast", windowsName)
    cv.destroyAllWindows()

    return alpha/100


def preprocess(frame, contrast, blur, threshold):

    # B&W, normalize, contrast
    frame = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
    frame = cv.normalize(frame, None, 0, 255, cv.NORM_MINMAX)
    frame = cv.convertScaleAbs(frame, alpha=contrast, beta=0)

    if blur:
        # Clean Noise
        frame = cv.GaussianBlur(frame, (5, 5), 0, 0)
        frame = cv.medianBlur(frame, 7)

    if threshold:
        # OTSU Threshold
        _ret, frame = cv.threshold(frame, 0, 255, cv.THRESH_BINARY_INV+cv.THRESH_OTSU)
     
        # Dilate and close the image for a better edges detection
        morphSize = 2
        element = cv.getStructuringElement(cv.MORPH_ELLIPSE, (2*morphSize+1, 2*morphSize+1), (morphSize, morphSize))
        frame = cv.morphologyEx(frame, cv.MORPH_DILATE, element, iterations=2)
        frame = cv.morphologyEx(frame, cv.MORPH_CLOSE, element, iterations=2) 

    # # DebugOnly: Show preprocess image
    # cv.imshow("PreProcess",frame)
    # cv.waitKey(1)

    return frame


def getFishContours(frame, fAreaMin, fAreaMax):

    # Auto Canny Edge-Detection
    v = np.median(frame)
    sigma = 0.33
    lower = int(max(0, (1.0 - sigma) * v))
    upper = int(min(255, (1.0 + sigma) * v))
    frame = cv.Canny(frame, lower, upper)

    # Find and draw Contours
    contours, _hier = cv.findContours(frame, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_NONE)

    # Delete unnecessary blobs
    iFishContour = 0
    for i in range(np.size(contours, 0)):

        area = cv.contourArea(contours[i])
        if (area > fAreaMin) and (area < fAreaMax):
            iFishContour = i
    
    # # DebugOnly: Draw fish contours
    # drawing = np.zeros((np.size(frame, 0), np.size(frame, 1)), np.uint8)
    # cv.drawContours(drawing, contours, iFishContour, WHITE, 2)
    # cv.imshow("Fish Contours", drawing)
    # cv.waitKey(1)

    # # DebugOnly: Draw all contours
    # drawing2 = np.zeros((np.size(frame, 0), np.size(frame, 1)), np.uint8)
    # cv.drawContours(drawing2,contours,-1,WHITE,2) #-1 to print all contours
    # cv.imshow("All Contours",drawing2)
    # cv.waitKey(0)

    return contours[iFishContour]


def getFishSkeleton(frame):

    # Find the skeleton through Zhang-Suen thinning 
    frame = cv.ximgproc.thinning(frame, thinningType=cv.ximgproc.THINNING_ZHANGSUEN)
    
    # Find the Skeleton
    contours, _hier = cv.findContours(frame, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_NONE)

    # Delete unnecessary lines
    maxLen = 0
    for i in range(np.size(contours,0)):
        length = cv.arcLength(contours[i], False)
        if length > maxLen:
            maxLen = length
            iFishSkeleton = i

    return contours[iFishSkeleton]


def checkFrame(fishSkeleton,fishContours, fishContoursPrev):

    # Check the ressemblance of the blob detected fish shape in the previous frame
    if cv.matchShapes(fishContours, fishContoursPrev, 3, 0.0) > 0.1:
        return False

    # Check if the fish rect. boundary contains the fish skeleton
    (fx, fy, fw, fh) = cv.boundingRect(fishContours)
    for i in range(np.size(fishSkeleton, 0)):
        if not ((fx < fishSkeleton[i][0, 0] < (fx+fw)) and (fy < fishSkeleton[i][0, 1] < (fy+fh))):
            return False
    
    # Check if the skeleton contains branches
    fishSkeleton = np.reshape(fishSkeleton, (np.size(fishSkeleton, 0), 2))  # convert the array-points to a matrix
    fishSkeleton = fishSkeleton[np.argsort(fishSkeleton[:, 0])]  # sort points by x

    for i in range(1, len(fishSkeleton)):
        if (fishSkeleton[i-1, 0] == fishSkeleton[i, 0]) and (np.abs(fishSkeleton[i-1, 1]-fishSkeleton[i, 1])>3):
            return False
    
    return True


def drawResults(frame, contours, skeleton, vidOut, validFrame=False):

    # # Contours rectangle
    # (fx, fy, fw, fh) = cv.boundingRect(contours)
    # cv.rectangle(frame, (fx,fy),(fw+fx,fy+fh), GREEN, 1, 8, 0)

    # Draw and Save the frame in file
    cv.drawContours(frame, contours, -1, BLUE, 1)
    cv.drawContours(frame, skeleton, -1, RED, 1)

    if validFrame:
        vidOut.write(frame)


def exportResults(dataPath, expID, fishSkeleton, step, validFrame):

    # Save skeleton to a numpy binary array file *.npy
    if (validFrame):
        np.save(pathlib.Path(dataPath, expID, "skeleton", expID + "_" + str(step)), fishSkeleton)
    else:
        # Write an empty file if the frame is failed
        np.save(pathlib.Path(dataPath, expID, "skeleton", expID + "_" + str(step)), 0)


if __name__ == "__main__":

    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s] %(levelname)s: %(message)s (%(funcName)s:%(lineno)d)"
    )

    fps = 1000
    videoPath = "./test/testVideo.avi"
    expID = "testID"
    exportPath = "./export/"

    _failedFrames, _contrast = swimTunnel(videoPath, exportPath, expID, fps)
    
    logging.info("DONE.")
