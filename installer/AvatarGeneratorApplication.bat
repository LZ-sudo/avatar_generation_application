@echo off
cd /d "%~dp0avatar_generation_application"
start "" "%~dp0avatar_generation_application\.venv\Scripts\pythonw.exe" -m gui.main
