# ============================================================
#   Project: Integra Book Price Calculator Pro (Engineering Edition)
#   Author:  XINYULI (KELLY)
#   Version: 3.0 (UI/UX Refactored)
#   Description: Professional FX pricing tool with OOP architecture
# ============================================================

import tkinter as tk
from tkinter import ttk, messagebox
import requests
import socket
import threading
from datetime import datetime

# ---- 配置常量 ----
CONFIG = {
    "SUPPORTED_CURRENCIES": ("JPY", "SGD", "MYR", "HKD", "TWD", "CNY", "AUD"),
    "DEFAULT_MARGIN": 0.15,
    "API_URL": "https://open.er-api.com/v6/latest/AUD",
    "COLORS": {
        "ACCENT": "#007AFF",       # 苹果蓝
        "STANDARD": "#333333",     # 深黑
        "BG": "#F2F2F7",           # 整体背景
        "CARD_BG": "#FFFFFF",      # 卡片白
        "TEXT_GRAY": "#86868B",
        "SUCCESS": "#34C759",
        "ERROR": "#FF3B30",
        "TICKET_BG": "#E5E5EA"     # 结果区背景
    }
}

class ExchangeRateService:
    """服务层：负责网络请求"""
    def __init__(self):
        self.rates = {}
        self.last_update = "未更新"
        self.is_loading = False

    def check_internet(self, host="8.8.8.8", port=53, timeout=3):
        try:
            socket.setdefaulttimeout(timeout)
            socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
            return True
        except Exception:
            return False

    def fetch_rates(self, callback_success, callback_error):
        if self.is_loading: return
        self.is_loading = True
        
        def task():
            try:
                if not self.check_internet():
                    raise ConnectionError("网络不可用")
                
                resp = requests.get(CONFIG["API_URL"], timeout=10)
                resp.raise_for_status()
                data = resp.json()
                
                if data.get("result") != "success":
                    raise ValueError(f"API异常: {data}")

                self.rates = data["rates"]
                utc_time = data.get("time_last_update_utc", "")
                self.last_update = utc_time[:19] if utc_time else datetime.now().strftime("%Y-%m-%d %H:%M")
                callback_success()
            except Exception as e:
                callback_error(str(e))
            finally:
                self.is_loading = False

        threading.Thread(target=task, daemon=True).start()

    def get_cross_rate(self, from_curr, to_curr):
        if not self.rates: return 0.0
        if from_curr == to_curr: return 1.0
        rate_from_to_aud = 1.0 if from_curr == "AUD" else (1.0 / self.rates.get(from_curr, 1.0))
        rate_aud_to_to = 1.0 if to_curr == "AUD" else self.rates.get(to_curr, 1.0)
        return rate_from_to_aud * rate_aud_to_to

class BookRow(ttk.Frame):
    """组件层：单行书籍UI"""
    def __init__(self, parent, on_change_callback, on_delete_callback, default_price="", is_used=False):
        super().__init__(parent)
        self.on_change = on_change_callback
        self.is_used = is_used
        self.columnconfigure(2, weight=1) 
        
        self.var_currency = tk.StringVar(value="AUD" if is_used else "JPY")
        self.cb_currency = ttk.Combobox(
            self, textvariable=self.var_currency, 
            values=CONFIG["SUPPORTED_CURRENCIES"], 
            width=5, state="readonly"
        )
        self.cb_currency.pack(side="left", padx=(0, 5))
        self.cb_currency.bind("<<ComboboxSelected>>", self._trigger_change)

        self.var_price = tk.StringVar(value=str(default_price))
        self.var_price.trace_add("write", self._trigger_change)
        vcmd = (self.register(self._validate_number), '%P')
        self.entry_price = ttk.Entry(
            self, textvariable=self.var_price, width=10, 
            validate="key", validatecommand=vcmd,
            state="readonly" if is_used else "normal"
        )
        self.entry_price.pack(side="left", padx=5)

        if is_used:
            ttk.Label(self, text="[二手]", foreground=CONFIG["COLORS"]["TEXT_GRAY"]).pack(side="left", padx=5)
            self.var_recommend = tk.BooleanVar(value=False)
        else:
            self.var_recommend = tk.BooleanVar(value=False)
            self.chk_recommend = ttk.Checkbutton(
                self, text="推荐", variable=self.var_recommend, 
                command=self._trigger_change
            )
            self.chk_recommend.pack(side="left", padx=5)

        self.btn_del = ttk.Button(self, text="×", width=3, command=lambda: on_delete_callback(self))
        self.btn_del.pack(side="right", padx=5)

    def _validate_number(self, new_value):
        if new_value == "": return True
        try:
            float(new_value)
            return True
        except ValueError:
            return False

    def _trigger_change(self, *args):
        self.on_change()

    def get_data(self):
        try: price = float(self.var_price.get())
        except ValueError: price = 0.0
        return {
            "currency": self.var_currency.get(),
            "price": price,
            "is_recommend": self.var_recommend.get(),
            "is_used": self.is_used
        }

