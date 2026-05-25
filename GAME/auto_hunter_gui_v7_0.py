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
import winsound
from PIL import Image, ImageTk

# 설정 파일 경로 (v7.0 전용)
CONFIG_FILE = "hunter_premium_v7_0_config.json"

# --- DPI 보정 ---
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except:
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except:
        pass

class AutoHunterV7_0:
    def __init__(self, root):
        self.root = root
        self.root.title("오토헌터 v7.0")
        self.root.geometry("450x800")
        self.root.configure(bg="#1e1e1e")
        self.root.attributes("-topmost", True) # 기본 항상 위
        
        self.is_running = False
        self.is_previewing = True
        self.is_anti_macro_working = False
        self.is_selling = False
        
        # 거탐 추적용
        self.last_anti_pos = None; self.last_anti_vel = (0, 0); self.anti_lost_time = 0
        
        # 기본 키 설정
        self.KEY_ATTACK = tk.StringVar(value="end")
        self.KEY_DASH = tk.StringVar(value="space")
        self.KEY_JUMP = tk.StringVar(value="alt")
        self.KEY_PERIODIC = tk.StringVar(value="del")
        self.KEY_SHOP = tk.StringVar(value="m") # 상점 NPC 대화 키 등
        
        # 인식 범위 (노랑/빨강)
        self.base_lower = np.array([245, 230, 0]); self.base_upper = np.array([254, 255, 129])
        self.anti_lower = np.array([0, 0, 220]); self.anti_upper = np.array([180, 30, 255])
        
        # 변수 설정
        self.profiles_data = {}
        self.current_profile_name = tk.StringVar(value="기본 사냥터")
        self.reg_t = tk.IntVar(value=100); self.reg_l = tk.IntVar(value=100)
        self.reg_w = tk.IntVar(value=200); self.reg_h = tk.IntVar(value=150)
        self.x_min = tk.IntVar(value=20); self.x_max = tk.IntVar(value=180)
        self.color_margin = tk.IntVar(value=60) 
        self.attack_delay_ms = tk.IntVar(value=500); self.dash_delay_ms = tk.IntVar(value=1500)
        self.use_dash = tk.BooleanVar(value=True); self.use_anti_macro = tk.BooleanVar(value=True)
        self.use_sound_alert = tk.BooleanVar(value=True)
        self.hunt_mode = tk.IntVar(value=0) # 0:이동, 1:제자리
        self.stationary_range = tk.IntVar(value=5)
        self.use_periodic = tk.BooleanVar(value=True); self.periodic_interval_min = tk.IntVar(value=5)
        self.always_on_top = tk.BooleanVar(value=True)
        self.ui_opacity = tk.DoubleVar(value=1.0)
        self.custom_sound_path = tk.StringVar(value="")
        
        # 텔레그램 설정 (오케스트레이터 정보 연동)
        self.TELEGRAM_TOKEN = "8204355471:AAHSapDO4DNvuVgRD0vxSWFymQcg_4l6mzw"
        self.TELEGRAM_CHAT_ID = "6046121539"
        
        # 판매 루틴 변수
        self.use_auto_sell = tk.BooleanVar(value=False)
        self.sell_interval_min = tk.IntVar(value=30)
        self.last_sell_time = time.time()
        self.shop_npc_pos = [0, 0] # [x, y]
        self.shop_sell_btn_pos = [0, 0] # [x, y]

        self.setup_styles()
        self.setup_ui()
        self.load_all_profiles()
        
        threading.Thread(target=self.monitor_loop, daemon=True).start()
        threading.Thread(target=self.anti_macro_loop, daemon=True).start()
        keyboard.add_hotkey('f12', self.toggle_running_from_key)

    def setup_styles(self):
        style = ttk.Style(); style.theme_use('clam')
        style.configure("TFrame", background="#1e1e1e")
        style.configure("TNotebook", background="#1e1e1e", borderwidth=0)
        style.configure("TNotebook.Tab", background="#393e46", foreground="#eeeeee", padding=[10, 5])
        style.map("TNotebook.Tab", background=[("selected", "#00adb5")], foreground=[("selected", "white")])
        style.configure("TLabelframe", background="#1e1e1e", foreground="#00adb5", bordercolor="#393e46")
        style.configure("TLabelframe.Label", foreground="#00adb5", font=("Malgun Gothic", 9, "bold"))
        style.configure("TLabel", background="#1e1e1e", foreground="#eeeeee", font=("Malgun Gothic", 9))
        style.configure("TButton", background="#393e46", foreground="#eeeeee", font=("Malgun Gothic", 9, "bold"))
        style.map("TButton", background=[('active', '#00adb5')])
        style.configure("TCheckbutton", background="#1e1e1e", foreground="#eeeeee")
        style.configure("TRadiobutton", background="#1e1e1e", foreground="#eeeeee")

    def setup_ui(self):
        # 상단 제어 바
        top_bar = ttk.Frame(self.root); top_bar.pack(fill=tk.X, padx=5, pady=5)
        self.profile_combo = ttk.Combobox(top_bar, state="readonly", width=15); self.profile_combo.pack(side=tk.LEFT, padx=5)
        self.profile_combo.bind("<<ComboboxSelected>>", self.on_profile_change)
        ttk.Button(top_bar, text="저장", command=self.save_current_profile, width=5).pack(side=tk.LEFT, padx=2)
        
        self.start_btn = tk.Button(top_bar, text="시작 (F12)", bg="#00adb5", fg="white", font=("Malgun Gothic", 9, "bold"), command=self.toggle_running)
        self.start_btn.pack(side=tk.RIGHT, padx=5, fill=tk.Y)

        # 탭 시스템 (UI 소형화 핵심)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # 1. 메인 탭 (미니맵 & 기본 제어)
        self.tab_main = ttk.Frame(self.notebook); self.notebook.add(self.tab_main, text="메인")
        
        self.preview_label = tk.Label(self.tab_main, text="미니맵 대기 중", bg="#121212", fg="#393e46", height=10)
        self.preview_label.pack(fill=tk.X, padx=5, pady=5)
        
        btn_f = ttk.Frame(self.tab_main); btn_f.pack(fill=tk.X, padx=5)
        ttk.Button(btn_f, text="영역 드래그", command=self.open_selector).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)
        ttk.Button(btn_f, text="좌표(F1/F2)", command=self.start_coord_detection).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)
        
        mode_f = ttk.LabelFrame(self.tab_main, text=" 사냥 모드 "); mode_f.pack(fill=tk.X, padx=5, pady=5)
        ttk.Radiobutton(mode_f, text="이동", variable=self.hunt_mode, value=0).pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(mode_f, text="제자리", variable=self.hunt_mode, value=1).pack(side=tk.LEFT, padx=10)
        ttk.Checkbutton(mode_f, text="거탐알림", variable=self.use_sound_alert).pack(side=tk.RIGHT, padx=10)

        range_f = ttk.LabelFrame(self.tab_main, text=" 이동 범위 (미니맵 기준) "); range_f.pack(fill=tk.X, padx=5, pady=5)
        r_row = ttk.Frame(range_f); r_row.pack(fill=tk.X, pady=2)
        ttk.Label(r_row, text="MIN X:").pack(side=tk.LEFT); ttk.Scale(r_row, from_=0, to=300, variable=self.x_min).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)
        ttk.Entry(r_row, textvariable=self.x_min, width=5).pack(side=tk.RIGHT)
        r_row2 = ttk.Frame(range_f); r_row2.pack(fill=tk.X, pady=2)
        ttk.Label(r_row2, text="MAX X:").pack(side=tk.LEFT); ttk.Scale(r_row2, from_=0, to=300, variable=self.x_max).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)
        ttk.Entry(r_row2, textvariable=self.x_max, width=5).pack(side=tk.RIGHT)

        # 2. 스킬/수치 탭
        self.tab_skill = ttk.Frame(self.notebook); self.notebook.add(self.tab_skill, text="스킬")
        
        s_group = ttk.LabelFrame(self.tab_skill, text=" 딜레이 및 설정 "); s_group.pack(fill=tk.X, padx=5, pady=5)
        for label, var, min_v, max_v in [
            ("공격 주기 (ms):", self.attack_delay_ms, 100, 3000), 
            ("이동 주기 (ms):", self.dash_delay_ms, 100, 10000),
            ("제자리 반경:", self.stationary_range, 1, 20),
            ("주기 스킬 (분):", self.periodic_interval_min, 1, 60),
            ("인식 여유분:", self.color_margin, 0, 150)
        ]:
            f = ttk.Frame(s_group); f.pack(fill=tk.X, pady=2)
            ttk.Label(f, text=label, width=12).pack(side=tk.LEFT)
            ttk.Scale(f, from_=min_v, to=max_v, variable=var).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)
            ttk.Entry(f, textvariable=var, width=6).pack(side=tk.RIGHT)

        k_group = ttk.LabelFrame(self.tab_skill, text=" 키 설정 "); k_group.pack(fill=tk.X, padx=5, pady=5)
        for label, var in [("공격:", self.KEY_ATTACK), ("대시:", self.KEY_DASH), ("점프:", self.KEY_JUMP), ("주기:", self.KEY_PERIODIC)]:
            f = ttk.Frame(k_group); f.pack(side=tk.LEFT, expand=True)
            ttk.Label(f, text=label).pack(); ttk.Entry(f, textvariable=var, width=7).pack()

        # 3. 상점/부가 탭
        self.tab_extra = ttk.Frame(self.notebook); self.notebook.add(self.tab_extra, text="기능")
        
        sell_f = ttk.LabelFrame(self.tab_extra, text=" 자동 판매 (실험적) "); sell_f.pack(fill=tk.X, padx=5, pady=5)
        ttk.Checkbutton(sell_f, text="자동 판매 루틴 활성화", variable=self.use_auto_sell).pack(anchor=tk.W, padx=5, pady=5)
        f = ttk.Frame(sell_f); f.pack(fill=tk.X, pady=2)
        ttk.Label(f, text="판매 주기 (분):").pack(side=tk.LEFT); ttk.Entry(f, textvariable=self.sell_interval_min, width=5).pack(side=tk.LEFT, padx=5)
        ttk.Label(f, text="상점키:").pack(side=tk.LEFT, padx=5); ttk.Entry(f, textvariable=self.KEY_SHOP, width=5).pack(side=tk.LEFT)
        
        btn_f2 = ttk.Frame(sell_f); btn_f2.pack(fill=tk.X, pady=5)
        ttk.Button(btn_f2, text="NPC 위치 지정", command=lambda: self.open_point_selector("npc")).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)
        ttk.Button(btn_f2, text="판매버튼 위치 지정", command=lambda: self.open_point_selector("btn")).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)
        
        ui_f = ttk.LabelFrame(self.tab_extra, text=" UI 및 사운드 설정 "); ui_f.pack(fill=tk.X, padx=5, pady=5)
        ttk.Checkbutton(ui_f, text="항상 위", variable=self.always_on_top, command=self.update_ui_settings).pack(anchor=tk.W, padx=5)
        f_op = ttk.Frame(ui_f); f_op.pack(fill=tk.X, pady=2)
        ttk.Label(f_op, text="투명도:").pack(side=tk.LEFT); ttk.Scale(f_op, from_=0.2, to=1.0, variable=self.ui_opacity, command=lambda x: self.update_ui_settings()).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)
        
        f_snd = ttk.Frame(ui_f); f_snd.pack(fill=tk.X, pady=5)
        ttk.Label(f_snd, text="알림음:").pack(side=tk.LEFT)
        ttk.Entry(f_snd, textvariable=self.custom_sound_path, width=20).pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        ttk.Button(f_snd, text="찾기", command=self.browse_sound, width=5).pack(side=tk.LEFT)
        ttk.Button(f_snd, text="▶", command=self.play_custom_sound, width=3).pack(side=tk.LEFT, padx=2)

        # 로그 영역
        self.log_text = tk.Text(self.root, height=8, bg="#121212", fg="#aaaaaa", borderwidth=0, font=("Consolas", 8), padx=5, pady=5)
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    def log(self, msg):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, f"[{time.strftime('%H:%M:%S')}] {msg}\n")
        self.log_text.see(tk.END); self.log_text.config(state=tk.DISABLED)

    def update_ui_settings(self):
        self.root.attributes("-topmost", self.always_on_top.get())
        self.root.attributes("-alpha", self.ui_opacity.get())

    def send_telegram(self, msg, photo_path=None):
        def _send():
            try:
                url = f"https://api.telegram.org/bot{self.TELEGRAM_TOKEN}/"
                if photo_path and os.path.exists(photo_path):
                    with open(photo_path, 'rb') as f:
                        requests.post(url + "sendPhoto", data={"chat_id": self.TELEGRAM_CHAT_ID, "caption": msg}, files={"photo": f}, timeout=10)
                else:
                    requests.post(url + "sendMessage", json={"chat_id": self.TELEGRAM_CHAT_ID, "text": msg}, timeout=10)
            except Exception as e:
                self.log(f"[텔레그램 에러] {e}")
        threading.Thread(target=_send, daemon=True).start()

    def play_custom_sound(self):
        def _play():
            # 20초간 지옥의 알람 재생
            start_time = time.time()
            self.log("🔊 [지옥의 알람] 20초간 가동!")
            while time.time() - start_time < 20:
                # 1단계: 초고주파 엇박자
                for _ in range(3):
                    winsound.Beep(3500, 100); winsound.Beep(4000, 50)
                # 2단계: '드르륵' 소음
                for freq in range(2500, 4500, 150): winsound.Beep(freq, 20)
                # 3단계: 긴급 사이렌
                for _ in range(2):
                    winsound.Beep(3000, 150); winsound.Beep(1500, 150)
                if not self.use_sound_alert.get(): break # 도중에 끄면 중단
        threading.Thread(target=_play, daemon=True).start()

    def open_selector(self):
        self.selector = tk.Toplevel(self.root); self.selector.attributes("-alpha", 0.3); self.selector.attributes("-fullscreen", True)
        self.selector.attributes("-topmost", True); self.selector.config(cursor="cross")
        self.sel_canvas = tk.Canvas(self.selector, cursor="cross", bg="grey"); self.sel_canvas.pack(fill="both", expand=True)
        self.start_x = None; self.start_y = None; self.rect = None
        self.sel_canvas.bind("<ButtonPress-1>", self.on_sel_press); self.sel_canvas.bind("<B1-Motion>", self.on_sel_drag); self.sel_canvas.bind("<ButtonRelease-1>", self.on_sel_release)

    def on_sel_press(self, e): self.start_x, self.start_y = e.x, e.y; self.rect = self.sel_canvas.create_rectangle(e.x, e.y, e.x, e.y, outline="cyan", width=3)
    def on_sel_drag(self, e): self.sel_canvas.coords(self.rect, self.start_x, self.start_y, e.x, e.y)
    def on_sel_release(self, e):
        w, h = abs(e.x - self.start_x), abs(e.y - self.start_y)
        if w > 5: self.reg_l.set(min(self.start_x, e.x)); self.reg_t.set(min(self.start_y, e.y)); self.reg_w.set(w); self.reg_h.set(h); self.x_max.set(w-15); self.log(f"영역 설정: {w}x{h}")
        self.selector.destroy()

    def start_coord_detection(self): threading.Thread(target=self._detection_worker, daemon=True).start()
    def _detection_worker(self):
        t_l = None; self.log("F1(좌상단) -> F2(우하단) 입력하세요.")
        while True:
            if keyboard.is_pressed('f1'): p = pyautogui.position(); self.reg_l.set(p.x); self.reg_t.set(p.y); self.log("좌상단 확정"); t_l = p; time.sleep(0.5)
            if keyboard.is_pressed('f2'):
                p = pyautogui.position()
                if t_l: w, h = p.x - t_l.x, p.y - t_l.y; self.reg_w.set(w); self.reg_h.set(h); self.x_max.set(w-15); self.log(f"좌표 확정: {w}x{h}"); break
            time.sleep(0.1)

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
                        
                        # 범위 시각화 (v7.0 추가)
                        cv2.line(p_img, (self.x_min.get(), 0), (self.x_min.get(), self.reg_h.get()), (255, 0, 0), 1)
                        cv2.line(p_img, (self.x_max.get(), 0), (self.x_max.get(), self.reg_h.get()), (0, 0, 255), 1)
                        
                        if np.any(mask):
                            M = cv2.moments(mask)
                            if M["m00"] > 0: cx, cy = int(M["m10"]/M["m00"]), int(M["m01"]/M["m00"]); cv2.circle(p_img, (cx, cy), 6, (0, 255, 0), -1)
                        self.update_preview(p_img)
                    except: pass
                time.sleep(0.08)

    def anti_macro_loop(self):
        last_alert_time = 0
        # 감시할 이미지 파일 리스트 (anti4 추가)
        ANTI_IMAGES = ["anti1.png", "anti2.png", "anti3.png", "anti4.png"]
        
        with mss.mss() as sct:
            while True:
                if self.use_anti_macro.get():
                    try:
                        # 1. 화면 전체 캡처
                        scr_w, scr_h = pyautogui.size()
                        monitor = {"top": 0, "left": 0, "width": scr_w, "height": scr_h}
                        img = np.array(sct.grab(monitor))
                        img_gray = cv2.cvtColor(img, cv2.COLOR_BGRA2GRAY)
                        
                        found = False
                        for img_name in ANTI_IMAGES:
                            if not os.path.exists(img_name): continue # 파일 없으면 스킵
                            
                            # 템플릿 이미지 로드 (회색조)
                            template = cv2.imread(img_name, cv2.IMREAD_GRAYSCALE)
                            if template is None: continue
                            
                            # 2. 이미지 매칭 실행
                            res = cv2.matchTemplate(img_gray, template, cv2.TM_CCOEFF_NORMED)
                            threshold = 0.5 # [업데이트] 50% 이상 일치하면 검출 (더 민감하게)
                            loc = np.where(res >= threshold)
                            
                            if len(loc[0]) > 0: # 이미지를 찾았다면
                                found = True
                                self.log(f"🚨 [거탐 검출] 이미지 일치 포착({int(np.max(res)*100)}%): {img_name}")
                                break
                        
                        if found:
                            now = time.time()
                            if now - last_alert_time > 60: # 1분 이내 중복 방지
                                # [업데이트] 사냥 중단 로직 제거 (사용자 요청)
                                
                                # [지옥의 알람 재생]
                                if self.use_sound_alert.get():
                                    self.play_custom_sound()
                                
                                # [대기 및 캡처] 5.5초 대기 후 중앙 게임 화면 캡처
                                time.sleep(5.5)
                                self.log("📸 중앙 게임 화면 캡처 중...")
                                
                                center_roi = {"top": (scr_h // 2) - 300, "left": (scr_w // 2) - 400, "width": 800, "height": 600}
                                shot = np.array(sct.grab(center_roi))
                                cv2.imwrite("anti_game_center.png", cv2.cvtColor(shot, cv2.COLOR_BGRA2BGR))
                                self.log("✅ 캡처 완료 (텔레그램 전송은 비활성 상태).")
                                
                                last_alert_time = now
                                time.sleep(30) # 상황 정리 대기
                    except Exception as e:
                        print(f"이미지 매칭 루프 오류: {e}")
                
                time.sleep(1.0) # 이미지 매칭은 연산량이 있으므로 주기를 1초로 설정

    def update_preview(self, img):
        try:
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB); img_pil = Image.fromarray(img_rgb).resize((400, 200), Image.Resampling.LANCZOS)
            img_tk = ImageTk.PhotoImage(img_pil); self.preview_label.config(image=img_tk, text=""); self.preview_label.image = img_tk
        except: pass

    def press_key(self, key): pyautogui.keyDown(key); time.sleep(random.uniform(0.08, 0.12)); pyautogui.keyUp(key)

    def toggle_running_from_key(self): self.root.after(0, self.toggle_running)
    def toggle_running(self):
        if self.is_running:
            self.is_running = False; self.start_btn.config(text="시작 (F12)", bg="#00adb5"); self.log("사냥 중단")
            pyautogui.keyUp('left'); pyautogui.keyUp('right')
        else:
            self.is_running = True; self.start_btn.config(text="중지 (F12)", bg="#ff4b2b"); self.log("사냥 시작!")
            threading.Thread(target=self.hunter_core, daemon=True).start()

    def hunter_core(self):
        cur_dir = 'right'; last_x, stuck_cnt = -1, 0; l_att, l_dash = 0, 0; l_del_time = time.time(); start_cx = None
        while self.is_running:
            if self.is_anti_macro_working or self.is_selling: time.sleep(0.5); continue
            
            # 자동 판매 루틴 체크
            if self.use_auto_sell.get() and (time.time() - self.last_sell_time) >= (self.sell_interval_min.get() * 60):
                self.run_sell_routine(); continue

            # [추가] 15분 주기 스크린샷 저장 (누적 가동 시간 기준)
            now = time.time()
            if now - self.last_screenshot_time >= self.screenshot_interval_sec:
                try:
                    with mss.mss() as s_sct:
                        filename = f"hunt_{time.strftime('%Y%m%d_%H%M%S')}.png"
                        filepath = os.path.join(self.SCREENSHOT_DIR, filename)
                        shot = np.array(s_sct.grab(s_sct.monitors[1]))
                        cv2.imwrite(filepath, cv2.cvtColor(shot, cv2.COLOR_BGRA2BGR))
                        self.log(f"📸 주기적 스크린샷 저장 완료: {filename}")
                        self.last_screenshot_time = now
                except Exception as e:
                    self.log(f"[스크린샷 에러] {e}")

            with mss.mss() as sct:
                region = {"top": self.reg_t.get(), "left": self.reg_l.get(), "width": self.reg_w.get(), "height": self.reg_h.get()}
                try:
                    shot = np.array(sct.grab(region)); img = cv2.cvtColor(shot, cv2.COLOR_BGRA2BGR)
                    m = self.color_margin.get()
                    low = np.array([max(0, self.base_lower[2]-m), max(0, self.base_lower[1]-m), max(0, self.base_lower[0]-m)])
                    high = np.array([min(255, self.base_upper[2]+m), min(255, self.base_upper[1]+m), min(255, self.base_upper[0]+m)])
                    mask = cv2.inRange(img, low, high)
                    if np.any(mask):
                        M = cv2.moments(mask); cx = -1
                        if M["m00"] > 0:
                            cx = int(M["m10"] / M["m00"])
                            if self.hunt_mode.get() == 1: # 제자리
                                if start_cx is None: start_cx = cx
                                r = self.stationary_range.get()
                                if cx >= start_cx + r and cur_dir == 'right': pyautogui.keyUp('right'); cur_dir = 'left'
                                elif cx <= start_cx - r and cur_dir == 'left': pyautogui.keyUp('left'); cur_dir = 'right'
                                pyautogui.keyDown(cur_dir)
                            else: # 이동
                                start_cx = None
                                if cx >= self.x_max.get() and cur_dir == 'right': pyautogui.keyUp('right'); cur_dir = 'left'
                                elif cx <= self.x_min.get() and cur_dir == 'left': pyautogui.keyUp('left'); cur_dir = 'right'
                                pyautogui.keyDown(cur_dir)
                            now = time.time() * 1000
                            if now - l_att >= self.attack_delay_ms.get(): self.press_key(self.KEY_ATTACK.get()); l_att = now
                            if self.use_dash.get() and now - l_dash >= self.dash_delay_ms.get(): self.press_key(self.KEY_DASH.get()); l_dash = now
                            if self.use_periodic.get() and (time.time() - l_del_time) >= (self.periodic_interval_min.get() * 60):
                                self.log("[주기] 스킬 실행"); self.press_key(self.KEY_PERIODIC.get()); l_del_time = time.time()
                        
                        if cx != -1:
                            if abs(cx - last_x) < 2: stuck_cnt += 1
                            else: stuck_cnt = 0; last_x = cx
                            if stuck_cnt > 35: self.press_key(self.KEY_JUMP.get()); stuck_cnt = 0
                except: pass
            time.sleep(0.04)

    def open_point_selector(self, target):
        self.selector = tk.Toplevel(self.root); self.selector.attributes("-alpha", 0.3); self.selector.attributes("-fullscreen", True)
        self.selector.attributes("-topmost", True); self.selector.config(cursor="hand2")
        self.sel_canvas = tk.Canvas(self.selector, bg="grey"); self.sel_canvas.pack(fill="both", expand=True)
        self.log(f"[{target}] 위치를 마우스로 클릭하세요.")
        self.sel_canvas.bind("<Button-1>", lambda e: self.on_point_release(e, target))

    def on_point_release(self, e, target):
        if target == "npc": self.shop_npc_pos = [e.x, e.y]; self.log(f"NPC 좌표 설정: {e.x}, {e.y}")
        elif target == "btn": self.shop_sell_btn_pos = [e.x, e.y]; self.log(f"판매버튼 좌표 설정: {e.x}, {e.y}")
        self.selector.destroy()

    def run_sell_routine(self):
        self.is_selling = True; self.log("[상점] 판매 루틴 시작"); pyautogui.keyUp('left'); pyautogui.keyUp('right')
        try:
            # 1. NPC 클릭 (지정된 좌표)
            if self.shop_npc_pos != [0, 0]:
                pyautogui.click(self.shop_npc_pos[0], self.shop_npc_pos[1]); time.sleep(1.5)
            else:
                self.press_key(self.KEY_SHOP.get()); time.sleep(1.5)
            
            # 2. 판매 버튼 클릭 (지정된 좌표)
            if self.shop_sell_btn_pos != [0, 0]:
                pyautogui.click(self.shop_sell_btn_pos[0], self.shop_sell_btn_pos[1]); time.sleep(1.0)
            
            # 3. 확인창 엔터 등
            for _ in range(2): self.press_key('enter'); time.sleep(0.5)
            self.log("[상점] 판매 완료"); winsound.Beep(800, 300)
        except: self.log("[오류] 판매 루틴 실패")
        self.last_sell_time = time.time(); self.is_selling = False

    def save_current_profile(self):
        n = self.current_profile_name.get()
        self.profiles_data[n] = {
            "reg": {"t": self.reg_t.get(), "l": self.reg_l.get(), "w": self.reg_w.get(), "h": self.reg_h.get()},
            "range": {"min": self.x_min.get(), "max": self.x_max.get()},
            "keys": {"att": self.KEY_ATTACK.get(), "dash": self.KEY_DASH.get(), "jump": self.KEY_JUMP.get(), "per": self.KEY_PERIODIC.get(), "shop": self.KEY_SHOP.get()},
            "shop_pos": {"npc": self.shop_npc_pos, "btn": self.shop_sell_btn_pos},
            "params": {
                "margin": self.color_margin.get(), "ad": self.attack_delay_ms.get(), "dd": self.dash_delay_ms.get(),
                "use_dash": self.use_dash.get(), "use_anti": self.use_anti_macro.get(), "mode": self.hunt_mode.get(),
                "use_per": self.use_periodic.get(), "per_int": self.periodic_interval_min.get(), "st_range": self.stationary_range.get(),
                "use_sound": self.use_sound_alert.get(), "top": self.always_on_top.get(), "opacity": self.ui_opacity.get(),
                "use_sell": self.use_auto_sell.get(), "sell_int": self.sell_interval_min.get()
            }
        }
        with open(CONFIG_FILE, "w", encoding="utf-8") as f: json.dump(self.profiles_data, f, ensure_ascii=False)
        self.update_profile_list(); self.log(f"저장 완료: {n}")

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
        d = self.profiles_data[n]; p = d["params"]; k = d.get("keys", {}); s = d.get("shop_pos", {})
        self.reg_t.set(d["reg"]["t"]); self.reg_l.set(d["reg"]["l"]); self.reg_w.set(d["reg"]["w"]); self.reg_h.set(d["reg"]["h"])
        self.x_min.set(d["range"]["min"]); self.x_max.set(d["range"]["max"])
        self.shop_npc_pos = s.get("npc", [0, 0]); self.shop_sell_btn_pos = s.get("btn", [0, 0])
        self.KEY_ATTACK.set(k.get("att", "end")); self.KEY_DASH.set(k.get("dash", "space")); self.KEY_JUMP.set(k.get("jump", "alt")); self.KEY_PERIODIC.set(k.get("per", "del")); self.KEY_SHOP.set(k.get("shop", "m"))
        self.color_margin.set(p.get("margin", 60)); self.attack_delay_ms.set(p.get("ad", 500)); self.dash_delay_ms.set(p.get("dd", 1500))
        self.use_dash.set(p.get("use_dash", True)); self.use_anti_macro.set(p.get("use_anti", True)); self.hunt_mode.set(p.get("mode", 0))
        self.use_periodic.set(p.get("use_per", True)); self.periodic_interval_min.set(p.get("per_int", 5)); self.stationary_range.set(p.get("st_range", 5))
        self.use_sound_alert.set(p.get("use_sound", True)); self.always_on_top.set(p.get("top", True)); self.ui_opacity.set(p.get("opacity", 1.0))
        self.use_auto_sell.set(p.get("use_sell", False)); self.sell_interval_min.set(p.get("sell_int", 30))
        self.update_ui_settings()

if __name__ == "__main__":
    root = tk.Tk(); app = AutoHunterV7_0(root); root.mainloop()
"]["l"]); self.reg_w.set(d["reg"]["w"]); self.reg_h.set(d["reg"]["h"])
        self.x_min.set(d["range"]["min"]); self.x_max.set(d["range"]["max"])
        self.shop_npc_pos = s.get("npc", [0, 0]); self.shop_sell_btn_pos = s.get("btn", [0, 0])
        self.KEY_ATTACK.set(k.get("att", "end")); self.KEY_DASH.set(k.get("dash", "space")); self.KEY_JUMP.set(k.get("jump", "alt")); self.KEY_PERIODIC.set(k.get("per", "del")); self.KEY_SHOP.set(k.get("shop", "m"))
        self.color_margin.set(p.get("margin", 60)); self.attack_delay_ms.set(p.get("ad", 500)); self.dash_delay_ms.set(p.get("dd", 1500))
        self.use_dash.set(p.get("use_dash", True)); self.use_anti_macro.set(p.get("use_anti", True)); self.hunt_mode.set(p.get("mode", 0))
        self.use_periodic.set(p.get("use_per", True)); self.periodic_interval_min.set(p.get("per_int", 5)); self.stationary_range.set(p.get("st_range", 5))
        self.use_sound_alert.set(p.get("use_sound", True)); self.always_on_top.set(p.get("top", True)); self.ui_opacity.set(p.get("opacity", 1.0))
        self.use_auto_sell.set(p.get("use_sell", False)); self.sell_interval_min.set(p.get("sell_int", 30))
        self.update_ui_settings()

if __name__ == "__main__":
    root = tk.Tk(); app = AutoHunterV7_0(root); root.mainloop()
