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
from PIL import Image, ImageTk

# 설정 파일 경로
CONFIG_FILE = "hunter_premium_config.json"

class AutoHunterV4:
    def __init__(self, root):
        self.root = root
        self.root.title("AUTO-HUNTER PREMIUM v4.0")
        self.root.geometry("520x950")
        self.root.configure(bg="#1e1e1e") # 다크 배경
        
        self.is_running = False
        self.base_lower = np.array([245, 230, 0]) 
        self.base_upper = np.array([254, 255, 129]) 
        
        # 스타일 설정
        self.setup_styles()
        
        # 프로필 관련 변수
        self.current_profile_idx = tk.StringVar(value="Profile 1")
        
        # 설정 변수들 (프로필별 저장 대상)
        self.region_top = tk.IntVar(value=100)
        self.region_left = tk.IntVar(value=100)
        self.region_width = tk.IntVar(value=200)
        self.region_height = tk.IntVar(value=150)
        
        self.x_min = tk.IntVar(value=20)
        self.x_max = tk.IntVar(value=180)
        
        self.color_margin = tk.IntVar(value=50) 
        self.attack_freq = tk.IntVar(value=50)
        self.dash_freq = tk.IntVar(value=30)
        
        self.key_attack = tk.StringVar(value="ctrl")
        self.key_dash = tk.StringVar(value="shift")
        self.key_jump = tk.StringVar(value="space")
        
        self.profiles_data = {} # 전체 프로필 데이터 저장소
        
        self.setup_ui()
        self.load_all_profiles()
        
        keyboard.add_hotkey('f12', self.toggle_running_from_key)

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        
        # 다크 테마 커스텀
        style.configure("TFrame", background="#1e1e1e")
        style.configure("TLabelframe", background="#1e1e1e", foreground="#00adb5", bordercolor="#393e46")
        style.configure("TLabelframe.Label", background="#1e1e1e", foreground="#00adb5", font=("Helvetica", 10, "bold"))
        
        style.configure("TLabel", background="#1e1e1e", foreground="#eeeeee", font=("Helvetica", 9))
        style.configure("TButton", background="#393e46", foreground="#eeeeee", borderwidth=0, font=("Helvetica", 9, "bold"))
        style.map("TButton", background=[('active', '#00adb5')])
        
        style.configure("Accent.TButton", background="#00adb5", foreground="#ffffff")
        style.configure("TEntry", fieldbackground="#393e46", foreground="#ffffff", borderwidth=0)
        style.configure("TCombobox", fieldbackground="#393e46", foreground="#ffffff", arrowcolor="#00adb5")

    def setup_ui(self):
        main_container = ttk.Frame(self.root, padding="15")
        main_container.pack(fill=tk.BOTH, expand=True)

        # --- 상단 프로필 선택 섹션 ---
        profile_frame = ttk.Frame(main_container)
        profile_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(profile_frame, text="SELECT PROFILE:", font=("Helvetica", 10, "bold"), foreground="#00adb5").pack(side=tk.LEFT)
        self.profile_combo = ttk.Combobox(profile_frame, textvariable=self.current_profile_idx, values=[f"Profile {i}" for i in range(1, 11)], state="readonly", width=15)
        self.profile_combo.pack(side=tk.LEFT, padx=10)
        self.profile_combo.bind("<<ComboboxSelected>>", self.on_profile_change)
        
        ttk.Button(profile_frame, text="SAVE", command=self.save_current_profile, width=8).pack(side=tk.RIGHT)

        # --- 1. 미니맵 모니터링 ---
        group1 = ttk.LabelFrame(main_container, text=" 1. MINIMAP MONITORING ", padding="10")
        group1.pack(fill=tk.X, pady=5)
        
        btn_frame = ttk.Frame(group1)
        btn_frame.pack(fill=tk.X, pady=(0, 10))
        ttk.Button(btn_frame, text="SET REGION (F1, F2)", command=self.start_coord_detection).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)
        
        self.preview_label = tk.Label(group1, text="LIVE PREVIEW", bg="#121212", fg="#393e46", font=("Helvetica", 8))
        self.preview_label.pack(fill=tk.X, pady=5)

        # --- 2. 인식 엔진 설정 ---
        group2 = ttk.LabelFrame(main_container, text=" 2. RECOGNITION ENGINE ", padding="10")
        group2.pack(fill=tk.X, pady=5)
        
        # Margin 설정
        ttk.Label(group2, text="COLOR MARGIN (TOLERANCE):").pack(anchor=tk.W)
        m_frame = ttk.Frame(group2)
        m_frame.pack(fill=tk.X)
        ttk.Scale(m_frame, from_=0, to=150, variable=self.color_margin, orient=tk.HORIZONTAL).pack(side=tk.LEFT, expand=True, fill=tk.X)
        ttk.Entry(m_frame, textvariable=self.color_margin, width=5, font=("Helvetica", 10, "bold")).pack(side=tk.LEFT, padx=5)

        # --- 3. 전투 및 이동 제어 ---
        group3 = ttk.LabelFrame(main_container, text=" 3. COMBAT & MOVEMENT ", padding="10")
        group3.pack(fill=tk.X, pady=5)
        
        # Attack Freq
        ttk.Label(group3, text="ATTACK FREQUENCY (%):").pack(anchor=tk.W)
        af_frame = ttk.Frame(group3)
        af_frame.pack(fill=tk.X, pady=(0, 10))
        ttk.Scale(af_frame, from_=0, to=100, variable=self.attack_freq, orient=tk.HORIZONTAL).pack(side=tk.LEFT, expand=True, fill=tk.X)
        ttk.Entry(af_frame, textvariable=self.attack_freq, width=5, font=("Helvetica", 10, "bold")).pack(side=tk.LEFT, padx=5)
        
        # Dash Freq
        ttk.Label(group3, text="DASH FREQUENCY (%):").pack(anchor=tk.W)
        df_frame = ttk.Frame(group3)
        df_frame.pack(fill=tk.X)
        ttk.Scale(df_frame, from_=0, to=100, variable=self.dash_freq, orient=tk.HORIZONTAL).pack(side=tk.LEFT, expand=True, fill=tk.X)
        ttk.Entry(df_frame, textvariable=self.dash_freq, width=5, font=("Helvetica", 10, "bold")).pack(side=tk.LEFT, padx=5)

        # --- 4. 범위 및 단축키 ---
        group4 = ttk.LabelFrame(main_container, text=" 4. BOUNDS & HOTKEYS ", padding="10")
        group4.pack(fill=tk.X, pady=5)
        
        r_frame = ttk.Frame(group4)
        r_frame.pack(fill=tk.X, pady=5)
        ttk.Label(r_frame, text="MIN X:").pack(side=tk.LEFT)
        ttk.Entry(r_frame, textvariable=self.x_min, width=8).pack(side=tk.LEFT, padx=5)
        ttk.Label(r_frame, text="MAX X:").pack(side=tk.LEFT, padx=(10, 0))
        ttk.Entry(r_frame, textvariable=self.x_max, width=8).pack(side=tk.LEFT, padx=5)
        
        k_frame = ttk.Frame(group4)
        k_frame.pack(fill=tk.X, pady=10)
        keys_cfg = [("ATT", self.key_attack), ("DSH", self.key_dash), ("JMP", self.key_jump)]
        for i, (l, v) in enumerate(keys_cfg):
            ttk.Label(k_frame, text=l).grid(row=0, column=i*2, padx=2)
            ttk.Entry(k_frame, textvariable=v, width=7).grid(row=0, column=i*2+1, padx=2)

        # --- 실행 제어 ---
        self.start_btn = tk.Button(main_container, text="START HUNTER (F12)", bg="#00adb5", fg="white", font=("Helvetica", 12, "bold"), borderwidth=0, command=self.toggle_running)
        self.start_btn.pack(fill=tk.X, pady=15, ipady=10)

        # --- 콘솔 로그 ---
        self.log_text = tk.Text(main_container, height=10, bg="#121212", fg="#eeeeee", borderwidth=0, font=("Consolas", 9), padx=10, pady=10)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        self.log_text.config(state=tk.DISABLED)

    def log(self, msg):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, f"[{time.strftime('%H:%M:%S')}] {msg}\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)

    def start_coord_detection(self):
        self.log("DETECTION MODE: PRESS F1 (TOP-LEFT) & F2 (BOTTOM-RIGHT)")
        threading.Thread(target=self._worker, daemon=True).start()

    def _worker(self):
        t_l = None
        while True:
            if keyboard.is_pressed('f1'):
                t_l = pyautogui.position()
                self.region_top.set(t_l.y); self.region_left.set(t_l.x)
                time.sleep(0.5)
            if keyboard.is_pressed('f2'):
                br = pyautogui.position()
                if t_l:
                    w, h = br.x - t_l.x, br.y - t_l.y
                    self.region_width.set(w); self.region_height.set(h)
                    self.x_max.set(w - 20)
                    self.log(f"REGION SET: {w}x{h}")
                    break
            time.sleep(0.1)

    # --- 프로필 관리 ---
    def save_current_profile(self):
        p_name = self.current_profile_idx.get()
        self.profiles_data[p_name] = {
            "reg": {"t": self.region_top.get(), "l": self.region_left.get(), "w": self.region_width.get(), "h": self.region_height.get()},
            "range": {"min": self.x_min.get(), "max": self.x_max.get()},
            "keys": {"a": self.key_attack.get(), "d": self.key_dash.get(), "j": self.key_jump.get()},
            "params": {"margin": self.color_margin.get(), "af": self.attack_freq.get(), "df": self.dash_freq.get()}
        }
        with open(CONFIG_FILE, "w") as f:
            json.dump(self.profiles_data, f)
        self.log(f"SAVED: {p_name}")

    def load_all_profiles(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r") as f:
                    self.profiles_data = json.load(f)
                self.apply_profile_data("Profile 1")
            except: pass

    def on_profile_change(self, event):
        p_name = self.current_profile_idx.get()
        self.apply_profile_data(p_name)
        self.log(f"LOADED: {p_name}")

    def apply_profile_data(self, p_name):
        if p_name in self.profiles_data:
            d = self.profiles_data[p_name]
            self.region_top.set(d["reg"]["t"]); self.region_left.set(d["reg"]["l"])
            self.region_width.set(d["reg"]["w"]); self.region_height.set(d["reg"]["h"])
            self.x_min.set(d["range"]["min"]); self.x_max.set(d["range"]["max"])
            self.key_attack.set(d["keys"]["a"]); self.key_dash.set(d["keys"]["d"]); self.key_jump.set(d["keys"]["j"])
            self.color_margin.set(d["params"].get("margin", 50))
            self.attack_freq.set(d["params"].get("af", 50))
            self.dash_freq.set(d["params"].get("df", 30))

    def toggle_running_from_key(self):
        self.root.after(0, self.toggle_running)

    def toggle_running(self):
        if self.is_running:
            self.is_running = False
            self.start_btn.config(text="START HUNTER (F12)", bg="#00adb5")
            self.log("STOPPED.")
        else:
            self.is_running = True
            self.start_btn.config(text="STOP HUNTER (F12)", bg="#ff4b2b")
            self.log("STARTING IN 3S...")
            threading.Thread(target=self.hunter_main, daemon=True).start()

    def update_preview(self, img):
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img_pil = Image.fromarray(img_rgb).resize((220, 160), Image.Resampling.LANCZOS)
        img_tk = ImageTk.PhotoImage(img_pil)
        self.preview_label.config(image=img_tk, text=""); self.preview_label.image = img_tk

    def press_skill(self, key):
        pyautogui.keyDown(key)
        time.sleep(random.uniform(0.08, 0.12))
        pyautogui.keyUp(key)

    def hunter_main(self):
        time.sleep(3)
        reg = {"top": self.region_top.get(), "left": self.region_left.get(), "width": self.region_width.get(), "height": self.region_height.get()}
        x_min, x_max = self.x_min.get(), self.x_max.get()
        keys = {"a": self.key_attack.get(), "d": self.key_dash.get(), "j": self.key_jump.get()}
        
        current_dir = "right"
        last_x, stuck_cnt = -1, 0
        
        with mss.mss() as sct:
            while self.is_running:
                screenshot = np.array(sct.grab(reg))
                img = cv2.cvtColor(screenshot, cv2.COLOR_BGRA2BGR)
                
                margin = self.color_margin.get()
                lower_bgr = np.array([max(0, self.base_lower[2]-margin), max(0, self.base_lower[1]-margin), max(0, self.base_lower[0]-margin)])
                upper_bgr = np.array([min(255, self.base_upper[2]+margin), min(255, self.base_upper[1]+margin), min(255, self.base_upper[0]+margin)])
                
                mask = cv2.inRange(img, lower_bgr, upper_bgr)
                mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((3,3), np.uint8))
                
                preview_img = img.copy()
                
                if np.any(mask):
                    M = cv2.moments(mask)
                    if M["m00"] > 0:
                        curr_x = int(M["m10"] / M["m00"])
                        curr_y = int(M["m01"] / M["m00"])
                        cv2.circle(preview_img, (curr_x, curr_y), 6, (0, 255, 0), -1) # 고급진 녹색 점
                        
                        # 끼임 체크
                        if abs(curr_x - last_x) < 2: stuck_cnt += 1
                        else: stuck_cnt = 0; last_x = curr_x
                        if stuck_cnt > 20:
                            self.log("[!] STUCK - JUMPING")
                            pyautogui.keyUp('left'); pyautogui.keyUp('right')
                            self.press_skill(keys["j"])
                            rev = "left" if current_dir == "right" else "right"
                            pyautogui.keyDown(rev); time.sleep(0.6); pyautogui.keyUp(rev)
                            stuck_cnt = 0; continue

                        # 방향 전환
                        if curr_x >= x_max and current_dir == "right":
                            pyautogui.keyUp('right'); current_dir = "left"
                            self.log(f">>> BOUNDARY RIGHT (X:{curr_x})")
                        elif curr_x <= x_min and current_dir == "left":
                            pyautogui.keyUp('left'); current_dir = "right"
                            self.log(f"<<< BOUNDARY LEFT (X:{curr_x})")
                        
                        pyautogui.keyDown(current_dir)
                        
                        # 스킬 로직 (공격/이동 분리)
                        a_freq = self.attack_freq.get() / 100.0
                        d_freq = self.dash_freq.get() / 100.0
                        
                        if random.random() < a_freq:
                            self.press_skill(keys["a"])
                        
                        if random.random() < d_freq:
                            self.press_skill(keys["d"])
                            time.sleep(0.05)
                            if random.random() < 0.5: self.press_skill(keys["a"])
                    else:
                        pyautogui.keyUp('left'); pyautogui.keyUp('right')
                else:
                    pyautogui.keyUp('left'); pyautogui.keyUp('right')

                # 프리뷰 가이드라인
                cv2.line(preview_img, (x_min, 0), (x_min, reg["height"]), (0, 173, 181), 1)
                cv2.line(preview_img, (x_max, 0), (x_max, reg["height"]), (0, 173, 181), 1)
                self.update_preview(preview_img)
                time.sleep(0.05)

        pyautogui.keyUp('left'); pyautogui.keyUp('right')

if __name__ == "__main__":
    root = tk.Tk()
    app = AutoHunterV4(root)
    root.mainloop()
