#!/bin/bash

arg=$1

# Pyinstaller routine with options
build_onefile() {
    pyinstaller --noconfirm --log-level=INFO \
    --onefile --noconsole\
    --add-data="README.md:." \
    $arg
}

# Clean all the build/execution extra files
clean() {
    rm -rf build
    rm -rf logs
    rm -rf export
    rm -rf __pycache__
    rm -rf models/__pycache__
    rm *.spec
}

# main
if [ "$arg" != "clean" ]
then
    build_onefile
    clean
else
    clean
    rm -rf dist
fi

