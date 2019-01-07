pyinstaller --noconfirm --log-level=INFO ^
    --onefile --noconsole ^
    --add-data="README.md;." ^
    --add-data="icons;icons" ^
    --icon=.\icons\gar-fish.ico ^
    app.py