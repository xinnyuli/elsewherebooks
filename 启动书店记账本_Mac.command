#!/bin/bash
# macOS 启动脚本 - 双击即可运行

# 获取脚本所在目录
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

# 检查 Python 3
if ! command -v python3 &> /dev/null; then
    osascript -e 'display dialog "请先安装 Python 3\n\n访问: https://www.python.org" buttons {"好的"} default button 1'
    exit 1
fi

# 检查依赖
python3 -c "import customtkinter" 2>/dev/null
if [ $? -ne 0 ]; then
    osascript -e 'display dialog "正在安装依赖...\n请稍等" buttons {"好的"} default button 1 giving up after 2'
    pip3 install customtkinter requests pypinyin pandas openpyxl
fi

# 启动程序（使用 pythonw 避免终端窗口）
if command -v pythonw3 &> /dev/null; then
    pythonw3 book_price_gui.py &
else
    python3 book_price_gui.py &
fi

# 延迟后关闭终端窗口
sleep 1
osascript -e 'tell application "Terminal" to close first window' & 2>/dev/null

exit 0
