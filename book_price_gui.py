# ============================================================
#   Project: Book Price Calculator
#   Author:  XINYULI (KELLY)
#   Version: 4.0 (UI/UX Refactored)
#   Description: Professional FX pricing tool with OOP architecture
# ============================================================

import customtkinter as ctk
import threading
import requests
import socket
import logging
import signal
import sys
from datetime import datetime
from typing import Dict, Tuple

# ---- 1. 基础设施配置 ----

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(message)s', datefmt='%H:%M:%S')
logger = logging.getLogger("Core")

class AppConfig:
    APP_NAME = "Pricing Calculator Pro"
    GEOMETRY = "500x780"
    THEME_MODE = "Dark"
    
    # 核心参数
    MARGIN_RATE = 0.15          # +15% 基础溢价
    CNY_COEFFICIENT = 0.3       # 非会员 CNY 换算系数
    RECOMMEND_DISCOUNT = 0.9    # 推荐书籍：会员额外 9 折
    
    API_URL = "https://open.er-api.com/v6/latest/AUD"
    CURRENCIES = ["JPY", "SGD", "MYR", "HKD", "TWD", "CNY", "AUD"]
    
    COLORS = {
        "PRIMARY": "#0A84FF", 
        "SECONDARY": ("#E5E5EA", "#2C2C2E"),
        "TEXT_MAIN": ("#000000", "#FFFFFF"),
        "TEXT_SUB": ("#8E8E93", "#98989D"), # 次要文字颜色
        "WARN": "#FF9F0A",
        "ERROR": "#FF453A"
    }

class RuntimeFixer:
    """系统稳定性补丁"""
    @staticmethod
    def apply_patches():
        def make_safe_destroy(cls_name):
            def safe_destroy(self):
                if hasattr(self, "_variable") and self._variable is not None:
                    try:
                        self._variable.trace_remove("write", self._trace_callback_name)
                    except Exception: pass
                super(cls_name, self).destroy()
            return safe_destroy
        ctk.CTkSwitch.destroy = make_safe_destroy(ctk.CTkSwitch)
        ctk.CTkOptionMenu.destroy = make_safe_destroy(ctk.CTkOptionMenu)

# ---- 2. 核心算法引擎 (重写) ----

class PricingEngine:
    @staticmethod
    def calculate(price: float, currency: str, is_recommend: bool, is_used: bool, rates: Dict[str, float]) -> Tuple[float, float]:
        """
        :return: (Member Price, Standard Price)
        """
        if price <= 0: return 0.0, 0.0
        
        # [逻辑分支 A] 二手书
        # 二手书通常是一口价，不涉及复杂换算，且没有会员折扣（根据行业惯例，或者你可以改为有折扣）
        if is_used:
            # 假设二手书输入的直接就是澳币卖价
            return price, price

        # [逻辑分支 B] 新书计算
        
        # 0. 汇率工具: X -> AUD
        def get_rate_to_aud(code):
            if code == "AUD": return 1.0
            return 1.0 / rates.get(code, 1.0)

        # 1. 计算【基础会员价】 (Base Member Price)
        # 公式：(原价 + 15%) -> 转为 AUD
        base_cost_native = price * (1 + AppConfig.MARGIN_RATE)
        rate_native_to_aud = get_rate_to_aud(currency)
        base_member_price_aud = base_cost_native * rate_native_to_aud

        # 2. 计算【基础非会员价】 (Base Standard Price)
        # 公式：(原价 + 15%) -> 转为 CNY -> 乘以 0.3
        # 路径：Native -> AUD -> CNY
        rate_aud_to_cny = rates.get("CNY", 1.0)
        val_in_cny = base_member_price_aud * rate_aud_to_cny
        base_standard_price_aud = val_in_cny * AppConfig.CNY_COEFFICIENT

        # 3. 应用【店长推荐】逻辑
        if is_recommend:
            # 逻辑变更点：
            # 非会员 -> 享受【基础会员价】
            final_standard = base_member_price_aud
            # 会员 -> 在【基础会员价】上再打 9 折
            final_member = base_member_price_aud * AppConfig.RECOMMEND_DISCOUNT
        else:
            # 普通情况
            final_standard = base_standard_price_aud
            final_member = base_member_price_aud

        return final_member, final_standard

