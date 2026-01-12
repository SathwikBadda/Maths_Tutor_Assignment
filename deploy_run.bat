@echo off
REM Build index for RAG before starting the app

REM Set working directory to script location
cd /d %~dp0

REM Install requirements (if not already installed)
python -m pip install --upgrade pip
pip install -r requirements.txt

REM Build the RAG index
python build_index.py

REM Start the Streamlit app
streamlit run app.py
