# SwimTunnelPy

**IMPORTANT**: At this moment this file contains just a few tips of the project. The project is under development.

## Description

CV - Movement detection/description of a fish in a swim-tunnel. 

## Install required libraries

The project is build under python v3.6 and opencv v3.4.

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

The executable files built with [PyInstaller](http://www.pyinstaller.org/) works without install libraries and ¿only with python>=3.6?

Build an executable file with PyInstaller, following the below steps:

1. Install PyInstaller through python package manager:

   ```bash
   pip3 install pyinstaller
   ```

2. Run `build.sh` under Gnu/Linux or `build.bat` under Windows.

3. The resultant executable, located in `./dist`, needs a copy of the folder `icons` in the same directory to be executed.

## TODO

- Able to kill the process.

- Mean skeleton: if there is not a repeated x, no uniqueMean.
- Add a check of the skeleton length.
- Use h and w in the blob check instead of area.

## Known bugs
