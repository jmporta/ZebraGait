@echo OFF
::RUN IN A WINDOWS POWERSHELL!


:: lib = <PATH_TO_PYtHON>\Lib\site-packages\cv2\opencv_ffmpeg<VERSION>.dll
set lib=%2
set arg=%1

:: Pyinstaller routine with options
:build_onefile
pyinstaller --noconfirm --log-level=INFO ^
    --onefile --noconsole ^
    --add-data="README.md;." ^
    --add-binary "lib;." ^
    --icon=.\models\icons\gar-fish.ico ^
    arg
EXIT /B 0

:: Clean all the build/execution extra files
:clean
    del build
    del logs
    del export
    del __pycache__
    del models\__pycache__
    del *.spec
EXIT /B 0

:: main
IF %1!="clean"
    call build_onefile arg, lib
    call clean
ELSE
    call clean
    del dist