# ---- 3. 服务层 ----

class ExchangeRateService:
    def __init__(self):
        self._rates = {}
        self._last_update = "等待更新..."
        self._lock = threading.Lock()

    @property
    def rates(self):
        with self._lock: return self._rates.copy()
    
    @property
    def last_update(self):
        with self._lock: return self._last_update

    def fetch_async(self, on_done, ctx):
        def task():
            try:
                socket.create_connection(("1.1.1.1", 53), timeout=3)
                resp = requests.get(AppConfig.API_URL, timeout=10)
                if resp.json().get("result") != "success": raise ValueError("API Error")
                with self._lock:
                    self._rates = resp.json()["rates"]
                    self._last_update = datetime.now().strftime("%H:%M")
                ctx.after(0, lambda: on_done(True, "同步成功"))
            except Exception as e:
                ctx.after(0, lambda: on_done(False, str(e)))
        threading.Thread(target=task, daemon=True).start()

# ---- 4. UI 组件 ----

class BookCardView(ctk.CTkFrame):
    def __init__(self, parent, on_change, on_delete, default_price="", is_used=False):
        super().__init__(parent, fg_color=AppConfig.COLORS["SECONDARY"], corner_radius=8)
        self.on_change = on_change
        self._is_used = is_used
        self.grid_columnconfigure(1, weight=1)

        # 货币
        self.curr_var = ctk.StringVar(value="AUD" if is_used else "JPY")
        self.curr_menu = ctk.CTkOptionMenu(
            self, variable=self.curr_var, values=AppConfig.CURRENCIES,
            width=75, height=28, fg_color=AppConfig.COLORS["SECONDARY"], # 实体颜色防崩
            button_color=("gray70", "gray30"), text_color=AppConfig.COLORS["TEXT_MAIN"],
            command=self._notify
        )
        self.curr_menu.grid(row=0, column=0, padx=(10, 5), pady=10)

        # 价格
        self.price_var = ctk.StringVar(value=str(default_price))
        self.price_var.trace_add("write", self._notify)
        ctk.CTkEntry(
            self, textvariable=self.price_var, width=100, height=28,
            placeholder_text="0.00", border_width=0, fg_color=("white", "gray20")
        ).grid(row=0, column=1, padx=5, sticky="ew")

        # 推荐/二手
        self.rec_var = ctk.BooleanVar(value=False)
        if is_used:
            ctk.CTkLabel(self, text="USED", text_color=AppConfig.COLORS["WARN"], font=("Arial", 11, "bold")).grid(row=0, column=2, padx=10)
        else:
            ctk.CTkSwitch(
                self, text="Rec", variable=self.rec_var, command=self._notify,
                width=60, height=20, font=("Arial", 11), progress_color=AppConfig.COLORS["PRIMARY"]
            ).grid(row=0, column=2, padx=10)

        # 删除
        ctk.CTkButton(
            self, text="×", width=30, height=28, fg_color="transparent", 
            hover_color=("gray80", "gray25"), text_color="gray50", font=("Arial", 18),
            command=lambda: on_delete(self)
        ).grid(row=0, column=3, padx=(0, 5))

    def _notify(self, *args): self.on_change()
    def get_data(self):
        try: p = float(self.price_var.get())
        except: p = 0.0
        return { "price": p, "currency": self.curr_var.get(), "is_recommend": self.rec_var.get(), "is_used": self._is_used }

class DashboardView(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color=AppConfig.COLORS["SECONDARY"], corner_radius=12, height=100)
        self.pack_propagate(False)
        self.grid_columnconfigure((0, 1), weight=1)
        
        self._make_box(0, "MEMBER PRICE", 28, AppConfig.COLORS["PRIMARY"], "lbl_mem")
        self._make_box(1, "STANDARD", 20, AppConfig.COLORS["TEXT_SUB"], "lbl_std")

    def _make_box(self, col, title, size, color, attr):
        f = ctk.CTkFrame(self, fg_color="transparent")
        f.grid(row=0, column=col, padx=20, sticky="w" if col==0 else "e")
        ctk.CTkLabel(f, text=title, font=("Arial", 10, "bold"), text_color="gray50").pack(anchor="w" if col==0 else "e")
        lbl = ctk.CTkLabel(f, text="$0.00", font=("Arial", size, "bold"), text_color=color)
        lbl.pack(anchor="w" if col==0 else "e")
        setattr(self, attr, lbl)

    def update(self, mem, std):
        self.lbl_mem.configure(text=f"${mem:,.2f}")
        self.lbl_std.configure(text=f"${std:,.2f}")

