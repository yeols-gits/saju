@echo off
start "FastAPI Background Process" /B ..\venv\Scripts\uvicorn main:app --reload