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
from PIL import Image, ImageTk

# 설정 파일 경로
CONFIG_FILE = "hunter_premium_v4_7_config.json"

# --- DPI 보정 ---
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except:
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except:
        pass

class AutoHunterV4_7:
    def __init__(self, root):
        self.root = root
        self.root.title("오토헌터 프리미엄 v4.7 (제자리 모드 + 관성 추적)")
        self.root.geometry("620x950")
        self.root.configure(bg="#1e1e1e")
        
        self.is_running = False
        self.is_previewing = True
        self.is_anti_macro_working = False
        
        # 거탐 추적용 변수 (관성 유지)
        self.last_anti_pos = None
        self.last_anti_vel = (0, 0)
        self.anti_lost_time = 0
        
        # 고정 키
        self.KEY_ATTACK = "end"
        self.KEY_DASH = "space"
        self.KEY_JUMP = "alt"
        self.KEY_PERIODIC = "del"
        
        self.base_lower = np.array([245, 230, 0]) 
        self.base_upper = np.array([254, 255, 129]) 
        
        # 거탐(Anti-Macro) 설정 - 하얀색 (HSV)
        # 하얀색은 채도(S)가 낮고 밝기(V)가 매우 높음
        self.anti_lower = np.array([0, 0, 200])
        self.anti_upper = np.array([180, 40, 255])
        
        self.setup_styles()
        
        # 설정 변수
        self.profiles_data = {}
        self.current_profile_name = tk.StringVar(value="사냥터 1")
        self.reg_t = tk.IntVar(value=100); self.reg_l = tk.IntVar(value=100)
        self.reg_w = tk.IntVar(value=200); self.reg_h = tk.IntVar(value=150)
        self.x_min = tk.IntVar(value=20); self.x_max = tk.IntVar(value=180)
        self.color_margin = tk.IntVar(value=60) 
        self.attack_delay_ms = tk.IntVar(value=500)
        self.dash_delay_ms = tk.IntVar(value=1500)
        
        # 신규 변수
        self.use_dash = tk.BooleanVar(value=True)
        self.use_anti_macro = tk.BooleanVar(value=False)
        self.hunt_mode = tk.IntVar(value=0) # 0: 이동사냥, 1: 제자리사냥
        
        self.setup_scrollable_ui()
        self.load_all_profiles()
        
        # 실시간 모니터링
        threading.Thread(target=self.monitor_loop, daemon=True).start()
        threading.Thread(target=self.anti_macro_loop, daemon=True).start()
        keyboard.add_hotkey('f12', self.toggle_running_from_key)

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TFrame", background="#1e1e1e")
        style.configure("TLabelframe", background="#1e1e1e", foreground="#00adb5", bordercolor="#393e46")
        style.configure("TLabelframe.Label", foreground="#00adb5", font=("Malgun Gothic", 10, "bold"))
        style.configure("TLabel", background="#1e1e1e", foreground="#eeeeee", font=("Malgun Gothic", 9))
        style.configure("TButton", background="#393e46", foreground="#eeeeee", font=("Malgun Gothic", 9, "bold"))
        style.map("TButton", background=[('active', '#00adb5')])
        style.configure("TCheckbutton", background="#1e1e1e", foreground="#eeeeee")
        style.configure("TRadiobutton", background="#1e1e1e", foreground="#eeeeee")
        style.configure("TEntry", fieldbackground="#393e46", foreground="#ffffff", insertcolor="white")
        style.configure("TCombobox", fieldbackground="#393e46", foreground="#ffffff")

    def setup_scrollable_ui(self):
        self.canvas = tk.Canvas(self.root, bg="#1e1e1e", highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)
        self.scrollable_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        container = self.scrollable_frame
        
        # 0. 프로필
        p_group = ttk.LabelFrame(container, text=" [ 0. 사냥터 관리 ] ", padding="10")
        p_group.pack(fill=tk.X, padx=10, pady=5)
        row1 = ttk.Frame(p_group); row1.pack(fill=tk.X)
        self.profile_combo = ttk.Combobox(row1, state="readonly", width=25); self.profile_combo.pack(side=tk.LEFT, padx=5)
        self.profile_combo.bind("<<ComboboxSelected>>", self.on_profile_change)
        ttk.Button(row1, text="삭제", command=self.delete_profile, width=5).pack(side=tk.RIGHT)
        row2 = ttk.Frame(p_group); row2.pack(fill=tk.X, pady=(10, 0))
        ttk.Entry(row2, textvariable=self.current_profile_name, width=30).pack(side=tk.LEFT, padx=10)
        ttk.Button(row2, text="설정 저장", command=self.save_current_profile).pack(side=tk.RIGHT)

        # 1. 프리뷰
        group1 = ttk.LabelFrame(container, text=" [ 1. 영역 지정 ] ", padding="10")
        group1.pack(fill=tk.X, padx=10, pady=5)
        btn_f = ttk.Frame(group1); btn_f.pack(fill=tk.X, pady=(0, 10))
        ttk.Button(btn_f, text="클래식 지정 (F1, F2)", command=self.start_coord_detection).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)
        ttk.Button(btn_f, text="드래그 선택", command=self.open_selector).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)
        self.preview_label = tk.Label(group1, text="영역을 지정하면 화면이 출력됩니다.", bg="#121212", fg="#393e46", font=("Malgun Gothic", 10))
        self.preview_label.pack(fill=tk.BOTH, expand=True, ipady=5)

        # 2. 사냥 모드 및 기능
        group2 = ttk.LabelFrame(container, text=" [ 2. 사냥 모드 및 기능 제어 ] ", padding="10")
        group2.pack(fill=tk.X, padx=10, pady=5)
        
        mode_f = ttk.Frame(group2); mode_f.pack(fill=tk.X, pady=5)
        ttk.Radiobutton(mode_f, text="이동 사냥", variable=self.hunt_mode, value=0).pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(mode_f, text="제자리 사냥 (±5)", variable=self.hunt_mode, value=1).pack(side=tk.LEFT, padx=10)

        check_f = ttk.Frame(group2); check_f.pack(fill=tk.X, pady=5)
        ttk.Checkbutton(check_f, text="이동 스킬 사용", variable=self.use_dash).pack(side=tk.LEFT, padx=5)
        ttk.Checkbutton(check_f, text="거탐 대응 (White)", variable=self.use_anti_macro).pack(side=tk.LEFT, padx=20)

        ttk.Label(group2, text="미니맵 노란색 감도:").pack(anchor=tk.W, pady=(10, 0))
        m_f = ttk.Frame(group2); m_f.pack(fill=tk.X)
        ttk.Scale(m_f, from_=0, to=150, variable=self.color_margin, orient=tk.HORIZONTAL).pack(side=tk.LEFT, expand=True, fill=tk.X)
        ttk.Entry(m_f, textvariable=self.color_margin, width=5, font=("Malgun Gothic", 10, "bold")).pack(side=tk.LEFT, padx=5)

        # 3. 주기
        group3 = ttk.LabelFrame(container, text=" [ 3. 스킬 주기 설정 (ms) ] ", padding="10")
        group3.pack(fill=tk.X, padx=10, pady=5)
        for label, var, max_v in [("공격 주기 (ms):", self.attack_delay_ms, 3000), ("이동 주기 (ms):", self.dash_delay_ms, 10000)]:
            ttk.Label(group3, text=label).pack(anchor=tk.W)
            f = ttk.Frame(group3); f.pack(fill=tk.X, pady=(0, 5))
            ttk.Scale(f, from_=100, to=max_v, variable=var, orient=tk.HORIZONTAL).pack(side=tk.LEFT, expand=True, fill=tk.X)
            ttk.Entry(f, textvariable=var, width=6, font=("Malgun Gothic", 10, "bold")).pack(side=tk.LEFT, padx=5)

        # 4. 범위
        group4 = ttk.LabelFrame(container, text=" [ 4. 활동 범위 (이동사냥 전용) ] ", padding="10")
        group4.pack(fill=tk.X, padx=10, pady=5)
        r_f = ttk.Frame(group4); r_f.pack(fill=tk.X)
        ttk.Label(r_f, text="최소 X:").pack(side=tk.LEFT); ttk.Entry(r_f, textvariable=self.x_min, width=8).pack(side=tk.LEFT, padx=5)
        ttk.Label(r_f, text="최대 X:").pack(side=tk.LEFT, padx=(20, 0)); ttk.Entry(r_f, textvariable=self.x_max, width=8).pack(side=tk.LEFT, padx=5)

        self.start_btn = tk.Button(container, text="사냥 시작 (F12)", bg="#00adb5", fg="white", font=("Malgun Gothic", 13, "bold"), borderwidth=0, command=self.toggle_running)
        self.start_btn.pack(fill=tk.X, padx=10, pady=10, ipady=12)
        self.log_text = tk.Text(container, height=10, bg="#121212", fg="#eeeeee", borderwidth=0, font=("Consolas", 9), padx=10, pady=10)
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

    def log(self, msg):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, f"[{time.strftime('%H:%M:%S')}] {msg}\n")
        self.log_text.see(tk.END); self.log_text.config(state=tk.DISABLED)

    # --- 영역 선택 (Selector) ---
    def open_selector(self):
        self.selector = tk.Toplevel(self.root); self.selector.attributes("-alpha", 0.3); self.selector.attributes("-fullscreen", True)
        self.selector.attributes("-topmost", True); self.selector.config(cursor="cross")
        self.sel_canvas = tk.Canvas(self.selector, cursor="cross", bg="grey"); self.sel_canvas.pack(fill="both", expand=True)
        self.start_x = None; self.start_y = None; self.rect = None
        self.sel_canvas.bind("<ButtonPress-1>", self.on_sel_press); self.sel_canvas.bind("<B1-Motion>", self.on_sel_drag)
        self.sel_canvas.bind("<ButtonRelease-1>", self.on_sel_release)

    def on_sel_press(self, e): self.start_x, self.start_y = e.x, e.y; self.rect = self.sel_canvas.create_rectangle(e.x, e.y, e.x, e.y, outline="cyan", width=3)
    def on_sel_drag(self, e): self.sel_canvas.coords(self.rect, self.start_x, self.start_y, e.x, e.y)
    def on_sel_release(self, e):
        w, h = abs(e.x - self.start_x), abs(e.y - self.start_y)
        if w > 5: self.reg_l.set(min(self.start_x, e.x)); self.reg_t.set(min(self.start_y, e.y)); self.reg_w.set(w); self.reg_h.set(h); self.x_max.set(w-15); self.log(f"영역 설정: {w}x{h}")
        self.selector.destroy()

    def start_coord_detection(self): threading.Thread(target=self._detection_worker, daemon=True).start()
    def _detection_worker(self):
        t_l = None
        while True:
            if keyboard.is_pressed('f1'): p = pyautogui.position(); self.reg_l.set(p.x); self.reg_t.set(p.y); self.log("좌상단 확정"); t_l = p; time.sleep(0.5)
            if keyboard.is_pressed('f2'):
                p = pyautogui.position()
                if t_l: w, h = p.x - t_l.x, p.y - t_l.y; self.reg_w.set(w); self.reg_h.set(h); self.x_max.set(w-15); self.log(f"설정 완료: {w}x{h}"); break
            time.sleep(0.1)

    # --- 메인 모니터링 ---
    def monitor_loop(self):
        with mss.mss() as sct:
            while self.is_previewing:
                if self.reg_w.get() > 5:
                    region = {"top": self.reg_t.get(), "left": self.reg_l.get(), "width": self.reg_w.get(), "height": self.reg_h.get()}
                    try:
                        shot = np.array(sct.grab(region)); img = cv2.cvtColor(shot, cv2.COLOR_BGRA2BGR)
                        m = self.color_margin.get()
                        low = np.array([max(0, self.base_lower[2]-m), max(0, self.base_lower[1]-m), max(0, self.base_lower[0]-m)])
                        high = np.array([min(255, self.base_upper[2]+m), min(255, self.base_upper[1]+m), min(255, self.base_upper[0]+m)])
                        mask = cv2.inRange(img, low, high); p_img = img.copy()
                        if np.any(mask):
                            M = cv2.moments(mask)
                            if M["m00"] > 0: cx, cy = int(M["m10"]/M["m00"]), int(M["m01"]/M["m00"]); cv2.circle(p_img, (cx, cy), 8, (0, 255, 0), -1)
                        cv2.line(p_img, (self.x_min.get(), 0), (self.x_min.get(), region["height"]), (0, 173, 181), 2)
                        cv2.line(p_img, (self.x_max.get(), 0), (self.x_max.get(), region["height"]), (0, 173, 181), 2)
                        self.update_preview(p_img)
                    except: pass
                time.sleep(0.08)

    # --- 거탐 추적 (하얀색 + 관성 추적) ---
    def anti_macro_loop(self):
        with mss.mss() as sct:
            while True:
                if self.use_anti_macro.get():
                    scr_w, scr_h = pyautogui.size()
                    region = {"top": 0, "left": 0, "width": scr_w, "height": scr_h}
                    try:
                        shot = np.array(sct.grab(region)); img = cv2.cvtColor(shot, cv2.COLOR_BGRA2BGR)
                        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
                        mask = cv2.inRange(hsv, self.anti_lower, self.anti_upper)
                        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                        
                        found = False
                        for cnt in contours:
                            if cv2.contourArea(cnt) > 150:
                                M = cv2.moments(cnt)
                                if M["m00"] > 0:
                                    cx, cy = int(M["m10"]/M["m00"]), int(M["m01"]/M["m00"])
                                    if not self.is_anti_macro_working: self.log("[위험] 하얀색 거탐 감지!"); self.is_anti_macro_working = True
                                    
                                    # 속도 계산 (관성용)
                                    if self.last_anti_pos:
                                        self.last_anti_vel = (cx - self.last_anti_pos[0], cy - self.last_anti_pos[1])
                                    self.last_anti_pos = (cx, cy); self.anti_lost_time = 0
                                    
                                    pyautogui.moveTo(cx + random.randint(-2, 2), cy + random.randint(-2, 2), duration=0.05)
                                    found = True; break
                        
                        # 도형이 사라졌을 때 (관성 추적)
                        if not found and self.is_anti_macro_working:
                            if self.anti_lost_time < 20: # 약 1초간 관성 유지 (0.05 * 20)
                                self.anti_lost_time += 1
                                # 마지막 속도 방향으로 계속 이동
                                pred_x = self.last_anti_pos[0] + self.last_anti_vel[0]
                                pred_y = self.last_anti_pos[1] + self.last_anti_vel[1]
                                self.last_anti_pos = (pred_x, pred_y)
                                pyautogui.moveTo(pred_x, pred_y, duration=0.05)
                            else:
                                self.is_anti_macro_working = False; self.last_anti_pos = None; self.log("[정보] 거탐 종료됨")
                            
                    except: pass
                time.sleep(0.05)

    def update_preview(self, img):
        try:
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB); img_pil = Image.fromarray(img_rgb).resize((480, 320), Image.Resampling.LANCZOS)
            img_tk = ImageTk.PhotoImage(img_pil); self.preview_label.config(image=img_tk, text=""); self.preview_label.image = img_tk
        except: pass

    def press_key(self, key): pyautogui.keyDown(key); time.sleep(random.uniform(0.08, 0.12)); pyautogui.keyUp(key)

    def toggle_running_from_key(self): self.root.after(0, self.toggle_running)
    def toggle_running(self):
        if self.is_running:
            self.is_running = False; self.start_btn.config(text="사냥 시작 (F12)", bg="#00adb5"); self.log("사냥 중단")
            pyautogui.keyUp('left'); pyautogui.keyUp('right')
        else:
            self.is_running = True; self.start_btn.config(text="사냥 중지 (F12)", bg="#ff4b2b"); self.log("사냥 시작!")
            threading.Thread(target=self.hunter_core, daemon=True).start()

    def hunter_core(self):
        cur_dir = 'right'
        last_x, stuck_cnt = -1, 0
        l_att, l_dash = 0, 0
        l_del_time = time.time()
        
        # 제자리 사냥용 변수
        start_cx = None
        
        with mss.mss() as sct:
            while self.is_running:
                if self.is_anti_macro_working: pyautogui.keyUp('left'); pyautogui.keyUp('right'); time.sleep(0.5); continue

                region = {"top": self.reg_t.get(), "left": self.reg_l.get(), "width": self.reg_w.get(), "height": self.reg_h.get()}
                try:
                    shot = np.array(sct.grab(region)); img = cv2.cvtColor(shot, cv2.COLOR_BGRA2BGR)
                    m = self.color_margin.get()
                    low = np.array([max(0, self.base_lower[2]-m), max(0, self.base_lower[1]-m), max(0, self.base_lower[0]-m)])
                    high = np.array([min(255, self.base_upper[2]+m), min(255, self.base_upper[1]+m), min(255, self.base_upper[0]+m)])
                    mask = cv2.inRange(img, low, high)
                    
                    if np.any(mask):
                        M = cv2.moments(mask)
                        if M["m00"] > 0:
                            cx = int(M["m10"] / M["m00"])
                            
                            # 1. 제자리 사냥 로직
                            if self.hunt_mode.get() == 1:
                                if start_cx is None: start_cx = cx; self.log(f"제자리 기준점: {cx}")
                                target_min, target_max = start_cx - 5, start_cx + 5
                                
                                if cx >= target_max and cur_dir == 'right': pyautogui.keyUp('right'); cur_dir = 'left'
                                elif cx <= target_min and cur_dir == 'left': pyautogui.keyUp('left'); cur_dir = 'right'
                                pyautogui.keyDown(cur_dir)
                            # 2. 이동 사냥 로직
                            else:
                                start_cx = None # 초기화
                                if cx >= self.x_max.get() and cur_dir == 'right': pyautogui.keyUp('right'); cur_dir = 'left'; self.log("우측 전환")
                                elif cx <= self.x_min.get() and cur_dir == 'left': pyautogui.keyUp('left'); cur_dir = 'right'; self.log("좌측 전환")
                                pyautogui.keyDown(cur_dir)
                            
                            now = time.time() * 1000
                            if now - l_att >= self.attack_delay_ms.get(): self.press_key(self.KEY_ATTACK); l_att = now
                            if self.use_dash.get() and now - l_dash >= self.dash_delay_ms.get(): self.press_key(self.KEY_DASH); l_dash = now
                            
                            if (time.time() - l_del_time) >= 300:
                                self.log("[주기] DEL 키 2연타"); self.press_key(self.KEY_PERIODIC); time.sleep(0.2); self.press_key(self.KEY_PERIODIC)
                                l_del_time = time.time()
                        
                        if abs(cx - last_x) < 2: stuck_cnt += 1
                        else: stuck_cnt = 0; last_x = cx
                        if stuck_cnt > 35: self.press_key(self.KEY_JUMP); stuck_cnt = 0
                except: break
                time.sleep(0.04)

    def save_current_profile(self):
        n = self.current_profile_name.get()
        self.profiles_data[n] = {
            "reg": {"t": self.reg_t.get(), "l": self.reg_l.get(), "w": self.reg_w.get(), "h": self.reg_h.get()},
            "range": {"min": self.x_min.get(), "max": self.x_max.get()},
            "params": {
                "margin": self.color_margin.get(), "ad": self.attack_delay_ms.get(), "dd": self.dash_delay_ms.get(),
                "use_dash": self.use_dash.get(), "use_anti": self.use_anti_macro.get(), "mode": self.hunt_mode.get()
            }
        }
        with open(CONFIG_FILE, "w", encoding="utf-8") as f: json.dump(self.profiles_data, f, ensure_ascii=False)
        self.update_profile_list(); self.log(f"저장: {n}")

    def load_all_profiles(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f: self.profiles_data = json.load(f)
                self.update_profile_list()
                if self.profiles_data: n = list(self.profiles_data.keys())[0]; self.apply_profile_data(n); self.profile_combo.set(n)
            except: pass

    def update_profile_list(self): self.profile_combo['values'] = list(self.profiles_data.keys())
    def on_profile_change(self, e): n = self.profile_combo.get(); self.apply_profile_data(n); self.current_profile_name.set(n)
    def apply_profile_data(self, n):
        d = self.profiles_data[n]; self.reg_t.set(d["reg"]["t"]); self.reg_l.set(d["reg"]["l"])
        self.reg_w.set(d["reg"]["w"]); self.reg_h.set(d["reg"]["h"]); self.x_min.set(d["range"]["min"]); self.x_max.set(d["range"]["max"])
        p = d["params"]; self.color_margin.set(p.get("margin", 60)); self.attack_delay_ms.set(p.get("ad", 500))
        self.dash_delay_ms.set(p.get("dd", 1500)); self.use_dash.set(p.get("use_dash", True))
        self.use_anti_macro.set(p.get("use_anti", False)); self.hunt_mode.set(p.get("mode", 0))

    def delete_profile(self):
        n = self.profile_combo.get()
        if n in self.profiles_data: del self.profiles_data[n]; self.update_profile_list(); self.log(f"삭제: {n}")

if __name__ == "__main__":
    root = tk.Tk(); app = AutoHunterV4_7(root); root.mainloop()
