@echo off
rem Unified launcher: main.py starts the GUI by default.
cd /d "%~dp0"
where pythonw >nul 2>nul
if %errorlevel%==0 (
  start "" pythonw main.py
) else (
  chcp 65001 >nul
  start "" python main.py
)
