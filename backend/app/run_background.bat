@echo off
start "FastAPI Background Process" /B cmd /c "..\venv\Scripts\uvicorn main:app --reload"