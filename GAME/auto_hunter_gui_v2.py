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
CONFIG_FILE = "hunter_config_v2.json"
TEMPLATE_FILE = "player_template.png"

class AutoHunterV2:
    def __init__(self, root):
        self.root = root
        self.root.title("Auto-Hunter v2.0 (Template Matching)")
        self.root.geometry("500x800")
        
        self.is_running = False
        self.is_detecting_coords = False
        self.template_img = None
        
        # 설정 변수들
        self.region_top = tk.IntVar(value=100)
        self.region_left = tk.IntVar(value=100)
        self.region_width = tk.IntVar(value=200)
        self.region_height = tk.IntVar(value=150)
        
        self.x_min = tk.IntVar(value=20)
        self.x_max = tk.IntVar(value=180)
        self.conf_threshold = tk.DoubleVar(value=0.7) # 인식 신뢰도 임계값
        
        self.key_attack = tk.StringVar(value="ctrl")
        self.key_dash = tk.StringVar(value="shift")
        self.key_jump = tk.StringVar(value="space")
        
        self.load_config()
        self.setup_ui()
        
        # 종료 단축키
        keyboard.add_hotkey('f12', self.toggle_running_from_key)

    def setup_ui(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # --- 1. 미니맵 영역 및 템플릿 ---
        group1 = ttk.LabelFrame(main_frame, text=" 1. 미니맵 및 캐릭터 인식 ", padding="5")
        group1.pack(fill=tk.X, pady=5)
        
        ttk.Button(group1, text="미니맵 영역 지정 (F1:좌상, F2:우하)", command=self.start_coord_detection).pack(fill=tk.X, pady=2)
        ttk.Button(group1, text="캐릭터 점 이미지 캡처 (마우스를 점 위에 두고 F3)", command=self.start_template_capture).pack(fill=tk.X, pady=2)
        
        # 미니맵 실시간 프리뷰 라벨
        self.preview_label = ttk.Label(group1, text="미니맵 프리뷰 영역")
        self.preview_label.pack(pady=5)

        # --- 2. 활동 범위 및 인식 정밀도 ---
        group2 = ttk.LabelFrame(main_frame, text=" 2. 세부 설정 ", padding="5")
        group2.pack(fill=tk.X, pady=5)
        
        range_frame = ttk.Frame(group2)
        range_frame.pack(fill=tk.X)
        ttk.Label(range_frame, text="Min X:").pack(side=tk.LEFT)
        ttk.Entry(range_frame, textvariable=self.x_min, width=7).pack(side=tk.LEFT, padx=5)
        ttk.Label(range_frame, text="Max X:").pack(side=tk.LEFT)
        ttk.Entry(range_frame, textvariable=self.x_max, width=7).pack(side=tk.LEFT, padx=5)
        
        conf_frame = ttk.Frame(group2)
        conf_frame.pack(fill=tk.X, pady=5)
        ttk.Label(conf_frame, text="인식 정밀도(0.5~0.9):").pack(side=tk.LEFT)
        ttk.Entry(conf_frame, textvariable=self.conf_threshold, width=7).pack(side=tk.LEFT, padx=5)

        # --- 3. 키 설정 ---
        group3 = ttk.LabelFrame(main_frame, text=" 3. 단축키 설정 ", padding="5")
        group3.pack(fill=tk.X, pady=5)
        key_grid = ttk.Frame(group3)
        key_grid.pack(fill=tk.X)
        for i, (l, v) in enumerate([("공격", self.key_attack), ("대시", self.key_dash), ("점프", self.key_jump)]):
            ttk.Label(key_grid, text=l).grid(row=0, column=i*2, padx=5)
            ttk.Entry(key_grid, textvariable=v, width=8).grid(row=0, column=i*2+1, padx=2)

        # --- 제어 버튼 ---
        self.start_btn = ttk.Button(main_frame, text="매크로 시작 (F12 종료)", command=self.toggle_running)
        self.start_btn.pack(fill=tk.X, pady=10)
        ttk.Button(main_frame, text="설정 저장", command=self.save_config).pack(fill=tk.X)

        # --- 로그창 ---
        self.log_text = tk.Text(main_frame, height=12, state=tk.DISABLED, font=("Consolas", 9))
        self.log_text.pack(fill=tk.BOTH, expand=True)

    def log(self, msg):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, f"[{time.strftime('%H:%M:%S')}] {msg}\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)

    # --- 유틸리티 기능 ---
    def start_coord_detection(self):
        self.is_detecting_coords = True
        self.log("영역 지정 모드: 미니맵 좌상/우하단에 마우스 대고 F1, F2 클릭")
        threading.Thread(target=self._detection_worker, args=('coord',), daemon=True).start()

    def start_template_capture(self):
        self.log("템플릿 캡처: 캐릭터 점 위에 마우스 대고 F3 클릭")
        threading.Thread(target=self._detection_worker, args=('template',), daemon=True).start()

    def _detection_worker(self, mode):
        t_l = None
        while True:
            if mode == 'coord':
                if keyboard.is_pressed('f1'):
                    t_l = pyautogui.position()
                    self.region_top.set(t_l.y); self.region_left.set(t_l.x)
                    self.log(f"좌상단 확정: {t_l}")
                    time.sleep(0.5)
                if keyboard.is_pressed('f2'):
                    br = pyautogui.position()
                    if t_l:
                        self.region_width.set(br.x - t_l.x); self.region_height.set(br.y - t_l.y)
                        self.log(f"영역 설정 완료: {br.x - t_l.x}x{br.y - t_l.y}")
                        break
            elif mode == 'template':
                if keyboard.is_pressed('f3'):
                    p = pyautogui.position()
                    # 마우스 주변 10x10 영역 캡처
                    with mss.mss() as sct:
                        shot = np.array(sct.grab({"top": p.y-5, "left": p.x-5, "width": 10, "height": 10}))
                        cv2.imwrite(TEMPLATE_FILE, cv2.cvtColor(shot, cv2.COLOR_BGRA2BGR))
                        self.template_img = cv2.imread(TEMPLATE_FILE, 0)
                        self.log("캐릭터 템플릿 저장 완료 (player_template.png)")
                        break
            time.sleep(0.1)

    def save_config(self):
        config = {
            "region": {"top": self.region_top.get(), "left": self.region_left.get(), "width": self.region_width.get(), "height": self.region_height.get()},
            "x_range": {"min": self.x_min.get(), "max": self.x_max.get()},
            "keys": {"attack": self.key_attack.get(), "dash": self.key_dash.get(), "jump": self.key_jump.get()},
            "conf": self.conf_threshold.get()
        }
        with open(CONFIG_FILE, "w") as f: json.dump(config, f)
        self.log("설정 파일 저장 완료.")

    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r") as f:
                    c = json.load(f)
                    self.region_top.set(c["region"]["top"]); self.region_left.set(c["region"]["left"])
                    self.region_width.set(c["region"]["width"]); self.region_height.set(c["region"]["height"])
                    self.x_min.set(c["x_range"]["min"]); self.x_max.set(c["x_range"]["max"])
                    self.key_attack.set(c["keys"]["attack"]); self.key_dash.set(c["keys"]["dash"]); self.key_jump.set(c["keys"]["jump"])
                    self.conf_threshold.set(c.get("conf", 0.7))
            except: pass
        if os.path.exists(TEMPLATE_FILE):
            self.template_img = cv2.imread(TEMPLATE_FILE, 0)

    def toggle_running_from_key(self):
        self.root.after(0, self.toggle_running)

    def toggle_running(self):
        if self.is_running:
            self.is_running = False
            self.start_btn.config(text="매크로 시작 (F12 종료)")
            self.log("매크로 중단")
        else:
            if self.template_img is None:
                messagebox.showerror("오류", "먼저 캐릭터 점 이미지를 캡처(F3)해주세요!")
                return
            self.is_running = True
            self.start_btn.config(text="매크로 중지 (F12)")
            self.log("3초 후 시작합니다...")
            threading.Thread(target=self.hunter_main, daemon=True).start()

    def update_preview(self, img):
        """GUI 내부에 프리뷰 업데이트"""
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img_pil = Image.fromarray(img_rgb)
        # 크기 조절 (GUI에 맞게)
        img_pil = img_pil.resize((200, 150), Image.Resampling.LANCZOS)
        img_tk = ImageTk.PhotoImage(img_pil)
        self.preview_label.config(image=img_tk)
        self.preview_label.image = img_tk

    def hunter_main(self):
        time.sleep(3)
        reg = {"top": self.region_top.get(), "left": self.region_left.get(), "width": self.region_width.get(), "height": self.region_height.get()}
        x_min, x_max = self.x_min.get(), self.x_max.get()
        keys = {"attack": self.key_attack.get(), "dash": self.key_dash.get(), "jump": self.key_jump.get()}
        threshold = self.conf_threshold.get()
        
        current_dir = "right"
        last_x, stuck_cnt = -1, 0
        
        with mss.mss() as sct:
            while self.is_running:
                # 1. 캡처 및 템플릿 매칭
                screenshot = np.array(sct.grab(reg))
                img_gray = cv2.cvtColor(screenshot, cv2.COLOR_BGRA2GRAY)
                
                res = cv2.matchTemplate(img_gray, self.template_img, cv2.TM_CCOEFF_NORMED)
                min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
                
                curr_x, curr_y = max_loc
                confidence = max_val
                
                # 프리뷰용 이미지 생성
                preview_img = cv2.cvtColor(screenshot, cv2.COLOR_BGRA2BGR)
                
                # 2. 결과 분석
                if confidence < threshold:
                    self.log(f"[?] 캐릭터 분실 (신뢰도:{confidence:.2f}) - 정지 중")
                    pyautogui.keyUp('left'); pyautogui.keyUp('right')
                    self.update_preview(preview_img)
                    time.sleep(0.5)
                    continue

                # 인식 성공 시 시각화
                cv2.rectangle(preview_img, max_loc, (max_loc[0]+10, max_loc[1]+10), (0, 0, 255), 2)
                cv2.line(preview_img, (x_min, 0), (x_min, reg["height"]), (255, 0, 0), 1)
                cv2.line(preview_img, (x_max, 0), (x_max, reg["height"]), (255, 0, 0), 1)
                self.update_preview(preview_img)

                # 3. 끼임 방지
                if abs(curr_x - last_x) < 2: stuck_cnt += 1
                else: stuck_cnt = 0; last_x = curr_x
                
                if stuck_cnt > 20:
                    self.log(f"[!] 끼임 감지 (X:{curr_x}) - 탈출 시도")
                    pyautogui.keyUp('left'); pyautogui.keyUp('right')
                    pyautogui.press(keys["jump"])
                    rev = "left" if current_dir == "right" else "right"
                    pyautogui.keyDown(rev); time.sleep(0.6); pyautogui.keyUp(rev)
                    stuck_cnt = 0; continue

                # 4. 방향 제어
                if curr_x >= x_max:
                    if current_dir != "left":
                        pyautogui.keyUp('right'); current_dir = "left"
                        self.log(f">>> 우측 끝 (X:{curr_x}, Conf:{confidence:.2f}) -> 좌측 이동")
                elif curr_x <= x_min:
                    if current_dir != "right":
                        pyautogui.keyUp('left'); current_dir = "right"
                        self.log(f"<<< 좌측 끝 (X:{curr_x}, Conf:{confidence:.2f}) -> 우측 이동")
                
                # 5. 행동
                pyautogui.keyDown(current_dir)
                if random.random() < 0.25:
                    pyautogui.press(keys["dash"])
                    time.sleep(random.uniform(0.05, 0.1))
                    pyautogui.press(keys["attack"])
                
                time.sleep(random.uniform(0.1, 0.2))

        pyautogui.keyUp('left'); pyautogui.keyUp('right')

if __name__ == "__main__":
    root = tk.Tk()
    app = AutoHunterV2(root)
    root.mainloop()
