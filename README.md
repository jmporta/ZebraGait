# SwimTunnelPy

**IMPORTANT**: At this moment this file contains just a few tips of the project. The project is under development.

## Description

CV - Movement detection/description of a fish in a swim-tunnel. 

## Install required libraries

+ OpenCV libraries:

    Choose ONLY one of them:

    * Install the OpenCV-base and OpenCV-contrib libraries manually from the source code. 
    * Install the precompiled python packages through pip3. 

+ Python libraries:

    ```
    pip3 install -r requirements.txt
    ```

## TODO
+ `swimTunnell.py`: Obtain a smaller fish location domain using the previous fish bounding box. Check if the current skeleton is in it.
+ `swimTunnell.py`: No area, longitud or size absolute values in the code. Descrive them in the config file and if it is possible make them relative to something.

## Known bugs
+ `swimTunnell.py`: The raw/avi original fish video throw a warning in opencv videocapture function. Cause: lack metadata? need codecs?
+ `treatData.py`: The matrix A reshape of the imported skeleton data crash with the raw/avi original fish video. Cause: maybe a limit index situation?
