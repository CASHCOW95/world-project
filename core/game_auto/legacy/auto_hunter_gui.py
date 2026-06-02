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

# 설정 파일 경로
CONFIG_FILE = "hunter_config.json"

class AutoHunterGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Auto-Hunter Prototype v1.1 (Debug Mode)")
        self.root.geometry("450x650")
        
        self.is_running = False
        self.is_detecting_coords = False
        self.show_debug = tk.BooleanVar(value=True)
        
        # 설정 변수들
        self.region_top = tk.IntVar(value=100)
        self.region_left = tk.IntVar(value=100)
        self.region_width = tk.IntVar(value=200)
        self.region_height = tk.IntVar(value=150)
        
        self.x_min = tk.IntVar(value=20)
        self.x_max = tk.IntVar(value=180)
        
        self.key_attack = tk.StringVar(value="ctrl")
        self.key_dash = tk.StringVar(value="shift")
        self.key_jump = tk.StringVar(value="space")
        
        self.load_config()
        self.setup_ui()
        
        keyboard.add_hotkey('f12', self.toggle_running_from_key)

    def setup_ui(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # --- 미니맵 설정 ---
        ttk.Label(main_frame, text="[ 1. 미니맵 설정 ]", font=("Helvetica", 11, "bold")).pack(pady=5)
        ttk.Button(main_frame, text="영역 지정 (마우스를 미니맵에 대고 F1:좌상, F2:우하)", command=self.start_coord_detection).pack(fill=tk.X, pady=2)
        
        reg_grid = ttk.Frame(main_frame)
        reg_grid.pack(fill=tk.X, pady=5)
        fields = [("Top", self.region_top), ("Left", self.region_left), ("Width", self.region_width), ("Height", self.region_height)]
        for i, (label, var) in enumerate(fields):
            ttk.Label(reg_grid, text=label).grid(row=i//2, column=(i%2)*2, padx=5, pady=2)
            ttk.Entry(reg_grid, textvariable=var, width=10).grid(row=i//2, column=(i%2)*2+1, padx=5, pady=2)

        # --- 활동 범위 ---
        ttk.Label(main_frame, text="[ 2. 활동 범위 (Min X ~ Max X) ]", font=("Helvetica", 11, "bold")).pack(pady=5)
        x_frame = ttk.Frame(main_frame)
        x_frame.pack(fill=tk.X)
        ttk.Label(x_frame, text="Min X:").pack(side=tk.LEFT, padx=5)
        ttk.Entry(x_frame, textvariable=self.x_min, width=8).pack(side=tk.LEFT, padx=5)
        ttk.Label(x_frame, text="Max X:").pack(side=tk.LEFT, padx=5)
        ttk.Entry(x_frame, textvariable=self.x_max, width=8).pack(side=tk.LEFT, padx=5)
        ttk.Label(main_frame, text="(Width 값 안의 숫자로 입력하세요)", foreground="gray").pack()

        # --- 키 설정 ---
        ttk.Label(main_frame, text="[ 3. 키 설정 ]", font=("Helvetica", 11, "bold")).pack(pady=5)
        key_grid = ttk.Frame(main_frame)
        key_grid.pack(fill=tk.X)
        keys = [("공격 키", self.key_attack), ("대시 키", self.key_dash), ("점프 키", self.key_jump)]
        for i, (label, var) in enumerate(keys):
            ttk.Label(key_grid, text=label).grid(row=i, column=0, padx=5, pady=2)
            ttk.Entry(key_grid, textvariable=var, width=15).grid(row=i, column=1, padx=5, pady=2)

        # --- 옵션 ---
        ttk.Checkbutton(main_frame, text="인식 확인 창(Debug) 보이기", variable=self.show_debug).pack(pady=5)

        # --- 제어 ---
        self.start_btn = ttk.Button(main_frame, text="매크로 시작 (F12 종료)", command=self.toggle_running)
        self.start_btn.pack(fill=tk.X, pady=10)
        ttk.Button(main_frame, text="설정 저장", command=self.save_config).pack(fill=tk.X)

        # --- 로그 ---
        self.log_text = tk.Text(main_frame, height=8, state=tk.DISABLED, font=("Consolas", 9))
        self.log_text.pack(fill=tk.BOTH, expand=True, pady=5)

    def log(self, message):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, f"[{time.strftime('%H:%M:%S')}] {message}\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)

    def start_coord_detection(self):
        if self.is_detecting_coords: return
        self.is_detecting_coords = True
        self.log("영역 지정 시작: 미니맵 끝에 마우스 대고 F1, F2 누르기")
        threading.Thread(target=self._coord_detection_thread, daemon=True).start()

    def _coord_detection_thread(self):
        t_l = None
        while self.is_detecting_coords:
            if keyboard.is_pressed('f1'):
                t_l = pyautogui.position()
                self.region_top.set(t_l.y); self.region_left.set(t_l.x)
                self.log(f"좌상단 확정: ({t_l.x}, {t_l.y})")
                time.sleep(0.5)
            if keyboard.is_pressed('f2'):
                br = pyautogui.position()
                if t_l:
                    w, h = br.x - t_l.x, br.y - t_l.y
                    self.region_width.set(w); self.region_height.set(h)
                    self.x_max.set(w - 20) # 자동 Max X 추천값
                    self.log(f"설정 완료: {w}x{h} 크기")
                    self.is_detecting_coords = False
                time.sleep(0.5)
            time.sleep(0.1)

    def save_config(self):
        config = {
            "region": {"top": self.region_top.get(), "left": self.region_left.get(), "width": self.region_width.get(), "height": self.region_height.get()},
            "x_range": {"min": self.x_min.get(), "max": self.x_max.get()},
            "keys": {"attack": self.key_attack.get(), "dash": self.key_dash.get(), "jump": self.key_jump.get()}
        }
        with open(CONFIG_FILE, "w") as f: json.dump(config, f)
        self.log("설정 저장 완료.")

    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r") as f:
                    c = json.load(f)
                    self.region_top.set(c["region"]["top"]); self.region_left.set(c["region"]["left"])
                    self.region_width.set(c["region"]["width"]); self.region_height.set(c["region"]["height"])
                    self.x_min.set(c["x_range"]["min"]); self.x_max.set(c["x_range"]["max"])
                    self.key_attack.set(c["keys"]["attack"]); self.key_dash.set(c["keys"]["dash"]); self.key_jump.set(c["keys"]["jump"])
            except: pass

    def toggle_running_from_key(self):
        self.root.after(0, self.toggle_running)

    def toggle_running(self):
        if self.is_running:
            self.is_running = False
            self.start_btn.config(text="매크로 시작 (F12 종료)")
            cv2.destroyAllWindows()
            self.log("매크로 중단.")
        else:
            self.is_running = True
            self.start_btn.config(text="매크로 중지 (F12)")
            self.log("3초 후 시작합니다...")
            threading.Thread(target=self.hunter_main, daemon=True).start()

    def hunter_main(self):
        time.sleep(3)
        reg = {"top": self.region_top.get(), "left": self.region_left.get(), "width": self.region_width.get(), "height": self.region_height.get()}
        x_min, x_max = self.x_min.get(), self.x_max.get()
        keys = {"attack": self.key_attack.get(), "dash": self.key_dash.get(), "jump": self.key_jump.get()}
        
        current_dir = "right"
        last_x, stuck_cnt = -1, 0
        
        with mss.mss() as sct:
            while self.is_running:
                # 1. 화면 캡처 및 인식
                screenshot = np.array(sct.grab(reg))
                img_bgr = cv2.cvtColor(screenshot, cv2.COLOR_BGRA2BGR)
                
                # [개선] 노란색 점 찾기 (일반적인 캐릭터 점) + 가장 밝은 곳 하이브리드
                hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)
                lower_yellow = np.array([20, 100, 100])
                upper_yellow = np.array([40, 255, 255])
                mask = cv2.inRange(hsv, lower_yellow, upper_yellow)
                
                # 노란색 점이 있으면 그곳을, 없으면 가장 밝은 곳을 선택
                if np.any(mask):
                    M = cv2.moments(mask)
                    curr_x = int(M["m10"] / M["m00"])
                    curr_y = int(M["m01"] / M["m00"])
                else:
                    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
                    _, _, _, max_loc = cv2.minMaxLoc(gray)
                    curr_x, curr_y = max_loc
                
                # 2. 디버그 창 업데이트
                if self.show_debug.get():
                    debug_img = img_bgr.copy()
                    cv2.circle(debug_img, (curr_x, curr_y), 5, (0, 0, 255), -1) # 빨간 점
                    cv2.line(debug_img, (x_min, 0), (x_min, reg["height"]), (255, 0, 0), 1) # Min X 선
                    cv2.line(debug_img, (x_max, 0), (x_max, reg["height"]), (255, 0, 0), 1) # Max X 선
                    cv2.imshow("Macro Monitor (Debug)", debug_img)
                    cv2.waitKey(1)

                # 3. 끼임 방지
                if curr_x == last_x: stuck_cnt += 1
                else: stuck_cnt = 0; last_x = curr_x
                if stuck_cnt > 25:
                    self.log(f"[!] 끼임 감지 (X:{curr_x}) - 점프 시도")
                    pyautogui.keyUp('left'); pyautogui.keyUp('right')
                    pyautogui.press(keys["jump"])
                    rev = "left" if current_dir == "right" else "right"
                    pyautogui.keyDown(rev); time.sleep(0.5); pyautogui.keyUp(rev)
                    stuck_cnt = 0; continue

                # 4. 방향 제어 로직
                if curr_x >= x_max:
                    if current_dir != "left":
                        pyautogui.keyUp('right'); current_dir = "left"
                        self.log(f">>> 우측 끝 도달 (X:{curr_x}) -> 좌측 이동")
                elif curr_x <= x_min:
                    if current_dir != "right":
                        pyautogui.keyUp('left'); current_dir = "right"
                        self.log(f"<<< 좌측 끝 도달 (X:{curr_x}) -> 우측 이동")
                
                # 5. 공격 및 이동
                pyautogui.keyDown(current_dir)
                if random.random() < 0.2: # 20% 확률로 스킬
                    pyautogui.press(keys["dash"])
                    time.sleep(random.uniform(0.05, 0.1))
                    pyautogui.press(keys["attack"])
                
                time.sleep(random.uniform(0.1, 0.2))

        pyautogui.keyUp('left'); pyautogui.keyUp('right')
        cv2.destroyAllWindows()

if __name__ == "__main__":
    root = tk.Tk()
    app = AutoHunterGUI(root)
    root.mainloop()
