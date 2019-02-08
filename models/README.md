## Compile a Qt-Designer files

PyQt5 has a tool to convert files *.ui to *.py:
```
pyuic5 -x window.ui -o window_ui.py
```
PyQt5 has a tool to convert files *.qrc to *.py:
```
pyrcc5 -o resources_rc.py resources.qrc 

```

Delete `import resource_rc` from al models and add it into the main Qt pyhton file.
