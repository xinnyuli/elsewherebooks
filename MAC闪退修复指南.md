# Mac 闪退问题修复指南

## 问题症状
运行 `python3 book_price_gui.py` 后：
- 终端显示 `English.lproj` 或 `Info.plist`
- 程序立即闪退
- 无任何窗口出现

---

## 🎯 根本原因

**macOS 的 GUI 应用必须使用 `pythonw3` 而不是 `python3`**

- `python3`：命令行模式，无法正确初始化 Tk 图形框架
- `pythonw3`：macOS GUI 模式，正确加载 Tk/Tcl 框架

---

## ✅ 解决方案（按顺序尝试）

### 方法 1：使用 pythonw3 启动（推荐）

```bash
cd ~/elsewherebooks  # 你的项目路径
pythonw3 book_price_gui.py
```

如果提示 `pythonw3: command not found`，说明你的 Python 安装不完整，跳到方法 2。

---

### 方法 2：重新安装官方 Python（最可靠）

**问题：** Homebrew 的 Python 通常缺少 `pythonw3` 和完整的 Tk 框架

**解决步骤：**

1. **下载官方 Python**
   - 访问：https://www.python.org/downloads/macos/
   - 下载最新稳定版（3.10+）
   - 选择 **macOS 64-bit universal2 installer**

2. **安装并验证**
   ```bash
   # 验证 pythonw3 存在
   which pythonw3
   # 输出应该类似: /Library/Frameworks/Python.framework/Versions/3.x/bin/pythonw3
   
   # 测试 Tkinter
   pythonw3 -c "import tkinter; tkinter.Tk().withdraw(); print('✓ Tkinter 正常')"
   ```

3. **重新安装依赖**
   ```bash
   pip3 install --upgrade customtkinter requests pypinyin pandas openpyxl
   ```

4. **启动程序**
   ```bash
   cd ~/elsewherebooks
   pythonw3 book_price_gui.py
   ```

---

### 方法 3：使用启动脚本（一键运行）

**下载启动脚本：**
```bash
cd ~/elsewherebooks
chmod +x 启动书店记账本_Mac.command
```

**双击** `启动书店记账本_Mac.command` 文件即可启动

该脚本会自动：
- 检测 pythonw3 可用性
- 安装缺失依赖
- 使用正确方式启动程序

---

## 🔍 诊断命令

如果以上方法都不行，运行诊断：

```bash
echo "=== Python 信息 ==="
which python3
python3 --version

echo ""
echo "=== pythonw3 检查 ==="
which pythonw3
pythonw3 --version

echo ""
echo "=== Tkinter 测试 ==="
python3 << 'EOF'
import tkinter as tk
root = tk.Tk()
print(f"Tk 版本: {tk.TkVersion}")
root.withdraw()
root.destroy()
print("✓ Tkinter 正常")
EOF

echo ""
echo "=== customtkinter 测试 ==="
python3 -c "import customtkinter; print(f'✓ customtkinter {customtkinter.__version__}')"
```

**将诊断结果发给开发者**，包括：
- Python 版本和路径
- pythonw3 是否存在
- Tkinter 测试结果
- 完整错误信息

---

## 📌 常见问答

**Q: 为什么 Windows 不需要 pythonw？**  
A: Windows 有 `python.exe`（命令行）和 `pythonw.exe`（GUI）两个版本，macOS 类似但命名不同。

**Q: Homebrew Python 能用吗？**  
A: 可以，但通常缺少 pythonw3。建议使用 Python.org 官方版本。

**Q: 如何知道我的 Python 来源？**  
```bash
which python3
# Homebrew: /usr/local/bin/python3 或 /opt/homebrew/bin/python3
# 官方: /Library/Frameworks/Python.framework/...
```

**Q: 能否在终端看到完整错误？**  
```bash
pythonw3 book_price_gui.py 2>&1 | tee ~/Desktop/error_log.txt
# 错误会同时显示在终端和保存到桌面的 error_log.txt
```

---

## 🆘 仍然无法解决？

联系开发者并提供：
1. `python3 --version` 输出
2. `which python3` 输出
3. `which pythonw3` 输出
4. 完整错误信息（使用上面的 `2>&1 | tee` 命令）
5. macOS 版本（系统偏好设置 → 关于本机）
