# Kinematics Zebra

**IMPORTANT**: At this moment this file contains just a few tips of the project. The project is under development.

Motion detection/description of a zebra fish in a swimming-tunnel. 

## Description

The `KinematicsZebra.py` executes a GUI to work and interact with the other scripts. Anyway, `swimTunnel.py`, `treatData.py`, and `showData.py` scripts can run in a standalone way, only changing the inputs of each one in the `__main__` function:

* The `swimTunnel.py` script extracts and saves the raw data of the fish skeleton from a given video.

* The `treatData.py` script treats the raw data of the fish skeleton to obtain a detailed description of the fish movement, saving the whole data set into a csv file.

* The `showData.py` scripts shows the treated data through plots.

## Install required libraries

The project is built under python v3.6 and opencv v3.4.

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
## Build an executable

The executable files built with [PyInstaller](http://www.pyinstaller.org/) work without install libraries or python.

Build an executable file with PyInstaller, following the steps below:

1. Install PyInstaller through python package manager:

   ```bash
   pip3 install pyinstaller
   ```

2. Run `build.sh` under Gnu/Linux or `build.bat` under Windows.
    
    In Windows we must add the location of ffmpeg dll, editing the above line in `build.bat`:
    ```bash
    --add-binary "<PATH_TO_PYTHON>\Lib\site-packages\cv2\opencv_ffmpeg<VERSION_ARCH>.dll;."
    ```

3. The resultant executable, located in `./dist`, needs a copy of the folder `icons` in the same directory to be executed.

## TODO

- Allow the inputs through command line arguments.
- Mean skeleton: if there is not a repeated x, no uniqueMean.
- Add a check of the skeleton length.
- Use h and w in the blob check instead of the area.

## Known bugs

+ None