@echo off
chcp 65001 >nul
title Article Generator
cd /d "%~dp0"

echo ============================================================
echo    Article Generator  -  запуск приложения
echo ============================================================
echo.

where python >nul 2>nul
if errorlevel 1 (
    echo [Ошибка] Python не найден в PATH.
    echo Установите Python 3.10 или новее с https://www.python.org/downloads/
    echo При установке отметьте галочку "Add python.exe to PATH".
    echo.
    pause
    exit /b 1
)

if not exist ".venv" (
    echo [1/3] Создаю виртуальное окружение .venv ...
    python -m venv .venv
    if errorlevel 1 (
        echo [Ошибка] Не удалось создать виртуальное окружение.
        echo.
        pause
        exit /b 1
    )
) else (
    echo [1/3] Виртуальное окружение .venv найдено
)

echo [2/3] Проверяю зависимости (fastapi, uvicorn, ollama, httpx) ...
".venv\Scripts\python.exe" -m pip install --disable-pip-version-check -q -r requirements.txt
if errorlevel 1 (
    echo [Ошибка] Не удалось установить зависимости.
    echo Проверьте подключение к интернету и повторите запуск.
    echo.
    pause
    exit /b 1
)

echo [3/3] Запускаю сервер:  http://127.0.0.1:8000
echo.
echo    Остановить сервер можно сочетанием клавиш Ctrl+C
echo    Страница откроется в браузере по адресу http://127.0.0.1:8000
echo.
".venv\Scripts\python.exe" -m uvicorn main:app --host 127.0.0.1 --port 8000

echo.
echo Сервер остановлен.
pause
