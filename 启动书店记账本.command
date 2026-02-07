#!/bin/bash
# 书店记账本启动脚本

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

# 检查Python是否安装
if ! command -v python3 &> /dev/null; then
    echo "❌ 未找到Python3，请先安装："
    echo "   brew install python@3.10"
    exit 1
fi

# 检查依赖
echo "📚 检查依赖包..."
python3 -c "import customtkinter, requests" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "⚠️  首次运行，正在安装依赖..."
    pip3 install customtkinter requests pypinyin
fi

# 启动程序
echo "🚀 启动书店记账本..."
python3 book_price_gui.py

# 如果程序异常退出，等待用户按键
if [ $? -ne 0 ]; then
    echo ""
    echo "❌ 程序异常退出，按任意键关闭..."
    read -n 1
fi
