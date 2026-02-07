# 📚 书店记账本 - Mac部署指南

## ⚠️ 重要：Mac 必须使用 pythonw3

**如果程序闪退并显示 `English.lproj` 或 `Info.plist`，说明你用了 `python3` 启动！**

### ✅ 正确启动方式：
```bash
pythonw3 book_price_gui.py  # ✓ 正确
```

### ❌ 错误启动方式：
```bash
python3 book_price_gui.py   # ✗ 会闪退！
```

**原因：** macOS 的 GUI 程序需要 `pythonw3` 来正确加载 Tk 图形框架。

---

## 方法一：快速启动（推荐）⭐

### 1. 安装 Python（使用官方版本）
```bash
# 检查 pythonw3 是否存在
which pythonw3

# 如果不存在，必须从 Python.org 下载官方安装包
# 🔗 https://www.python.org/downloads/macos/
# Homebrew 的 Python 通常缺少 pythonw3！
```

### 2. 安装依赖包
```bash
pip3 install customtkinter requests pypinyin pandas openpyxl
```

### 3. 运行程序（使用 pythonw3）
```bash
cd /path/to/elsewherebooks
pythonw3 book_price_gui.py
```

完成！程序会直接启动。

---

## 方法二：一键启动脚本（最方便）

项目已包含 `启动书店记账本_Mac.command` 脚本，双击即可运行。

**如果无法双击启动，手动添加执行权限：**
```bash
cd /path/to/elsewherebooks
chmod +x 启动书店记账本_Mac.command
```

该脚本会自动：
- ✓ 检测 pythonw3 可用性（优先使用）
- ✓ 检查并安装缺失依赖
- ✓ 使用正确方式启动程序
- ✓ 自动关闭终端窗口

---

## 方法三：打包成独立应用（可选）

### 1. 安装打包工具
```bash
pip3 install pyinstaller
```

### 2. 执行打包命令
```bash
cd /path/to/MyBookCalculator

pyinstaller --name="书店记账本" \
  --windowed \
  --onefile \
  --add-data="使用指南.md:." \
  --hidden-import=PIL._tkinter_finder \
  book_price_gui.py
```

### 3. 获取应用
打包后的 `书店记账本.app` 在 `dist/` 目录，可以拖到"应用程序"文件夹

---

## 📦 需要传输的文件

将以下文件/文件夹拷贝到Mac：
- `book_price_gui.py` （主程序）
- `使用指南.md` （可选）
- `MAC部署说明.md` （本文件）

---

## � 故障诊断（程序闪退/无法启动）

如果程序启动后立即闪退，请按照以下步骤逐一排查：

### 步骤 1：检查 Python 版本
```bash
python3 --version
```
**要求：** Python 3.10 或更高版本  
**如果版本过低：** `brew install python@3.10`

### 步骤 2：检查 Tkinter 支持
```bash
python3 -c "import tkinter; print('✓ Tkinter OK')"
```
**如果报错：** 说明 Python 缺少 Tkinter 支持  
**解决方法：**
```bash
# 使用 Homebrew 重装带 Tkinter 的 Python
brew install python-tk@3.10
```

### 步骤 3：安装所有依赖
```bash
pip3 install customtkinter requests pypinyin pandas openpyxl
```

### 步骤 4：查看详细错误信息
```bash
cd /path/to/MyBookCalculator
python3 book_price_gui.py 2>&1 | head -30
```
**这会显示前 30 行错误信息，可以帮助定位具体问题**

### 常见错误及解决方案

#### ❌ ModuleNotFoundError: No module named 'customtkinter'
**原因：** 缺少依赖包  
**解决：** `pip3 install customtkinter`

#### ❌ ImportError: dlopen(): Library not loaded
**原因：** Tkinter 库损坏或缺失  
**解决：** 
```bash
brew reinstall python-tk@3.10
```

#### ❌ ValueError: unknown locale: UTF-8
**原因：** Mac 语言环境设置问题  
**解决：** 在 `~/.bash_profile` 或 `~/.zshrc` 添加：
```bash
export LC_ALL=en_US.UTF-8
export LANG=en_US.UTF-8
```
然后运行 `source ~/.zshrc` 或重启终端

#### ❌ 程序启动但无窗口显示
**原因：** 可能是信号处理问题（已在最新版本修复）  
**解决：** 更新到最新版本的 `book_price_gui.py`

### 完整诊断命令（一键排查）
```bash
#!/bin/bash
echo "=== Python 版本 ==="
python3 --version

echo -e "\n=== Tkinter 检查 ==="
python3 -c "import tkinter; print('✓ Tkinter 正常')" 2>&1

echo -e "\n=== 依赖检查 ==="
python3 -c "
try:
    import customtkinter
    print('✓ customtkinter 已安装')
except:
    print('✗ customtkinter 未安装')

try:
    import requests
    print('✓ requests 已安装')
except:
    print('✗ requests 未安装')
"

echo -e "\n=== 尝试启动程序 ==="
python3 book_price_gui.py 2>&1 | head -20
```

**将以上内容保存为 `诊断.sh`，添加执行权限后运行：**
```bash
chmod +x 诊断.sh
./诊断.sh
```

---

## 🔧 常见问题

### Q: 提示找不到customtkinter？
A: 运行 `pip3 install customtkinter requests pypinyin pandas openpyxl`

### Q: 双击.py文件没反应？
A: 使用终端执行 `python3 book_price_gui.py`

### Q: 字体显示异常？
A: Mac自带Georgia字体，应该正常显示

### Q: 数据存储在哪？
A: `~/.bookstore_data/` 目录（用户主目录下）

### Q: 如何更新程序？
A: 替换 `book_price_gui.py` 文件，数据文件会自动保留

---

## 🚀 快速开始（一键命令）

```bash
# 进入项目目录
cd /path/to/MyBookCalculator

# 安装依赖并运行
pip3 install customtkinter requests pypinyin && python3 book_price_gui.py
```

---

## 💡 提示

- 首次运行会自动创建数据目录
- 需要联网获取汇率（首次启动）
- 建议使用Python 3.10或更高版本
- 程序完全跨平台，数据格式通用
