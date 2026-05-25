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
CONFIG_FILE = "hunter_ultimate_config.json"
TARGET_TITLE_PART = "MapleStory Worlds-메이"

class AutoHunterV5_4:
    def __init__(self, root):
        self.root = root
        self.root.title("오토헌터 비활성 v5.4 (ULTIMATE)")
        self.root.geometry("600x1050")
        self.root.configure(bg="#1e1e1e")
        
        self.is_running = False
        self.is_previewing = True
        self.hwnd = None
        
        # 색상 범위 (노란색)
        self.base_lower = np.array([245, 230, 0]) 
        self.base_upper = np.array([254, 255, 129]) 
        
        self.setup_styles()
        
        # 설정 변수
        self.profiles_data = {}
        self.current_profile_name = tk.StringVar(value="사냥터 1")
        self.rel_t = tk.IntVar(value=50); self.rel_l = tk.IntVar(value=50)
        self.rel_w = tk.IntVar(value=200); self.rel_h = tk.IntVar(value=150)
        self.x_min = tk.IntVar(value=20); self.x_max = tk.IntVar(value=180)
        self.color_margin = tk.IntVar(value=60) 
        self.attack_delay_ms = tk.IntVar(value=500)
        self.dash_delay_ms = tk.IntVar(value=1500)
        self.key_attack = tk.StringVar(value="end")
        self.key_dash = tk.StringVar(value="space")
        self.key_jump = tk.StringVar(value="alt")
        
        self.setup_ui()
        self.load_all_profiles()
        
        # 메인 프리뷰 루프 시작
        threading.Thread(target=self.main_monitor_loop, daemon=True).start()
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
        style.configure("TEntry", fieldbackground="#393e46", foreground="#ffffff")
        style.configure("TCombobox", fieldbackground="#393e46", foreground="#ffffff")

    def setup_ui(self):
        container = ttk.Frame(self.root, padding="15")
        container.pack(fill=tk.BOTH, expand=True)

        # 0. 프로필
        p_group = ttk.LabelFrame(container, text=" [ 사냥터 프로필 관리 ] ", padding="10")
        p_group.pack(fill=tk.X, pady=5)
        row1 = ttk.Frame(p_group); row1.pack(fill=tk.X)
        self.profile_combo = ttk.Combobox(row1, state="readonly", width=25)
        self.profile_combo.pack(side=tk.LEFT, padx=5); self.profile_combo.bind("<<ComboboxSelected>>", self.on_profile_change)
        ttk.Button(row1, text="삭제", command=self.delete_profile, width=5).pack(side=tk.RIGHT)
        row2 = ttk.Frame(p_group); row2.pack(fill=tk.X, pady=(10, 0))
        ttk.Entry(row2, textvariable=self.current_profile_name, width=30).pack(side=tk.LEFT, padx=10)
        ttk.Button(row2, text="현재 설정 저장", command=self.save_current_profile).pack(side=tk.RIGHT)

        # 1. 프리뷰 (대형 사이즈)
        group1 = ttk.LabelFrame(container, text=" [ 1. 실시간 미니맵 상황 (비활성 모니터링) ] ", padding="10")
        group1.pack(fill=tk.X, pady=5)
        ttk.Button(group1, text="미니맵 영역 재설정 (F1:좌상, F2:우하)", command=self.start_coord_detection).pack(fill=tk.X, pady=(0, 10))
        self.preview_label = tk.Label(group1, text="영역을 지정하면 화면이 크게 출력됩니다.", bg="#121212", fg="#00adb5", font=("Malgun Gothic", 9), height=15)
        self.preview_label.pack(fill=tk.BOTH, expand=True)

        # 2. 정밀도
        group2 = ttk.LabelFrame(container, text=" [ 2. 인식 정밀도 설정 ] ", padding="10")
        group2.pack(fill=tk.X, pady=5)
        ttk.Label(group2, text="색상 허용 마진:").pack(anchor=tk.W)
        m_f = ttk.Frame(group2); m_f.pack(fill=tk.X)
        ttk.Scale(m_f, from_=0, to=150, variable=self.color_margin, orient=tk.HORIZONTAL).pack(side=tk.LEFT, expand=True, fill=tk.X)
        ttk.Entry(m_f, textvariable=self.color_margin, width=5).pack(side=tk.LEFT, padx=5)

        # 3. 키/주기
        group3 = ttk.LabelFrame(container, text=" [ 3. 키 입력 및 주기 설정 ] ", padding="10")
        group3.pack(fill=tk.X, pady=5)
        k_f = ttk.Frame(group3); k_f.pack(fill=tk.X, pady=(0, 10))
        for l, v in [("공격:", self.key_attack), ("이동:", self.key_dash), ("점프:", self.key_jump)]:
            f = ttk.Frame(k_f); f.pack(side=tk.LEFT, expand=True)
            ttk.Label(f, text=l).pack(side=tk.LEFT); ttk.Entry(f, textvariable=v, width=6).pack(side=tk.LEFT, padx=2)
        for label, var, max_v in [("공격 주기 (ms):", self.attack_delay_ms, 3000), ("이동 주기 (ms):", self.dash_delay_ms, 10000)]:
            ttk.Label(group3, text=label).pack(anchor=tk.W)
            f = ttk.Frame(group3); f.pack(fill=tk.X, pady=(0, 5))
            ttk.Scale(f, from_=100, to=max_v, variable=var, orient=tk.HORIZONTAL).pack(side=tk.LEFT, expand=True, fill=tk.X)
            ttk.Entry(f, textvariable=var, width=6).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(group3, text="※ 5분마다 DEL 키 2회 자동 연타 기능 활성화됨", foreground="#00adb5", font=("Malgun Gothic", 8)).pack(anchor=tk.W, pady=(5,0))

        # 4. 활동 범위
        group4 = ttk.LabelFrame(container, text=" [ 4. 캐릭터 활동 범위 ] ", padding="10")
        group4.pack(fill=tk.X, pady=5)
        r_f = ttk.Frame(group4); r_f.pack(fill=tk.X)
        ttk.Label(r_f, text="좌측한계:").pack(side=tk.LEFT); ttk.Entry(r_f, textvariable=self.x_min, width=8).pack(side=tk.LEFT, padx=5)
        ttk.Label(r_f, text="우측한계:").pack(side=tk.LEFT, padx=(20, 0)); ttk.Entry(r_f, textvariable=self.x_max, width=8).pack(side=tk.LEFT, padx=5)

        # 실행 버튼
        self.start_btn = tk.Button(container, text="얼티밋 매크로 시작 (F12)", bg="#00adb5", fg="white", font=("Malgun Gothic", 13, "bold"), borderwidth=0, command=self.toggle_running)
        self.start_btn.pack(fill=tk.X, pady=10, ipady=12)
        self.log_text = tk.Text(container, height=8, bg="#121212", fg="#eeeeee", borderwidth=0, font=("Consolas", 9), padx=10, pady=10)
        self.log_text.pack(fill=tk.BOTH, expand=True)

    def log(self, msg):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, f"[{time.strftime('%H:%M:%S')}] {msg}\n")
        self.log_text.see(tk.END); self.log_text.config(state=tk.DISABLED)

    def find_game_window(self):
        found = []
        win32gui.EnumWindows(lambda h, _: found.append(h) if TARGET_TITLE_PART in win32gui.GetWindowText(h) and win32gui.IsWindowVisible(h) else None, None)
        if found: self.hwnd = found[0]; return True
        return False

    def get_client_image(self, region=None):
        if not self.hwnd or not win32gui.IsWindow(self.hwnd): return None
        try:
            l, t, r, b = win32gui.GetClientRect(self.hwnd)
            w, h = r - l, b - t
            if w <= 0 or h <= 0: return None
            hwndDC = win32gui.GetDC(self.hwnd)
            mfcDC  = win32ui.CreateDCFromHandle(hwndDC)
            saveDC = mfcDC.CreateCompatibleDC()
            saveBitMap = win32ui.CreateBitmap()
            saveBitMap.CreateCompatibleBitmap(mfcDC, w, h)
            saveDC.SelectObject(saveBitMap)
            saveDC.BitBlt((0, 0), (w, h), mfcDC, (0, 0), win32con.SRCCOPY)
            bmpinfo = saveBitMap.GetInfo()
            bmpstr = saveBitMap.GetBitmapBits(True)
            img = np.frombuffer(bmpstr, dtype='uint8')
            img.shape = (bmpinfo['bmHeight'], bmpinfo['bmpWidth'], 4)
            win32gui.DeleteObject(saveBitMap.GetHandle())
            saveDC.DeleteDC(); mfcDC.DeleteDC(); win32gui.ReleaseDC(self.hwnd, hwndDC)
            img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
            if region:
                t, l, rw, rh = region['t'], region['l'], region['w'], region['h']
                img = img[max(0, t):min(h, t+rh), max(0, l):min(w, l+rw)]
            return img
        except: return None

    def start_coord_detection(self):
        if not self.find_game_window():
            messagebox.showerror("오류", "게임을 찾을 수 없습니다.")
            return
        self.log("영역 지정 시작 (F1, F2 클릭)")
        threading.Thread(target=self._detection_worker, daemon=True).start()

    def _detection_worker(self):
        t_l = None
        while True:
            if keyboard.is_pressed('f1'):
                p = pyautogui.position()
                rel_p = win32gui.ScreenToClient(self.hwnd, (p.x, p.y))
                self.rel_l.set(rel_p[0]); self.rel_t.set(rel_p[1])
                self.log(f"좌상단 설정: {rel_p}"); t_l = rel_p; time.sleep(0.5)
            if keyboard.is_pressed('f2'):
                p = pyautogui.position()
                if t_l:
                    rel_p = win32gui.ScreenToClient(self.hwnd, (p.x, p.y))
                    w, h = rel_p[0] - t_l[0], rel_p[1] - t_l[1]
                    self.rel_w.set(w); self.rel_h.set(h)
                    self.x_max.set(w - 20)
                    self.log(f"영역 설정 완료: {w}x{h}"); break
            time.sleep(0.1)

    def main_monitor_loop(self):
        while True:
            if self.hwnd and self.rel_w.get() > 5:
                reg = {"t": self.rel_t.get(), "l": self.rel_l.get(), "w": self.rel_w.get(), "h": self.rel_h.get()}
                img = self.get_client_image(reg)
                if img is not None:
                    margin = self.color_margin.get()
                    low = np.array([max(0, self.base_lower[2]-margin), max(0, self.base_lower[1]-margin), max(0, self.base_lower[0]-margin)])
                    high = np.array([min(255, self.base_upper[2]+margin), min(255, self.base_upper[1]+margin), min(255, self.base_upper[0]+margin)])
                    mask = cv2.inRange(img, low, high)
                    p_img = img.copy()
                    if np.any(mask):
                        M = cv2.moments(mask)
                        if M["m00"] > 0:
                            cx, cy = int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"])
                            cv2.circle(p_img, (cx, cy), 10, (0, 255, 0), -1)
                    cv2.line(p_img, (self.x_min.get(), 0), (self.x_min.get(), reg["h"]), (0, 173, 181), 2)
                    cv2.line(p_img, (self.x_max.get(), 0), (self.x_max.get(), reg["h"]), (0, 173, 181), 2)
                    self.update_preview(p_img)
                else: self.find_game_window()
            time.sleep(0.1)

    def update_preview(self, img):
        try:
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            img_pil = Image.fromarray(img_rgb).resize((480, 320), Image.Resampling.LANCZOS)
            img_tk = ImageTk.PhotoImage(img_pil)
            self.preview_label.config(image=img_tk, text=""); self.preview_label.image = img_tk
        except: pass

    def send_key(self, key_name, duration=0.1):
        try:
            m = {"end": 0x23, "space": 0x20, "alt": 0x12, "left": 0x25, "right": 0x27, "ctrl": 0x11, "shift": 0x10, "del": 0x2E}
            vk = m.get(key_name.lower(), 0x23)
            win32gui.PostMessage(self.hwnd, win32con.WM_KEYDOWN, vk, 0)
            time.sleep(duration)
            win32gui.PostMessage(self.hwnd, win32con.WM_KEYUP, vk, 0)
        except: pass

    def toggle_running_from_key(self): self.root.after(0, self.toggle_running)

    def toggle_running(self):
        if self.is_running:
            self.is_running = False
            self.start_btn.config(text="얼티밋 매크로 시작 (F12)", bg="#00adb5")
            self.log("중단됨.")
        else:
            if not self.hwnd: self.find_game_window()
            if not self.hwnd: return
            self.is_running = True
            self.start_btn.config(text="중지 (F12)", bg="#ff4b2b")
            self.log("매크로 시작!")
            threading.Thread(target=self.hunter_core, daemon=True).start()

    def hunter_core(self):
        cur_dir_vk = win32con.VK_RIGHT
        last_x, stuck_cnt = -1, 0
        l_att, l_dash = 0, 0
        l_del_time = time.time() # DEL 키 타이머
        
        while self.is_running:
            reg = {"t": self.rel_t.get(), "l": self.rel_l.get(), "w": self.rel_w.get(), "h": self.rel_h.get()}
            img = self.get_client_image(reg)
            if img is None: break

            margin = self.color_margin.get()
            low = np.array([max(0, self.base_lower[2]-margin), max(0, self.base_lower[1]-margin), max(0, self.base_lower[0]-margin)])
            high = np.array([min(255, self.base_upper[2]+margin), min(255, self.base_upper[1]+margin), min(255, self.base_upper[0]+margin)])
            mask = cv2.inRange(img, low, high)
            
            if np.any(mask):
                M = cv2.moments(mask)
                if M["m00"] > 0:
                    cx = int(M["m10"] / M["m00"])
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
                    
                    # --- 5분 주기 DEL 키 연타 ---
                    if (time.time() - l_del_time) >= 300: # 300초 = 5분
                        self.log("[주기적 기능] DEL 키 2회 연타")
                        self.send_key("del"); time.sleep(0.2); self.send_key("del")
                        l_del_time = time.time()
                
                if abs(cx - last_x) < 2: stuck_cnt += 1
                else: stuck_cnt = 0; last_x = cx
                if stuck_cnt > 40:
                    self.send_key(self.key_jump.get(), 0.2); stuck_cnt = 0
            
            time.sleep(0.04)
        win32gui.PostMessage(self.hwnd, win32con.WM_KEYUP, win32con.VK_LEFT, 0)
        win32gui.PostMessage(self.hwnd, win32con.WM_KEYUP, win32con.VK_RIGHT, 0)

    # --- 프로필 관리 ---
    def save_current_profile(self):
        n = self.current_profile_name.get()
        self.profiles_data[n] = {
            "reg": {"t": self.rel_t.get(), "l": self.rel_l.get(), "w": self.rel_w.get(), "h": self.rel_h.get()},
            "range": {"min": self.x_min.get(), "max": self.x_max.get()},
            "params": {"margin": self.color_margin.get(), "ad": self.attack_delay_ms.get(), "dd": self.dash_delay_ms.get()},
            "keys": {"a": self.key_attack.get(), "d": self.key_dash.get(), "j": self.key_jump.get()}
        }
        with open(CONFIG_FILE, "w", encoding="utf-8") as f: json.dump(self.profiles_data, f, ensure_ascii=False)
        self.update_profile_list(); self.log(f"저장됨: {n}")

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
        d = self.profiles_data[n]
        self.rel_t.set(d["reg"]["t"]); self.rel_l.set(d["reg"]["l"])
        self.rel_w.set(d["reg"]["w"]); self.rel_h.set(d["reg"]["h"])
        self.x_min.set(d["range"]["min"]); self.x_max.set(d["range"]["max"])
        self.color_margin.set(d["params"]["margin"]); self.attack_delay_ms.set(d["params"]["ad"]); self.dash_delay_ms.set(d["params"]["dd"])
        self.key_attack.set(d["keys"]["a"]); self.key_dash.set(d["keys"]["d"]); self.key_jump.set(d["keys"]["j"])
    def delete_profile(self):
        n = self.profile_combo.get()
        if n in self.profiles_data: del self.profiles_data[n]; self.update_profile_list(); self.log(f"삭제됨: {n}")

if __name__ == "__main__":
    try: win32api.SetProcessDPIAware()
    except: pass
    root = tk.Tk()
    app = AutoHunterV5_4(root)
    root.mainloop()
