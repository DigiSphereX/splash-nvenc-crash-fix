@echo off
title Splash NVENC Crash Fix
color 0A
echo ============================================
echo   Splash Player - NVENC Crash Fix
echo   Fixes exit code 1 on Windows 10/11
echo ============================================
echo.

:: Check for admin
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] This fix requires Administrator rights.
    echo     Requesting elevation...
    powershell -Command "Start-Process '%~f0' -Verb RunAs"
    exit /b
)

:: Detect Splash installation
set "SPLASH_DIR="
if exist "C:\Program Files (x86)\Mirillis\Splash\Splash.exe" (
    set "SPLASH_DIR=C:\Program Files (x86)\Mirillis\Splash"
) else if exist "C:\Program Files\Mirillis\Splash\Splash.exe" (
    set "SPLASH_DIR=C:\Program Files\Mirillis\Splash"
) else (
    echo [ERROR] Splash Player not found!
    echo Please install Splash from https://mirillis.com/downloads
    pause
    exit /b 1
)

echo [OK] Splash found: %SPLASH_DIR%

:: Check if fix already applied
if exist "%SPLASH_DIR%\nvEncodeAPI.dll" (
    echo [!] nvEncodeAPI.dll already exists in Splash folder.
    echo     Fix may already be applied.
    echo.
    choice /c YN /m "Overwrite with fresh fix?"
    if errorlevel 2 (
        echo Cancelled.
        pause
        exit /b
    )
)

:: Verify Python is available (avoid resolving to the Store alias or a malicious entry)
set "PYCMD="
where python >nul 2>nul
if %errorlevel% equ 0 (
    set "PYCMD=python"
) else (
    where py >nul 2>nul
    if %errorlevel% equ 0 (
        set "PYCMD=py -3"
    )
)
if not defined PYCMD (
    echo [ERROR] Python is not installed.
    echo   Download it from https://www.python.org/downloads/
    echo   IMPORTANT: tick "Add python.exe to PATH" during installation.
    pause
    exit /b 1
)

:: Generate the stub DLL using Python
echo [1/2] Generating stub nvEncodeAPI.dll...
if exist "%SPLASH_DIR%\nvEncodeAPI.dll" del /f "%SPLASH_DIR%\nvEncodeAPI.dll"
if exist "%SPLASH_DIR%\nvEncodeAPI.dll" (
    echo [ERROR] Cannot remove the old nvEncodeAPI.dll (permissions?).
    pause
    exit /b 1
)
%PYCMD% "%~dp0fix\generate_stub.py" "%SPLASH_DIR%\nvEncodeAPI.dll"
if %errorlevel% neq 0 (
    echo [ERROR] Failed to generate DLL.
    pause
    exit /b 1
)
if not exist "%SPLASH_DIR%\nvEncodeAPI.dll" (
    echo [ERROR] nvEncodeAPI.dll was not created - check the Python output above.
    pause
    exit /b 1
)

echo [2/2] Done!
echo.
echo ============================================
echo   Fix applied successfully!
echo   You can now launch Splash normally.
echo ============================================
echo.
pause
