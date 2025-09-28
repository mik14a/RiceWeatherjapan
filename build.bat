@echo off
echo ===================================
echo  Rice Weather Japan - EXE Builder
echo ===================================
echo.
echo Building executable file...
echo Please wait, this may take a few minutes.
echo.

python -m PyInstaller --onefile --windowed --name "RiceWeatherJapan" --add-data "assets;assets" "Rice Weather japan_v1.7.py"

echo.
echo Build complete! The executable can be found in the 'dist' folder.
pause
