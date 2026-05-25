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

# 설정 파일 경로
CONFIG_FILE = "hunter_premium_v7_0_config.json"

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
    start_signal = Signal() # 사냥 시작 전용
    stop_signal = Signal()  # 사냥 중지 전용
    sell_signal = Signal()  # 판매 전용
    shape_monitor_signal = Signal(object) # (img, log_msg) 튜플 전용

class ShapeMonitorWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("AI 도형거탐 디버깅 엔진 [MOTION TRACKER]")
        self.setFixedSize(1000, 700)
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.setStyleSheet("background-color: #0b0e14; color: white;")
        
        main_layout = QVBoxLayout()
        
        # 1. 시각화 영역
        self.img_label = QLabel("디버깅 엔진 대기 중...")
        self.img_label.setAlignment(Qt.AlignCenter)
        self.img_label.setStyleSheet("background-color: #000000; border: 2px solid #30363d; border-radius: 10px;")
        main_layout.addWidget(self.img_label, 7)
        
        # 2. 실시간 연산 로그 (터미널 스타일)
        self.console_log = QTextEdit()
        self.console_log.setReadOnly(True)
        self.console_log.setStyleSheet("""
            background-color: #0d1117; 
            color: #58a6ff; 
            font-family: 'Consolas', 'Courier New', monospace; 
            font-size: 11px; 
            border: 1px solid #30363d;
            border-radius: 5px;
        """)
        main_layout.addWidget(self.console_log, 3)
        
        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

    def update_frame(self, frame):
        h, w, c = frame.shape
        bytes_per_line = c * w
        q_img = QImage(frame.data, w, h, bytes_per_line, QImage.Format_RGB888).rgbSwapped()
        pixmap = QPixmap.fromImage(q_img).scaled(self.img_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.img_label.setPixmap(pixmap)

    def append_console(self, msg):
        self.console_log.append(msg)
        # 자동 스크롤
        self.console_log.verticalScrollBar().setValue(self.console_log.verticalScrollBar().maximum())
        # 로그 과부하 방지 (최근 100줄 유지)
        if self.console_log.document().blockCount() > 100:
            cursor = self.console_log.textCursor()
            cursor.movePosition(cursor.Start)
            cursor.select(cursor.BlockUnderCursor)
            cursor.removeSelectedText()
            cursor.deleteChar()

class AutoHunterV7_0(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AUTOmaple 도형거탐버전 v9.5.0 (2026.05.26)")
        self.setMinimumSize(1400, 950) # 가로폭 확장
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        
        # 1. 상태 변수 초기화
        self.is_running = False
        self.is_selling = False
        self.total_hunting_time = 0
        self.current_hunt_start = 0
        self.program_start_time = time.time()
        self.actions_cnt = 0
        self.err_cnt = 0
        self.last_sell_time = time.time()
        self.frame_num = 0
        
        # 2. 사냥 설정 초기화
        self.reg_t, self.reg_l = 100, 100
        self.reg_w, self.reg_h = 200, 150
        self.x_min, self.x_max = 20, 180
        self.stationary_range = 15
        self.precision_val = 1.0
        self.color_margin = 60
        self.attack_delay_ms = 500
        self.dash_delay_ms = 1500
        self.periodic_interval_min = 5
        self.sell_interval_min = 15
        self.use_auto_sell = False
        self.use_anti_macro = True
        self.use_shape_anti = False
        self.use_sound_alert = True
        self.hunt_mode = 0 
        
        self.base_lower = np.array([245, 230, 0])
        self.base_upper = np.array([254, 255, 129])
        self.profiles_data = {}

        # 3. 시그널 생성
        self.signals = Communicate()
        self.signals.log_signal.connect(self.update_log)
        self.signals.preview_signal.connect(self.update_minimap_preview)
        self.signals.shape_monitor_signal.connect(self.update_shape_analytics)
        self.signals.status_signal.connect(self.update_status_ui)
        self.signals.alert_signal.connect(self.play_custom_sound)

        # 4. UI 구성
        self.setup_ui()
        self.apply_qss()
        
        # 5. 시그널-버튼 물리적 연결
        self.signals.start_signal.connect(self.start_btn.click)
        self.signals.stop_signal.connect(self.stop_btn.click)
        self.signals.sell_signal.connect(self.manual_sell_btn.click)

        # 6. 프로필 로드
        self.load_all_profiles()

        # 7. 백그라운드 스레드 가동
        self.stop_threads = False
        threading.Thread(target=self.monitor_loop, daemon=True).start()
        threading.Thread(target=self.anti_macro_loop, daemon=True).start()
        threading.Thread(target=self.shape_tracking_loop, daemon=True).start()
        threading.Thread(target=self.status_update_loop, daemon=True).start()
        
        # 8. 전역 단축키 등록
        try:
            keyboard.unhook_all()
            keyboard.add_hotkey('f8', self.hotkey_start_handler)
            keyboard.add_hotkey('f9', self.hotkey_stop_handler)
            keyboard.add_hotkey('f11', lambda: self.signals.sell_signal.emit())
        except: pass

    def update_shape_analytics(self, data):
        img, log_msg = data
        self.update_shape_preview(img)
        if log_msg:
            self.append_shape_console(log_msg)

    def append_shape_console(self, msg):
        self.shape_console.append(msg)
        self.shape_console.verticalScrollBar().setValue(self.shape_console.verticalScrollBar().maximum())
        if self.shape_console.document().blockCount() > 50:
            cursor = self.shape_console.textCursor()
            cursor.movePosition(cursor.Start)
            cursor.select(cursor.BlockUnderCursor)
            cursor.removeSelectedText()
            cursor.deleteChar()

    def update_minimap_preview(self, img):
        h, w, c = img.shape; bytes_per_line = c * w; q_img = QImage(img.data, w, h, bytes_per_line, QImage.Format_RGB888).rgbSwapped()
        pixmap = QPixmap.fromImage(q_img).scaled(370, 210, Qt.KeepAspectRatio, Qt.SmoothTransformation); self.minimap_preview.setPixmap(pixmap)

    def update_shape_preview(self, img):
        h, w, c = img.shape; bytes_per_line = c * w; q_img = QImage(img.data, w, h, bytes_per_line, QImage.Format_RGB888).rgbSwapped()
        pixmap = QPixmap.fromImage(q_img).scaled(self.shape_preview.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation); self.shape_preview.setPixmap(pixmap)

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(25, 25, 25, 25)
        main_layout.setSpacing(20)

        header = QHBoxLayout()
        self.title_label = QLabel("AUTOmaple")
        self.title_label.setObjectName("mainTitle")
        header.addWidget(self.title_label); header.addStretch()
        
        p_box = QVBoxLayout()
        p_box.addWidget(QLabel("AI 프로필 관리 센터 /", objectName="subLabel"))
        self.profile_combo = QComboBox()
        self.profile_combo.setMinimumWidth(320); self.profile_combo.setFixedHeight(45)
        self.profile_combo.setEditable(True)
        self.profile_combo.currentTextChanged.connect(self.on_profile_change)
        p_box.addWidget(self.profile_combo)
        header.addLayout(p_box)
        
        self.save_btn = QPushButton("설정 저장")
        self.save_btn.setObjectName("saveBtn"); self.save_btn.setFixedSize(140, 60)
        self.save_btn.clicked.connect(self.save_current_profile)
        header.addWidget(self.save_btn)
        main_layout.addLayout(header)

        content_layout = QHBoxLayout(); content_layout.setSpacing(20)

        # [변경 1] Analytics Panel (기존 우측 -> 좌측 이동)
        left_frame = QFrame(); left_frame.setObjectName("panelFrame"); left_frame.setFixedWidth(500)
        left_vbox = QVBoxLayout(left_frame); left_vbox.setContentsMargins(15, 20, 15, 15)
        
        # Minimap Section with Small Button
        mini_header = QHBoxLayout()
        mini_header.addWidget(QLabel("MINIMAP ANALYTICS", objectName="panelTitle"))
        mini_header.addStretch()
        self.sel_btn = QPushButton("영역 설정"); self.sel_btn.setFixedSize(80, 25)
        self.sel_btn.setStyleSheet("font-size: 10px; padding: 2px; border-radius: 5px;")
        self.sel_btn.clicked.connect(self.open_selector)
        mini_header.addWidget(self.sel_btn)
        left_vbox.addLayout(mini_header)
        
        self.minimap_preview = QLabel("WAITING..."); self.minimap_preview.setObjectName("previewLabel")
        self.minimap_preview.setFixedSize(470, 200); self.minimap_preview.setAlignment(Qt.AlignCenter)
        left_vbox.addWidget(self.minimap_preview)
        
        left_vbox.addSpacing(15)
        
        # Shape Detection Section
        left_vbox.addWidget(QLabel("MACRO DETECTION ENGINE [LIVE]", objectName="panelTitle"))
        self.shape_preview = QLabel("SEARCHING..."); self.shape_preview.setObjectName("previewLabel")
        self.shape_preview.setFixedSize(470, 260); self.shape_preview.setAlignment(Qt.AlignCenter)
        left_vbox.addWidget(self.shape_preview)
        
        self.shape_console = QTextEdit(); self.shape_console.setReadOnly(True)
        self.shape_console.setFixedHeight(100); self.shape_console.setObjectName("logTerminal")
        self.shape_console.setStyleSheet("color: #58a6ff; font-size: 10px;")
        left_vbox.addWidget(self.shape_console)
        
        content_layout.addWidget(left_frame)

        # [변경 2] Algorithm Panel (중앙 유지)
        center_frame = QFrame(objectName="panelFrame")
        center_vbox = QVBoxLayout(center_frame); center_vbox.setContentsMargins(15, 30, 15, 15)
        center_vbox.addWidget(QLabel("CORE ALGORITHM", objectName="panelTitle"))
        
        self.main_tabs = QTabWidget(); center_vbox.addWidget(self.main_tabs)
        
        # Tabs (LR, ST, Skill, Advanced)
        self.mode_tabs = QTabWidget(); self.mode_tabs.currentChanged.connect(self.on_hunt_mode_tab_changed)
        tab_lr_widget = QWidget(); tab_lr_vbox = QVBoxLayout(tab_lr_widget)
        self.x_min_slider = self.create_slider_row(tab_lr_vbox, "좌측 경계:", 0, 400, self.x_min, self.update_x_min)
        self.x_max_slider = self.create_slider_row(tab_lr_vbox, "우측 경계:", 0, 400, self.x_max, self.update_x_max)
        tab_lr_vbox.addStretch(); self.mode_tabs.addTab(tab_lr_widget, "좌우 이동")
        
        tab_st_widget = QWidget(); tab_st_vbox = QVBoxLayout(tab_st_widget)
        self.stat_range_slider = self.create_slider_row(tab_st_vbox, "제자리 범위:", 1, 100, self.stationary_range, self.update_stat_range)
        tab_st_vbox.addStretch(); self.mode_tabs.addTab(tab_st_widget, "제자리 사냥")
        self.main_tabs.addTab(self.mode_tabs, "작동 모드")

        tab_skill_widget = QWidget(); tab_skill_vbox = QVBoxLayout(tab_skill_widget)
        self.precision_slider = self.create_slider_row(tab_skill_vbox, "인식 정밀도:", 1, 30, int(self.precision_val*10), self.update_precision, is_float=True)
        self.att_slider = self.create_slider_row(tab_skill_vbox, "공격 주기:", 100, 3000, self.attack_delay_ms, self.update_att_delay)
        self.dash_slider = self.create_slider_row(tab_skill_vbox, "이동 주기:", 100, 10000, self.dash_delay_ms, self.update_dash_delay)
        self.pet_slider = self.create_slider_row(tab_skill_vbox, "소모품(분):", 1, 60, self.periodic_interval_min, self.update_pet_interval)
        key_grid = QGridLayout(); key_grid.setSpacing(12)
        self.key_att_cb = self.create_key_combo(key_grid, "공격", 0, 0, "end"); self.key_dash_cb = self.create_key_combo(key_grid, "이동", 0, 1, "space")
        self.key_jump_cb = self.create_key_combo(key_grid, "점프", 1, 0, "alt"); self.key_pet_cb = self.create_key_combo(key_grid, "소모품", 1, 1, "del")
        tab_skill_vbox.addLayout(key_grid); tab_skill_vbox.addStretch(); self.main_tabs.addTab(tab_skill_widget, "단축키/정밀도")

        tab_adv_widget = QWidget(); tab_adv_vbox = QVBoxLayout(tab_adv_widget)
        self.chk_alert = QCheckBox("거탐 알람 울리기"); self.chk_alert.setChecked(True); self.chk_alert.toggled.connect(self.update_use_alert); tab_adv_vbox.addWidget(self.chk_alert)
        self.chk_shape_anti = QCheckBox("투명 도형 추적 엔진 활성화"); self.chk_shape_anti.setChecked(False); self.chk_shape_anti.toggled.connect(self.update_use_shape_anti); tab_adv_vbox.addWidget(self.chk_shape_anti)
        self.chk_sell = QCheckBox("자동 판매 (준비 중)"); self.chk_sell.setEnabled(False); tab_adv_vbox.addWidget(self.chk_sell)
        self.sell_slider = self.create_slider_row(tab_adv_vbox, "판매 주기:", 10, 60, self.sell_interval_min, self.update_sell_interval)
        self.chk_top = QCheckBox("창 맨 위로 고정"); self.chk_top.setChecked(True); self.chk_top.toggled.connect(self.update_window_flags); tab_adv_vbox.addWidget(self.chk_top)
        self.opacity_slider = self.create_slider_row(tab_adv_vbox, "투명도:", 30, 100, 100, self.update_opacity)
        tab_adv_vbox.addStretch(); self.main_tabs.addTab(tab_adv_widget, "시스템 환경")
        content_layout.addWidget(center_frame)

        # [변경 3] Metrics & Logs Panel (기존 좌측 -> 우측 이동)
        right_frame = QFrame(objectName="panelFrame"); right_frame.setFixedWidth(330)
        right_vbox = QVBoxLayout(right_frame); right_vbox.setContentsMargins(20, 30, 20, 20)
        
        right_vbox.addWidget(QLabel("SYSTEM METRICS", objectName="panelTitle"))
        self.cpu_label = QLabel("CPU 사용률(0%)", objectName="subLabel"); right_vbox.addWidget(self.cpu_label)
        self.cpu_bar = QProgressBar(objectName="metricBar"); self.cpu_bar.setFixedHeight(12); self.cpu_bar.setTextVisible(False); right_vbox.addWidget(self.cpu_bar)
        right_vbox.addSpacing(10)
        self.ram_label = QLabel("RAM 점유율(0%)", objectName="subLabel"); right_vbox.addWidget(self.ram_label)
        self.ram_bar = QProgressBar(objectName="metricBar"); self.ram_bar.setFixedHeight(12); self.ram_bar.setTextVisible(False); right_vbox.addWidget(self.ram_bar)
        
        right_vbox.addSpacing(25)
        self.data_runtime = self.create_data_row(right_vbox, "가동 시간", "00:00:00")
        self.data_total_time = self.create_data_row(right_vbox, "누적 사냥", "00:00:00")
        self.data_actions = self.create_data_row(right_vbox, "명령 횟수", "0")
        self.data_errors = self.create_data_row(right_vbox, "탐지 기록", "0회")
        
        right_vbox.addSpacing(25)
        
        # System Logs (Moved here)
        right_vbox.addWidget(QLabel("SYSTEM LOGS", objectName="panelTitle"))
        self.log_text = QTextEdit(); self.log_text.setObjectName("logTerminal"); self.log_text.setReadOnly(True)
        right_vbox.addWidget(self.log_text)
        
        content_layout.addWidget(right_frame)
        main_layout.addLayout(content_layout)

        # Footer Actions
        footer = QHBoxLayout(); footer.setSpacing(15)
        self.start_btn = QPushButton("사냥 시작 [F8]", objectName="startBtn"); self.start_btn.setFixedHeight(85); self.start_btn.clicked.connect(self.start_hunting); footer.addWidget(self.start_btn, 2)
        self.stop_btn = QPushButton("사냥 중지 [F9]", objectName="stopBtn"); self.stop_btn.setFixedHeight(85); self.stop_btn.clicked.connect(self.stop_hunting); self.stop_btn.setEnabled(False); footer.addWidget(self.stop_btn, 2)
        self.manual_sell_btn = QPushButton("판매 [F11]", objectName="sellBtn"); self.manual_sell_btn.setFixedHeight(85); self.manual_sell_btn.clicked.connect(self.run_manual_sell); footer.addWidget(self.manual_sell_btn, 1)
        self.stop_all_btn = QPushButton("종료"); self.stop_all_btn.setObjectName("stopBtn"); self.stop_all_btn.setFixedHeight(85); self.stop_all_btn.clicked.connect(self.close); footer.addWidget(self.stop_all_btn, 1)
        main_layout.addLayout(footer)
        # Footer Actions
        footer = QHBoxLayout(); footer.setSpacing(15)
        self.start_btn = QPushButton("사냥 시작 [F8]", objectName="startBtn"); self.start_btn.setFixedHeight(85); self.start_btn.clicked.connect(self.start_hunting)
        footer.addWidget(self.start_btn, 2)
        
        self.stop_btn = QPushButton("사냥 중지 [F9]", objectName="stopBtn"); self.stop_btn.setFixedHeight(85); self.stop_btn.clicked.connect(self.stop_hunting); self.stop_btn.setEnabled(False)
        footer.addWidget(self.stop_btn, 2)
        
        self.manual_sell_btn = QPushButton("인벤 판매 [F11]", objectName="sellBtn"); self.manual_sell_btn.setFixedHeight(85); self.manual_sell_btn.clicked.connect(self.run_manual_sell)
        footer.addWidget(self.manual_sell_btn, 1)
        
        self.stop_all_btn = QPushButton("종료"); self.stop_all_btn.setObjectName("stopBtn"); self.stop_all_btn.setFixedHeight(85); self.stop_all_btn.clicked.connect(self.close)
        footer.addWidget(self.stop_all_btn, 1)
        main_layout.addLayout(footer)

    def apply_qss(self):
        font_stack = "'Pretendard', 'NanumSquare', 'Segoe UI', sans-serif"
        style = f"""
            QMainWindow {{ background-color: #0b0e14; font-family: {font_stack}; }}
            #mainTitle {{ color: #ffffff; font-size: 42px; font-weight: 900; letter-spacing: -1.5px; }}
            #panelTitle {{ color: #00d2ff; font-size: 16px; font-weight: 800; text-transform: uppercase; }}
            #subLabel {{ color: #8a99af; font-size: 13px; font-weight: 600; }}
            #dataLabel {{ color: #64748b; font-size: 15px; font-weight: 500; }}
            #dataValue {{ color: #ffffff; font-size: 18px; font-family: 'Consolas'; font-weight: 700; }}
            #panelFrame {{ background-color: #161b22; border: 1px solid #30363d; border-radius: 25px; }}
            QTabWidget::pane {{ border: 1px solid #30363d; background: #161b22; border-radius: 15px; top: -1px; }}
            QTabBar::tab {{ background: #0d1117; color: #8b949e; padding: 12px 25px; font-size: 13px; font-weight: 700; border-top-left-radius: 12px; border-top-right-radius: 12px; margin-right: 5px; }}
            QTabBar::tab:selected {{ background: #161b22; color: #00d2ff; border-bottom: 3px solid #00d2ff; }}
            QPushButton {{ background-color: #21262d; color: #c9d1d9; border: 1px solid #30363d; border-radius: 15px; padding: 10px; font-size: 15px; font-weight: 700; }}
            #startBtn {{ background-color: #238636; color: #ffffff; border: none; font-size: 28px; font-weight: 900; }}
            #startBtn:disabled {{ background-color: #1a3a21; color: #8b949e; }}
            #stopBtn {{ background-color: #161b22; color: #f85149; border: 2px solid #f85149; font-size: 24px; font-weight: 900; }}
            #stopBtn:disabled {{ border-color: #3a1a1a; color: #64302d; }}
            #sellBtn {{ color: #e3b341; border: 2px solid #e3b341; }}
            #saveBtn {{ background-color: #1f6feb; color: white; border: none; }}
            QProgressBar#metricBar {{ background-color: #0d1117; border: 1px solid #30363d; border-radius: 4px; }}
            QProgressBar#metricBar::chunk {{ background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #00d2ff, stop:1 #3a7bd5); border-radius: 3px; }}
            QTextEdit#logTerminal {{ background-color: #0d1117; color: #8b949e; border: 1px solid #30363d; font-family: 'Consolas'; font-size: 11px; border-radius: 15px; padding: 12px; }}
            QLabel#previewLabel {{ background-color: #000000; border-radius: 20px; border: 2px solid #30363d; color: #484f58; }}
            QComboBox {{ background-color: #0d1117; color: white; border: 1px solid #30363d; border-radius: 12px; padding: 10px; font-size: 14px; }}
            QSlider::handle:horizontal {{ background: #00d2ff; width: 22px; height: 22px; border-radius: 11px; margin: -9px 0; }}
            QSlider::groove:horizontal {{ background: #30363d; height: 4px; border-radius: 2px; }}
            QCheckBox {{ color: #c9d1d9; font-size: 14px; font-weight: 600; padding: 5px; }}
        """
        self.setStyleSheet(style)

    def start_hunting(self):
        if not self.is_running:
            self.is_running = True; self.start_btn.setEnabled(False); self.stop_btn.setEnabled(True)
            self.current_hunt_start = time.time(); self.log("AI 오토메이션 엔진이 가동되었습니다.")
            threading.Thread(target=self.hunter_core, daemon=True).start()

    def stop_hunting(self):
        if self.is_running:
            self.is_running = False; self.start_btn.setEnabled(True); self.stop_btn.setEnabled(False)
            self.log("AI 시퀀스를 중단했습니다.")
            self.total_hunting_time += int(time.time() - self.current_hunt_start)
            pyautogui.keyUp('left'); pyautogui.keyUp('right')

    def hotkey_start_handler(self):
        self.log("단축키 신호가 감지되었습니다. (F8)"); self.signals.start_signal.emit()

    def hotkey_stop_handler(self):
        self.log("단축키 신호가 감지되었습니다. (F9)"); self.signals.stop_signal.emit()

    def hunter_core(self):
        cur_dir = 'right'; last_x, stuck_cnt = -1, 0; l_att, l_dash = 0, 0; l_del_time = time.time(); start_cx = None
        while self.is_running:
            if keyboard.is_pressed('f9'): self.signals.stop_signal.emit(); break
            if self.is_selling: time.sleep(0.5); continue
            with mss.mss() as sct:
                region = {"top": self.reg_t, "left": self.reg_l, "width": self.reg_w, "height": self.reg_h}
                try:
                    shot = np.array(sct.grab(region)); img = cv2.cvtColor(shot, cv2.COLOR_BGRA2BGR); m = self.color_margin
                    low = np.array([max(0, self.base_lower[2]-m), max(0, self.base_lower[1]-m), max(0, self.base_lower[0]-m)])
                    high = np.array([min(255, self.base_upper[2]+m), min(255, self.base_upper[1]+m), min(255, self.base_upper[0]+m)])
                    mask = cv2.inRange(img, low, high)
                    if np.any(mask):
                        M = cv2.moments(mask); cx = -1
                        if M["m00"] > 0:
                            cx = int(M["m10"] / M["m00"])
                            if self.hunt_mode == 1:
                                if start_cx is None: start_cx = cx
                                if cx >= start_cx + self.stationary_range and cur_dir == 'right': pyautogui.keyUp('right'); cur_dir = 'left'
                                elif cx <= start_cx - self.stationary_range and cur_dir == 'left': pyautogui.keyUp('left'); cur_dir = 'right'
                                pyautogui.keyDown(cur_dir)
                            else:
                                start_cx = None
                                if cx >= self.x_max and cur_dir == 'right': pyautogui.keyUp('right'); cur_dir = 'left'
                                elif cx <= self.x_min and cur_dir == 'left': pyautogui.keyUp('left'); cur_dir = 'right'
                                pyautogui.keyDown(cur_dir)
                            now_ms = time.time() * 1000
                            if now_ms - l_att >= self.attack_delay_ms: self.press_key(self.key_att_cb.currentText()); l_att = now_ms
                            if now_ms - l_dash >= self.dash_delay_ms: self.press_key(self.key_dash_cb.currentText()); l_dash = now_ms
                            if (time.time() - l_del_time) >= (self.periodic_interval_min * 60):
                                self.log("소모품을 자동으로 사용했습니다."); self.press_key(self.key_pet_cb.currentText()); l_del_time = time.time()
                        if cx != -1:
                            if abs(cx - last_x) < 2: stuck_cnt += 1
                            else: stuck_cnt = 0; last_x = cx
                            if stuck_cnt > 40: self.press_key(self.key_jump_cb.currentText()); stuck_cnt = 0
                except: pass
            time.sleep(0.04)

    def run_manual_sell(self):
        self.log("인벤토리 판매 기능은 현재 업데이트 준비 중입니다.")
        winsound.Beep(500, 100)

    def find_and_click(self, img_path, double=False):
        if not os.path.exists(img_path): return False
        template = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
        with mss.mss() as sct:
            monitor = sct.monitors[0]
            scr = np.array(sct.grab(monitor)); scr_gray = cv2.cvtColor(scr, cv2.COLOR_BGRA2GRAY)
            res = cv2.matchTemplate(scr_gray, template, cv2.TM_CCOEFF_NORMED); _, max_val, _, max_loc = cv2.minMaxLoc(res)
            self.log(f"[{os.path.basename(img_path)}] 매칭률: {max_val:.2f}")
            if max_val >= 0.75:
                h, w = template.shape; tx, ty = max_loc[0] + w // 2, max_loc[1] + h // 2
                if double: pyautogui.doubleClick(tx, ty)
                else: pyautogui.click(tx, ty)
                return True
        return False

    def update_status_ui(self, data):
        self.data_runtime.setText(data.get("uptime", "00:00:00")); self.data_total_time.setText(data.get("total_uptime", "00:00:00"))
        cpu = data.get('cpu', 0); ram = data.get('ram', 0)
        self.cpu_label.setText(f"CPU 사용률({cpu}%)"); self.cpu_bar.setValue(cpu)
        self.ram_label.setText(f"RAM 점유율({ram}%)"); self.ram_bar.setValue(ram)
        self.data_actions.setText(str(data.get("actions", 0))); self.data_errors.setText(f"{data.get('err_cnt', 0)}회")

    def update_x_min(self, v): self.x_min = v
    def update_x_max(self, v): self.x_max = v
    def update_stat_range(self, v): self.stationary_range = v
    def update_precision(self, v): self.precision_val = v / 10.0; self.color_margin = int(self.precision_val * 50)
    def update_att_delay(self, v): self.attack_delay_ms = v
    def update_dash_delay(self, v): self.dash_delay_ms = v
    def update_pet_interval(self, v): self.periodic_interval_min = v
    def update_sell_interval(self, v): self.sell_interval_min = v
    def update_use_sell(self, b): self.use_auto_sell = b
    def update_use_alert(self, b): self.use_sound_alert = b
    def update_use_shape_anti(self, b): self.use_shape_anti = b
    def update_opacity(self, v): self.setWindowOpacity(v / 100.0)
    def on_hunt_mode_tab_changed(self, idx): self.hunt_mode = idx

    def create_data_row(self, layout, label, value):
        row = QHBoxLayout(); lbl = QLabel(label); lbl.setObjectName("dataLabel"); val = QLabel(value); val.setObjectName("dataValue"); row.addWidget(lbl); row.addStretch(); row.addWidget(val); layout.addLayout(row); return val

    def create_slider_row(self, layout, label, min_v, max_v, current_v, callback, is_float=False):
        row = QHBoxLayout(); lbl = QLabel(label); lbl.setFixedWidth(140); lbl.setObjectName("dataLabel"); slider = QSlider(Qt.Horizontal); slider.setRange(min_v, max_v); slider.setValue(int(current_v)); slider.setFixedHeight(30)
        val_lbl = QLabel(str(current_v/10.0 if is_float else current_v)); val_lbl.setFixedWidth(40); val_lbl.setStyleSheet("color: #00d2ff; font-weight: bold;")
        slider.valueChanged.connect(lambda v: (val_lbl.setText(str(v/10.0 if is_float else v)), callback(v))); row.addWidget(lbl); row.addWidget(slider); row.addWidget(val_lbl); layout.addLayout(row); return slider

    def create_key_combo(self, grid, title, r, c, default_v):
        box = QVBoxLayout(); lbl = QLabel(title); lbl.setObjectName("subLabel"); cb = QComboBox(); cb.setFixedHeight(35); cb.addItems(["space", "ctrl", "alt", "shift", "insert", "del", "home", "end", "pgup", "pgdn", "enter", "tab", "esc", "up", "down", "left", "right"] + list("abcdefghijklmnopqrstuvwxyz") + [str(i) for i in range(10)])
        cb.setCurrentText(default_v); box.addWidget(lbl); box.addWidget(cb); grid.addLayout(box, r, c); return cb

    def update_log(self, msg):
        timestamp = time.strftime("%H:%M:%S")
        self.log_text.append(f"<span style='color:#484f58'>[{timestamp}]</span> <span style='color:#c9d1d9'>{msg}</span>")
        self.log_text.verticalScrollBar().setValue(self.log_text.verticalScrollBar().maximum())

    def update_minimap_preview(self, img):
        h, w, c = img.shape; bytes_per_line = c * w; q_img = QImage(img.data, w, h, bytes_per_line, QImage.Format_RGB888).rgbSwapped()
        pixmap = QPixmap.fromImage(q_img).scaled(370, 210, Qt.KeepAspectRatio, Qt.SmoothTransformation); self.minimap_preview.setPixmap(pixmap)

    def update_shape_preview(self, img):
        h, w, c = img.shape; bytes_per_line = c * w; q_img = QImage(img.data, w, h, bytes_per_line, QImage.Format_RGB888).rgbSwapped()
        pixmap = QPixmap.fromImage(q_img).scaled(370, 210, Qt.KeepAspectRatio, Qt.SmoothTransformation); self.shape_preview.setPixmap(pixmap)

    def update_window_flags(self):
        if self.chk_top.isChecked(): self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        else: self.setWindowFlags(self.windowFlags() & ~Qt.WindowStaysOnTopHint)
        self.show()

    def play_custom_sound(self):
        if not self.use_sound_alert: return
        def _play():
            start = time.time()
            while time.time() - start < 15:
                winsound.Beep(3500, 100); winsound.Beep(4000, 50)
                if not self.use_sound_alert: break
        threading.Thread(target=_play, daemon=True).start()

    def monitor_loop(self):
        with mss.mss() as sct:
            while not self.stop_threads:
                if self.reg_w > 5:
                    region = {"top": self.reg_t, "left": self.reg_l, "width": self.reg_w, "height": self.reg_h}
                    try:
                        shot = np.array(sct.grab(region)); img = cv2.cvtColor(shot, cv2.COLOR_BGRA2BGR); m = self.color_margin
                        low = np.array([max(0, self.base_lower[2]-m), max(0, self.base_lower[1]-m), max(0, self.base_lower[0]-m)])
                        high = np.array([min(255, self.base_upper[2]+m), min(255, self.base_upper[1]+m), min(255, self.base_upper[0]+m)])
                        mask = cv2.inRange(img, low, high); p_img = img.copy()
                        cv2.line(p_img, (self.x_min, 0), (self.x_min, self.reg_h), (59, 130, 246), 3)
                        cv2.line(p_img, (self.x_max, 0), (self.x_max, self.reg_h), (239, 68, 68), 3)
                        if np.any(mask):
                            M = cv2.moments(mask)
                            if M["m00"] > 0: cx, cy = int(M["m10"]/M["m00"]), int(M["m01"]/M["m00"]); cv2.circle(p_img, (cx, cy), 7, (34, 197, 94), -1)
                        self.signals.preview_signal.emit(p_img)
                    except: pass
                time.sleep(0.1)

    def anti_macro_loop(self):
        ANTI_IMAGES = ["anti1.png", "anti2.png", "anti3.png", "anti4.png"]
        last_alert = 0
        with mss.mss() as sct:
            while not self.stop_threads:
                if self.use_anti_macro:
                    try:
                        scr_w, scr_h = pyautogui.size(); monitor = {"top": 0, "left": 0, "width": scr_w, "height": scr_h}
                        img = np.array(sct.grab(monitor)); img_gray = cv2.cvtColor(img, cv2.COLOR_BGRA2GRAY)
                        for img_name in ANTI_IMAGES:
                            if not os.path.exists(img_name): continue
                            template = cv2.imread(img_name, cv2.IMREAD_GRAYSCALE)
                            res = cv2.matchTemplate(img_gray, template, cv2.TM_CCOEFF_NORMED)
                            if np.max(res) >= 0.8:
                                if time.time() - last_alert > 60:
                                    self.err_cnt += 1; self.log(f"⚠️ 경고: 거탐 감지! (누적 {self.err_cnt}회)"); self.signals.alert_signal.emit()
                                    last_alert = time.time()
                                break
                    except: pass
                time.sleep(2.0)

    def save_current_profile(self):
        n = self.profile_combo.currentText()
        if not n: return
        self.profiles_data[n] = {
            "reg": {"t": self.reg_t, "l": self.reg_l, "w": self.reg_w, "h": self.reg_h},
            "range": {"min": self.x_min, "max": self.x_max, "stat": self.stationary_range},
            "keys": {"att": self.key_att_cb.currentText(), "dash": self.key_dash_cb.currentText(), "jump": self.key_jump_cb.currentText(), "pet": self.key_pet_cb.currentText()},
            "params": {"margin": self.color_margin, "precision": self.precision_val, "ad": self.attack_delay_ms, "dd": self.dash_delay_ms, "mode": self.hunt_mode, "per_int": self.periodic_interval_min, "sell_int": self.sell_interval_min, "auto_sell": self.use_auto_sell, "sound": self.use_sound_alert, "shape_anti": self.use_shape_anti}
        }
        with open(CONFIG_FILE, "w", encoding="utf-8") as f: json.dump(self.profiles_data, f, ensure_ascii=False, indent=4)
        self.update_profile_list(); QMessageBox.information(self, "저장 완료", f"'{n}' 사냥터 프로필이 성공적으로 저장되었습니다.")

    def apply_profile_data(self, n):
        if n not in self.profiles_data: return
        d = self.profiles_data[n]; p = d["params"]; k = d.get("keys", {}); r = d.get("range", {})
        self.reg_t, self.reg_l = d["reg"]["t"], d["reg"]["l"]; self.reg_w, self.reg_h = d["reg"]["w"], d["reg"]["h"]
        self.x_min_slider.setValue(r.get("min", 20)); self.x_max_slider.setValue(r.get("max", 180)); self.stat_range_slider.setValue(r.get("stat", 15))
        self.precision_slider.setValue(int(p.get("precision", 1.0)*10)); self.att_slider.setValue(p.get("ad", 500)); self.dash_slider.setValue(p.get("dd", 1500))
        self.pet_slider.setValue(p.get("per_int", 5)); self.sell_slider.setValue(p.get("sell_int", 15))
        self.chk_alert.setChecked(p.get("sound", True))
        self.chk_shape_anti.setChecked(p.get("shape_anti", False))
        self.key_att_cb.setCurrentText(k.get("att", "end")); self.key_dash_cb.setCurrentText(k.get("dash", "space")); self.key_jump_cb.setCurrentText(k.get("jump", "alt")); self.key_pet_cb.setCurrentText(k.get("pet", "del"))
        mode = p.get("mode", 0); self.hunt_mode = mode; self.mode_tabs.setCurrentIndex(mode)

    def load_all_profiles(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f: self.profiles_data = json.load(f)
                self.update_profile_list()
                if self.profiles_data: n = list(self.profiles_data.keys())[0]; self.profile_combo.setCurrentText(n); self.apply_profile_data(n)
            except: pass

    def update_profile_list(self): self.profile_combo.blockSignals(True); self.profile_combo.clear(); self.profile_combo.addItems(list(self.profiles_data.keys())); self.profile_combo.blockSignals(False)

    def on_profile_change(self, n):
        if n in self.profiles_data: self.apply_profile_data(n)

    def open_selector(self):
        self.selector = QWidget(); self.selector.setWindowOpacity(0.3); self.selector.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint); self.selector.showFullScreen(); self.selector.setCursor(Qt.CrossCursor)
        self.selector.mousePressEvent = self.sel_press; self.selector.mouseReleaseEvent = self.sel_release; self.sel_start = None
        self.selector.show()

    def sel_press(self, e): self.sel_start = e.pos()

    def sel_release(self, e):
        if self.sel_start is not None:
            end = e.pos()
            self.reg_l, self.reg_t = min(self.sel_start.x(), end.x()), min(self.sel_start.y(), end.y())
            self.reg_w, self.reg_h = abs(self.sel_start.x() - end.x()), abs(self.sel_start.y() - end.y())
            self.log(f"사냥 범위 재설정: {self.reg_w}x{self.reg_h}")
        self.selector.close()
        self.selector.deleteLater()

    def bezier_move(self, target_x, target_y):
        try:
            pyautogui.PAUSE = 0
            start_x, start_y = pyautogui.position()
            
            # 거리 기반 단계 조절
            dist = np.hypot(target_x - start_x, target_y - start_y)
            if dist < 5: return # 이미 근처면 이동 생략
            
            steps = min(max(int(dist / 15), 10), 25)
            
            control_x = (start_x + target_x) / 2 + random.randint(-100, 100)
            control_y = (start_y + target_y) / 2 + random.randint(-100, 100)
            
            for i in range(steps + 1):
                t = i / steps
                ease_t = t * t * (3 - 2 * t)
                x = (1 - ease_t)**2 * start_x + 2 * (1 - ease_t) * ease_t * control_x + ease_t**2 * target_x
                y = (1 - ease_t)**2 * start_y + 2 * (1 - ease_t) * ease_t * control_y + ease_t**2 * target_y
                
                # Jitter (사람의 미세 떨림)
                jx, jy = x + random.uniform(-1, 1), y + random.uniform(-1, 1)
                pyautogui.moveTo(jx, jy)
                if i % 3 == 0: time.sleep(0.001)
            
            # 최종 정밀 안착
            pyautogui.moveTo(target_x + random.uniform(-1, 1), target_y + random.uniform(-1, 1))
        except: pass

    def shape_tracking_loop(self):
        # 실행 파일/스크립트의 실제 경로 확보
        if getattr(sys, 'frozen', False):
            base_dir = os.path.dirname(sys.executable)
        else:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            
        BG_PATTERN = os.path.join(base_dir, "game_background_pattern.png")
        last_log = 0
        
        while not self.stop_threads:
            if self.use_shape_anti:
                try:
                    with mss.mss() as sct:
                        # 1. 파일 체크
                        if not os.path.exists(BG_PATTERN):
                            if time.time() - last_log > 10:
                                self.log(f"⚠️ [도형엔진] 파일을 찾을 수 없습니다: {os.path.basename(BG_PATTERN)}")
                                last_log = time.time()
                            time.sleep(1); continue

                        # 2. 화면 캡처 (주 모니터)
                        monitor = sct.monitors[1]
                        scr = np.array(sct.grab(monitor))
                        scr_bgr = cv2.cvtColor(scr, cv2.COLOR_BGRA2BGR)
                        scr_gray = cv2.cvtColor(scr_bgr, cv2.COLOR_BGR2GRAY)
                        
                        # 3. 배경 이미지 로드 및 리사이징
                        bg_ref = cv2.imread(BG_PATTERN, cv2.IMREAD_GRAYSCALE)
                        if bg_ref is None: continue
                        if scr_gray.shape != bg_ref.shape:
                            bg_ref = cv2.resize(bg_ref, (scr_gray.shape[1], scr_gray.shape[0]))

                        # 4. 차분 연산 및 노이즈 필터링
                        diff = cv2.absdiff(scr_gray, bg_ref)
                        _, thresh = cv2.threshold(diff, 25, 255, cv2.THRESH_BINARY)
                        kernel = np.ones((5,5), np.uint8)
                        mask = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
                        
                        # 시각적 디버깅용 베이스 이미지 (어둡게 처리하여 가시성 확보)
                        debug_feed = scr_bgr.copy()
                        debug_feed = cv2.addWeighted(debug_feed, 0.4, np.zeros(debug_feed.shape, debug_feed.dtype), 0, 0)
                        
                        self.frame_num += 1
                        log_msg = ""
                        conf = 0.0

                        # 5. 외곽선 탐지 및 인프레임 렌더링
                        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                        if contours:
                            best_cnt = max(contours, key=cv2.contourArea)
                            area = cv2.contourArea(best_cnt)
                            if area > 50:
                                # 신뢰도 계산 (면적 및 형태 기반)
                                conf = min(area / 1000.0, 1.0)
                                M = cv2.moments(best_cnt)
                                if M["m00"] > 0:
                                    cX_local = int(M["m10"]/M["m00"])
                                    cY_local = int(M["m01"]/M["m00"])
                                    cX_global = cX_local + monitor["left"]
                                    cY_global = cY_local + monitor["top"]
                                    
                                    # [기능 1] 감지 구역 바운딩 박스 (빨간색 사각형)
                                    x, y, w, h = cv2.boundingRect(best_cnt)
                                    cv2.rectangle(debug_feed, (x, y), (x+w, y+h), (0, 0, 255), 2)
                                    
                                    # [기능 2] 중심점 타겟 마킹 (초록색 조준점)
                                    cv2.drawMarker(debug_feed, (cX_local, cY_local), (0, 255, 0), 
                                                 markerType=cv2.MARKER_CROSS, markerSize=20, thickness=2)
                                    
                                    # 상단 정보 표시
                                    cv2.putText(debug_feed, f"TRACKING: {conf:.2f}", (x, y-10), 
                                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)

                                    # 실제 마우스 이동
                                    self.bezier_move(cX_global, cY_global)
                                    
                                    # [기능 3] 콘솔 로그 생성
                                    log_msg = f"f [{self.frame_num:05d}] tracked conf={conf:.4f} tracker=motion"
                        
                        if not log_msg:
                            log_msg = f"f [{self.frame_num:05d}] searching..."

                        # 화면에 프레임 번호 고정 출력
                        cv2.putText(debug_feed, f"FRAME: {self.frame_num}", (10, 30), 
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

                        # 프리뷰 및 디버그 신호 전송
                        self.signals.shape_monitor_signal.emit((debug_feed, log_msg))

                except Exception as e:
                    pass
            time.sleep(0.05)

    def log(self, msg):
        self.signals.log_signal.emit(msg)

    def status_update_loop(self):
        while not self.stop_threads:
            try:
                # 가동 시간 계산
                uptime_sec = int(time.time() - self.current_hunt_start) if self.is_running else 0
                total_uptime_sec = int(time.time() - self.program_start_time)
                
                h, m, s = uptime_sec // 3600, (uptime_sec % 3600) // 60, uptime_sec % 60
                th, tm, ts = total_uptime_sec // 3600, (total_uptime_sec % 3600) // 60, total_uptime_sec % 60
                
                status_data = {
                    "uptime": f"{h:02d}:{m:02d}:{s:02d}",
                    "total_uptime": f"{th:02d}:{tm:02d}:{ts:02d}",
                    "cpu": int(psutil.cpu_percent()),
                    "ram": int(psutil.virtual_memory().percent),
                    "actions": self.actions_cnt,
                    "err_cnt": self.err_cnt
                }
                self.signals.status_signal.emit(status_data)
            except: pass
            time.sleep(1.0)

    def press_key(self, key): 
        pyautogui.keyDown(key)
        time.sleep(random.uniform(0.05, 0.1))
        pyautogui.keyUp(key)
        self.actions_cnt += 1

    def closeEvent(self, event): 
        self.stop_threads = True
        self.is_running = False
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv); window = AutoHunterV7_0(); window.show(); sys.exit(app.exec())
