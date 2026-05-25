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
CONFIG_FILE = "hunter_premium_config_v5_1.json"
TARGET_TITLE_PART = "MapleStory Worlds-메이"

class AutoHunterV5_1:
    def __init__(self, root):
        self.root = root
        self.root.title("오토헌터 비활성 v5.1 (최종 보완판)")
        self.root.geometry("550x980")
        self.root.configure(bg="#1e1e1e")
        
        self.is_running = False
        self.hwnd = None
        
        # 기본 RGB 범위 (노란색)
        self.base_lower = np.array([245, 230, 0]) 
        self.base_upper = np.array([254, 255, 129]) 
        
        self.setup_styles()
        
        # 프로필 및 설정 변수
        self.profiles_data = {}
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
        
        # 키 설정 (기본값 설정)
        self.key_attack = tk.StringVar(value="end")
        self.key_dash = tk.StringVar(value="space")
        self.key_jump = tk.StringVar(value="alt")
        
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

        # --- 프로필 섹션 ---
        p_group = ttk.LabelFrame(main_container, text=" [ 0. 사냥터 프로필 관리 ] ", padding="10")
        p_group.pack(fill=tk.X, pady=(0, 10))
        
        row1 = ttk.Frame(p_group)
        row1.pack(fill=tk.X)
        self.profile_combo = ttk.Combobox(row1, state="readonly", width=20)
        self.profile_combo.pack(side=tk.LEFT, padx=5)
        self.profile_combo.bind("<<ComboboxSelected>>", self.on_profile_change)
        ttk.Button(row1, text="삭제", command=self.delete_profile, width=5).pack(side=tk.RIGHT)
        
        row2 = ttk.Frame(p_group)
        row2.pack(fill=tk.X, pady=(10, 0))
        ttk.Label(row2, text="프로필 이름:").pack(side=tk.LEFT)
        ttk.Entry(row2, textvariable=self.current_profile_name, width=22).pack(side=tk.LEFT, padx=10)
        ttk.Button(row2, text="현재 설정 저장", command=self.save_current_profile).pack(side=tk.RIGHT)

        # --- 1. 미니맵 설정 ---
        group1 = ttk.LabelFrame(main_container, text=" [ 1. 비활성 미니맵 설정 ] ", padding="10")
        group1.pack(fill=tk.X, pady=5)
        ttk.Button(group1, text="영역 지정 (F1:좌상, F2:우하)", command=self.start_coord_detection).pack(fill=tk.X, pady=(0, 5))
        self.preview_label = tk.Label(group1, text="미니맵 대기 중...", bg="#121212", fg="#00adb5", font=("Malgun Gothic", 8), height=9)
        self.preview_label.pack(fill=tk.X)

        # --- 2. 인식 엔진 ---
        group2 = ttk.LabelFrame(main_container, text=" [ 2. 인식 정밀도 설정 ] ", padding="10")
        group2.pack(fill=tk.X, pady=5)
        ttk.Label(group2, text="색상 오차 허용치 (Margin):").pack(anchor=tk.W)
        m_frame = ttk.Frame(group2)
        m_frame.pack(fill=tk.X)
        ttk.Scale(m_frame, from_=0, to=150, variable=self.color_margin, orient=tk.HORIZONTAL).pack(side=tk.LEFT, expand=True, fill=tk.X)
        ttk.Entry(m_frame, textvariable=self.color_margin, width=5, font=("Malgun Gothic", 10, "bold")).pack(side=tk.LEFT, padx=5)

        # --- 3. 키 및 주기 설정 ---
        group3 = ttk.LabelFrame(main_container, text=" [ 3. 키 및 주기 설정 ] ", padding="10")
        group3.pack(fill=tk.X, pady=5)
        
        # 키 입력 칸
        k_frame = ttk.Frame(group3)
        k_frame.pack(fill=tk.X, pady=(0, 10))
        for l, v in [("공격키:", self.key_attack), ("이동키:", self.key_dash), ("점프키:", self.key_jump)]:
            f = ttk.Frame(k_frame)
            f.pack(side=tk.LEFT, expand=True)
            ttk.Label(f, text=l).pack(side=tk.LEFT)
            ttk.Entry(f, textvariable=v, width=6).pack(side=tk.LEFT, padx=2)

        # 주기 설정
        for label, var, max_val in [("공격 간격 (ms):", self.attack_delay_ms, 3000), ("이동 간격 (ms):", self.dash_delay_ms, 10000)]:
            ttk.Label(group3, text=label).pack(anchor=tk.W)
            f = ttk.Frame(group3)
            f.pack(fill=tk.X, pady=(0, 5))
            ttk.Scale(f, from_=100, to=max_val, variable=var, orient=tk.HORIZONTAL).pack(side=tk.LEFT, expand=True, fill=tk.X)
            ttk.Entry(f, textvariable=var, width=6).pack(side=tk.LEFT, padx=5)

        # --- 4. 활동 범위 ---
        group4 = ttk.LabelFrame(main_container, text=" [ 4. 활동 범위 (X좌표) ] ", padding="10")
        group4.pack(fill=tk.X, pady=5)
        r_frame = ttk.Frame(group4)
        r_frame.pack(fill=tk.X)
        ttk.Label(r_frame, text="최소 X:").pack(side=tk.LEFT)
        ttk.Entry(r_frame, textvariable=self.x_min, width=8).pack(side=tk.LEFT, padx=5)
        ttk.Label(r_frame, text="최대 X:").pack(side=tk.LEFT, padx=(20, 0))
        ttk.Entry(r_frame, textvariable=self.x_max, width=8).pack(side=tk.LEFT, padx=5)

        # --- 실행 제어 ---
        self.start_btn = tk.Button(main_container, text="비활성 매크로 시작 (F12)", bg="#00adb5", fg="white", font=("Malgun Gothic", 12, "bold"), borderwidth=0, command=self.toggle_running)
        self.start_btn.pack(fill=tk.X, pady=15, ipady=10)

        # --- 로그 ---
        self.log_text = tk.Text(main_container, height=8, bg="#121212", fg="#eeeeee", borderwidth=0, font=("Consolas", 9), padx=10, pady=10)
        self.log_text.pack(fill=tk.BOTH, expand=True)

    def log(self, msg):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, f"[{time.strftime('%H:%M:%S')}] {msg}\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)

    def find_game_window(self):
        """강화된 창 찾기 로직 (부분 일치 검색)"""
        def callback(hwnd, windows):
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd)
                if TARGET_TITLE_PART in title:
                    windows.append(hwnd)
        
        found_windows = []
        win32gui.EnumWindows(callback, found_windows)
        
        if found_windows:
            self.hwnd = found_windows[0]
            self.log(f"창 발견: {win32gui.GetWindowText(self.hwnd)}")
            return True
        else:
            self.log(f"'{TARGET_TITLE_PART}' 이름이 포함된 창을 찾을 수 없습니다.")
            return False

    def get_window_image(self, region=None):
        if not self.hwnd or not win32gui.IsWindow(self.hwnd): return None
        try:
            l, t, r, b = win32gui.GetWindowRect(self.hwnd)
            w, h = r - l, b - t
            hwndDC = win32gui.GetWindowDC(self.hwnd)
            mfcDC  = win32ui.CreateDCFromHandle(hwndDC)
            saveDC = mfcDC.CreateCompatibleDC()
            saveBitMap = win32ui.CreateBitmap()
            saveBitMap.CreateCompatibleBitmap(mfcDC, w, h)
            saveDC.SelectObject(saveBitMap)
            win32gui.PrintWindow(self.hwnd, saveDC.GetSafeHdc(), 3)
            
            bmpinfo = saveBitMap.GetInfo()
            bmpstr = saveBitMap.GetBitmapBits(True)
            img = np.frombuffer(bmpstr, dtype='uint8')
            img.shape = (bmpinfo['bmHeight'], bmpinfo['bmpWidth'], 4)
            
            win32gui.DeleteObject(saveBitMap.GetHandle())
            saveDC.DeleteDC(); mfcDC.DeleteDC(); win32gui.ReleaseDC(self.hwnd, hwndDC)
            
            img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
            if region:
                img = img[region['t']:region['t']+region['h'], region['l']:region['l']+region['w']]
            return img
        except: return None

    def start_coord_detection(self):
        if not self.find_game_window():
            messagebox.showerror("오류", f"'{TARGET_TITLE_PART}' 창을 먼저 실행해주세요.")
            return
        self.log("영역 지정 시작: 게임 창 안에서 미니맵의 좌상/우하단을 F1, F2로 클릭!")
        threading.Thread(target=self._detection_worker, daemon=True).start()

    def _detection_worker(self):
        t_l = None
        while True:
            if keyboard.is_pressed('f1'):
                p = pyautogui.position()
                w_l, w_t, _, _ = win32gui.GetWindowRect(self.hwnd)
                self.rel_top.set(p.y - w_t); self.rel_left.set(p.x - w_l)
                self.log(f"좌상단(상대좌표) 저장됨")
                t_l = p; time.sleep(0.5)
            if keyboard.is_pressed('f2'):
                p = pyautogui.position()
                if t_l:
                    w, h = p.x - t_l.x, p.y - t_l.y
                    self.rel_width.set(w); self.rel_height.set(h)
                    self.x_max.set(w - 20)
                    self.log(f"영역 설정 완료: {w}x{h}")
                    break
            time.sleep(0.1)

    def save_current_profile(self):
        p_name = self.current_profile_name.get().strip()
        self.profiles_data[p_name] = {
            "reg": {"t": self.rel_top.get(), "l": self.rel_left.get(), "w": self.rel_width.get(), "h": self.rel_height.get()},
            "range": {"min": self.x_min.get(), "max": self.x_max.get()},
            "keys": {"a": self.key_attack.get(), "d": self.key_dash.get(), "j": self.key_jump.get()},
            "params": {"margin": self.color_margin.get(), "ad": self.attack_delay_ms.get(), "dd": self.dash_delay_ms.get()}
        }
        with open(CONFIG_FILE, "w", encoding="utf-8") as f: json.dump(self.profiles_data, f, ensure_ascii=False)
        self.update_profile_list(); self.log(f"저장 완료: {p_name}")

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
        self.key_attack.set(d["keys"]["a"]); self.key_dash.set(d["keys"]["d"]); self.key_jump.set(d["keys"]["j"])
        self.color_margin.set(d["params"]["margin"]); self.attack_delay_ms.set(d["params"]["ad"]); self.dash_delay_ms.set(d["params"]["dd"])

    def delete_profile(self):
        name = self.profile_combo.get()
        if name in self.profiles_data:
            del self.profiles_data[name]
            with open(CONFIG_FILE, "w", encoding="utf-8") as f: json.dump(self.profiles_data, f, ensure_ascii=False)
            self.update_profile_list(); self.log(f"삭제됨: {name}")

    def toggle_running_from_key(self):
        self.root.after(0, self.toggle_running)

    def toggle_running(self):
        if self.is_running:
            self.is_running = False
            self.start_btn.config(text="비활성 매크로 시작 (F12)", bg="#00adb5")
            self.log("중단됨.")
        else:
            if not self.find_game_window():
                messagebox.showerror("오류", "게임을 먼저 실행해주세요.")
                return
            self.is_running = True
            self.start_btn.config(text="매크로 중지 (F12)", bg="#ff4b2b")
            self.log("동작 시작...")
            threading.Thread(target=self.hunter_main, daemon=True).start()

    def update_preview(self, img):
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img_pil = Image.fromarray(img_rgb).resize((220, 160), Image.Resampling.LANCZOS)
        img_tk = ImageTk.PhotoImage(img_pil)
        self.preview_label.config(image=img_tk, text=""); self.preview_label.image = img_tk

    def send_key(self, key_name, duration=0.1):
        # 텍스트 키 이름을 가상 키코드로 변환
        vk = win32api.VkKeyScan(key_name) if len(key_name) == 1 else self.get_special_vk(key_name)
        win32gui.PostMessage(self.hwnd, win32con.WM_KEYDOWN, vk, 0)
        time.sleep(duration)
        win32gui.PostMessage(self.hwnd, win32con.WM_KEYUP, vk, 0)

    def get_special_vk(self, name):
        maps = {"end": win32con.VK_END, "space": win32con.VK_SPACE, "alt": win32con.VK_MENU, "left": win32con.VK_LEFT, "right": win32con.VK_RIGHT, "ctrl": win32con.VK_CONTROL, "shift": win32con.VK_SHIFT}
        return maps.get(name.lower(), win32con.VK_END)

    def hunter_main(self):
        time.sleep(2)
        cur_dir_vk = win32con.VK_RIGHT
        last_x, stuck_cnt = -1, 0
        l_att, l_dash = 0, 0
        
        while self.is_running:
            reg = {"t": self.rel_top.get(), "l": self.rel_left.get(), "w": self.rel_width.get(), "h": self.rel_height.get()}
            img = self.get_window_image(reg)
            if img is None: break

            margin = self.color_margin.get()
            lower = np.array([max(0, self.base_lower[2]-margin), max(0, self.base_lower[1]-margin), max(0, self.base_lower[0]-margin)])
            upper = np.array([min(255, self.base_upper[2]+margin), min(255, self.base_upper[1]+margin), min(255, self.base_upper[0]+margin)])
            mask = cv2.inRange(img, lower, upper)
            mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((3,3), np.uint8))
            
            p_img = img.copy()
            if np.any(mask):
                M = cv2.moments(mask)
                if M["m00"] > 0:
                    cx = int(M["m10"] / M["m00"])
                    cv2.circle(p_img, (cx, int(M["m01"] / M["m00"])), 6, (0, 255, 0), -1)
                    
                    if cx >= self.x_max.get() and cur_dir_vk == win32con.VK_RIGHT:
                        win32gui.PostMessage(self.hwnd, win32con.WM_KEYUP, win32con.VK_RIGHT, 0)
                        cur_dir_vk = win32con.VK_LEFT; self.log("우측 끝 -> 좌회전")
                    elif cx <= self.x_min.get() and cur_dir_vk == win32con.VK_LEFT:
                        win32gui.PostMessage(self.hwnd, win32con.WM_KEYUP, win32con.VK_LEFT, 0)
                        cur_dir_vk = win32con.VK_RIGHT; self.log("좌측 끝 -> 우회전")
                    
                    win32gui.PostMessage(self.hwnd, win32con.WM_KEYDOWN, cur_dir_vk, 0)

                    now = time.time() * 1000
                    if now - l_att >= self.attack_delay_ms.get():
                        self.send_key(self.key_attack.get()); l_att = now
                    if now - l_dash >= self.dash_delay_ms.get():
                        self.send_key(self.key_dash.get()); l_dash = now
                
                if abs(cx - last_x) < 2: stuck_cnt += 1
                else: stuck_cnt = 0; last_x = cx
                if stuck_cnt > 30:
                    self.send_key(self.key_jump.get(), 0.2); stuck_cnt = 0
            
            self.update_preview(p_img)
            time.sleep(0.05)

        win32gui.PostMessage(self.hwnd, win32con.WM_KEYUP, win32con.VK_LEFT, 0)
        win32gui.PostMessage(self.hwnd, win32con.WM_KEYUP, win32con.VK_RIGHT, 0)

if __name__ == "__main__":
    try: win32api.SetProcessDPIAware()
    except: pass
    root = tk.Tk()
    app = AutoHunterV5_1(root)
    root.mainloop()
