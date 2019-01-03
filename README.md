# SwimTunnelPy

**IMPORTANT**: At this moment this file contains just a few tips of the project. The project is under development.

## Description

CV - Movement detection/description of a fish in a swim-tunnel. 

## Install required libraries

The project is constructed under python3.6

Choose ONLY one of the below option to install all the required libraries:

* OpenCV libraries from the source:
     1. Install the OpenCV-base and OpenCV-contrib libraries manually from the source code. 

     2. Install the python required libraries:

       ```bash
     pip3 install -r requirementsFromSource.txt
       ```
* OpenCV libraries from the unofficial python packages:
    ```bash
    pip3 install -r requirements.txt
    ```
## Build an executable

Build an only one executable file with PyInstaller, following the below steps:

1.  Run `compile.sh` under Gnu/Linux or `compile.bat` under Windows.
2.  The resultant executable in `./dist` needs the folder icons to be executed.

## TODO

- Able to kill the process.
- Contrast and fps in csv.

- Mean skeleton: if there is not a repeated x, no uniqueMean.
- Add a check of the skeleton length.
- Use h and w in the blob check instead of area.

## Known bugs
