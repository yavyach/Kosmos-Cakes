@echo off
chcp 65001 >nul
REM ============================================================
REM   Один клик: коммитит ИСХОДНИКИ и пушит в main (без веток).
REM   Сгенерированный HTML не коммитится — его дописывает CI на GitHub.
REM ============================================================

cd /d "%~dp0"

if not exist ".git" (
  echo.
  echo [!] Это не git-репозиторий.
  pause
  exit /b 1
)

echo === Сборка (локально, для проверки) ===
python build.py
if errorlevel 1 (
  echo.
  echo [!] Ошибка сборки.
  pause
  exit /b 1
)

echo === Сбрасываю сгенерированный HTML (в git его кладёт только CI) ===
git checkout -- site/cakes site/index.html site/preview.html site/delivery.html site/tilda-embed.html site/catalog-init.js 2>nul
git checkout -- calculator/cakes 2>nul

echo === Подтягиваю origin/main (rebase, без merge-веток) ===
git pull --rebase origin main
if errorlevel 1 (
  echo.
  echo [!] Конфликт при rebase. Напиши в чат — разберём.
  pause
  exit /b 1
)

echo === Что изменилось (только исходники) ===
git status --short

echo.
set /p MSG=Описание коммита (Enter — авто-дата):

if "%MSG%"=="" (
  set "MSG=update %DATE% %TIME%"
)

echo.
echo === Коммит ===
git add -A
git commit -m "%MSG%"

if errorlevel 1 (
  echo.
  echo [!] Нечего коммитить.
  pause
  exit /b 1
)

echo === Push в main ===
git push origin main

if errorlevel 1 (
  echo.
  echo [!] Push не прошёл — снова: git pull --rebase origin main
  pause
  exit /b 1
)

echo.
echo === Готово! CI обновит HTML на Pages за 1-3 мин ===
echo https://yavyach.github.io/Kosmos-Cakes/site/
timeout /t 5
