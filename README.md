# Zebra Gait

Motion detection/description of a zebra fish in a swimming-tunnel. 

## Description

**Video recording setup** 

Experiments for assessing the swimming kinematics were performed in 170 mL miniature swim tunnels (Loligo® Systems, Denmark; Supplementary Figure S1).  Standard length of the fish was measured three days before the swimming  experiments, in order to avoid this source of stress during the  kinematic analysis. The day of the experiment, swim tunnel was submerged  in a 20 L water tank supplied with fish water. Water flow velocities  were calibrated using a Flow Tracking system (DPTV), based on 2D video  tracking of green laser illuminated flourescent sheres with neutral  buyancy (Loligo®  Systems, Denmark). One fish was placed in the swim tunnel between two  honeycombs and acclimated at a water velocity of 1 body length (BL)/s  for 30 min. After acclimation, the fish was forced to swim against the  current of 2 BL/s, a mild to moderate swimming speed in zebrafish. The  videos of the fishes were recorded with a high-speed Photron Fastcam  Mini UX100 (Photron USA Inc., San Diego, CA, USA) at 1280 x 312 pixel  resolution using a Sigma 50 mm F1.4 DG lens at 1000 frames per second (Supplementary Video SV2).  The tunnel was indirectly illuminated by a white LED (Multiled LT-V9,  GS Vitec, Germany). The light intensity in the tunnel was measured with a  Iso-Tech-1332A digital illuminance meter (Iso-Tech LTD, England) and  adjusted to 486 lux. After each experiment, the videos were retrieved  form the memory of the camera and saved as an AVI file without  compression. 

 *See the test reference video in `test` folder of the project.*

**Kinematic analysis ** 

The  video analysis tools have been developed in Python v3.6 using the OpenCV  v4.0 libraries to process the images. In a pre-process, the images are  normalized, their contrast is enhanced to eliminate irrelevant parts of  the fish such as the fins or the tail, and a Gaussian filter is applied  to reduce the noise. Then, the user marks the area of interest in the  image (i.e., the fish chamber in the flow tunnel). To speed up the image  processing, the selected area is further clipped using motion detection  techniques (background subtraction methods).  In this way, the computation is focused on the relevant parts of the  captured image. The process continues with a binarization of the area of  interest using the Otsu algorithm,  which automatically calculates the optimal threshold to separate  objects and background. The blobs in the resulting binary images are  detected and the one fulfilling a particular set of parameters with  respect to its size and shape is assumed to be the fish. The skeleton of  this blob is computed using the Zhang-Suen thinning algorithm  to identify the dorsal of the fish. Several checks are performed in the  different steps of the process to ensure that the final result is  valid. These checks consider aspects such as the number of detected  blobs, their sizes, or the inclusion of the skeleton in a particular blob. If any of the checks fails, the frame is considered invalid. Only videos with less than 10% of invalid frames are used in the evaluation.  

Once the dorsal of the fish is identified, we extract numerical values to  evaluate the fish behavior. In our process, the dorsal is approximated  with three straight segments, connecting four points equidistributed  along the dorsal (points A, B, C, and D). These segments  provide a good approximation of the posture of the fish. Using them, we  compute the angle α between segment BC and the line including segment AB ￼, the angle β between segment BD￼ and the line including segment AB, and the angle γ between segment CD￼ and the line including segment BC￼. Moreover, we compute the amplitude of the swim movement, a, as the distance between point D and the line including segment AB. From these values, we calculated three main parameters: (1) *curvatures*: the three selected angles (head-trunk angle: α, head-tail angle: β ; trunk-tail angle: γ. (2) *tail-beat amplitude*: distance between the end of the caudal peduncle and the line including BC the head segment. (3) *mean tail-beat frequency,* using data from  all the cycles of the video fragment. 

## Structure

The `zebraGait_Tk.py`, `zebraGait_Qt.py` executes a GUI to work and interact with the other scripts. Anyway, `swimTunnel.py`, `treatData.py` and `showData.py` scripts can run standalone, only changing the inputs of each one in the `__main__`.

* The `swimTunnel.py` script extracts and saves the raw data of the fish skeleton from a given video.

* The `treatData.py` script treats the raw data of the fish skeleton to obtain a detailed description of the fish movement, saving the whole data set into a csv file.

* The `showData.py` scripts shows the treated data through plots.

## Test

The test folder contains the reference video to test the scripts. 

## Models

The models folder contains the masonry of the GUI and the instructions to modify it.

## Install required libraries

The project is built under python v3.6 and opencv v4.0.0

Choose ONLY one of the below options to install all the required libraries:

* OpenCV libraries from the source:
  1. Install the OpenCV-base and OpenCV-contrib libraries [manually](https://docs.opencv.org/3.4.5/d7/d9f/tutorial_linux_install.html) from the source code. 

  2. Install the python required libraries:
      ```bash
      pip3 install -r requirementsFromSource.txt
      ```
* OpenCV libraries from the unofficial python packages:
    ```bash
    pip3 install -r requirements.txt
    ```
## Build an executable (only with python-opencv)

The executable files built with [PyInstaller](http://www.pyinstaller.org/) work without install libraries or python.

Build an executable file from main scripts `zebraGait_Tk.py` or `zebraGait_Qt.py` with PyInstaller, following the steps below:

1. Install PyInstaller through python package manager:

   ```bash
   pip3 install pyinstaller
   ```

2. Edit `build.sh` under Gnu/Linux or `build.bat` under Windows, specifying the main script and the desired options.
   
    In Windows, we must add the location of ffmpeg dll, editing the above line in `build.bat`:
    ```bash
    --add-binary "<PATH_TO_PYTHON>\Lib\site-packages\cv2\opencv_ffmpeg<VERSION_ARCH>.dll;."
    ```
3. Run the `build.sh` or `build.bat` script.

## TODO

- `treatData.py`: In the mean of the skeleton, if there is not a repeated x, no uniqueMean.
- `swimTunnel.py`: Add a check of the skeleton length.
- `swimTunnel.py`: Use h and w in the blob check instead of the area.
- `zebraGait_Qt.py`: Create a loggerHandler and display the logs on a widget.

## Known bugs

+ None
