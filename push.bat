@echo off
chcp 65001 >nul
REM ============================================================
REM   Один клик: коммитит все изменения и пушит в GitHub.
REM   Положи этот файл в КОРЕНЬ репозитория (рядом с .git папкой).
REM   Дабл-клик = всё залилось.
REM ============================================================

cd /d "%~dp0"

if not exist ".git" (
  echo.
  echo [!] Это не git-репозиторий. Сначала запусти клонирование:
  echo     git clone https://github.com/yavyach/Kosmos-Cakes.git
  echo.
  pause
  exit /b 1
)

echo === Проверяю что изменилось ===
git status --short

echo.
set /p MSG=Описание коммита (Enter — авто-дата):

if "%MSG%"=="" (
  set "MSG=update %DATE% %TIME%"
)

echo.
echo === Добавляю изменения ===
git add -A

echo === Коммитую: "%MSG%" ===
git commit -m "%MSG%"

if errorlevel 1 (
  echo.
  echo [!] Нечего коммитить (или ошибка). Проверь git status.
  pause
  exit /b 1
)

echo === Пушу на GitHub ===
git push

if errorlevel 1 (
  echo.
  echo [!] Push не прошёл. Проверь интернет / токен.
  pause
  exit /b 1
)

echo.
echo === Готово! Через 30-60 сек GitHub Pages обновится ===
echo URL: https://yavyach.github.io/Kosmos-Cakes/site/
echo.
timeout /t 5
