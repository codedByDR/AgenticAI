@echo off
setlocal enabledelayedexpansion
cd /d "c:\Users\DIVYARANI RAJKUMAR\Workspace\Poemagent"

echo Starting PoemAgent Backend Server with Groq API...
start "PoemAgent-Backend" "C:\Users\DIVYARANI RAJKUMAR\anaconda3\python.exe" -m uvicorn main:app --reload --host 0.0.0.0 --port 8000

timeout /t 4

echo Starting PoemAgent Streamlit Frontend...
"C:\Users\DIVYARANI RAJKUMAR\anaconda3\python.exe" -m streamlit run app.py
