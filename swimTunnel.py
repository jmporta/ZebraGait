import cv2 as cv
import numpy as np


def swimTunnel(filePath,expID):
    # Get the video
    vid = cv.VideoCapture(filePath)
    _, frame = vid.read()

    # Select ROI
    r = cv.selectROI(frame)

    while(frame is not None):

        # Crop image
        frame = frame[r[1]:(r[1]+r[3]), r[0]:(r[0]+r[2])]
        originalFrame = frame

        frame = preprocess(frame)
        fishContours = getFishContours(frame)
        fishSkeleton = getFishSkeleton(frame)

        x,y,w,h = cv.boundingRect(fishContours)
        cv.polylines(originalFrame, fishContours, True,(0, 255, 0), 2)
        cv.polylines(originalFrame, fishSkeleton, True, (0, 0, 255), 1)
        cv.rectangle(originalFrame, (x,y),(w+x,y+h), (255, 255, 255), 1, 8, 0)
        
        cv.imshow('Video', originalFrame)
        cv.waitKey(10)
        _, frame = vid.read()

    # Clean
    vid.release()
    cv.destroyAllWindows()

def preprocess(frame):

    # Force B&W
    frame = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)

    # Apply gamma correction using the lookup table
    invGamma = 1.0/2
    table = np.array([((i / 255.0) ** invGamma) * 255 for i in np.arange(0, 256)]).astype("uint8")
    frame = cv.LUT(frame, table)

    # Clean Noise
    frame = cv.GaussianBlur(frame, (3, 3), 0, 0)
    frame = cv.medianBlur(frame, 9)

    # Threshold by color to a binary image
    frame = cv.inRange(frame, 0, 110)

    return frame

def getFishContours(frame):

    # Canny Edge-Detection
    frame = cv.Canny(frame, 100, 200)

    # Find and draw Contours
    frame, contours, _ = cv.findContours(frame, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)

    # Delete unnecessary blobs
    iFishContour = 0
    for i in range(np.size(contours)):
        area = cv.contourArea(contours[i], False)

        if (area > 5500 and area < 6500):
            iFishContour = i
    
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







