import sys
import os
import time
import json
import random
import threading
import ctypes
import winsound
import cv2
import numpy as np
import mss
import pyautogui
import keyboard
import psutil
from PIL import Image

from PySide6.QtCore import Qt, QTimer, Signal, QObject, QSize, QPoint
from PySide6.QtGui import QColor, QFont, QImage, QPixmap, QIcon, QAction
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QGridLayout, QFrame, QLabel, QPushButton, QComboBox, QSlider, 
    QLineEdit, QTabWidget, QCheckBox, QRadioButton, QButtonGroup,
    QProgressBar, QTextEdit, QSizePolicy, QSpacerItem, QMessageBox
)

# 경로 설정
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(BASE_DIR, "AUTOmaple_v9.7_config.json")

# --- DPI 보정 ---
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except:
    pass

class Communicate(QObject):
    log_signal = Signal(str)
    preview_signal = Signal(np.ndarray)
    status_signal = Signal(dict)
    alert_signal = Signal()
    start_signal = Signal()
    stop_signal = Signal()
    sell_signal = Signal()
    shape_start_signal = Signal()
    shape_stop_signal = Signal()
    shape_monitor_signal = Signal(object)

class AUTOmapleV9_7(QMainWindow):
    def __init__(self):
        super().__init__()
        self.version = "v9.7.4"
        self.setWindowTitle(f"AUTOmaple Human-Engine {self.version} (2026.06.02)")
        self.setMinimumSize(1400, 950)
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        
        # 상태 변수
        self.is_running = False
        self.is_selling = False
        self.total_hunting_time = 0
        self.current_hunt_start = 0
        self.program_start_time = time.time()
        self.actions_cnt = 0
        self.err_cnt = 0
        self.frame_num = 0
        self.is_dragging_anti = False
        
        # 트래킹 관련 내부 변수
        self.last_target_pos = None
        self.velocity = [0, 0]
        
        # 기본 설정
        self.reg_t, self.reg_l, self.reg_w, self.reg_h = 100, 100, 200, 150
        self.x_min, self.x_max, self.stationary_range = 20, 180, 15
        self.precision_val, self.color_margin = 1.0, 60
        self.attack_delay_ms, self.dash_delay_ms = 500, 1500
        self.periodic_interval_min, self.sell_interval_min = 5, 15
        self.use_auto_sell, self.use_anti_macro, self.use_shape_anti, self.use_sound_alert = False, True, False, True
        self.hunt_mode = 0 
        self.base_lower = np.array([245, 230, 0]); self.base_upper = np.array([254, 255, 129])
        self.profiles_data = {}

        self.signals = Communicate()
        self.signals.log_signal.connect(self.update_log)
        self.signals.preview_signal.connect(self.update_minimap_preview)
        self.signals.shape_monitor_signal.connect(self.update_shape_analytics)
        self.signals.status_signal.connect(self.update_status_ui)
        self.signals.alert_signal.connect(self.play_custom_sound)

        self.setup_ui(); self.apply_qss()
        
        self.signals.start_signal.connect(self.start_btn.click)
        self.signals.stop_signal.connect(self.stop_btn.click)
        self.signals.sell_signal.connect(self.manual_sell_btn.click)
        self.signals.shape_start_signal.connect(lambda: self.chk_shape_anti.setChecked(True))
        self.signals.shape_stop_signal.connect(lambda: self.chk_shape_anti.setChecked(False))

        self.load_all_profiles()
        self.stop_threads = False
        threading.Thread(target=self.monitor_loop, daemon=True).start()
        threading.Thread(target=self.anti_macro_loop, daemon=True).start()
        threading.Thread(target=self.shape_tracking_loop, daemon=True).start()
        threading.Thread(target=self.status_update_loop, daemon=True).start()
        
        try:
            keyboard.unhook_all()
            keyboard.add_hotkey('f8', self.hotkey_start_handler)
            keyboard.add_hotkey('f9', self.hotkey_stop_handler)
            keyboard.add_hotkey('f2', self.hotkey_shape_start_handler)
            keyboard.add_hotkey('f3', self.hotkey_shape_stop_handler)
            keyboard.add_hotkey('f11', lambda: self.signals.sell_signal.emit())
        except: pass

    # --- 고급 마우스 트래킹 로직 (인간미 극대화) ---
    def human_mouse_move(self, tx, ty):
        """베지에 곡선 및 가속도 제어를 결합한 인간미 있는 마우스 트래킹"""
        try:
            pyautogui.PAUSE = 0
            cx, cy = pyautogui.position()
            
            # 목표물과의 거리 계산
            dist = np.hypot(tx - cx, ty - cy)
            if dist < 2: return

            # 1. 반응 지연 및 가속도 시뮬레이션
            # 거리가 멀면 빠르게, 가까우면 정밀하게 접근 (인간의 추적 본능)
            lerp_factor = random.uniform(0.15, 0.45) if dist > 50 else random.uniform(0.5, 0.8)
            
            # 2. 오버슈트 및 미세 떨림 추가
            # 타겟 주변에서 살짝 흔들리거나 지나치는 현상 구현
            overshoot_x = random.uniform(-3, 3) if dist < 20 else 0
            overshoot_y = random.uniform(-3, 3) if dist < 20 else 0
            
            target_x = cx + (tx - cx) * lerp_factor + overshoot_x
            target_y = cy + (ty - cy) * lerp_factor + overshoot_y
            
            # 3. 마우스 이동 실행
            pyautogui.moveTo(target_x, target_y)
            
        except Exception as e:
            pass

    def get_anti_target_color(self):
        """anti1.png에서 타겟 색상 정밀 추출 (핑크/보라 계열 우선 순위)"""
        path = os.path.join(BASE_DIR, "anti1.png")
        if not os.path.exists(path): 
            self.log("❌ [AI-Engine] anti1.png 누락 - 기본 색상값 사용")
            return np.array([140, 50, 50]), np.array([175, 255, 255]) # 일반적인 핑크계열 HSV
        try:
            img = cv2.imread(path)
            hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
            mask = cv2.inRange(hsv, (140, 50, 50), (175, 255, 255)) # 핑크 영역만 추출 시도
            if np.any(mask):
                target_hsv = hsv[mask > 0]
                avg_hsv = np.mean(target_hsv, axis=0)
            else:
                avg_hsv = np.mean(hsv[img.shape[0]//4:3*img.shape[0]//4, img.shape[1]//4:3*img.shape[1]//4], axis=(0,1))
            
            self.log(f"💡 [AI-Engine] 타겟 색상 분석 완료: HSV {int(avg_hsv[0])}")
            lower = np.array([max(0, avg_hsv[0]-20), max(40, avg_hsv[1]-60), max(40, avg_hsv[2]-60)])
            upper = np.array([min(180, avg_hsv[0]+20), min(255, avg_hsv[1]+60), min(255, avg_hsv[2]+60)])
            return lower, upper
        except: return None, None

    def shape_tracking_loop(self):
        BG_PATTERN = os.path.join(BASE_DIR, "game_background_pattern.png")
        last_log, detect_cnt, lost_cnt = 0, 0, 0
        target_lower, target_upper = None, None
        
        while not self.stop_threads:
            if self.use_shape_anti:
                try:
                    if target_lower is None: target_lower, target_upper = self.get_anti_target_color()
                    with mss.mss() as sct:
                        monitor = sct.monitors[1] # 주 모니터
                        scr = np.array(sct.grab(monitor))
                        scr_bgr = cv2.cvtColor(scr, cv2.COLOR_BGRA2BGR)
                        
                        # 1. 배경 제거 (Static Background Removal)
                        bg_ref = cv2.imread(BG_PATTERN, cv2.IMREAD_GRAYSCALE)
                        if bg_ref is not None:
                            scr_gray = cv2.cvtColor(scr_bgr, cv2.COLOR_BGR2GRAY)
                            if scr_gray.shape != bg_ref.shape: bg_ref = cv2.resize(bg_ref, (scr_gray.shape[1], scr_gray.shape[0]))
                            diff = cv2.absdiff(scr_gray, bg_ref)
                            _, moving_mask = cv2.threshold(diff, 30, 255, cv2.THRESH_BINARY)
                        else: moving_mask = np.ones((scr.shape[0], scr.shape[1]), dtype=np.uint8) * 255

                        # 2. 색상 필터링 (Target Color Matching)
                        hsv = cv2.cvtColor(scr_bgr, cv2.COLOR_BGR2HSV)
                        color_mask = cv2.inRange(hsv, target_lower, target_upper)
                        
                        # 3. 최종 마스크 결합 및 노이즈 제거
                        final_mask = cv2.bitwise_and(moving_mask, color_mask)
                        final_mask = cv2.morphologyEx(final_mask, cv2.MORPH_OPEN, np.ones((5,5), np.uint8))
                        
                        debug_feed = cv2.addWeighted(scr_bgr, 0.5, np.zeros(scr_bgr.shape, scr_bgr.dtype), 0, 0)
                        self.frame_num += 1; log_msg, found_valid = "", False
                        
                        contours, _ = cv2.findContours(final_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                        if contours:
                            valid_contours = [c for c in contours if cv2.contourArea(c) > 70]
                            if valid_contours:
                                best_cnt = max(valid_contours, key=cv2.contourArea)
                                area = cv2.contourArea(best_cnt)
                                x, y, w, h = cv2.boundingRect(best_cnt)
                                if 0.4 < w/h < 2.5:
                                    detect_cnt += 1; lost_cnt = 0; found_valid = True
                                    M = cv2.moments(best_cnt)
                                    if M["m00"] > 0:
                                        tx, ty = int(M["m10"]/M["m00"]) + monitor["left"], int(M["m01"]/M["m00"]) + monitor["top"]
                                        cv2.rectangle(debug_feed, (x, y), (x+w, y+h), (0, 255, 0), 2)
                                        
                                        if detect_cnt >= 1:
                                            if not self.is_dragging_anti:
                                                pyautogui.mouseDown(); self.is_dragging_anti = True
                                                self.log("🎯 [Human-Engine] 타겟 고정 - 추적 시작")
                                            self.human_mouse_move(tx, ty)
                                            log_msg = f"f [{self.frame_num:05d}] TRACKING target pos=({tx},{ty})"
                        
                        if not found_valid:
                            detect_cnt = 0; lost_cnt += 1
                            if lost_cnt > 6 and self.is_dragging_anti:
                                pyautogui.mouseUp(); self.is_dragging_anti = False; self.log("🏁 [Human-Engine] 추적 종료")
                        
                        self.signals.shape_monitor_signal.emit((debug_feed, log_msg))
                except Exception as e: pass
            else:
                if self.is_dragging_anti: pyautogui.mouseUp(); self.is_dragging_anti = False
                target_lower, target_upper = None, None
            time.sleep(0.02) # 50FPS급 추적 성능

    # --- UI 및 유틸리티 (기존 로직 유지/최적화) ---
    def setup_ui(self):
        central_widget = QWidget(); self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget); main_layout.setContentsMargins(25, 25, 25, 40); main_layout.setSpacing(20)
        header = QHBoxLayout(); self.title_label = QLabel("AUTOmaple"); self.title_label.setObjectName("mainTitle")
        header.addWidget(self.title_label); header.addStretch()
        p_box = QVBoxLayout(); p_box.addWidget(QLabel("AI 프로필 관리 센터 /", objectName="subLabel"))
        self.profile_combo = QComboBox(); self.profile_combo.setMinimumWidth(320); self.profile_combo.setFixedHeight(45)
        self.profile_combo.setEditable(True); self.profile_combo.currentTextChanged.connect(self.on_profile_change); p_box.addWidget(self.profile_combo)
        header.addLayout(p_box); self.save_btn = QPushButton("설정 저장"); self.save_btn.setObjectName("saveBtn"); self.save_btn.setFixedSize(140, 60); self.save_btn.clicked.connect(self.save_current_profile); header.addWidget(self.save_btn); main_layout.addLayout(header)
        content_layout = QHBoxLayout(); content_layout.setSpacing(20)
        left_frame = QFrame(); left_frame.setObjectName("panelFrame"); left_frame.setFixedWidth(500); left_vbox = QVBoxLayout(left_frame); left_vbox.setContentsMargins(15, 20, 15, 15)
        mini_header = QHBoxLayout(); mini_header.addWidget(QLabel("MINIMAP ANALYTICS", objectName="panelTitle")); mini_header.addStretch()
        self.sel_btn = QPushButton("영역 설정"); self.sel_btn.setFixedSize(80, 25); self.sel_btn.setStyleSheet("font-size: 10px; padding: 2px; border-radius: 5px; background-color: #238636; color: white;"); self.sel_btn.clicked.connect(self.open_selector); mini_header.addWidget(self.sel_btn); left_vbox.addLayout(mini_header)
        self.minimap_preview = QLabel("WAITING..."); self.minimap_preview.setObjectName("previewLabel"); self.minimap_preview.setFixedSize(470, 200); self.minimap_preview.setAlignment(Qt.AlignCenter); left_vbox.addWidget(self.minimap_preview); left_vbox.addSpacing(15); left_vbox.addWidget(QLabel("MACRO DETECTION ENGINE [LIVE]", objectName="panelTitle"))
        self.shape_preview = QLabel("SEARCHING..."); self.shape_preview.setObjectName("previewLabel"); self.shape_preview.setFixedSize(470, 260); self.shape_preview.setAlignment(Qt.AlignCenter); left_vbox.addWidget(self.shape_preview); self.shape_console = QTextEdit(); self.shape_console.setReadOnly(True); self.shape_console.setFixedHeight(100); self.shape_console.setObjectName("logTerminal"); self.shape_console.setStyleSheet("color: #58a6ff; font-size: 10px;"); left_vbox.addWidget(self.shape_console); content_layout.addWidget(left_frame)
        center_frame = QFrame(objectName="panelFrame"); center_vbox = QVBoxLayout(center_frame); center_vbox.setContentsMargins(15, 30, 15, 15); center_vbox.addWidget(QLabel("CORE ALGORITHM", objectName="panelTitle")); self.main_tabs = QTabWidget(); center_vbox.addWidget(self.main_tabs)
        self.mode_tabs = QTabWidget(); self.mode_tabs.currentChanged.connect(self.on_hunt_mode_tab_changed); tab_lr_widget = QWidget(); tab_lr_vbox = QVBoxLayout(tab_lr_widget); self.x_min_slider = self.create_slider_row(tab_lr_vbox, "좌측 경계:", 0, 400, self.x_min, self.update_x_min); self.x_max_slider = self.create_slider_row(tab_lr_vbox, "우측 경계:", 0, 400, self.x_max, self.update_x_max); tab_lr_vbox.addStretch(); self.mode_tabs.addTab(tab_lr_widget, "좌우 이동"); tab_st_widget = QWidget(); tab_st_vbox = QVBoxLayout(tab_st_widget); self.stat_range_slider = self.create_slider_row(tab_st_vbox, "제자리 범위:", 1, 100, self.stationary_range, self.update_stat_range); tab_st_vbox.addStretch(); self.mode_tabs.addTab(tab_st_widget, "제자리 사냥"); self.main_tabs.addTab(self.mode_tabs, "작동 모드")
        tab_skill_widget = QWidget(); tab_skill_vbox = QVBoxLayout(tab_skill_widget); self.precision_slider = self.create_slider_row(tab_skill_vbox, "인식 정밀도:", 1, 30, int(self.precision_val*10), self.update_precision, is_float=True); self.att_slider = self.create_slider_row(tab_skill_vbox, "공격 주기:", 100, 3000, self.attack_delay_ms, self.update_att_delay); self.dash_slider = self.create_slider_row(tab_skill_vbox, "이동 주기:", 100, 10000, self.dash_delay_ms, self.update_dash_delay); self.pet_slider = self.create_slider_row(tab_skill_vbox, "소모품(분):", 1, 60, self.periodic_interval_min, self.update_pet_interval); key_grid = QGridLayout(); key_grid.setSpacing(12); self.key_att_cb = self.create_key_combo(key_grid, "공격", 0, 0, "end"); self.key_dash_cb = self.create_key_combo(key_grid, "이동", 0, 1, "space"); self.key_jump_cb = self.create_key_combo(key_grid, "점프", 1, 0, "alt"); self.key_pet_cb = self.create_key_combo(key_grid, "소모품", 1, 1, "del"); tab_skill_vbox.addLayout(key_grid); tab_skill_vbox.addStretch(); self.main_tabs.addTab(tab_skill_widget, "단축키/정밀도")
        tab_adv_widget = QWidget(); tab_adv_vbox = QVBoxLayout(tab_adv_widget); self.chk_alert = QCheckBox("거탐 알람 울리기"); self.chk_alert.setChecked(True); self.chk_alert.toggled.connect(self.update_use_alert); tab_adv_vbox.addWidget(self.chk_alert); self.chk_shape_anti = QCheckBox("투명 도형 추적 엔진 활성화"); self.chk_shape_anti.setChecked(False); self.chk_shape_anti.toggled.connect(self.update_use_shape_anti); tab_adv_vbox.addWidget(self.chk_shape_anti); self.chk_sell = QCheckBox("자동 판매 (준비 중)"); self.chk_sell.setEnabled(False); tab_adv_vbox.addWidget(self.chk_sell); self.sell_slider = self.create_slider_row(tab_adv_vbox, "판매 주기:", 10, 60, self.sell_interval_min, self.update_sell_interval); self.chk_top = QCheckBox("창 항상 맨 위로 고정"); self.chk_top.setChecked(True); self.chk_top.toggled.connect(self.update_window_flags); tab_adv_vbox.addWidget(self.chk_top); self.opacity_slider = self.create_slider_row(tab_adv_vbox, "투명도:", 30, 100, 100, self.update_opacity); tab_adv_vbox.addStretch(); self.main_tabs.addTab(tab_adv_widget, "시스템 환경"); content_layout.addWidget(center_frame)
        right_frame = QFrame(objectName="panelFrame"); right_frame.setFixedWidth(330); right_vbox = QVBoxLayout(right_frame); right_vbox.setContentsMargins(20, 30, 20, 20); right_vbox.addWidget(QLabel("SYSTEM METRICS", objectName="panelTitle")); self.cpu_label = QLabel("CPU 사용률(0%)", objectName="subLabel"); right_vbox.addWidget(self.cpu_label); self.cpu_bar = QProgressBar(objectName="metricBar"); self.cpu_bar.setFixedHeight(12); self.cpu_bar.setTextVisible(False); right_vbox.addWidget(self.cpu_bar); right_vbox.addSpacing(10); self.ram_label = QLabel("RAM 점유율(0%)", objectName="subLabel"); right_vbox.addWidget(self.ram_label); self.ram_bar = QProgressBar(objectName="metricBar"); self.ram_bar.setFixedHeight(12); self.ram_bar.setTextVisible(False); right_vbox.addWidget(self.ram_bar); right_vbox.addSpacing(25); self.data_runtime = self.create_data_row(right_vbox, "가동 시간", "00:00:00"); self.data_total_time = self.create_data_row(right_vbox, "누적 사냥", "00:00:00"); self.data_actions = self.create_data_row(right_vbox, "명령 횟수", "0"); self.data_errors = self.create_data_row(right_vbox, "탐지 기록", "0회"); right_vbox.addSpacing(25); right_vbox.addWidget(QLabel("SYSTEM LOGS", objectName="panelTitle")); self.log_text = QTextEdit(); self.log_text.setObjectName("logTerminal"); self.log_text.setReadOnly(True); right_vbox.addWidget(self.log_text); content_layout.addWidget(right_frame); main_layout.addLayout(content_layout)
        footer = QHBoxLayout(); footer.setSpacing(15); self.start_btn = QPushButton("사냥 시작 [F8]", objectName="startBtn"); self.start_btn.setFixedHeight(85); self.start_btn.clicked.connect(self.start_hunting); footer.addWidget(self.start_btn, 2); self.stop_btn = QPushButton("사냥 중지 [F9]", objectName="stopBtn"); self.stop_btn.setFixedHeight(85); self.stop_btn.clicked.connect(self.stop_hunting); self.stop_btn.setEnabled(False); footer.addWidget(self.stop_btn, 2); self.manual_sell_btn = QPushButton("인벤 판매 [F11]", objectName="sellBtn"); self.manual_sell_btn.setFixedHeight(85); self.manual_sell_btn.clicked.connect(self.run_manual_sell); footer.addWidget(self.manual_sell_btn, 1); self.stop_all_btn = QPushButton("종료"); self.stop_all_btn.setObjectName("stopBtn"); self.stop_all_btn.setFixedHeight(85); self.stop_all_btn.clicked.connect(self.close); footer.addWidget(self.stop_all_btn, 1); main_layout.addLayout(footer)

    def apply_qss(self):
        style = """QMainWindow { background-color: #0b0e14; } #mainTitle { color: #ffffff; font-size: 42px; font-weight: 900; } #panelTitle { color: #00d2ff; font-size: 16px; font-weight: 800; } #subLabel { color: #8a99af; font-size: 13px; } #dataLabel { color: #64748b; font-size: 15px; } #dataValue { color: #ffffff; font-size: 18px; font-weight: 700; } #panelFrame { background-color: #161b22; border: 1px solid #30363d; border-radius: 25px; } QTabWidget::pane { border: 1px solid #30363d; background: #161b22; border-radius: 15px; } QTabBar::tab { background: #0d1117; color: #8b949e; padding: 12px 10px; min-width: 110px; } QTabBar::tab:selected { background: #161b22; color: #00d2ff; border-bottom: 3px solid #00d2ff; } QPushButton { background-color: #21262d; color: #c9d1d9; border-radius: 15px; font-weight: 700; } #startBtn { background-color: #238636; color: #ffffff; font-size: 28px; } #stopBtn { border: 2px solid #f85149; color: #f85149; font-size: 24px; } #logTerminal { background-color: #0d1117; color: #8b949e; border-radius: 15px; padding: 10px; } QLabel#previewLabel { background-color: #000000; border-radius: 20px; border: 2px solid #30363d; }"""
        self.setStyleSheet(style)

    def update_log(self, msg):
        self.log_text.append(f"<span style='color:#484f58'>[{time.strftime('%H:%M:%S')}]</span> {msg}")
        self.log_text.verticalScrollBar().setValue(self.log_text.verticalScrollBar().maximum())

    def update_status_ui(self, data):
        self.data_runtime.setText(data.get("uptime", "00:00:00")); self.data_total_time.setText(data.get("total_uptime", "00:00:00"))
        self.cpu_bar.setValue(data.get('cpu', 0)); self.ram_bar.setValue(data.get('ram', 0))
        self.data_actions.setText(str(data.get("actions", 0))); self.data_errors.setText(f"{data.get('err_cnt', 0)}회")

    def hunter_core(self):
        cur_dir, last_x, stuck_cnt, l_att, l_dash, l_del = 'right', -1, 0, 0, 0, time.time()
        try:
            while self.is_running:
                if self.is_selling or self.is_dragging_anti: 
                    if self.is_dragging_anti: pyautogui.keyUp('left'); pyautogui.keyUp('right')
                    time.sleep(0.1); continue
                with mss.mss() as sct:
                    reg = {"top": self.reg_t, "left": self.reg_l, "width": self.reg_w, "height": self.reg_h}
                    shot = np.array(sct.grab(reg)); img = cv2.cvtColor(shot, cv2.COLOR_BGRA2BGR); m = self.color_margin
                    low = np.array([max(0, self.base_lower[2]-m), max(0, self.base_lower[1]-m), max(0, self.base_lower[0]-m)])
                    high = np.array([min(255, self.base_upper[2]+m), min(255, self.base_upper[1]+m), min(255, self.base_upper[0]+m)])
                    mask = cv2.inRange(img, low, high)
                    if np.any(mask):
                        M = cv2.moments(mask); cx = int(M["m10"]/M["m00"]) if M["m00"] > 0 else -1
                        if cx != -1:
                            if self.hunt_mode == 0:
                                if cx >= self.x_max and cur_dir == 'right': pyautogui.keyUp('right'); cur_dir = 'left'
                                elif cx <= self.x_min and cur_dir == 'left': pyautogui.keyUp('left'); cur_dir = 'right'
                            pyautogui.keyDown(cur_dir)
                            now = time.time()*1000
                            if now - l_att >= self.attack_delay_ms: self.press_key(self.key_att_cb.currentText()); l_att = now
                            if now - l_dash >= self.dash_delay_ms: self.press_key(self.key_dash_cb.currentText()); l_dash = now
                            if time.time() - l_del >= self.periodic_interval_min*60: self.press_key(self.key_pet_cb.currentText()); l_del = time.time()
                time.sleep(0.04)
        finally: pyautogui.keyUp('left'); pyautogui.keyUp('right'); self.is_running = False

    def monitor_loop(self):
        with mss.mss() as sct:
            while not self.stop_threads:
                if self.reg_w > 5:
                    reg = {"top": self.reg_t, "left": self.reg_l, "width": self.reg_w, "height": self.reg_h}
                    try:
                        shot = np.array(sct.grab(reg)); img = cv2.cvtColor(shot, cv2.COLOR_BGRA2BGR); m = self.color_margin
                        low = np.array([max(0, self.base_lower[2]-m), max(0, self.base_lower[1]-m), max(0, self.base_lower[0]-m)])
                        high = np.array([min(255, self.base_upper[2]+m), min(255, self.base_upper[1]+m), min(255, self.base_upper[0]+m)])
                        mask = cv2.inRange(img, low, high); p_img = img.copy()
                        cv2.line(p_img, (self.x_min, 0), (self.x_min, self.reg_h), (59, 130, 246), 2)
                        cv2.line(p_img, (self.x_max, 0), (self.x_max, self.reg_h), (239, 68, 68), 2)
                        if np.any(mask):
                            M = cv2.moments(mask)
                            if M["m00"] > 0: cx, cy = int(M["m10"]/M["m00"]), int(M["m01"]/M["m00"]); cv2.circle(p_img, (cx, cy), 5, (34, 197, 94), -1)
                        self.signals.preview_signal.emit(p_img)
                    except: pass
                time.sleep(0.1)

    def status_update_loop(self):
        while not self.stop_threads:
            try:
                up = int(time.time() - self.current_hunt_start) if self.is_running else 0
                total = self.total_hunting_time + up
                self.signals.status_signal.emit({
                    "uptime": f"{up//3600:02d}:{(up%3600)//60:02d}:{up%60:02d}",
                    "total_uptime": f"{total//3600:02d}:{(total%3600)//60:02d}:{total%60:02d}",
                    "cpu": int(psutil.cpu_percent()), "ram": int(psutil.virtual_memory().percent),
                    "actions": self.actions_cnt, "err_cnt": self.err_cnt
                })
            except: pass
            time.sleep(1.0)

    def press_key(self, k): pyautogui.keyDown(k); time.sleep(random.uniform(0.05, 0.1)); pyautogui.keyUp(k); self.actions_cnt += 1
    def start_hunting(self): self.is_running = True; self.start_btn.setEnabled(False); self.stop_btn.setEnabled(True); self.current_hunt_start = time.time(); threading.Thread(target=self.hunter_core, daemon=True).start()
    def stop_hunting(self): self.is_running = False; self.start_btn.setEnabled(True); self.stop_btn.setEnabled(False); self.total_hunting_time += int(time.time()-self.current_hunt_start); pyautogui.keyUp('left'); pyautogui.keyUp('right')
    def hotkey_start_handler(self): self.signals.start_signal.emit()
    def hotkey_stop_handler(self): self.signals.stop_signal.emit()
    def hotkey_shape_start_handler(self): self.signals.shape_start_signal.emit()
    def hotkey_shape_stop_handler(self): self.signals.shape_stop_signal.emit()
    def update_use_shape_anti(self, b): self.use_shape_anti = b
    def update_use_alert(self, b): self.use_sound_alert = b
    def update_x_min(self, v): self.x_min = v
    def update_x_max(self, v): self.x_max = v
    def update_stat_range(self, v): self.stationary_range = v
    def update_precision(self, v): self.precision_val = v/10.0; self.color_margin = int(self.precision_val*50)
    def update_att_delay(self, v): self.attack_delay_ms = v
    def update_dash_delay(self, v): self.dash_delay_ms = v
    def update_pet_interval(self, v): self.periodic_interval_min = v
    def update_sell_interval(self, v): self.sell_interval_min = v
    def update_opacity(self, v): self.setWindowOpacity(v/100.0)
    def update_window_flags(self): self.setWindowFlags((self.windowFlags() | Qt.WindowStaysOnTopHint) if self.chk_top.isChecked() else (self.windowFlags() & ~Qt.WindowStaysOnTopHint)); self.show()
    def on_hunt_mode_tab_changed(self, i): self.hunt_mode = i
    def update_shape_analytics(self, d): self.update_shape_preview(d[0]); (self.shape_console.append(d[1]), self.shape_console.verticalScrollBar().setValue(self.shape_console.verticalScrollBar().maximum())) if d[1] else None
    def update_minimap_preview(self, i): h, w, c = i.shape; self.minimap_preview.setPixmap(QPixmap.fromImage(QImage(i.data, w, h, c*w, QImage.Format_RGB888).rgbSwapped()).scaled(self.minimap_preview.size(), Qt.IgnoreAspectRatio, Qt.SmoothTransformation))
    def update_shape_preview(self, i): h, w, c = i.shape; self.shape_preview.setPixmap(QPixmap.fromImage(QImage(i.data, w, h, c*w, QImage.Format_RGB888).rgbSwapped()).scaled(self.shape_preview.size(), Qt.IgnoreAspectRatio, Qt.SmoothTransformation))
    def on_profile_change(self, n): self.apply_profile_data(n) if n in self.profiles_data else None
    def update_profile_list(self): self.profile_combo.blockSignals(True); self.profile_combo.clear(); self.profile_combo.addItems(list(self.profiles_data.keys())); self.profile_combo.blockSignals(False)
    def load_all_profiles(self): (self.profiles_data.update(json.load(open(CONFIG_FILE, "r", encoding="utf-8"))), self.update_profile_list(), self.apply_profile_data(list(self.profiles_data.keys())[0])) if os.path.exists(CONFIG_FILE) else None
    def save_current_profile(self): n = self.profile_combo.currentText(); self.profiles_data[n] = {"reg": {"t": self.reg_t, "l": self.reg_l, "w": self.reg_w, "h": self.reg_h}, "range": {"min": self.x_min, "max": self.x_max, "stat": self.stationary_range}, "keys": {"att": self.key_att_cb.currentText(), "dash": self.key_dash_cb.currentText(), "jump": self.key_jump_cb.currentText(), "pet": self.key_pet_cb.currentText()}, "params": {"margin": self.color_margin, "precision": self.precision_val, "ad": self.attack_delay_ms, "dd": self.dash_delay_ms, "mode": self.hunt_mode, "per_int": self.periodic_interval_min, "sell_int": self.sell_interval_min, "sound": self.use_sound_alert, "shape_anti": self.use_shape_anti}}; json.dump(self.profiles_data, open(CONFIG_FILE, "w", encoding="utf-8"), ensure_ascii=False, indent=4); self.update_profile_list(); QMessageBox.information(self, "저장", "프로필 저장됨")
    def apply_profile_data(self, n): d = self.profiles_data[n]; p = d["params"]; self.reg_t, self.reg_l, self.reg_w, self.reg_h = d["reg"]["t"], d["reg"]["l"], d["reg"]["w"], d["reg"]["h"]; self.x_min_slider.setValue(d["range"]["min"]); self.x_max_slider.setValue(d["range"]["max"]); self.stat_range_slider.setValue(d["range"]["stat"]); self.precision_slider.setValue(int(p["precision"]*10)); self.att_slider.setValue(p["ad"]); self.dash_slider.setValue(p["dd"]); self.pet_slider.setValue(p["per_int"]); self.sell_slider.setValue(p["sell_int"]); self.chk_alert.setChecked(p["sound"]); self.chk_shape_anti.setChecked(p["shape_anti"]); self.mode_tabs.setCurrentIndex(p["mode"])
    def open_selector(self): self.selector = QWidget(); self.selector.setWindowOpacity(0.3); self.selector.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint); self.selector.showFullScreen(); self.selector.mousePressEvent = lambda e: setattr(self, 'sel_start', e.pos()); self.selector.mouseReleaseEvent = self.sel_finish; self.selector.show()
    def sel_finish(self, e): end = e.pos(); self.reg_l, self.reg_t, self.reg_w, self.reg_h = min(self.sel_start.x(), end.x()), min(self.sel_start.y(), end.y()), abs(self.sel_start.x()-end.x()), abs(self.sel_start.y()-end.y()); self.selector.close()
    def play_custom_sound(self): 
        def _p():
            s = time.time()
            while time.time()-s < 10 and self.use_sound_alert: winsound.Beep(3000, 100); winsound.Beep(4000, 100)
        threading.Thread(target=_p, daemon=True).start()
    def create_slider_row(self, l, txt, min_v, max_v, cur, cb, is_float=False): row = QHBoxLayout(); row.addWidget(QLabel(txt, objectName="dataLabel")); s = QSlider(Qt.Horizontal); s.setRange(min_v, max_v); s.setValue(int(cur)); v_lbl = QLabel(str(cur/10.0 if is_float else cur)); s.valueChanged.connect(lambda v: (v_lbl.setText(str(v/10.0 if is_float else v)), cb(v))); row.addWidget(s); row.addWidget(v_lbl); l.addLayout(row); return s
    def create_key_combo(self, g, txt, r, c, d): box = QVBoxLayout(); box.addWidget(QLabel(txt, objectName="subLabel")); cb = QComboBox(); cb.addItems(["space", "ctrl", "alt", "shift", "insert", "del", "home", "end", "pgup", "pgdn"] + list("abcdefghijklmnopqrstuvwxyz")); cb.setCurrentText(d); box.addWidget(cb); g.addLayout(box, r, c); return cb
    def log(self, m): self.signals.log_signal.emit(m)
    def closeEvent(self, e): self.stop_threads = True; self.is_running = False; (pyautogui.keyUp('left'), pyautogui.keyUp('right'), pyautogui.mouseUp()) if True else None; e.accept()
    def anti_macro_loop(self):
        while not self.stop_threads:
            if self.use_anti_macro:
                try:
                    with mss.mss() as sct:
                        img = np.array(sct.grab(sct.monitors[0])); gray = cv2.cvtColor(img, cv2.COLOR_BGRA2GRAY)
                        for i in range(1, 5):
                            p = os.path.join(BASE_DIR, f"anti{i}.png")
                            if os.path.exists(p) and np.max(cv2.matchTemplate(gray, cv2.imread(p, 0), cv2.TM_CCOEFF_NORMED)) > 0.8:
                                self.err_cnt += 1; self.signals.alert_signal.emit(); break
                except: pass
            time.sleep(2)

if __name__ == "__main__":
    app = QApplication(sys.argv); window = AUTOmapleV9_7(); window.show(); sys.exit(app.exec())
