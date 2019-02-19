## Compile a Qt-Designer files

**Note:** If you want to compile the source code through `pyinstaller` do not use on-the-fly compilation of Qt models.



The `*.ui` files are the GUI models designed by Qt-Designer, and the `*.qrc` files are a byte-codes of pictures used in the design. To work in python they must be compiled.

`PyQt5` has a tool to convert files `*.ui` to `*.py`: 

```bash
pyuic5 -x <window>.ui -o <window>_ui.py
```

`PyQt5` has a tool to convert files `*.qrc` to `*.py`: 

```bash
pyrcc5 -o resources_rc.py resources.qrc
```



Delete `import resource_rc` from all `<windows>_ui.py` and add it into the main Qt pyhton file.