# ---- 5. 主程序 ----

class Application(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title(AppConfig.APP_NAME)
        self.geometry(AppConfig.GEOMETRY)
        ctk.set_appearance_mode(AppConfig.THEME_MODE)
        self.service = ExchangeRateService()
        self.rows = []
        self._setup_ui()
        self.after(500, self.refresh_data)

    def _setup_ui(self):
        # Header
        h = ctk.CTkFrame(self, fg_color="transparent")
        h.pack(fill="x", padx=20, pady=20)
        ctk.CTkLabel(h, text="Pricing Calc", font=("Arial", 24, "bold")).pack(side="left")
        self.status = ctk.CTkLabel(h, text="Ready", text_color="gray50")
        self.status.pack(side="right", padx=10)
        self.btn_ref = ctk.CTkButton(h, text="↻", width=30, fg_color="transparent", border_width=1, text_color="gray", command=self.refresh_data)
        self.btn_ref.pack(side="right")

        # Scroll
        self.scroll = ctk.CTkScrollableFrame(self, fg_color="transparent", label_text="ITEMS", label_font=("Arial", 12, "bold"))
        self.scroll.pack(fill="both", expand=True, padx=15)
        self.empty = ctk.CTkLabel(self.scroll, text="No books added", text_color="gray40")
        self.empty.pack(pady=40)

        # Footer
        f = ctk.CTkFrame(self, fg_color="transparent")
        f.pack(fill="x", padx=15, pady=15)
        b = ctk.CTkFrame(f, fg_color="transparent")
        b.pack(fill="x", pady=(0, 15))
        ctk.CTkButton(b, text="+ New Book", height=40, fg_color=AppConfig.COLORS["PRIMARY"], font=("Arial", 14, "bold"), command=self.add_new).pack(side="left", expand=True, fill="x", padx=(0,5))
        ctk.CTkButton(b, text="+ Used $5", height=40, width=80, fg_color="transparent", border_width=1, text_color=AppConfig.COLORS["TEXT_MAIN"], command=lambda: self.add_used(5)).pack(side="left")
        self.dash = DashboardView(f)
        self.dash.pack(fill="x")

    def refresh_data(self):
        self.status.configure(text="Updating...", text_color=AppConfig.COLORS["WARN"])
        self.btn_ref.configure(state="disabled")
        self.service.fetch_async(self._on_done, self)

    def _on_done(self, ok, msg):
        self.btn_ref.configure(state="normal")
        self.status.configure(text=msg if not ok else f"Updated {self.service.last_update}", text_color=AppConfig.COLORS["TEXT_SUB"] if ok else "red")
        self.recalc()

    def add_new(self): self._add_row()
    def add_used(self, p): self._add_row(str(p), True)

    def _add_row(self, p="", used=False):
        if not self.rows: self.empty.pack_forget()
        r = BookCardView(self.scroll, self.recalc, self._del_row, p, used)
        r.pack(fill="x", pady=4)
        self.rows.append(r)
        self.recalc()

    def _del_row(self, r):
        r.destroy()
        if r in self.rows: self.rows.remove(r)
        if not self.rows: self.empty.pack(pady=40)
        self.recalc()

    def recalc(self):
        t_mem, t_std = 0.0, 0.0
        rates = self.service.rates
        for r in self.rows:
            d = r.get_data()
            m, s = PricingEngine.calculate(d["price"], d["currency"], d["is_recommend"], d["is_used"], rates)
            t_mem += m
            t_std += s
        self.dash.update(t_mem, t_std)

if __name__ == "__main__":
    RuntimeFixer.apply_patches()
    signal.signal(signal.SIGINT, lambda s, f: sys.exit(0))
    Application().mainloop()