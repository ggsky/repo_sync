#!/bin/bash
echo "Building repo_sync GUI executable..."

# Install required packages
pip install pyinstaller
pip install -e .

# Build the executable
pyinstaller --onefile --windowed --name "RepoSync" --add-data "repo_sync/config.yml:repo_sync" main_gui.py

echo ""
echo "Build completed! The executable is in the dist folder."
echo "" 