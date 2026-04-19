@echo off

if not exist "venv" (
	echo Creating venv...
	py -m venv venv
	
	echo Upgrading pip...
	"venv\Scripts\python.exe" -m pip install --upgrade pip

	echo Installing dependencies...
	"venv\Scripts\pip.exe" install -r requirements.txt
	
	echo.
)

"venv\Scripts\python.exe" apply.py

pause
