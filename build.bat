@echo off
echo Building repo_sync GUI executable...

REM Install required packages
pip install pyinstaller
pip install -e .

REM Build the executable
pyinstaller --onefile --windowed --name "RepoSync" --icon=icon.ico --add-data "repo_sync/config.yml;repo_sync" main_gui.py

echo.
echo Build completed! The executable is in the dist folder.
echo. 