pyinstaller --noconfirm --log-level=INFO \
    --onefile \
    --add-data="README.md:." \
    --add-data="icons:icons" \
    app.py
