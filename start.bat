@echo off
chcp 65001 >nul
title 马克思主义基本原理刷题系统
echo ======================================================================
echo    📚 马克思主义基本原理 · 在线刷题平台 (539题全收录)
echo    涵盖：导论、唯物辩证法、认识论、唯物史观、资本主义与科学社会主义
echo ======================================================================
echo.
echo [1/2] 正在检查依赖环境...
python -c "import flask" >nul 2>&1
if errorlevel 1 (
    echo 正在自动安装 Flask 依赖，请稍候...
    pip install -r requirements.txt
)

echo [2/2] 正在启动本地服务...
echo.
echo 本地服务已启动！请在浏览器打开以下地址：
echo 👉 http://localhost:8080
echo.
echo (按 Ctrl+C 可停止服务)
echo ----------------------------------------------------------------------
start http://localhost:8080
python webapp/app.py
pause
