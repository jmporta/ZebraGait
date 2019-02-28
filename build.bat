pyinstaller --noconfirm --log-level=INFO ^
    --onefile --console ^
    --add-data="README.md;." ^
    --add-binary "C:\Users\Arnau\AppData\Local\Programs\Python\Python37\Lib\site-packages\cv2\opencv_ffmpeg400_64.dll;." ^
    --icon=.\models\icons\gar-fish.ico ^
    zebraGait_Qt.py
