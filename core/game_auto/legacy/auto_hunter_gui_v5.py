import tkinter as tk
from tkinter import ttk, messagebox
import cv2
import numpy as np
import pyautogui
import time
import random
import keyboard
import threading
import json
import os
import win32gui, win32ui, win32con, win32api
from PIL import Image, ImageTk

# 설정 파일 경로
CONFIG_FILE = "hunter_premium_config_v5.json"
WINDOW_TITLE = "MapleStory Worlds-메이"

class AutoHunterV5:
    def __init__(self, root):
        self.root = root
        self.root.title("오토헌터 비활성 v5.0 (PREMIUM)")
        self.root.geometry("520x980")
        self.root.configure(bg="#1e1e1e")
        
        self.is_running = False
        self.hwnd = None
        
        # 기본 RGB 범위 (노란색)
        self.base_lower = np.array([245, 230, 0]) 
        self.base_upper = np.array([254, 255, 129]) 
        
        # 고정 핫키 (가상 키코드)
        self.VK_ATTACK = win32con.VK_END
        self.VK_DASH = win32con.VK_SPACE
        self.VK_JUMP = win32con.VK_MENU # ALT
        
        # 방향키 가상 키코드
        self.VK_LEFT = win32con.VK_LEFT
        self.VK_RIGHT = win32con.VK_RIGHT

        self.setup_styles()
        
        # 설정 변수 (창 기준 상대 좌표)
        self.current_profile_name = tk.StringVar(value="사냥터 1")
        self.rel_top = tk.IntVar(value=50)
        self.rel_left = tk.IntVar(value=50)
        self.rel_width = tk.IntVar(value=200)
        self.rel_height = tk.IntVar(value=150)
        
        self.x_min = tk.IntVar(value=20)
        self.x_max = tk.IntVar(value=180)
        self.color_margin = tk.IntVar(value=50) 
        self.attack_delay_ms = tk.IntVar(value=500)
        self.dash_delay_ms = tk.IntVar(value=1500)
        
        self.profiles_data = {}
        self.setup_ui()
        self.load_all_profiles()
        
        # 매크로 시작/종료 단축키 (비동기 리스너)
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
        style.configure("TEntry", fieldbackground="#393e46", foreground="#ffffff", borderwidth=0)
        style.configure("TCombobox", fieldbackground="#393e46", foreground="#ffffff", arrowcolor="#00adb5")

    def setup_ui(self):
        main_container = ttk.Frame(self.root, padding="15")
        main_container.pack(fill=tk.BOTH, expand=True)

        # --- 프로필 섹션 ---
        p_group = ttk.LabelFrame(main_container, text=" [ 사냥터 프로필 관리 ] ", padding="10")
        p_group.pack(fill=tk.X, pady=(0, 10))
        
        row1 = ttk.Frame(p_group)
        row1.pack(fill=tk.X)
        self.profile_combo = ttk.Combobox(row1, state="readonly", width=20)
        self.profile_combo.pack(side=tk.LEFT, padx=5)
        self.profile_combo.bind("<<ComboboxSelected>>", self.on_profile_change)
        ttk.Button(row1, text="삭제", command=self.delete_profile, width=5).pack(side=tk.RIGHT)
        
        row2 = ttk.Frame(p_group)
        row2.pack(fill=tk.X, pady=(10, 0))
        ttk.Entry(row2, textvariable=self.current_profile_name, width=22).pack(side=tk.LEFT, padx=5)
        ttk.Button(row2, text="현재 설정 저장", command=self.save_current_profile).pack(side=tk.RIGHT)

        # --- 1. 미니맵 설정 ---
        group1 = ttk.LabelFrame(main_container, text=" 1. 비활성 미니맵 설정 (창 기준) ", padding="10")
        group1.pack(fill=tk.X, pady=5)
        ttk.Button(group1, text="영역 지정 (F1:좌상, F2:우하)", command=self.start_coord_detection).pack(fill=tk.X, pady=(0, 5))
        self.preview_label = tk.Label(group1, text="창을 찾을 수 없습니다.", bg="#121212", fg="#ff4b2b", font=("Malgun Gothic", 8), height=10)
        self.preview_label.pack(fill=tk.X)

        # --- 2. 정밀도 ---
        group2 = ttk.LabelFrame(main_container, text=" 2. 인식 정밀도 및 마진 ", padding="10")
        group2.pack(fill=tk.X, pady=5)
        m_frame = ttk.Frame(group2)
        m_frame.pack(fill=tk.X)
        ttk.Scale(m_frame, from_=0, to=150, variable=self.color_margin, orient=tk.HORIZONTAL).pack(side=tk.LEFT, expand=True, fill=tk.X)
        ttk.Entry(m_frame, textvariable=self.color_margin, width=5).pack(side=tk.LEFT, padx=5)

        # --- 3. 비활성 주기 설정 ---
        group3 = ttk.LabelFrame(main_container, text=" 3. 비활성 스킬 주기 (ms) ", padding="10")
        group3.pack(fill=tk.X, pady=5)
        
        for label, var, max_val in [("공격 주기:", self.attack_delay_ms, 3000), ("이동 주기:", self.dash_delay_ms, 10000)]:
            ttk.Label(group3, text=label).pack(anchor=tk.W)
            f = ttk.Frame(group3)
            f.pack(fill=tk.X, pady=(0, 5))
            ttk.Scale(f, from_=100, to=max_val, variable=var, orient=tk.HORIZONTAL).pack(side=tk.LEFT, expand=True, fill=tk.X)
            ttk.Entry(f, textvariable=var, width=6).pack(side=tk.LEFT, padx=5)
            ttk.Label(f, text="ms").pack(side=tk.LEFT)

        # --- 4. 범위 설정 ---
        group4 = ttk.LabelFrame(main_container, text=" 4. 활동 범위 ", padding="10")
        group4.pack(fill=tk.X, pady=5)
        r_frame = ttk.Frame(group4)
        r_frame.pack(fill=tk.X)
        ttk.Label(r_frame, text="최소 X:").pack(side=tk.LEFT)
        ttk.Entry(r_frame, textvariable=self.x_min, width=8).pack(side=tk.LEFT, padx=5)
        ttk.Label(r_frame, text="최대 X:").pack(side=tk.LEFT, padx=(10, 0))
        ttk.Entry(r_frame, textvariable=self.x_max, width=8).pack(side=tk.LEFT, padx=5)

        # --- 실행 ---
        self.start_btn = tk.Button(main_container, text="비활성 매크로 시작 (F12)", bg="#00adb5", fg="white", font=("Malgun Gothic", 12, "bold"), borderwidth=0, command=self.toggle_running)
        self.start_btn.pack(fill=tk.X, pady=10, ipady=8)

        self.log_text = tk.Text(main_container, height=8, bg="#121212", fg="#eeeeee", borderwidth=0, font=("Consolas", 9), padx=10)
        self.log_text.pack(fill=tk.BOTH, expand=True)

    def log(self, msg):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, f"[{time.strftime('%H:%M:%S')}] {msg}\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)

    def find_game_window(self):
        self.hwnd = win32gui.FindWindow(None, WINDOW_TITLE)
        if not self.hwnd:
            self.preview_label.config(text=f"'{WINDOW_TITLE}' 창을 찾을 수 없습니다.", fg="#ff4b2b")
            return False
        return True

    def get_window_image(self, region=None):
        """비활성 상태의 창 화면을 캡처"""
        if not self.hwnd: return None
        
        # 창 크기 정보
        left, top, right, bot = win32gui.GetWindowRect(self.hwnd)
        w = right - left
        h = bot - top

        hwndDC = win32gui.GetWindowDC(self.hwnd)
        mfcDC  = win32ui.CreateDCFromHandle(hwndDC)
        saveDC = mfcDC.CreateCompatibleDC()

        saveBitMap = win32ui.CreateBitmap()
        saveBitMap.CreateCompatibleBitmap(mfcDC, w, h)
        saveDC.SelectObject(saveBitMap)

        # 비활성 캡처 핵심 API
        result = win32gui.PrintWindow(self.hwnd, saveDC.GetSafeHdc(), 3) # 3: PW_RENDERFULLCONTENT

        bmpinfo = saveBitMap.GetInfo()
        bmpstr = saveBitMap.GetBitmapBits(True)
        img = np.frombuffer(bmpstr, dtype='uint8')
        img.shape = (bmpinfo['bmHeight'], bmpinfo['bmpWidth'], 4)

        # 리소스 해제
        win32gui.DeleteObject(saveBitMap.GetHandle())
        saveDC.DeleteDC()
        mfcDC.DeleteDC()
        win32gui.ReleaseDC(self.hwnd, hwndDC)

        if result == 1:
            img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
            if region:
                # 짤림 방지를 위한 창 크기 내 자르기
                rt, rl, rw, rh = region['t'], region['l'], region['w'], region['h']
                img = img[rt:rt+rh, rl:rl+rw]
            return img
        return None

    def start_coord_detection(self):
        if not self.find_game_window(): return
        self.log("영역 지정: 창 안에서 미니맵의 좌상/우하단을 F1, F2로 클릭하세요.")
        threading.Thread(target=self._detection_worker, daemon=True).start()

    def _detection_worker(self):
        t_l = None
        while True:
            if keyboard.is_pressed('f1'):
                p = pyautogui.position()
                w_l, w_t, _, _ = win32gui.GetWindowRect(self.hwnd)
                self.rel_top.set(p.y - w_t); self.rel_left.set(p.x - w_l)
                self.log(f"좌상단(상대): {p.x - w_l}, {p.y - w_t}")
                t_l = p
                time.sleep(0.5)
            if keyboard.is_pressed('f2'):
                p = pyautogui.position()
                if t_l:
                    self.rel_width.set(p.x - t_l.x); self.rel_height.set(p.y - t_l.y)
                    self.x_max.set(p.x - t_l.x - 20)
                    self.log(f"영역 완료: {p.x - t_l.x}x{p.y - t_l.y}")
                    break
            time.sleep(0.1)

    def save_current_profile(self):
        p_name = self.current_profile_name.get()
        self.profiles_data[p_name] = {
            "reg": {"t": self.rel_top.get(), "l": self.rel_left.get(), "w": self.rel_width.get(), "h": self.rel_height.get()},
            "range": {"min": self.x_min.get(), "max": self.x_max.get()},
            "params": {"margin": self.color_margin.get(), "ad": self.attack_delay_ms.get(), "dd": self.dash_delay_ms.get()}
        }
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(self.profiles_data, f, ensure_ascii=False)
        self.update_profile_list(); self.log(f"저장: {p_name}")

    def load_all_profiles(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f: self.profiles_data = json.load(f)
                self.update_profile_list()
                if self.profiles_data: 
                    name = list(self.profiles_data.keys())[0]
                    self.apply_profile_data(name); self.profile_combo.set(name)
            except: pass

    def update_profile_list(self):
        self.profile_combo['values'] = list(self.profiles_data.keys())

    def on_profile_change(self, e):
        name = self.profile_combo.get()
        self.apply_profile_data(name); self.current_profile_name.set(name)

    def apply_profile_data(self, name):
        d = self.profiles_data[name]
        self.rel_top.set(d["reg"]["t"]); self.rel_left.set(d["reg"]["l"])
        self.rel_width.set(d["reg"]["w"]); self.rel_height.set(d["reg"]["h"])
        self.x_min.set(d["range"]["min"]); self.x_max.set(d["range"]["max"])
        self.color_margin.set(d["params"]["margin"]); self.attack_delay_ms.set(d["params"]["ad"]); self.dash_delay_ms.set(d["params"]["dd"])

    def delete_profile(self):
        name = self.profile_combo.get()
        if name in self.profiles_data:
            del self.profiles_data[name]
            with open(CONFIG_FILE, "w", encoding="utf-8") as f: json.dump(self.profiles_data, f, ensure_ascii=False)
            self.update_profile_list(); self.log(f"삭제: {name}")

    def toggle_running_from_key(self):
        self.root.after(0, self.toggle_running)

    def toggle_running(self):
        if self.is_running:
            self.is_running = False
            self.start_btn.config(text="비활성 매크로 시작 (F12)", bg="#00adb5")
            self.log("중단.")
        else:
            if not self.find_game_window():
                messagebox.showerror("오류", "게임을 먼저 실행해주세요.")
                return
            self.is_running = True
            self.start_btn.config(text="매크로 중지 (F12)", bg="#ff4b2b")
            self.log("비활성 매크로 가동...")
            threading.Thread(target=self.hunter_main, daemon=True).start()

    def update_preview(self, img):
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img_pil = Image.fromarray(img_rgb).resize((220, 160), Image.Resampling.LANCZOS)
        img_tk = ImageTk.PhotoImage(img_pil)
        self.preview_label.config(image=img_tk, text=""); self.preview_label.image = img_tk

    def post_key(self, vk_code, duration=0.1):
        """비활성 창에 키 신호 전송"""
        win32gui.PostMessage(self.hwnd, win32con.WM_KEYDOWN, vk_code, 0)
        time.sleep(duration)
        win32gui.PostMessage(self.hwnd, win32con.WM_KEYUP, vk_code, 0)

    def hunter_main(self):
        time.sleep(2)
        current_dir = self.VK_RIGHT
        last_x, stuck_cnt = -1, 0
        last_attack, last_dash = 0, 0
        
        while self.is_running:
            # 1. 비활성 캡처
            reg = {"t": self.rel_top.get(), "l": self.rel_left.get(), "w": self.rel_width.get(), "h": self.rel_height.get()}
            img = self.get_window_image(reg)
            if img is None: 
                self.log("캡처 실패 - 창을 확인하세요."); break

            # 2. 색상 인식
            margin = self.color_margin.get()
            lower = np.array([max(0, self.base_lower[2]-margin), max(0, self.base_lower[1]-margin), max(0, self.base_lower[0]-margin)])
            upper = np.array([min(255, self.base_upper[2]+margin), min(255, self.base_upper[1]+margin), min(255, self.base_upper[0]+margin)])
            mask = cv2.inRange(img, lower, upper)
            mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((3,3), np.uint8))
            
            preview_img = img.copy()
            if np.any(mask):
                M = cv2.moments(mask)
                if M["m00"] > 0:
                    curr_x = int(M["m10"] / M["m00"])
                    cv2.circle(preview_img, (curr_x, int(M["m01"] / M["m00"])), 6, (0, 255, 0), -1)
                    
                    # 방향 전환 및 이동
                    if curr_x >= self.x_max.get() and current_dir == self.VK_RIGHT:
                        current_dir = self.VK_LEFT; self.log("우측 끝 -> 좌회전")
                    elif curr_x <= self.x_min.get() and current_dir == self.VK_LEFT:
                        current_dir = self.VK_RIGHT; self.log("좌측 끝 -> 우회전")
                    
                    # 비활성 이동 신호 (계속 누름 효과를 위해 주기적으로 보냄)
                    win32gui.PostMessage(self.hwnd, win32con.WM_KEYDOWN, current_dir, 0)

                    # 스킬 주기 (ms)
                    now = time.time() * 1000
                    if now - last_attack >= self.attack_delay_ms.get():
                        self.post_key(self.VK_ATTACK); last_attack = now
                    if now - last_dash >= self.dash_delay_ms.get():
                        self.post_key(self.VK_DASH); last_dash = now
                
                # 끼임 체크
                if abs(curr_x - last_x) < 2: stuck_cnt += 1
                else: stuck_cnt = 0; last_x = curr_x
                if stuck_cnt > 30:
                    self.post_key(self.VK_JUMP, 0.2); stuck_cnt = 0
            
            self.update_preview(preview_img)
            time.sleep(0.05)

        # 종료 시 키 떼기
        win32gui.PostMessage(self.hwnd, win32con.WM_KEYUP, self.VK_LEFT, 0)
        win32gui.PostMessage(self.hwnd, win32con.WM_KEYUP, self.VK_RIGHT, 0)

if __name__ == "__main__":
    # DPI 인식 설정 (짤림 방지 핵심)
    try: win32api.SetProcessDPIAware()
    except: pass
    root = tk.Tk()
    app = AutoHunterV5(root)
    root.mainloop()
