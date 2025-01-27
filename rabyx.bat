@echo off
cd /d C:\ROOT_FROST\bin

:: Check if a parameter is passed
if "%1"=="" (
    echo No tool name provided. Please specify one of the following tools: apktool, jadx, jadx-gui, jadx-gui.bat, jadx.bat
    exit /b
)

:: Handle the specified tool
if "%1"=="apktool" (
    echo Running apktool.jar...
    java -jar apktool.jar
) else if "%1"=="jadx" (
    echo Running jadx...
    jadx
) else if "%1"=="jadx-gui" (
    echo Running jadx-gui...
    jadx-gui
) else if "%1"=="jadx-gui.bat" (
    echo Running jadx-gui.bat...
    call jadx-gui.bat
) else if "%1"=="jadx.bat" (
    echo Running jadx.bat...
    call jadx.bat
) else (
    echo Invalid tool name specified. Please specify one of the following tools: apktool, jadx, jadx-gui, jadx-gui.bat, jadx.bat
    exit /b
)

pause
