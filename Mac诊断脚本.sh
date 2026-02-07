#!/bin/bash
# Mac 环境诊断脚本 - 用于排查程序启动问题

echo "================================"
echo "📚 书店记账本 - Mac 环境诊断"
echo "================================"

# 切换到脚本所在目录
cd "$(dirname "$0")"

echo -e "\n🔍 1. 检查 Python 版本"
echo "--------------------"
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo "✓ $PYTHON_VERSION"
    
    # 检查版本号
    VERSION_NUM=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
    if (( $(echo "$VERSION_NUM >= 3.10" | bc -l) )); then
        echo "✓ 版本满足要求 (需要 >= 3.10)"
    else
        echo "⚠️  版本过低，建议升级: brew install python@3.10"
    fi
else
    echo "✗ Python 3 未安装"
    echo "  解决方法: brew install python@3.10"
    exit 1
fi

echo -e "\n🔍 2. 检查 Tkinter 支持"
echo "--------------------"
if python3 -c "import tkinter" 2>/dev/null; then
    echo "✓ Tkinter 可用"
else
    echo "✗ Tkinter 不可用"
    echo "  解决方法: brew install python-tk@3.10"
fi

echo -e "\n🔍 3. 检查依赖包"
echo "--------------------"

check_package() {
    if python3 -c "import $1" 2>/dev/null; then
        echo "✓ $1 已安装"
    else
        echo "✗ $1 未安装"
        MISSING_PACKAGES="$MISSING_PACKAGES $1"
    fi
}

MISSING_PACKAGES=""
check_package "customtkinter"
check_package "requests"
check_package "pypinyin"

if [ -n "$MISSING_PACKAGES" ]; then
    echo -e "\n⚠️  缺少依赖包，执行以下命令安装："
    echo "  pip3 install$MISSING_PACKAGES"
fi

echo -e "\n🔍 4. 检查程序文件"
echo "--------------------"
if [ -f "book_price_gui.py" ]; then
    FILE_SIZE=$(wc -c < book_price_gui.py)
    echo "✓ book_price_gui.py 存在 ($FILE_SIZE 字节)"
else
    echo "✗ book_price_gui.py 不存在"
    exit 1
fi

echo -e "\n🔍 5. 测试程序启动"
echo "--------------------"
echo "尝试启动程序（5秒后自动退出）..."

# 启动程序并捕获错误
timeout 5 python3 book_price_gui.py 2>&1 | head -20 &
PID=$!

sleep 2

if ps -p $PID > /dev/null 2>&1; then
    echo "✓ 程序启动正常"
    kill $PID 2>/dev/null
else
    echo "✗ 程序启动失败，错误信息："
    python3 book_price_gui.py 2>&1 | head -20
fi

echo -e "\n================================"
echo "📋 诊断完成"
echo "================================"
echo ""
echo "如果仍有问题，请："
echo "1. 截图错误信息"
echo "2. 联系技术支持（微信：棱决）"
echo ""
