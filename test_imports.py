#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试各个导入模块，找出导致 Mac 闪退的原因
"""

print("========== 开始测试导入 ==========")

try:
    print("1. 测试标准库...")
    import threading
    import socket
    import logging
    import signal
    import sys
    import json
    import re
    from datetime import datetime, timedelta
    from typing import Dict, Tuple, List, Set
    from pathlib import Path
    from collections import defaultdict
    print("   ✓ 标准库导入成功")
except Exception as e:
    print(f"   ✗ 标准库导入失败: {e}")
    sys.exit(1)

try:
    print("2. 测试 requests...")
    import requests
    print("   ✓ requests 导入成功")
except Exception as e:
    print(f"   ✗ requests 导入失败: {e}")

try:
    print("3. 测试 pypinyin...")
    from pypinyin import lazy_pinyin
    print("   ✓ pypinyin 导入成功")
except ImportError:
    print("   ⚠ pypinyin 未安装（非必需）")

try:
    print("4. 测试 customtkinter...")
    import customtkinter as ctk
    print("   ✓ customtkinter 导入成功")
    print(f"   版本: {ctk.__version__ if hasattr(ctk, '__version__') else '未知'}")
except Exception as e:
    print(f"   ✗ customtkinter 导入失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

try:
    print("5. 测试创建 CTk 根窗口...")
    root = ctk.CTk()
    print("   ✓ CTk 根窗口创建成功")
    root.withdraw()  # 隐藏窗口
    root.destroy()
    print("   ✓ CTk 根窗口销毁成功")
except Exception as e:
    print(f"   ✗ CTk 根窗口创建/销毁失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n========== 所有测试通过 ==========")
print("如果看到这条消息，说明所有模块导入正常。")
print("问题可能在程序的其他部分。")
