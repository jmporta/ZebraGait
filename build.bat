pyinstaller --noconfirm --log-level=INFO ^
    --onefile --noconsole ^
    --add-data="README.md;." ^
    --add-data="icons;icons" ^
    --add-binary "C:\Users\Arnau\AppData\Local\Programs\Python\Python36\Lib\site-packages\cv2\opencv_ffmpeg345_64.dll;." ^
    --icon=.\icons\gar-fish.ico ^
    kinematicsZebra_Qt.py
