pyinstaller --noconfirm --log-level=INFO \
    --onefile --noconsole\
    --add-data="README.md:." \
    zebraGait_Qt.py
