@echo off
REM Build the Life360 Desktop Windows executable.
REM Produces dist\Life360.exe

setlocal

echo === Creating virtual environment ===
python -m venv .venv || goto :error
call .venv\Scripts\activate.bat || goto :error

echo === Installing dependencies ===
python -m pip install --upgrade pip || goto :error
pip install -r requirements.txt -r requirements-build.txt || goto :error

echo === Building executable ===
pyinstaller Life360.spec --noconfirm --clean || goto :error

echo.
echo === Done! The executable is at: dist\Life360.exe ===
goto :eof

:error
echo.
echo Build failed. See the messages above.
exit /b 1
