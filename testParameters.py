import cv2 as cv
import numpy as np
 
window_name = "ThresholdTest"

cap = cv.VideoCapture("./video/fishbo.avi")
_ret, src =cap.read()

# Choose ROI
(rx, ry, rw, rh) = cv.selectROI("Choosse a ROI", src)
cv.destroyAllWindows()

# Crop the tank
src = src[ry:(ry+rh), rx:(rx+rw)]

# Convert the image to Gray
src = cv.cvtColor(src, cv.COLOR_BGR2GRAY)
cv.namedWindow(window_name)


def Threshold(val):
    threshold_type = cv.getTrackbarPos(trackbar_type, window_name)
    threshold_value = cv.getTrackbarPos("Threshold", window_name)
    alpha = cv.getTrackbarPos("Contrast", window_name)
    beta = cv.getTrackbarPos("Brightness", window_name)

    _, res = cv.threshold(src, threshold_value, 255, threshold_type )

    res = cv.convertScaleAbs(res, alpha=(alpha/100), beta=beta)

    cv.imshow(window_name, res)
    

# Create Trackbar to choose Threshold value
trackbar_type = 'Type: \n 0: Binary \n 1: Binary Inverted \n 2: Truncate \n 3: To Zero \n 4: To Zero Inverted'
cv.createTrackbar(trackbar_type, window_name , 3, 4, Threshold)
# Create Trackbar to choose Threshold value
cv.createTrackbar("Threshold", window_name , 0, 255, Threshold)
# Create Trackbar to choose contrast value
cv.createTrackbar("Contrast", window_name , 100, 300, Threshold)
# Create Trackbar to choose brightness value
cv.createTrackbar("Brightness", window_name , 0, 100, Threshold)

# Call the function to initialize
Threshold(0)

# Wait until user finishes program
cv.waitKey(0)
cap.release()