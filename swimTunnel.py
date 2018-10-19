import cv2 as cv
import numpy as np


def swimTunnel(filePath,expID):

    # Open the video in a VideoCapture object
    vid = cv.VideoCapture(filePath)

    # Check if the video object has opened the reference
    if (not vid.isOpened()):
        raise Exception("Could not open the video reference: " + filePath)

    # Define main objects
    totalFrames = 0
    failFrames = 0

    # Read the first frame for second video walk
    _, frame = vid.read()

    # Select ROI
    crop = cv.selectROI(frame)
    cv.destroyAllWindows()

    while(frame is not None):

        totalFrames += 1

        # Step1 -- Crop the region of interest
        frame = frame[crop[1]:(crop[1]+crop[3]), crop[0]:(crop[0]+crop[2])]
        originalFrame = frame

        # Step2 - - PreProcess the image
        frame = preprocess(frame, True, True)

        # Step3.2 -- Fish contour and skeleton detection
        fishContours = getFishContours(frame)
        fishSkeleton = getFishSkeleton(frame)

        
        x,y,w,h = cv.boundingRect(fishContours)
        cv.polylines(originalFrame, fishContours, True,(0, 255, 0), 1)
        cv.polylines(originalFrame, fishSkeleton, True, (0, 0, 255), 1)
        cv.rectangle(originalFrame, (x,y),(w+x,y+h), (255, 255, 255), 1, 8, 0)
        
        cv.imshow('Video', originalFrame)
        cv.waitKey(10)
        _, frame = vid.read()

    # Clean
    vid.release()
    cv.destroyAllWindows()

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
        # Threshold by color to a binary image
        frame = cv.inRange(frame, 0, 110)

    # Debug Only: Show preprocess image
    cv.imshow("PreProcess",frame)
    cv.waitKey(1)

    return frame

def getFishContours(frame):

    # Canny Edge-Detection
    frame = cv.Canny(frame, 100, 200)

    # Find and draw Contours
    frame, contours, _ = cv.findContours(frame, cv.RETR_TREE, cv.CHAIN_APPROX_NONE)

    # Delete unnecessary blobs TODO: No absolute values!
    iFishContour = 0
    for i in range(np.size(contours)):

        area = cv.contourArea(contours[i], False)

        if (area > 5500 and area < 6500):
            iFishContour = i
    
    # Debug Only: Draw all contours
    drawing = np.zeros((np.size(frame, 0), np.size(frame, 1)), np.uint8)
    cv.drawContours(drawing, contours, iFishContour, (255, 255, 255), 2)
    cv.imshow("Fish Contours", drawing)
    cv.waitKey(1)

    # # Debug Only: Draw all contours
    # drawing2 = np.zeros((np.size(frame, 0), np.size(frame, 1)), np.uint8)
    # cv.drawContours(drawing2,contours,-1,(0,0,255),2)#-1 to print all contours
    # cv.imshow("All Contours",drawing2)
    # cv.waitKey(1)

    return contours[iFishContour]

def getFishSkeleton(frame):

    # Create the skeleton through Zhang-Suen thinning
    frame = cv.ximgproc.thinning(frame, 0)

    # Find the Skeleton
    frame, contours, _ = cv.findContours(frame, cv.RETR_CCOMP, cv.CHAIN_APPROX_NONE)

    # Delete unnecessary lines
    maxLen = 0
    for i in range(np.size(contours)):
        length = cv.arcLength(contours[i], False)
        if (length > maxLen):
            maxLen = length
            iFishSkeleton = i

    return contours[iFishSkeleton]







