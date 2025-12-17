@echo off
cd /d "%~dp0"
echo Starting Anti-Bullying App...
python -m uvicorn app.main:app --reload
pause
