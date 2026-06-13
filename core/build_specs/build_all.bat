@echo off
chcp 65001 >nul
title EXE Build All - 오픈폼 + 게임

set PROJECT_ROOT=%~dp0..\..
set SPEC_DIR=%~dp0
set EXE_DIR=%PROJECT_ROOT%\exe

echo ========================================
echo  EXE 일괄 빌드 스크립트
echo ========================================
echo.

REM exe 폴더 구조 생성
if not exist "%EXE_DIR%\게임" mkdir "%EXE_DIR%\게임"
if not exist "%EXE_DIR%\오픈폼" mkdir "%EXE_DIR%\오픈폼"

echo [1/3] 오픈폼 v12.6 빌드 중...
echo ----------------------------------------
cd /d "%PROJECT_ROOT%"
pyinstaller --noconfirm --distpath "%EXE_DIR%\오픈폼" --workpath "%PROJECT_ROOT%\build\openform" "%SPEC_DIR%OpenForm_v12.6.spec"
if %ERRORLEVEL% neq 0 (
    echo [실패] 오픈폼 빌드 실패!
    pause
    exit /b 1
)
echo [완료] 오픈폼 v12.6 빌드 성공

echo.
echo [2/3] 게임 V4 상용 배포판 빌드 중...
echo ----------------------------------------
pyinstaller --noconfirm --distpath "%EXE_DIR%\게임" --workpath "%PROJECT_ROOT%\build\game_v4" "%SPEC_DIR%AUTOmaple_v2.0.0_V4.spec"
if %ERRORLEVEL% neq 0 (
    echo [실패] 게임 V4 빌드 실패!
    pause
    exit /b 1
)
echo [완료] 게임 V4 상용 배포판 빌드 성공

echo.
echo [3/3] 게임 경량판 빌드 중...
echo ----------------------------------------
pyinstaller --noconfirm --distpath "%EXE_DIR%\게임" --workpath "%PROJECT_ROOT%\build\game_light" "%SPEC_DIR%AUTOmaple_v2.0.0_Light.spec"
if %ERRORLEVEL% neq 0 (
    echo [실패] 게임 경량판 빌드 실패!
    pause
    exit /b 1
)
echo [완료] 게임 경량판 빌드 성공

echo.
echo ========================================
echo  모든 빌드가 완료되었습니다!
echo ========================================
echo.
echo  exe/오픈폼/OpenForm_v12.6/
echo  exe/게임/AUTOmaple_v2.0.0_LK/
echo  exe/게임/AUTOmaple_v2.0.0_경량/
echo.
pause
