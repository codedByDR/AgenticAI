@echo off
cd /d "c:\Users\DIVYARANI RAJKUMAR\Workspace\Poemagent"
echo Starting PoemAgent Backend Server...
start "PoemAgent Backend" "C:\Users\DIVYARANI RAJKUMAR\anaconda3\python.exe" -m uvicorn main:app --reload
timeout /t 3
echo Starting PoemAgent Streamlit App...
"C:\Users\DIVYARANI RAJKUMAR\anaconda3\python.exe" -m streamlit run app.py
