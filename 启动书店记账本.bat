@echo off
REM 书店记账本快速启动脚本 - Windows版本
REM 双击此文件即可启动

cd /d "%~dp0"
echo.
echo ========================================
echo    📚 Elsewhere Books 记账本
echo ========================================
echo.
echo 正在启动...
echo.

REM 尝试使用python命令
python --version >nul 2>&1
if %errorlevel% equ 0 (
    start "" pythonw book_price_gui.py
    exit
)

REM 尝试使用py命令
py --version >nul 2>&1
if %errorlevel% equ 0 (
    start "" pyw book_price_gui.py
    exit
)

REM 如果都失败了，显示错误信息
echo ❌ 未找到Python！
echo.
echo 请先安装Python 3.10或更高版本
echo 下载地址: https://www.python.org/downloads/
echo.
pause
