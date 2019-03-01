@echo OFF

:: lib = <PATH_TO_PYtHON>\Lib\site-packages\cv2\opencv_ffmpeg<VERSION>.dll
set arg=%1
set lib=%2

:: main
IF NOT "%arg%"=="clean" (
    call :build_onefile
) ELSE (
    call :clean
)

EXIT /B 0

:: Pyinstaller routine with options
:build_onefile
pyinstaller --noconfirm --log-level=INFO ^
    --onefile --noconsole ^
    --add-data="README.md;." ^
    --add-binary "%lib%;." ^
    --icon=.\models\icons\gar-fish.ico ^
    %arg%
EXIT /B 0

:: Clean all the build/execution extra files
:clean
    del -r build
    del -r dist
    del -r logs
    del -r export
    del -r __pycache__
    del -r  models\__pycache__
    del *.spec
EXIT /B 0
