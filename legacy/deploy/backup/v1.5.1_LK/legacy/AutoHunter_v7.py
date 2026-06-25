import tkinter as tk
from tkinter import ttk, messagebox
import cv2
import numpy as np
import mss
import pyautogui
import time
import random
import keyboard
import threading
import json
import os
import ctypes
import winsound
from PIL import Image, ImageTk

# 설정 파일 경로
CONFIG_FILE = "hunter_premium_v7_0_config.json"

# --- DPI 보정 ---
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except:
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except:
        pass

class AutoHunterV7_0:
    def __init__(self, root):
        self.root = root
        self.root.title("AutoHunter Premium v7.1")
        # 창 크기를 950으로 늘려 잘림 방지 (스크롤바 제외)
        self.root.geometry("450x950")
        self.root.configure(bg="#0f172a") 
        self.root.attributes("-topmost", True)
        
        self.is_running = False
        self.is_previewing = True
        self.is_anti_macro_working = False
        self.is_selling = False
        
        # 기본 변수 초기화
        self.last_screenshot_time = time.time()
        self.screenshot_interval_sec = 15 * 60
        self.SCREENSHOT_DIR = "screenshots"
        if not os.path.exists(self.SCREENSHOT_DIR): os.makedirs(self.SCREENSHOT_DIR)
        
        self.last_sell_time = time.time()
        self.shop_npc_pos = [0, 0]
        self.shop_sell_btn_pos = [0, 0]

        # 기본 키 설정
        self.KEY_ATTACK = tk.StringVar(value="end")
        self.KEY_DASH = tk.StringVar(value="space")
        self.KEY_JUMP = tk.StringVar(value="alt")
        self.KEY_PETFOOD = tk.StringVar(value="del")
        self.KEY_SHOP = tk.StringVar(value="m")
        
        # 인식 범위 및 정밀도 (80% 적용)
        self.base_lower = np.array([245, 230, 0]); self.base_upper = np.array([254, 255, 129])
        self.anti_lower = np.array([0, 0, 220]); self.anti_upper = np.array([180, 30, 255])
        
        # UI 및 제어 변수
        self.profiles_data = {}
        self.current_profile_name = tk.StringVar(value="기본 사냥터")
        self.reg_t = tk.IntVar(value=100); self.reg_l = tk.IntVar(value=100)
        self.reg_w = tk.IntVar(value=200); self.reg_h = tk.IntVar(value=150)
        self.x_min = tk.IntVar(value=20); self.x_max = tk.IntVar(value=180)
        self.color_margin = tk.IntVar(value=60) 
        self.attack_delay_ms = tk.IntVar(value=500); self.dash_delay_ms = tk.IntVar(value=1500)
        self.use_dash = tk.BooleanVar(value=True); self.use_anti_macro = tk.BooleanVar(value=True)
        self.use_sound_alert = tk.BooleanVar(value=True)
        self.hunt_mode = tk.IntVar(value=0) 
        self.stationary_range = tk.IntVar(value=5)
        self.use_periodic = tk.BooleanVar(value=True); self.periodic_interval_min = tk.IntVar(value=5)
        self.always_on_top = tk.BooleanVar(value=True)
        self.ui_opacity = tk.DoubleVar(value=1.0)
        self.ui_scale = tk.DoubleVar(value=1.1)
        
        # 자동 판매 설정
        self.use_auto_sell = tk.BooleanVar(value=False)
        self.sell_interval_min = tk.IntVar(value=15)
        self.sell_img_files = {"icon": "sell1.png", "btn_sell": "sell2.png", "btn_conf": "sell3.png", "btn_exit": "sell4.png"}

        self.setup_styles()
        self.setup_ui()
        self.load_all_profiles()
        
        threading.Thread(target=self.monitor_loop, daemon=True).start()
        threading.Thread(target=self.anti_macro_loop, daemon=True).start()
        keyboard.add_hotkey('f12', self.toggle_running_from_key)
        keyboard.add_hotkey('f11', self.run_manual_sell)

    def setup_styles(self):
        s = self.ui_scale.get()
        style = ttk.Style(); style.theme_use('clam')
        bg_main, bg_card, accent = "#0f172a", "#1e293b", "#0ea5e9"

        style.configure("TFrame", background=bg_main)
        style.configure("TNotebook", background=bg_main, borderwidth=0)
        style.configure("TNotebook.Tab", background=bg_card, foreground="#94a3b8", padding=[int(15*s), int(8*s)], font=("Malgun Gothic", int(9*s), "bold"))
        style.map("TNotebook.Tab", background=[("selected", accent)], foreground=[("selected", "white")])
        style.configure("TLabelframe", background=bg_main, foreground=accent, bordercolor=bg_card)
        style.configure("TLabelframe.Label", foreground=accent, font=("Malgun Gothic", int(9*s), "bold"))
        style.configure("TLabel", background=bg_main, foreground="#f1f5f9", font=("Malgun Gothic", int(9*s)))
        style.configure("TButton", background=bg_card, foreground="white", font=("Malgun Gothic", int(8*s), "bold"), borderwidth=0)
        style.map("TButton", background=[('active', accent)])
        style.configure("TCombobox", fieldbackground=bg_card, background=bg_card, foreground="white", font=("Malgun Gothic", int(8*s)))

    def setup_ui(self):
        for child in self.root.winfo_children(): child.destroy()
        s = self.ui_scale.get()
        self.root.geometry(f"{int(450*s)}x{int(950*s)}")

        # --- 상단 프로필 바 ---
        top_bar = tk.Frame(self.root, bg="#1e293b", height=int(55*s)); top_bar.pack(fill=tk.X, padx=10, pady=10)
        self.profile_combo = ttk.Combobox(top_bar, textvariable=self.current_profile_name, width=15); self.profile_combo.pack(side=tk.LEFT, padx=10, pady=12)
        self.profile_combo.bind("<<ComboboxSelected>>", self.on_profile_change)
        tk.Button(top_bar, text="SAVE", bg="#10b981", fg="white", font=("Malgun Gothic", int(8*s), "bold"), relief=tk.FLAT, command=self.save_current_profile, padx=8).pack(side=tk.LEFT, padx=5)
        self.start_btn = tk.Button(top_bar, text="START (F12)", bg="#0ea5e9", fg="white", font=("Malgun Gothic", int(9*s), "bold"), command=self.toggle_running, relief=tk.FLAT, padx=12)
        self.start_btn.pack(side=tk.RIGHT, padx=10)

        # --- 탭 시스템 ---
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.X, padx=10, pady=5)

        # 1. MONITOR 탭
        self.tab_main = ttk.Frame(self.notebook); self.notebook.add(self.tab_main, text=" MONITOR ")
        self.preview_frame = tk.Frame(self.tab_main, bg="#020617", bd=2, relief=tk.RIDGE); self.preview_frame.pack(fill=tk.X, padx=10, pady=10)
        self.preview_label = tk.Label(self.preview_frame, text="MINIMAP WAITING", bg="#020617", fg="#334155", height=int(12*s)); self.preview_label.pack(fill=tk.BOTH, expand=True)
        
        btn_grid = tk.Frame(self.tab_main, bg="#0f172a"); btn_grid.pack(fill=tk.X, padx=10)
        tk.Button(btn_grid, text="DRAG SELECT", bg="#334155", fg="white", font=("Malgun Gothic", int(8*s)), relief=tk.FLAT, command=self.open_selector).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)
        tk.Button(btn_grid, text="COORD(F1/F2)", bg="#334155", fg="white", font=("Malgun Gothic", int(8*s)), relief=tk.FLAT, command=self.start_coord_detection).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)
        
        mode_f = ttk.LabelFrame(self.tab_main, text=" HUNTING MODE "); mode_f.pack(fill=tk.X, padx=10, pady=10)
        ttk.Radiobutton(mode_f, text="Move", variable=self.hunt_mode, value=0).pack(side=tk.LEFT, padx=15, pady=8)
        ttk.Radiobutton(mode_f, text="Fixed", variable=self.hunt_mode, value=1).pack(side=tk.LEFT, padx=15, pady=8)
        ttk.Checkbutton(mode_f, text="Alert", variable=self.use_sound_alert).pack(side=tk.RIGHT, padx=15)

        range_f = ttk.LabelFrame(self.tab_main, text=" X-RANGE (PIXELS) "); range_f.pack(fill=tk.X, padx=10, pady=5)
        for lbl, var in [("MIN:", self.x_min), ("MAX:", self.x_max)]:
            row = tk.Frame(range_f, bg="#0f172a"); row.pack(fill=tk.X, padx=10, pady=4)
            tk.Label(row, text=lbl, bg="#0f172a", fg="#94a3b8", width=5).pack(side=tk.LEFT)
            ttk.Scale(row, from_=0, to=400, variable=var).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)
            tk.Entry(row, textvariable=var, width=5, bg="#1e293b", fg="white", borderwidth=0).pack(side=tk.RIGHT)

        # 2. SKILLS 탭
        self.tab_skill = ttk.Frame(self.notebook); self.notebook.add(self.tab_skill, text=" SKILLS ")
        s_group = ttk.LabelFrame(self.tab_skill, text=" DELAYS & VALUES "); s_group.pack(fill=tk.X, padx=10, pady=10)
        for label, var, min_v, max_v in [("Attack(ms):", self.attack_delay_ms, 100, 3000), ("Move(ms):", self.dash_delay_ms, 100, 10000), ("Pet(min):", self.periodic_interval_min, 1, 60), ("Margin:", self.color_margin, 0, 150)]:
            f = tk.Frame(s_group, bg="#0f172a"); f.pack(fill=tk.X, pady=6, padx=10)
            tk.Label(f, text=label, bg="#0f172a", fg="#f1f5f9", width=12, anchor=tk.W).pack(side=tk.LEFT)
            ttk.Scale(f, from_=min_v, to=max_v, variable=var).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)
            tk.Entry(f, textvariable=var, width=6, bg="#1e293b", fg="white", borderwidth=0).pack(side=tk.RIGHT)

        k_group = ttk.LabelFrame(self.tab_skill, text=" KEY BINDINGS "); k_group.pack(fill=tk.X, padx=10, pady=5)
        keys_list = ["space", "ctrl", "alt", "shift", "insert", "del", "home", "end", "pgup", "pgdn", "enter", "tab", "esc", "up", "down", "left", "right"] + list("abcdefghijklmnopqrstuvwxyz") + [str(i) for i in range(10)]
        for lbl, var in [("ATT:", self.KEY_ATTACK), ("MOV:", self.KEY_DASH), ("JMP:", self.KEY_JUMP), ("PET:", self.KEY_PETFOOD)]:
            f = tk.Frame(k_group, bg="#0f172a"); f.pack(side=tk.LEFT, expand=True, pady=8)
            tk.Label(f, text=lbl, bg="#0f172a", fg="#38bdf8", font=("Malgun Gothic", int(7*s), "bold")).pack()
            ttk.Combobox(f, textvariable=var, values=keys_list, width=6).pack()

        # 3. ADVANCED 탭
        self.tab_extra = ttk.Frame(self.notebook); self.notebook.add(self.tab_extra, text=" ADVANCED ")
        sell_f = ttk.LabelFrame(self.tab_extra, text=" AUTO SELL (F11) "); sell_f.pack(fill=tk.X, padx=10, pady=10)
        ttk.Checkbutton(sell_f, text="Enable Periodic Sell", variable=self.use_auto_sell).pack(anchor=tk.W, padx=10, pady=8)
        f_s1 = tk.Frame(sell_f, bg="#0f172a"); f_s1.pack(fill=tk.X, padx=10, pady=4)
        tk.Label(f_s1, text="Interval:", bg="#0f172a", fg="white").pack(side=tk.LEFT)
        ttk.Scale(f_s1, from_=10, to=30, variable=self.sell_interval_min).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)
        tk.Entry(f_s1, textvariable=self.sell_interval_min, width=4, bg="#1e293b", fg="white", borderwidth=0).pack(side=tk.RIGHT)
        cap_grid = tk.Frame(sell_f, bg="#0f172a"); cap_grid.pack(fill=tk.X, padx=5, pady=12)
        for i, (name, target) in enumerate([("SHOP ICON", "icon"), ("BATCH SELL", "btn_sell"), ("CONFIRM", "btn_conf"), ("EXIT BTN", "btn_exit")]):
            tk.Button(cap_grid, text=name, bg="#334155", fg="white", font=("Malgun Gothic", int(7*s), "bold"), relief=tk.FLAT, command=lambda t=target: self.capture_sell_img(t)).grid(row=i//2, column=i%2, sticky="nsew", padx=3, pady=3)
        cap_grid.columnconfigure(0, weight=1); cap_grid.columnconfigure(1, weight=1)

        ui_f = ttk.LabelFrame(self.tab_extra, text=" UI SETTINGS "); ui_f.pack(fill=tk.X, padx=10, pady=5)
        f_sc = tk.Frame(ui_f, bg="#0f172a"); f_sc.pack(fill=tk.X, padx=10, pady=8)
        tk.Label(f_sc, text="UI Scale:", bg="#0f172a", fg="white").pack(side=tk.LEFT)
        sc_cb = ttk.Combobox(f_sc, textvariable=self.ui_scale, values=[0.8, 1.0, 1.1, 1.25, 1.5], width=6)
        sc_cb.pack(side=tk.LEFT, padx=10); sc_cb.bind("<<ComboboxSelected>>", lambda e: self.rescale_ui())
        f_op = tk.Frame(ui_f, bg="#0f172a"); f_op.pack(fill=tk.X, padx=10, pady=4)
        tk.Label(f_op, text="Opacity:", bg="#0f172a", fg="white").pack(side=tk.LEFT); ttk.Scale(f_op, from_=0.3, to=1.0, variable=self.ui_opacity, command=lambda x: self.update_ui_settings()).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)

        # 로그 영역
        self.log_text = tk.Text(self.root, height=int(8*s), bg="#020617", fg="#64748b", borderwidth=0, font=("Consolas", int(9*s)), padx=10, pady=10)
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def log(self, msg):
        self.log_text.config(state=tk.NORMAL); self.log_text.insert(tk.END, f"[{time.strftime('%H:%M:%S')}] {msg}\n"); self.log_text.see(tk.END); self.log_text.config(state=tk.DISABLED)

    def update_ui_settings(self):
        self.root.attributes("-topmost", self.always_on_top.get()); self.root.attributes("-alpha", self.ui_opacity.get())

    def open_selector(self):
        self.selector = tk.Toplevel(self.root); self.selector.attributes("-alpha", 0.3); self.selector.attributes("-fullscreen", True); self.selector.attributes("-topmost", True); self.selector.config(cursor="cross")
        self.sel_canvas = tk.Canvas(self.selector, cursor="cross", bg="grey"); self.sel_canvas.pack(fill="both", expand=True)
        self.start_x = None; self.start_y = None; self.rect = None
        self.sel_canvas.bind("<ButtonPress-1>", self.on_sel_press); self.sel_canvas.bind("<B1-Motion>", self.on_sel_drag); self.sel_canvas.bind("<ButtonRelease-1>", self.on_sel_release)

    def on_sel_press(self, e): self.start_x, self.start_y = e.x, e.y; self.rect = self.sel_canvas.create_rectangle(e.x, e.y, e.x, e.y, outline="#0ea5e9", width=3)
    def on_sel_drag(self, e): self.sel_canvas.coords(self.rect, self.start_x, self.start_y, e.x, e.y)
    def on_sel_release(self, e):
        w, h = abs(e.x - self.start_x), abs(e.y - self.start_y)
        if w > 5: self.reg_l.set(min(self.start_x, e.x)); self.reg_t.set(min(self.start_y, e.y)); self.reg_w.set(w); self.reg_h.set(h); self.x_max.set(w-15); self.log(f"REGION SET: {w}x{h}")
        self.selector.destroy()

    def capture_sell_img(self, target):
        self.selector = tk.Toplevel(self.root); self.selector.attributes("-alpha", 0.3); self.selector.attributes("-fullscreen", True); self.selector.attributes("-topmost", True); self.selector.config(cursor="cross")
        self.sel_canvas = tk.Canvas(self.selector, cursor="cross", bg="grey"); self.sel_canvas.pack(fill="both", expand=True)
        self.start_x = None; self.start_y = None; self.rect = None
        self.sel_canvas.bind("<ButtonPress-1>", self.on_sel_press); self.sel_canvas.bind("<B1-Motion>", self.on_sel_drag); self.sel_canvas.bind("<ButtonRelease-1>", lambda e: self.on_sell_capture_release(e, target))

    def on_sell_capture_release(self, e, target):
        w, h = abs(e.x - self.start_x), abs(e.y - self.start_y)
        if w > 2 and h > 2:
            left, top = min(self.start_x, e.x), min(self.start_y, e.y)
            with mss.mss() as sct:
                monitor = {"top": top, "left": left, "width": w, "height": h}
                img = np.array(sct.grab(monitor)); cv2.imwrite(self.sell_img_files[target], cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)); self.log(f"📸 SAVED: {target}.png")
        self.selector.destroy()

    def find_and_click(self, img_path, double=False, msg=""):
        if not os.path.exists(img_path): return False
        template = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
        with mss.mss() as sct:
            scr = np.array(sct.grab(sct.monitors[0])); scr_gray = cv2.cvtColor(scr, cv2.COLOR_BGRA2GRAY); res = cv2.matchTemplate(scr_gray, template, cv2.TM_CCOEFF_NORMED); _, max_val, _, max_loc = cv2.minMaxLoc(res)
            if max_val > 0.8:
                h, w = template.shape; tx, ty = max_loc[0] + w // 2, max_loc[1] + h // 2
                if double: pyautogui.doubleClick(tx, ty)
                else: pyautogui.click(tx, ty)
                if msg: self.log(f"✅ {msg} ({int(max_val*100)}%)")
                return True
        return False

    def run_sell_routine(self):
        if self.is_selling: return
        self.is_selling = True; was_running = self.is_running
        if was_running: self.toggle_running() 
        self.log("💰 [AUTO SELL] START")
        try:
            time.sleep(1.0)
            shop_icons = ["sell1-1.png", "sell1-2.png", "sell1-3.png", "sell1.png"]
            found = False
            for f in shop_icons:
                if self.find_and_click(f, double=True, msg="SHOP ICON"): found = True; break
            if not found: raise Exception("SHOP ICON NOT FOUND")
            time.sleep(2.0)
            if not self.find_and_click("sell2.png", msg="BATCH SELL"): raise Exception("SELL BUTTON NOT FOUND")
            time.sleep(1.2)
            if not self.find_and_click("sell3.png", msg="CONFIRM"): self.log("⚠️ CONFIRM MISSING")
            time.sleep(1.0)
            if not self.find_and_click("sell4.png", msg="EXIT"): self.log("⚠️ EXIT MISSING")
            self.log("✨ [AUTO SELL] COMPLETE"); winsound.Beep(1000, 200)
        except Exception as e: self.log(f"❌ [SELL FAILED] {e}")
        self.last_sell_time = time.time(); self.is_selling = False
        if was_running: time.sleep(0.5); self.toggle_running()

    def run_manual_sell(self):
        if self.is_selling: return
        threading.Thread(target=self.run_sell_routine, daemon=True).start()

    def monitor_loop(self):
        with mss.mss() as sct:
            while self.is_previewing:
                if self.reg_w.get() > 5:
                    region = {"top": self.reg_t.get(), "left": self.reg_l.get(), "width": self.reg_w.get(), "height": self.reg_h.get()}
                    try:
                        shot = np.array(sct.grab(region)); img = cv2.cvtColor(shot, cv2.COLOR_BGRA2BGR); m = self.color_margin.get()
                        low = np.array([max(0, self.base_lower[2]-m), max(0, self.base_lower[1]-m), max(0, self.base_lower[0]-m)])
                        high = np.array([min(255, self.base_upper[2]+m), min(255, self.base_upper[1]+m), min(255, self.base_upper[0]+m)])
                        mask = cv2.inRange(img, low, high); p_img = img.copy()
                        cv2.line(p_img, (self.x_min.get(), 0), (self.x_min.get(), self.reg_h.get()), (255, 0, 0), 1)
                        cv2.line(p_img, (self.x_max.get(), 0), (self.x_max.get(), self.reg_h.get()), (0, 0, 255), 1)
                        if np.any(mask):
                            M = cv2.moments(mask)
                            if M["m00"] > 0: cx, cy = int(M["m10"]/M["m00"]), int(M["m01"]/M["m00"]); cv2.circle(p_img, (cx, cy), 6, (0, 255, 0), -1)
                        self.update_preview(p_img)
                    except: pass
                time.sleep(0.08)

    def anti_macro_loop(self):
        last_alert_time = 0; ANTI_IMAGES = ["anti1.png", "anti2.png", "anti3.png", "anti4.png"]
        with mss.mss() as sct:
            while True:
                if self.use_anti_macro.get():
                    try:
                        scr_w, scr_h = pyautogui.size(); monitor = {"top": 0, "left": 0, "width": scr_w, "height": scr_h}; img = np.array(sct.grab(monitor)); img_gray = cv2.cvtColor(img, cv2.COLOR_BGRA2GRAY); found = False
                        for img_name in ANTI_IMAGES:
                            if not os.path.exists(img_name): continue
                            template = cv2.imread(img_name, cv2.IMREAD_GRAYSCALE)
                            if template is None: continue
                            res = cv2.matchTemplate(img_gray, template, cv2.TM_CCOEFF_NORMED)
                            if np.max(res) >= 0.8: found = True; break
                        if found:
                            now = time.time()
                            if now - last_alert_time > 60:
                                if self.use_sound_alert.get(): self.play_custom_sound()
                                last_alert_time = now; time.sleep(30)
                    except: pass
                time.sleep(1.0)

    def update_preview(self, img):
        try:
            h, w = img.shape[:2]; target_w = 400; target_h = int(h * (target_w / w))
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB); img_pil = Image.fromarray(img_rgb).resize((target_w, target_h), Image.Resampling.LANCZOS)
            img_tk = ImageTk.PhotoImage(img_pil); self.preview_label.config(image=img_tk, text=""); self.preview_label.image = img_tk
        except: pass

    def press_key(self, key): pyautogui.keyDown(key); time.sleep(random.uniform(0.08, 0.12)); pyautogui.keyUp(key)
    def toggle_running_from_key(self): self.root.after(0, self.toggle_running)
    def toggle_running(self):
        if self.is_running: self.is_running = False; self.start_btn.config(text="START (F12)", bg="#0ea5e9"); self.log("STOPPED"); pyautogui.keyUp('left'); pyautogui.keyUp('right')
        else: self.is_running = True; self.start_btn.config(text="STOP (F12)", bg="#ff4b2b"); self.log("RUNNING!"); threading.Thread(target=self.hunter_core, daemon=True).start()

    def hunter_core(self):
        cur_dir = 'right'; last_x, stuck_cnt = -1, 0; l_att, l_dash = 0, 0; l_del_time = time.time(); start_cx = None
        while self.is_running:
            if self.is_anti_macro_working or self.is_selling: time.sleep(0.5); continue
            if self.use_auto_sell.get() and (time.time() - self.last_sell_time) >= (self.sell_interval_min.get() * 60): self.run_sell_routine(); continue
            with mss.mss() as sct:
                region = {"top": self.reg_t.get(), "left": self.reg_l.get(), "width": self.reg_w.get(), "height": self.reg_h.get()}
                try:
                    shot = np.array(sct.grab(region)); img = cv2.cvtColor(shot, cv2.COLOR_BGRA2BGR); m = self.color_margin.get()
                    low = np.array([max(0, self.base_lower[2]-m), max(0, self.base_lower[1]-m), max(0, self.base_lower[0]-m)])
                    high = np.array([min(255, self.base_upper[2]+m), min(255, self.base_upper[1]+m), min(255, self.base_upper[0]+m)])
                    mask = cv2.inRange(img, low, high)
                    if np.any(mask):
                        M = cv2.moments(mask); cx = -1
                        if M["m00"] > 0:
                            cx = int(M["m10"] / M["m00"])
                            if self.hunt_mode.get() == 1:
                                if start_cx is None: start_cx = cx
                                r = self.stationary_range.get()
                                if cx >= start_cx + r and cur_dir == 'right': pyautogui.keyUp('right'); cur_dir = 'left'
                                elif cx <= start_cx - r and cur_dir == 'left': pyautogui.keyUp('left'); cur_dir = 'right'
                                pyautogui.keyDown(cur_dir)
                            else:
                                start_cx = None
                                if cx >= self.x_max.get() and cur_dir == 'right': pyautogui.keyUp('right'); cur_dir = 'left'
                                elif cx <= self.x_min.get() and cur_dir == 'left': pyautogui.keyUp('left'); cur_dir = 'right'
                                pyautogui.keyDown(cur_dir)
                            now_ms = time.time() * 1000
                            if now_ms - l_att >= self.attack_delay_ms.get(): self.press_key(self.KEY_ATTACK.get()); l_att = now_ms
                            if self.use_dash.get() and now_ms - l_dash >= self.dash_delay_ms.get(): self.press_key(self.KEY_DASH.get()); l_dash = now_ms
                            if self.use_periodic.get() and (time.time() - l_del_time) >= (self.periodic_interval_min.get() * 60):
                                self.log("[PETFOOD] USE ITEM"); self.press_key(self.KEY_PETFOOD.get()); l_del_time = time.time()
                        if cx != -1:
                            if abs(cx - last_x) < 2: stuck_cnt += 1
                            else: stuck_cnt = 0; last_x = cx
                            if stuck_cnt > 35: self.press_key(self.KEY_JUMP.get()); stuck_cnt = 0
                except: pass
            time.sleep(0.04)

    def start_coord_detection(self): threading.Thread(target=self._detection_worker, daemon=True).start()
    def _detection_worker(self):
        t_l = None; self.log("F1(TOP-LEFT) -> F2(BOTTOM-RIGHT)")
        while True:
            if keyboard.is_pressed('f1'): p = pyautogui.position(); self.reg_l.set(p.x); self.reg_t.set(p.y); self.log("TOP-LEFT OK"); t_l = p; time.sleep(0.5)
            if keyboard.is_pressed('f2'):
                p = pyautogui.position()
                if t_l: w, h = p.x - t_l.x, p.y - t_l.y; self.reg_w.set(w); self.reg_h.set(h); self.x_max.set(w-15); self.log(f"COORD OK: {w}x{h}"); break
            time.sleep(0.1)

    def play_custom_sound(self):
        def _play():
            start_time = time.time()
            while time.time() - start_time < 20:
                for _ in range(3): winsound.Beep(3500, 100); winsound.Beep(4000, 50)
                for freq in range(2500, 4500, 150): winsound.Beep(freq, 20)
                for _ in range(2): winsound.Beep(3000, 150); winsound.Beep(1500, 150)
                if not self.use_sound_alert.get(): break
        threading.Thread(target=_play, daemon=True).start()

    def rescale_ui(self): self.setup_styles(); self.setup_ui(); self.update_ui_settings(); self.log(f"UI SCALED: {self.ui_scale.get()}x")

    def save_current_profile(self):
        n = self.current_profile_name.get()
        if not n: return
        self.profiles_data[n] = {
            "reg": {"t": self.reg_t.get(), "l": self.reg_l.get(), "w": self.reg_w.get(), "h": self.reg_h.get()},
            "range": {"min": self.x_min.get(), "max": self.x_max.get()},
            "keys": {"att": self.KEY_ATTACK.get(), "dash": self.KEY_DASH.get(), "jump": self.KEY_JUMP.get(), "pet": self.KEY_PETFOOD.get()},
            "params": {"margin": self.color_margin.get(), "ad": self.attack_delay_ms.get(), "dd": self.dash_delay_ms.get(), "mode": self.hunt_mode.get(), "per_int": self.periodic_interval_min.get(), "sell_int": self.sell_interval_min.get()}
        }
        with open(CONFIG_FILE, "w", encoding="utf-8") as f: json.dump(self.profiles_data, f, ensure_ascii=False, indent=4)
        self.update_profile_list(); messagebox.showinfo("COMPLETE", f"'{n}' SAVED")

    def load_all_profiles(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f: self.profiles_data = json.load(f)
                self.update_profile_list()
                if self.profiles_data: n = list(self.profiles_data.keys())[0]; self.apply_profile_data(n); self.profile_combo.set(n)
            except: pass

    def update_profile_list(self): self.profile_combo['values'] = list(self.profiles_data.keys())
    def on_profile_change(self, e): 
        n = self.profile_combo.get()
        if n in self.profiles_data: self.apply_profile_data(n); self.current_profile_name.set(n)

    def apply_profile_data(self, n):
        d = self.profiles_data[n]; p = d["params"]; k = d.get("keys", {})
        self.reg_t.set(d["reg"]["t"]); self.reg_l.set(d["reg"]["l"]); self.reg_w.set(d["reg"]["w"]); self.reg_h.set(d["reg"]["h"])
        self.x_min.set(d["range"]["min"]); self.x_max.set(d["range"]["max"])
        self.KEY_ATTACK.set(k.get("att", "end")); self.KEY_DASH.set(k.get("dash", "space")); self.KEY_JUMP.set(k.get("jump", "alt")); self.KEY_PETFOOD.set(k.get("pet", "del"))
        self.color_margin.set(p.get("margin", 60)); self.attack_delay_ms.set(p.get("ad", 500)); self.dash_delay_ms.set(p.get("dd", 1500))
        self.hunt_mode.set(p.get("mode", 0)); self.periodic_interval_min.set(p.get("per_int", 5)); self.sell_interval_min.set(p.get("sell_int", 15)); self.update_ui_settings()

if __name__ == "__main__":
    root = tk.Tk(); app = AutoHunterV7_0(root); root.mainloop()
