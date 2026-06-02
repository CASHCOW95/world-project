@echo off
setlocal enabledelayedexpansion

:: 1. 구글 폼 주소 입력
set "URL=https://docs.google.com/forms/d/1azMwS2BloToyS4Lxq3HSPMmfWNKeAbiL61MWLc1MAyo/edit

:: 2. 프로필 번호 목록
set "PROFILES=4 5 6 8 10 11 13 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31 32 34"

echo 초광속으로 폼 열기 시작한다! (0.05초 간격 세팅)

for %%n in (%PROFILES%) do (
    echo Profile %%n 실행 중...
    start "" "C:\Program Files\Google\Chrome\Application\chrome.exe" --profile-directory="Profile %%n" "%URL%"
    
    :: 0.05초 정도의 아주 짧은 딜레이를 주는 트릭이야
    pathping 127.0.0.1 -n -q 1 -p 50 >nul
)

echo 전부 다 띄웠어! 컴퓨터가 좀 놀랐을지도 몰라.
pause
