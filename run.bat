@echo off
title SkillLens - AI Internship Readiness Engine
echo ========================================================
echo Starting SkillLens Hackathon MVP...
echo ========================================================
echo.

if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" app.py
) else (
    python app.py
)

pause
