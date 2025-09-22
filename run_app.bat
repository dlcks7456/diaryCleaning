@echo off
chcp 65001 > nul
echo ========================================
echo Streamlit 앱 실행 스크립트
echo ========================================

echo.
echo [1단계] 가상환경 확인 및 설정...
if not exist "venv\" (
    echo 가상환경이 없습니다. 새로 생성합니다...
    python -m venv venv
    if %ERRORLEVEL% neq 0 (
        echo 가상환경 생성에 실패했습니다.
        pause
        exit /b 1
    )
    echo 가상환경이 생성되었습니다.
) else (
    echo 기존 가상환경을 찾았습니다.
)

echo.
echo [2단계] 가상환경 활성화...
call venv\Scripts\activate.bat
if %ERRORLEVEL% neq 0 (
    echo 가상환경 활성화에 실패했습니다.
    pause
    exit /b 1
)

echo.
echo [3단계] 패키지 설치...
pip install -r requirements.txt
if %ERRORLEVEL% neq 0 (
    echo 패키지 설치에 실패했습니다.
    pause
    exit /b 1
)

echo.
echo [4단계] Streamlit 앱 실행...
echo 참고: Streamlit에서 메일 입력창이 나오면 스킵하세요.
echo.
echo 앱이 시작됩니다...
timeout /t 3 > nul

uv run streamlit run main.py --server.headless true
if %ERRORLEVEL% neq 0 (
    echo UV를 사용한 실행에 실패했습니다. 일반 streamlit으로 재시도합니다...
    streamlit run main.py --server.headless true
)

echo.
echo 앱이 종료되었습니다.
pause
