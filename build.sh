pyinstaller --noconfirm --log-level=INFO \
    --onefile --noconsole\
    --add-data="README.md:." \
    --add-data="icons:icons" \
    kinematicsZebra_Tk.py
