@echo off
setlocal enabledelayedexpansion

:: Get the directory of this batch file dynamically
set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

:menu
cls
echo ===================================================
echo Spira Mod Manager - Compilation Toolkit (Nightly)
echo ===================================================
echo.
echo Please select a compilation option:
echo 1. Compile Spira Mod Manager
echo 2. Compile Plugin Trackers
echo 3. Compile All Targets (Manager and Trackers)
echo 4. Exit
echo.
set /p choice="Enter your choice (1-4): "

if "%choice%"=="1" (
    echo.
    echo === Compiling Spira Mod Manager ===
    python -m PyInstaller "SpiraModManager.spec" --noconfirm --clean
    if errorlevel 1 (
        echo Compilation FAILED for Spira Mod Manager.
    ) else (
        echo Successfully compiled Spira Mod Manager!
    )
    pause
    goto menu
)

if "%choice%"=="2" (
    echo.
    echo === Auto-Discovering and Compiling Plugin Trackers ===
    if not exist "plugins" (
        echo No plugins directory found.
    ) else (
        for /d %%D in (plugins\*) do (
            if exist "%%D\tracker.py" (
                echo.
                echo Compiling tracker for plugin '%%~nD'...
                python -m PyInstaller --noconsole --onefile --clean "%%D\tracker.py"
                if errorlevel 1 (
                    echo Compilation FAILED for tracker in %%~nD.
                ) else (
                    echo Successfully compiled tracker for %%~nD.
                    if exist "dist\tracker.exe" (
                        mkdir "dist\plugins\%%~nD" 2>nul
                        copy /y "dist\tracker.exe" "dist\plugins\%%~nD\tracker.exe" >nul
                        copy /y "dist\tracker.exe" "%%D\tracker.exe" >nul
                        echo Copied tracker executable to output and dev directories.
                    )
                )
            )
        )
        echo.
        echo Tracker compilation complete.
    )
    pause
    goto menu
)

if "%choice%"=="3" (
    echo.
    echo === Compiling Spira Mod Manager ===
    python -m PyInstaller "SpiraModManager.spec" --noconfirm --clean
    if errorlevel 1 (
        echo Compilation FAILED for Spira Mod Manager.
    ) else (
        echo Successfully compiled Spira Mod Manager!
    )

    echo.
    echo === Auto-Discovering and Compiling Plugin Trackers ===
    if not exist "plugins" (
        echo No plugins directory found.
    ) else (
        for /d %%D in (plugins\*) do (
            if exist "%%D\tracker.py" (
                echo.
                echo Compiling tracker for plugin '%%~nD'...
                python -m PyInstaller --noconsole --onefile --clean "%%D\tracker.py"
                if errorlevel 1 (
                    echo Compilation FAILED for tracker in %%~nD.
                ) else (
                    echo Successfully compiled tracker for %%~nD.
                    if exist "dist\tracker.exe" (
                        mkdir "dist\plugins\%%~nD" 2>nul
                        copy /y "dist\tracker.exe" "dist\plugins\%%~nD\tracker.exe" >nul
                        copy /y "dist\tracker.exe" "%%D\tracker.exe" >nul
                        echo Copied tracker executable to output and dev directories.
                    )
                )
            )
        )
        echo.
        echo Tracker compilation complete.
    )
    pause
    goto menu
)

if "%choice%"=="4" (
    echo Exiting.
    exit /b 0
)

echo Invalid selection. Please choose a number between 1 and 4.
pause
goto menu