class BookPriceApp(tk.Tk):
    """主程序控制器"""
    def __init__(self):
        super().__init__()
        self.title("📚 书价计算器 Pro | Dev: XINYULI(KELLY)")
        self.geometry("500x600") 
        self.configure(bg=CONFIG["COLORS"]["BG"])
        
        self.service = ExchangeRateService()
        self.rows = []

        self._setup_styles()
        self._build_ui()
        
        # 启动逻辑
        self.after(500, self.refresh_rates_action)
        self._update_ui_state()

    def _setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        
        # 基础样式
        style.configure("TFrame", background=CONFIG["COLORS"]["BG"])
        style.configure("TLabel", background=CONFIG["COLORS"]["BG"], foreground="#333", font=("Microsoft YaHei", 10))
        
        # 结果区样式 (Ticket Style)
        style.configure("Ticket.TFrame", background=CONFIG["COLORS"]["TICKET_BG"], relief="flat")
        style.configure("Ticket.TLabel", background=CONFIG["COLORS"]["TICKET_BG"], font=("Consolas", 9), foreground="#555")
        
        # 价格大数字
        style.configure("PriceMem.TLabel", font=("Microsoft YaHei", 22, "bold"), background=CONFIG["COLORS"]["TICKET_BG"], foreground=CONFIG["COLORS"]["ACCENT"])
        style.configure("PriceStd.TLabel", font=("Microsoft YaHei", 18, "bold"), background=CONFIG["COLORS"]["TICKET_BG"], foreground=CONFIG["COLORS"]["STANDARD"])
        style.configure("LabelMem.TLabel", font=("Microsoft YaHei", 9), background=CONFIG["COLORS"]["TICKET_BG"], foreground=CONFIG["COLORS"]["ACCENT"])
        style.configure("LabelStd.TLabel", font=("Microsoft YaHei", 9), background=CONFIG["COLORS"]["TICKET_BG"], foreground="#666")

        # 空状态
        style.configure("Empty.TLabel", font=("Microsoft YaHei", 11), foreground=CONFIG["COLORS"]["TEXT_GRAY"])

    def _build_ui(self):
        # 1. 顶部操作栏
        top_bar = ttk.Frame(self, padding=(10, 10, 10, 5))
        top_bar.pack(fill="x", side="top")
        
        btn_frame = ttk.Frame(top_bar)
        btn_frame.pack(side="left")
        ttk.Button(btn_frame, text="+ 新书", command=self.add_row_action).pack(side="left", padx=(0,5))
        ttk.Button(btn_frame, text="+ 二手 $5", command=lambda: self.add_used_book(5)).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="+ 二手 $10", command=lambda: self.add_used_book(10)).pack(side="left", padx=5)

        self.btn_refresh = ttk.Button(top_bar, text="🔄", width=3, command=self.refresh_rates_action)
        self.btn_refresh.pack(side="right")

        # 2. 状态栏
        self.status_bar = ttk.Label(self, text="系统初始化...", font=("Microsoft YaHei", 8), foreground="#999", padding=(10, 0, 10, 5))
        self.status_bar.pack(fill="x", side="top")

        # 3. 结果展示区 (Ticket Area) - 放在底部
        self.result_container = ttk.Frame(self, style="Ticket.TFrame", padding=15)
        self.result_container.pack(fill="x", side="bottom")

        # 3.1 明细 (Details)
        self.lbl_details = ttk.Label(self.result_container, text="", style="Ticket.TLabel", justify="left")
        self.lbl_details.pack(fill="x", pady=(0, 10))
        
        # 3.2 总价对比 (Dashboard)
        self.total_frame = ttk.Frame(self.result_container, style="Ticket.TFrame")
        self.total_frame.pack(fill="x")
        self.total_frame.columnconfigure(0, weight=1)
        self.total_frame.columnconfigure(1, weight=1)

        # 左侧：会员
        f_left = ttk.Frame(self.total_frame, style="Ticket.TFrame")
        f_left.grid(row=0, column=0, sticky="w")
        ttk.Label(f_left, text="会员总价", style="LabelMem.TLabel").pack(anchor="w")
        self.lbl_total_member = ttk.Label(f_left, text="$0.00", style="PriceMem.TLabel")
        self.lbl_total_member.pack(anchor="w")

        # 右侧：标准
        f_right = ttk.Frame(self.total_frame, style="Ticket.TFrame")
        f_right.grid(row=0, column=1, sticky="e")
        ttk.Label(f_right, text="非会员 / 标准价", style="LabelStd.TLabel").pack(anchor="e")
        self.lbl_total_non_member = ttk.Label(f_right, text="$0.00", style="PriceStd.TLabel")
        self.lbl_total_non_member.pack(anchor="e")

        # 4. 列表滚动区
        list_container = ttk.Frame(self, padding=10)
        list_container.pack(fill="both", expand=True)
        
        self.canvas = tk.Canvas(list_container, bg=CONFIG["COLORS"]["BG"], highlightthickness=0)
        scrollbar = ttk.Scrollbar(list_container, orient="vertical", command=self.canvas.yview)
        
        self.scrollable_frame = ttk.Frame(self.canvas, style="TFrame")
        self.scrollable_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas_window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        
        self.canvas.bind("<Configure>", lambda e: self.canvas.itemconfig(self.canvas_window, width=e.width))
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # 空状态文字
        self.lbl_empty = ttk.Label(
            self.scrollable_frame, 
            text="尚未添加书籍...", 
            style="Empty.TLabel"
        )

    # ---- 交互逻辑 ----
    def _update_ui_state(self):
        """控制空状态和结果区的显示"""
        if not self.rows:
            self.lbl_empty.pack(pady=50, padx=10)
            self.result_container.pack_forget()
        else:
            self.lbl_empty.pack_forget()
            self.result_container.pack(fill="x", side="bottom")

    def refresh_rates_action(self):
        self.btn_refresh.configure(state="disabled")
        self.status_bar.configure(text="正在更新汇率...", foreground="#FF9500")
        self.service.fetch_rates(self._on_rate_success, self._on_rate_error)

    def _on_rate_success(self):
        self.btn_refresh.configure(state="normal")
        self.status_bar.configure(text=f"汇率已更新 ({self.service.last_update})", foreground=CONFIG["COLORS"]["SUCCESS"])
        self.calculate_all()

    def _on_rate_error(self, error_msg):
        self.btn_refresh.configure(state="normal")
        self.status_bar.configure(text=f"离线模式 - {error_msg}", foreground=CONFIG["COLORS"]["ERROR"])

    def add_row_action(self):
        row = BookRow(self.scrollable_frame, self.calculate_all, self.remove_row_action)
        row.pack(fill="x", pady=2)
        self.rows.append(row)
        self._update_ui_state()
        self.calculate_all()

    def add_used_book(self, price):
        row = BookRow(self.scrollable_frame, self.calculate_all, self.remove_row_action, default_price=price, is_used=True)
        row.pack(fill="x", pady=2)
        self.rows.append(row)
        self._update_ui_state()
        self.calculate_all()

    def remove_row_action(self, row_instance):
        row_instance.destroy()
        if row_instance in self.rows:
            self.rows.remove(row_instance)
        self._update_ui_state()
        self.calculate_all()

    def calculate_all(self):
        if not self.service.rates:
            self.status_bar.configure(text="等待汇率数据...", foreground=CONFIG["COLORS"]["ERROR"])
            return

        total_member = 0.0
        total_non_member = 0.0
        details_text = []
        has_valid_data = False

        for row in self.rows:
            data = row.get_data()
            price = data["price"]
            currency = data["currency"]
            
            if price <= 0: continue
            has_valid_data = True

            # --- 核心计算逻辑 ---
            if currency == "AUD":
                std_mem = price
                std_non = price
            else:
                base = price * (1 + CONFIG["DEFAULT_MARGIN"])
                std_mem = base * self.service.get_cross_rate(currency, "AUD")
                std_non = base * self.service.get_cross_rate(currency, "CNY") * 0.3

            if data["is_recommend"]:
                fin_mem = std_mem * 0.9
                fin_non = std_mem
                tag = " [荐]" 
            else:
                fin_mem = std_mem
                fin_non = std_non
                tag = ""
            # ------------------
            
            details_text.append(f"{currency} {price:>6g} ➜ 会${fin_mem:>6.2f}{tag}")
            total_member += fin_mem
            total_non_member += fin_non

        if has_valid_data:
            self.lbl_details.configure(text="\n".join(details_text))
            self.lbl_total_member.configure(text=f"${total_member:.2f}")
            self.lbl_total_non_member.configure(text=f"${total_non_member:.2f}")
            # 确保结果区可见
            self.result_container.pack(fill="x", side="bottom")
            self.lbl_details.pack(fill="x", pady=(0, 10))
        else:
            self.lbl_details.pack_forget() 
            self.lbl_total_member.configure(text="$0.00")
            self.lbl_total_non_member.configure(text="$0.00")

if __name__ == "__main__":
    app = BookPriceApp()
    app.mainloop()