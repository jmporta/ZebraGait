pyinstaller --noconfirm --log-level=INFO \
    --onefile --noconsole\
    --add-data="README.md:." \
    zebraGait_Qt.py

rm -rf build
rm -rf logs
rm -rf export
rm -rf __pycache__
rm zebraGait_Qt.spec
