@echo off
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp099_SISTEM\buka_studio.ps1"
if errorlevel 1 pause
