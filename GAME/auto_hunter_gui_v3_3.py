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
CONFIG_FILE = "hunter_config_v3_3.json"

class AutoHunterV3_3:
    def __init__(self, root):
        self.root = root
        self.root.title("Auto-Hunter v3.3 (Pro Hunter)")
        self.root.geometry("450x850")
        
        self.is_running = False
        self.base_lower = np.array([245, 230, 0]) 
        self.base_upper = np.array([254, 255, 129]) 
        
        self.region_top = tk.IntVar(value=100)
        self.region_left = tk.IntVar(value=100)
        self.region_width = tk.IntVar(value=200)
        self.region_height = tk.IntVar(value=150)
        self.x_min = tk.IntVar(value=20)
        self.x_max = tk.IntVar(value=180)
        
        self.color_margin = tk.IntVar(value=50) 
        self.skill_freq = tk.IntVar(value=40) # 스킬 빈도 (%)
        
        self.key_attack = tk.StringVar(value="ctrl")
        self.key_dash = tk.StringVar(value="shift")
        self.key_jump = tk.StringVar(value="space")
        
        self.load_config()
        self.setup_ui()
        
        keyboard.add_hotkey('f12', self.toggle_running_from_key)

    def setup_ui(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # --- 1. 미니맵 영역 설정 ---
        group1 = ttk.LabelFrame(main_frame, text=" 1. 미니맵 영역 설정 ", padding="5")
        group1.pack(fill=tk.X, pady=5)
        ttk.Button(group1, text="미니맵 영역 지정 (F1:좌상, F2:우하)", command=self.start_coord_detection).pack(fill=tk.X, pady=2)
        self.preview_label = ttk.Label(group1, text="실시간 모니터링 창")
        self.preview_label.pack(pady=5)

        # --- 2. 인식 및 스킬 빈도 설정 ---
        group2 = ttk.LabelFrame(main_frame, text=" 2. 인식 및 스킬 제어 ", padding="5")
        group2.pack(fill=tk.X, pady=5)
        
        ttk.Label(group2, text="인식 허용 범위 (Margin):").pack(anchor=tk.W)
        ttk.Scale(group2, from_=0, to=150, variable=self.color_margin, orient=tk.HORIZONTAL).pack(fill=tk.X)
        
        ttk.Label(group2, text="스킬 사용 빈도 (%):").pack(anchor=tk.W, pady=(10, 0))
        ttk.Scale(group2, from_=0, to=100, variable=self.skill_freq, orient=tk.HORIZONTAL).pack(fill=tk.X)
        ttk.Label(group2, textvariable=self.skill_freq).pack(anchor=tk.E)

        # --- 3. 활동 범위 및 키 설정 ---
        group3 = ttk.LabelFrame(main_frame, text=" 3. 활동 범위 및 키 설정 ", padding="5")
        group3.pack(fill=tk.X, pady=5)
        
        range_frame = ttk.Frame(group3)
        range_frame.pack(fill=tk.X)
        ttk.Label(range_frame, text="Min X:").pack(side=tk.LEFT)
        ttk.Entry(range_frame, textvariable=self.x_min, width=7).pack(side=tk.LEFT, padx=5)
        ttk.Label(range_frame, text="Max X:").pack(side=tk.LEFT)
        ttk.Entry(range_frame, textvariable=self.x_max, width=7).pack(side=tk.LEFT, padx=5)

        key_grid = ttk.Frame(group3)
        key_grid.pack(fill=tk.X, pady=5)
        for i, (l, v) in enumerate([("공격", self.key_attack), ("대시", self.key_dash), ("점프", self.key_jump)]):
            ttk.Label(key_grid, text=l).grid(row=0, column=i*2, padx=5)
            ttk.Entry(key_grid, textvariable=v, width=8).grid(row=0, column=i*2+1, padx=2)

        # --- 제어 버튼 ---
        self.start_btn = ttk.Button(main_frame, text="매크로 시작 (F12 종료)", command=self.toggle_running)
        self.start_btn.pack(fill=tk.X, pady=10)
        ttk.Button(main_frame, text="설정 저장", command=self.save_config).pack(fill=tk.X)

        self.log_text = tk.Text(main_frame, height=12, state=tk.DISABLED, font=("Consolas", 9))
        self.log_text.pack(fill=tk.BOTH, expand=True)

    def log(self, msg):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, f"[{time.strftime('%H:%M:%S')}] {msg}\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)

    def start_coord_detection(self):
        self.log("영역 지정 시작 (F1:좌상, F2:우하)")
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
                    self.log(f"영역 설정 완료: {w}x{h}")
                    break
            time.sleep(0.1)

    def save_config(self):
        config = {
            "reg": {"t": self.region_top.get(), "l": self.region_left.get(), "w": self.region_width.get(), "h": self.region_height.get()},
            "range": {"min": self.x_min.get(), "max": self.x_max.get()},
            "keys": {"a": self.key_attack.get(), "d": self.key_dash.get(), "j": self.key_jump.get()},
            "margin": self.color_margin.get(),
            "freq": self.skill_freq.get()
        }
        with open(CONFIG_FILE, "w") as f: json.dump(config, f)
        self.log("설정 저장 완료.")

    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r") as f:
                    c = json.load(f)
                    self.region_top.set(c["reg"]["t"]); self.region_left.set(c["reg"]["l"])
                    self.region_width.set(c["reg"]["w"]); self.region_height.set(c["reg"]["h"])
                    self.x_min.set(c["range"]["min"]); self.x_max.set(c["range"]["max"])
                    self.key_attack.set(c["keys"]["a"]); self.key_dash.set(c["keys"]["d"]); self.key_jump.set(c["keys"]["j"])
                    self.color_margin.set(c.get("margin", 50))
                    self.skill_freq.set(c.get("freq", 40))
            except: pass

    def toggle_running_from_key(self):
        self.root.after(0, self.toggle_running)

    def toggle_running(self):
        if self.is_running:
            self.is_running = False
            self.start_btn.config(text="매크로 시작 (F12 종료)")
            self.log("매크로 중단")
        else:
            self.is_running = True
            self.start_btn.config(text="매크로 중지 (F12)")
            self.log("3초 후 시작합니다...")
            threading.Thread(target=self.hunter_main, daemon=True).start()

    def update_preview(self, img):
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img_pil = Image.fromarray(img_rgb).resize((200, 150), Image.Resampling.LANCZOS)
        img_tk = ImageTk.PhotoImage(img_pil)
        self.preview_label.config(image=img_tk); self.preview_label.image = img_tk

    def press_skill(self, key):
        """게임에서 인식할 수 있도록 키를 일정 시간 눌렀다 뗌"""
        pyautogui.keyDown(key)
        time.sleep(random.uniform(0.08, 0.12)) # 100ms 정도 유지
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
                        cv2.circle(preview_img, (curr_x, curr_y), 5, (0, 0, 255), -1)
                        
                        # 끼임 체크
                        if abs(curr_x - last_x) < 2: stuck_cnt += 1
                        else: stuck_cnt = 0; last_x = curr_x
                        if stuck_cnt > 20:
                            self.log("[!] 끼임 감지 - 탈출")
                            pyautogui.keyUp('left'); pyautogui.keyUp('right')
                            self.press_skill(keys["j"])
                            rev = "left" if current_dir == "right" else "right"
                            pyautogui.keyDown(rev); time.sleep(0.6); pyautogui.keyUp(rev)
                            stuck_cnt = 0; continue

                        # 방향 전환
                        if curr_x >= x_max and current_dir == "right":
                            pyautogui.keyUp('right'); current_dir = "left"
                            self.log(f">>> 우측 끝 (X:{curr_x})")
                        elif curr_x <= x_min and current_dir == "left":
                            pyautogui.keyUp('left'); current_dir = "right"
                            self.log(f"<<< 좌측 끝 (X:{curr_x})")
                        
                        # 이동 유지
                        pyautogui.keyDown(current_dir)
                        
                        # 스킬 사용 확률 체크
                        freq = self.skill_freq.get() / 100.0
                        if random.random() < freq:
                            # 70% 확률로 공격, 30% 확률로 대시 연계
                            if random.random() < 0.7:
                                self.log(f"[전투] {keys['a']} 사용")
                                self.press_skill(keys["a"])
                            else:
                                self.log(f"[이동] {keys['d']} 사용")
                                self.press_skill(keys["d"])
                                time.sleep(0.05)
                                self.press_skill(keys["a"])
                    else:
                        pyautogui.keyUp('left'); pyautogui.keyUp('right')
                else:
                    pyautogui.keyUp('left'); pyautogui.keyUp('right')

                cv2.line(preview_img, (x_min, 0), (x_min, reg["height"]), (255, 0, 0), 1)
                cv2.line(preview_img, (x_max, 0), (x_max, reg["height"]), (255, 0, 0), 1)
                self.update_preview(preview_img)
                time.sleep(0.05)

        pyautogui.keyUp('left'); pyautogui.keyUp('right')

if __name__ == "__main__":
    root = tk.Tk()
    app = AutoHunterV3_3(root)
    root.mainloop()
