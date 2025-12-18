@echo off
echo ========================================
echo  Starbroke Internet Cafe System
echo  Installation Script
echo ========================================
echo.

echo Checking Python installation...
python --version
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

echo.
echo Installing required packages...
echo.

echo Installing mysql-connector-python...
pip install mysql-connector-python

echo Installing pywin32 (for PC lock features)...
pip install pywin32

echo Installing Pillow (for image handling)...
pip install Pillow

echo.
echo ========================================
echo Installation Complete!
echo ========================================
echo.
echo Next steps:
echo 1. Make sure XAMPP/MySQL is running
echo 2. Run: python main.py
echo 3. Login to admin panel (admin/admin123)
echo.
echo Default admin credentials:
echo Username: admin
echo Password: admin123
echo.
pause