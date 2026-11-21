@echo off
title SkillLens - AI Internship Readiness Engine
echo ========================================================
echo Starting SkillLens Hackathon MVP...
echo ========================================================
echo.

set PYTHON_EXE=C:\Users\farve_y7b0tn1\AppData\Local\Python\pythoncore-3.14-64\python.exe

if exist "%PYTHON_EXE%" (
    "%PYTHON_EXE%" app.py
) else (
    python app.py
)

pause
