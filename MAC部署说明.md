# 📚 书店记账本 - Mac部署指南

## 方法一：直接运行（最简单）⭐

### 1. 安装Python环境
```bash
# 检查Python版本（需要3.10+）
python3 --version

# 如果没有安装，使用Homebrew安装
brew install python@3.10
```

### 2. 安装依赖包
```bash
pip3 install customtkinter requests pypinyin
```

### 3. 运行程序
```bash
cd /path/to/MyBookCalculator
python3 book_price_gui.py
```

完成！程序会直接启动。

---

## 方法二：创建桌面快捷启动

### 1. 创建启动脚本
在项目目录创建 `启动书店记账本.command` 文件：

```bash
#!/bin/bash
cd "$(dirname "$0")"
python3 book_price_gui.py
```

### 2. 添加执行权限
```bash
chmod +x 启动书店记账本.command
```

### 3. 双击运行
现在可以双击 `启动书店记账本.command` 启动程序

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

## 🔧 常见问题

### Q: 提示找不到customtkinter？
A: 运行 `pip3 install customtkinter requests pypinyin`

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
