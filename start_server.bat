@echo off
echo Installing required Python packages...
pip install -r requirements.txt

echo.
echo Starting the Excel Upload & Test Runner server...
echo The application will be available at: http://localhost:5000
echo.
echo Press Ctrl+C to stop the server
echo.

python app.py

pause
