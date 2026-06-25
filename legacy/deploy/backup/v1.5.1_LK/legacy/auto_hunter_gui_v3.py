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
CONFIG_FILE = "hunter_config_v3.json"

class AutoHunterV3:
    def __init__(self, root):
        self.root = root
        self.root.title("Auto-Hunter v3.0 (Color Tracker)")
        self.root.geometry("450x700")
        
        self.is_running = False
        self.target_color = None # (B, G, R)
        
        # 설정 변수들
        self.region_top = tk.IntVar(value=100)
        self.region_left = tk.IntVar(value=100)
        self.region_width = tk.IntVar(value=200)
        self.region_height = tk.IntVar(value=150)
        
        self.x_min = tk.IntVar(value=20)
        self.x_max = tk.IntVar(value=180)
        self.color_tolerance = tk.IntVar(value=30) # 색상 오차 허용 범위
        
        self.key_attack = tk.StringVar(value="ctrl")
        self.key_dash = tk.StringVar(value="shift")
        self.key_jump = tk.StringVar(value="space")
        
        self.load_config()
        self.setup_ui()
        
        keyboard.add_hotkey('f12', self.toggle_running_from_key)

    def setup_ui(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # --- 1. 미니맵 및 색상 설정 ---
        group1 = ttk.LabelFrame(main_frame, text=" 1. 미니맵 및 캐릭터 색상 인식 ", padding="5")
        group1.pack(fill=tk.X, pady=5)
        
        ttk.Button(group1, text="미니맵 영역 지정 (F1:좌상, F2:우하)", command=self.start_coord_detection).pack(fill=tk.X, pady=2)
        ttk.Button(group1, text="캐릭터 색상 샘플링 (점 위에 마우스 대고 F3)", command=self.start_color_sampling).pack(fill=tk.X, pady=2)
        
        # 선택된 색상 표시
        self.color_preview = tk.Label(group1, text="선택된 색상", bg="gray", width=20)
        self.color_preview.pack(pady=5)

        self.preview_label = ttk.Label(group1, text="실시간 모니터링 창")
        self.preview_label.pack(pady=5)

        # --- 2. 범위 및 정밀도 ---
        group2 = ttk.LabelFrame(main_frame, text=" 2. 세부 설정 ", padding="5")
        group2.pack(fill=tk.X, pady=5)
        
        range_frame = ttk.Frame(group2)
        range_frame.pack(fill=tk.X)
        ttk.Label(range_frame, text="Min X:").pack(side=tk.LEFT)
        ttk.Entry(range_frame, textvariable=self.x_min, width=7).pack(side=tk.LEFT, padx=5)
        ttk.Label(range_frame, text="Max X:").pack(side=tk.LEFT)
        ttk.Entry(range_frame, textvariable=self.x_max, width=7).pack(side=tk.LEFT, padx=5)
        
        tol_frame = ttk.Frame(group2)
        tol_frame.pack(fill=tk.X, pady=5)
        ttk.Label(tol_frame, text="색상 오차 범위 (10~100):").pack(side=tk.LEFT)
        ttk.Entry(tol_frame, textvariable=self.color_tolerance, width=7).pack(side=tk.LEFT, padx=5)

        # --- 3. 키 설정 ---
        group3 = ttk.LabelFrame(main_frame, text=" 3. 키 설정 ", padding="5")
        group3.pack(fill=tk.X, pady=5)
        key_grid = ttk.Frame(group3)
        key_grid.pack(fill=tk.X)
        for i, (l, v) in enumerate([("공격", self.key_attack), ("대시", self.key_dash), ("점프", self.key_jump)]):
            ttk.Label(key_grid, text=l).grid(row=0, column=i*2, padx=5)
            ttk.Entry(key_grid, textvariable=v, width=8).grid(row=0, column=i*2+1, padx=2)

        # --- 버튼 ---
        self.start_btn = ttk.Button(main_frame, text="매크로 시작 (F12 종료)", command=self.toggle_running)
        self.start_btn.pack(fill=tk.X, pady=10)
        ttk.Button(main_frame, text="설정 저장", command=self.save_config).pack(fill=tk.X)

        self.log_text = tk.Text(main_frame, height=10, state=tk.DISABLED, font=("Consolas", 9))
        self.log_text.pack(fill=tk.BOTH, expand=True)

    def log(self, msg):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, f"[{time.strftime('%H:%M:%S')}] {msg}\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)

    def start_coord_detection(self):
        self.log("영역 지정: F1(좌상), F2(우하)를 누르세요.")
        threading.Thread(target=self._worker, args=('coord',), daemon=True).start()

    def start_color_sampling(self):
        self.log("색상 샘플링: 캐릭터 점 위에 마우스를 대고 F3을 누르세요.")
        threading.Thread(target=self._worker, args=('color',), daemon=True).start()

    def _worker(self, mode):
        t_l = None
        while True:
            if mode == 'coord':
                if keyboard.is_pressed('f1'):
                    t_l = pyautogui.position()
                    self.region_top.set(t_l.y); self.region_left.set(t_l.x)
                    time.sleep(0.5)
                if keyboard.is_pressed('f2'):
                    br = pyautogui.position()
                    if t_l:
                        self.region_width.set(br.x - t_l.x); self.region_height.set(br.y - t_l.y)
                        self.log(f"영역 설정 완료: {br.x-t_l.x}x{br.y-t_l.y}")
                        break
            elif mode == 'color':
                if keyboard.is_pressed('f3'):
                    p = pyautogui.position()
                    color = pyautogui.pixel(p.x, p.y) # (R, G, B)
                    self.target_color = (color[2], color[1], color[0]) # BGR 변환
                    hex_color = '#%02x%02x%02x' % color
                    self.color_preview.config(bg=hex_color, text=f"RGB: {color}")
                    self.log(f"색상 샘플링 완료: {color}")
                    break
            time.sleep(0.1)

    def save_config(self):
        config = {
            "reg": {"t": self.region_top.get(), "l": self.region_left.get(), "w": self.region_width.get(), "h": self.region_height.get()},
            "range": {"min": self.x_min.get(), "max": self.x_max.get()},
            "keys": {"a": self.key_attack.get(), "d": self.key_dash.get(), "j": self.key_jump.get()},
            "tol": self.color_tolerance.get(),
            "color": self.target_color
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
                    self.color_tolerance.set(c.get("tol", 30))
                    self.target_color = c.get("color")
                    if self.target_color:
                        hex_c = '#%02x%02x%02x' % (self.target_color[2], self.target_color[1], self.target_color[0])
                        self.color_preview.config(bg=hex_c, text=f"로드된 색상")
            except: pass

    def toggle_running_from_key(self):
        self.root.after(0, self.toggle_running)

    def toggle_running(self):
        if self.is_running:
            self.is_running = False
            self.start_btn.config(text="매크로 시작 (F12 종료)")
            self.log("매크로 중단")
        else:
            if self.target_color is None:
                messagebox.showerror("오류", "먼저 캐릭터 색상을 샘플링(F3)해주세요!")
                return
            self.is_running = True
            self.start_btn.config(text="매크로 중지 (F12)")
            self.log("3초 후 시작합니다...")
            threading.Thread(target=self.hunter_main, daemon=True).start()

    def update_preview(self, img):
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img_pil = Image.fromarray(img_rgb).resize((200, 150), Image.Resampling.LANCZOS)
        img_tk = ImageTk.PhotoImage(img_pil)
        self.preview_label.config(image=img_tk); self.preview_label.image = img_tk

    def hunter_main(self):
        time.sleep(3)
        reg = {"top": self.region_top.get(), "left": self.region_left.get(), "width": self.region_width.get(), "height": self.region_height.get()}
        x_min, x_max = self.x_min.get(), self.x_max.get()
        keys = {"a": self.key_attack.get(), "d": self.key_dash.get(), "j": self.key_jump.get()}
        tol = self.color_tolerance.get()
        target = np.array(self.target_color)
        
        current_dir = "right"
        last_x, stuck_cnt = -1, 0
        
        with mss.mss() as sct:
            while self.is_running:
                screenshot = np.array(sct.grab(reg))
                img = cv2.cvtColor(screenshot, cv2.COLOR_BGRA2BGR)
                
                # 색상 기반 마스크 생성 (오차 범위 내 픽셀 찾기)
                lower = np.clip(target - tol, 0, 255)
                upper = np.clip(target + tol, 0, 255)
                mask = cv2.inRange(img, lower, upper)
                
                # 결과 시각화 준비
                preview_img = img.copy()
                
                if np.any(mask):
                    # 해당 색상을 가진 픽셀들의 중심점 찾기
                    coords = cv2.findNonZero(mask)
                    curr_x = int(np.mean(coords[:, :, 0]))
                    curr_y = int(np.mean(coords[:, :, 1]))
                    
                    cv2.circle(preview_img, (curr_x, curr_y), 5, (0, 0, 255), -1)
                    
                    # 끼임 및 방향 제어
                    if abs(curr_x - last_x) < 2: stuck_cnt += 1
                    else: stuck_cnt = 0; last_x = curr_x
                    
                    if stuck_cnt > 20:
                        self.log(f"[!] 끼임 감지 - 점프 탈출")
                        pyautogui.keyUp('left'); pyautogui.keyUp('right')
                        pyautogui.press(keys["j"])
                        rev = "left" if current_dir == "right" else "right"
                        pyautogui.keyDown(rev); time.sleep(0.6); pyautogui.keyUp(rev)
                        stuck_cnt = 0; continue

                    if curr_x >= x_max and current_dir == "right":
                        pyautogui.keyUp('right'); current_dir = "left"
                        self.log(f">>> 우측 끝 도달 (X:{curr_x}) -> 좌측 이동")
                    elif curr_x <= x_min and current_dir == "left":
                        pyautogui.keyUp('left'); current_dir = "right"
                        self.log(f"<<< 좌측 끝 도달 (X:{curr_x}) -> 우측 이동")
                    
                    pyautogui.keyDown(current_dir)
                    if random.random() < 0.2:
                        pyautogui.press(keys["d"])
                        time.sleep(random.uniform(0.05, 0.1))
                        pyautogui.press(keys["a"])
                else:
                    self.log("[?] 캐릭터 색상 못 찾음 - 정지 중")
                    pyautogui.keyUp('left'); pyautogui.keyUp('right')

                cv2.line(preview_img, (x_min, 0), (x_min, reg["height"]), (255, 0, 0), 1)
                cv2.line(preview_img, (x_max, 0), (x_max, reg["height"]), (255, 0, 0), 1)
                self.update_preview(preview_img)
                time.sleep(0.1)

        pyautogui.keyUp('left'); pyautogui.keyUp('right')

if __name__ == "__main__":
    root = tk.Tk()
    app = AutoHunterV3(root)
    root.mainloop()
