pyinstaller --noconfirm --log-level=INFO \
    --add-data="README.md:." \
    --add-data="icons:icons" \
    app.py
