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
CONFIG_FILE = "hunter_premium_config_v4_1.json"

class AutoHunterV4_1:
    def __init__(self, root):
        self.root = root
        self.root.title("오토헌터 프리미엄 v4.1")
        self.root.geometry("520x950")
        self.root.configure(bg="#1e1e1e")
        
        self.is_running = False
        self.base_lower = np.array([245, 230, 0]) 
        self.base_upper = np.array([254, 255, 129]) 
        
        # 고정 핫키 설정
        self.KEY_ATTACK = "end"
        self.KEY_DASH = "space"
        self.KEY_JUMP = "alt"
        
        self.setup_styles()
        
        # 프로필 관련
        self.profiles_data = {}
        self.current_profile_name = tk.StringVar(value="기본 사냥터")
        
        # 설정 변수들
        self.region_top = tk.IntVar(value=100)
        self.region_left = tk.IntVar(value=100)
        self.region_width = tk.IntVar(value=200)
        self.region_height = tk.IntVar(value=150)
        
        self.x_min = tk.IntVar(value=20)
        self.x_max = tk.IntVar(value=180)
        
        self.color_margin = tk.IntVar(value=50) 
        self.attack_delay_ms = tk.IntVar(value=500) # 공격 간격 (ms)
        self.dash_delay_ms = tk.IntVar(value=1500)   # 이동스킬 간격 (ms)
        
        self.setup_ui()
        self.load_all_profiles()
        
        keyboard.add_hotkey('f12', self.toggle_running_from_key)

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TFrame", background="#1e1e1e")
        style.configure("TLabelframe", background="#1e1e1e", foreground="#00adb5", bordercolor="#393e46")
        style.configure("TLabelframe.Label", background="#1e1e1e", foreground="#00adb5", font=("Malgun Gothic", 10, "bold"))
        style.configure("TLabel", background="#1e1e1e", foreground="#eeeeee", font=("Malgun Gothic", 9))
        style.configure("TButton", background="#393e46", foreground="#eeeeee", borderwidth=0, font=("Malgun Gothic", 9, "bold"))
        style.map("TButton", background=[('active', '#00adb5')])
        style.configure("TEntry", fieldbackground="#393e46", foreground="#ffffff", borderwidth=0, insertcolor="white")
        style.configure("TCombobox", fieldbackground="#393e46", foreground="#ffffff", arrowcolor="#00adb5")

    def setup_ui(self):
        main_container = ttk.Frame(self.root, padding="15")
        main_container.pack(fill=tk.BOTH, expand=True)

        # --- 프로필 관리 섹션 ---
        p_group = ttk.LabelFrame(main_container, text=" 사냥터 프로필 관리 ", padding="10")
        p_group.pack(fill=tk.X, pady=(0, 15))
        
        row1 = ttk.Frame(p_group)
        row1.pack(fill=tk.X)
        ttk.Label(row1, text="프로필 선택:").pack(side=tk.LEFT)
        self.profile_combo = ttk.Combobox(row1, values=[], state="readonly", width=20)
        self.profile_combo.pack(side=tk.LEFT, padx=10)
        self.profile_combo.bind("<<ComboboxSelected>>", self.on_profile_change)
        
        ttk.Button(row1, text="삭제", command=self.delete_profile, width=5).pack(side=tk.RIGHT)
        
        row2 = ttk.Frame(p_group)
        row2.pack(fill=tk.X, pady=(10, 0))
        ttk.Label(row2, text="프로필 이름:").pack(side=tk.LEFT)
        self.ent_profile_name = ttk.Entry(row2, textvariable=self.current_profile_name, width=22)
        self.ent_profile_name.pack(side=tk.LEFT, padx=10)
        ttk.Button(row2, text="현재 설정 저장", command=self.save_current_profile).pack(side=tk.RIGHT)

        # --- 1. 미니맵 모니터링 ---
        group1 = ttk.LabelFrame(main_container, text=" 1. 미니맵 실시간 모니터링 ", padding="10")
        group1.pack(fill=tk.X, pady=5)
        ttk.Button(group1, text="미니맵 영역 지정 (F1:좌상, F2:우하)", command=self.start_coord_detection).pack(fill=tk.X, pady=(0, 5))
        self.preview_label = tk.Label(group1, text="미니맵 대기 중...", bg="#121212", fg="#393e46", font=("Malgun Gothic", 8), height=8)
        self.preview_label.pack(fill=tk.X)

        # --- 2. 인식 엔진 설정 ---
        group2 = ttk.LabelFrame(main_container, text=" 2. 인식 정밀도 설정 ", padding="10")
        group2.pack(fill=tk.X, pady=5)
        ttk.Label(group2, text="색상 허용 오차 (Margin):").pack(anchor=tk.W)
        m_frame = ttk.Frame(group2)
        m_frame.pack(fill=tk.X)
        ttk.Scale(m_frame, from_=0, to=150, variable=self.color_margin, orient=tk.HORIZONTAL).pack(side=tk.LEFT, expand=True, fill=tk.X)
        ttk.Entry(m_frame, textvariable=self.color_margin, width=5, font=("Malgun Gothic", 10, "bold")).pack(side=tk.LEFT, padx=5)

        # --- 3. 전투 및 이동 제어 (MS 단위) ---
        group3 = ttk.LabelFrame(main_container, text=" 3. 스킬 사용 주기 설정 (ms 단위) ", padding="10")
        group3.pack(fill=tk.X, pady=5)
        
        # 공격 주기
        ttk.Label(group3, text="공격 스킬 간격 (작을수록 빠름):").pack(anchor=tk.W)
        af_frame = ttk.Frame(group3)
        af_frame.pack(fill=tk.X, pady=(0, 10))
        ttk.Scale(af_frame, from_=100, to=3000, variable=self.attack_delay_ms, orient=tk.HORIZONTAL).pack(side=tk.LEFT, expand=True, fill=tk.X)
        ttk.Entry(af_frame, textvariable=self.attack_delay_ms, width=6, font=("Malgun Gothic", 10, "bold")).pack(side=tk.LEFT, padx=5)
        ttk.Label(af_frame, text="ms").pack(side=tk.LEFT)
        
        # 이동주기
        ttk.Label(group3, text="이동 스킬 간격:").pack(anchor=tk.W)
        df_frame = ttk.Frame(group3)
        df_frame.pack(fill=tk.X)
        ttk.Scale(df_frame, from_=500, to=10000, variable=self.dash_delay_ms, orient=tk.HORIZONTAL).pack(side=tk.LEFT, expand=True, fill=tk.X)
        ttk.Entry(df_frame, textvariable=self.dash_delay_ms, width=6, font=("Malgun Gothic", 10, "bold")).pack(side=tk.LEFT, padx=5)
        ttk.Label(df_frame, text="ms").pack(side=tk.LEFT)

        # --- 4. 범위 및 단축키 안내 ---
        group4 = ttk.LabelFrame(main_container, text=" 4. 활동 범위 및 단축키 정보 ", padding="10")
        group4.pack(fill=tk.X, pady=5)
        
        r_frame = ttk.Frame(group4)
        r_frame.pack(fill=tk.X)
        ttk.Label(r_frame, text="최소 X:").pack(side=tk.LEFT)
        ttk.Entry(r_frame, textvariable=self.x_min, width=8).pack(side=tk.LEFT, padx=5)
        ttk.Label(r_frame, text="최대 X:").pack(side=tk.LEFT, padx=(10, 0))
        ttk.Entry(r_frame, textvariable=self.x_max, width=8).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(group4, text=f"고정 키 - 공격: {self.KEY_ATTACK.upper()} / 이동: {self.KEY_DASH.upper()} / 점프: {self.KEY_JUMP.upper()}", foreground="#00adb5", font=("Malgun Gothic", 8, "bold")).pack(pady=(10, 0))

        # --- 실행 제어 ---
        self.start_btn = tk.Button(main_container, text="매크로 시작 (F12)", bg="#00adb5", fg="white", font=("Malgun Gothic", 12, "bold"), borderwidth=0, command=self.toggle_running)
        self.start_btn.pack(fill=tk.X, pady=15, ipady=10)

        # --- 콘솔 로그 ---
        self.log_text = tk.Text(main_container, height=8, bg="#121212", fg="#eeeeee", borderwidth=0, font=("Consolas", 9), padx=10, pady=10)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        self.log_text.config(state=tk.DISABLED)

    def log(self, msg):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, f"[{time.strftime('%H:%M:%S')}] {msg}\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)

    def start_coord_detection(self):
        self.log("영역 지정 모드: 미니맵 끝에 마우스를 대고 F1, F2를 누르세요.")
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

    # --- 프로필 관리 ---
    def save_current_profile(self):
        p_name = self.current_profile_name.get().strip()
        if not p_name: 
            messagebox.showwarning("알림", "프로필 이름을 입력해주세요.")
            return
            
        self.profiles_data[p_name] = {
            "reg": {"t": self.region_top.get(), "l": self.region_left.get(), "w": self.region_width.get(), "h": self.region_height.get()},
            "range": {"min": self.x_min.get(), "max": self.x_max.get()},
            "params": {"margin": self.color_margin.get(), "ad": self.attack_delay_ms.get(), "dd": self.dash_delay_ms.get()}
        }
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(self.profiles_data, f, ensure_ascii=False)
        
        self.update_profile_list()
        self.profile_combo.set(p_name)
        self.log(f"저장 완료: {p_name}")

    def load_all_profiles(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    self.profiles_data = json.load(f)
                self.update_profile_list()
                if self.profiles_data:
                    first_p = list(self.profiles_data.keys())[0]
                    self.profile_combo.set(first_p)
                    self.apply_profile_data(first_p)
            except: pass

    def update_profile_list(self):
        names = list(self.profiles_data.keys())
        self.profile_combo['values'] = names

    def delete_profile(self):
        p_name = self.profile_combo.get()
        if p_name in self.profiles_data:
            if messagebox.askyesno("확인", f"'{p_name}' 프로필을 삭제하시겠습니까?"):
                del self.profiles_data[p_name]
                with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                    json.dump(self.profiles_data, f, ensure_ascii=False)
                self.update_profile_list()
                self.profile_combo.set("")
                self.log(f"삭제 완료: {p_name}")

    def on_profile_change(self, event):
        p_name = self.profile_combo.get()
        self.apply_profile_data(p_name)
        self.current_profile_name.set(p_name)
        self.log(f"로드 완료: {p_name}")

    def apply_profile_data(self, p_name):
        if p_name in self.profiles_data:
            d = self.profiles_data[p_name]
            self.region_top.set(d["reg"]["t"]); self.region_left.set(d["reg"]["l"])
            self.region_width.set(d["reg"]["w"]); self.region_height.set(d["reg"]["h"])
            self.x_min.set(d["range"]["min"]); self.x_max.set(d["range"]["max"])
            self.color_margin.set(d["params"].get("margin", 50))
            self.attack_delay_ms.set(d["params"].get("ad", 500))
            self.dash_delay_ms.set(d["params"].get("dd", 1500))

    def toggle_running_from_key(self):
        self.root.after(0, self.toggle_running)

    def toggle_running(self):
        if self.is_running:
            self.is_running = False
            self.start_btn.config(text="매크로 시작 (F12)", bg="#00adb5")
            self.log("매크로 중단")
        else:
            self.is_running = True
            self.start_btn.config(text="매크로 중지 (F12)", bg="#ff4b2b")
            self.log("3초 후 시작합니다...")
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
        
        current_dir = "right"
        last_x, stuck_cnt = -1, 0
        
        # 스킬 타이머 초기화
        last_attack_time = time.time()
        last_dash_time = time.time()
        
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
                        cv2.circle(preview_img, (curr_x, curr_y), 6, (0, 255, 0), -1)
                        
                        # 끼임 체크
                        if abs(curr_x - last_x) < 2: stuck_cnt += 1
                        else: stuck_cnt = 0; last_x = curr_x
                        if stuck_cnt > 20:
                            self.log("[!] 끼임 감지 - 점프 탈출")
                            pyautogui.keyUp('left'); pyautogui.keyUp('right')
                            self.press_skill(self.KEY_JUMP)
                            rev = "left" if current_dir == "right" else "right"
                            pyautogui.keyDown(rev); time.sleep(0.6); pyautogui.keyUp(rev)
                            stuck_cnt = 0; continue

                        # 방향 전환
                        if curr_x >= x_max and current_dir == "right":
                            pyautogui.keyUp('right'); current_dir = "left"
                            self.log(f">>> 우측 끝 도달")
                        elif curr_x <= x_min and current_dir == "left":
                            pyautogui.keyUp('left'); current_dir = "right"
                            self.log(f"<<< 좌측 끝 도달")
                        
                        pyautogui.keyDown(current_dir)
                        
                        # --- 스킬 주기 로직 (ms 단위 제어) ---
                        now = time.time()
                        
                        # 공격 주기 체크
                        if (now - last_attack_time) * 1000 >= self.attack_delay_ms.get():
                            self.press_skill(self.KEY_ATTACK)
                            last_attack_time = now
                        
                        # 이동 스킬 주기 체크
                        if (now - last_dash_time) * 1000 >= self.dash_delay_ms.get():
                            self.press_skill(self.KEY_DASH)
                            # 대시 후 연계 공격 (옵션)
                            time.sleep(0.05)
                            self.press_skill(self.KEY_ATTACK)
                            last_dash_time = now
                    else:
                        pyautogui.keyUp('left'); pyautogui.keyUp('right')
                else:
                    pyautogui.keyUp('left'); pyautogui.keyUp('right')

                cv2.line(preview_img, (x_min, 0), (x_min, reg["height"]), (0, 173, 181), 1)
                cv2.line(preview_img, (x_max, 0), (x_max, reg["height"]), (0, 173, 181), 1)
                self.update_preview(preview_img)
                time.sleep(0.05)

        pyautogui.keyUp('left'); pyautogui.keyUp('right')

if __name__ == "__main__":
    root = tk.Tk()
    app = AutoHunterV4_1(root)
    root.mainloop()
