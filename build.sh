pyinstaller --noconfirm --log-level=INFO \
    --onefile --noconsole\
    --add-data="README.md:." \
    kinematicsZebra_Qt.py
