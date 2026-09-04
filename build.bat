@echo off
REM build.bat — Скрипт сборки Markdown Editor для Windows
REM
REM Использование:
REM   build.bat              :: Сборка в папку (onedir)
REM   build.bat onefile      :: Сборка в один файл
REM   build.bat clean        :: Очистка артефактов сборки
REM
REM Требования:
REM   pip install pyinstaller PyQt6 PyQt6-WebEngine markdown

setlocal enabledelayedexpansion

set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

REM ─── Проверка зависимостей ─────────────────────────────────────────────
echo [INFO] Проверка зависимостей...

python --version >nul 2>&1 || (
    echo [ERROR] Python не найден. Установите Python 3.12+
    pause
    exit /b 1
)

pyinstaller --version >nul 2>&1 || (
    echo [WARN] PyInstaller не найден. Устанавливаю...
    pip install pyinstaller
)

REM Проверяем ресурсы
if not exist "markdown_editor_pkg\katex" (
    echo [WARN] Папка katex не найдена. Скачиваю ресурсы...
    python markdown_editor_pkg\download_katex.py
)

if not exist "markdown_editor_pkg\prism" (
    echo [WARN] Папка prism не найдена. Скачиваю ресурсы...
    python markdown_editor_pkg\download_prism.py
)

echo [OK] Зависимости проверены

REM ─── Сборка ────────────────────────────────────────────────────────────
set MODE=%1
if "%MODE%"=="" set MODE=onedir

echo [INFO] Сборка в режиме: %MODE%

set EXTRA_ARGS=
if "%MODE%"=="onedir" (
    echo [INFO] Режим: одна папка (рекомендуется для PyQt6-WebEngine)
) else if "%MODE%"=="onefile" (
    echo [WARN] Режим: один файл (медленнее старт, больше размер)
) else if "%MODE%"=="clean" (
    echo [INFO] Очистка артефактов сборки...
    rmdir /s /q build dist 2>nul
    for /d /r %%d in (__pycache__) do @rmdir /s /q "%%d" 2>nul
    echo [OK] Очистка завершена
    pause
    exit /b 0
) else (
    echo [ERROR] Неизвестный режим: %MODE%
    echo Использование: build.bat [onedir^|onefile^|clean]
    pause
    exit /b 1
)

echo [INFO] Запуск PyInstaller...
pyinstaller --clean --noconfirm markdown-editor.spec

if %ERRORLEVEL% EQU 0 (
    echo [OK] Сборка завершена!
    echo [INFO] Артефакты в: dist\
) else (
    echo [ERROR] Сборка не удалась
    pause
    exit /b 1
)

pause
