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
if getattr(sys, 'frozen', False):
    BASE_DIR = sys._MEIPASS
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(BASE_DIR, "AUTOmaple_v1.0.0_config.json")

# --- DPI 보정 ---
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except:
    pass

# --- Windows SendInput API & Logitech G HUB Driver Emulation ---
KEYEVENTF_KEYDOWN = 0x0000
KEYEVENTF_KEYUP = 0x0002
KEYEVENTF_SCANCODE = 0x0008

MOUSEEVENTF_MOVE = 0x0001
MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004
MOUSEEVENTF_RIGHTDOWN = 0x0008
MOUSEEVENTF_RIGHTUP = 0x0010

class MOUSEINPUT(ctypes.Structure):
    _fields_ = [
        ("dx", ctypes.c_long),
        ("dy", ctypes.c_long),
        ("mouseData", ctypes.c_ulong),
        ("dwFlags", ctypes.c_ulong),
        ("time", ctypes.c_ulong),
        ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong))
    ]

class KEYBDINPUT(ctypes.Structure):
    _fields_ = [
        ("wVk", ctypes.c_ushort),
        ("wScan", ctypes.c_ushort),
        ("dwFlags", ctypes.c_ulong),
        ("time", ctypes.c_ulong),
        ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong))
    ]

class HARDWAREINPUT(ctypes.Structure):
    _fields_ = [
        ("uMsg", ctypes.c_ulong),
        ("wParamL", ctypes.c_ushort),
        ("wParamH", ctypes.c_ushort)
    ]

class INPUT_UNION(ctypes.Union):
    _fields_ = [
        ("mi", MOUSEINPUT),
        ("ki", KEYBDINPUT),
        ("hi", HARDWAREINPUT)
    ]

class INPUT(ctypes.Structure):
    _fields_ = [
        ("type", ctypes.c_ulong),
        ("union", INPUT_UNION)
    ]

# 스캔 코드 매핑 테이블
KEY_SCAN_CODES = {
    'left': 0x4B, 'right': 0x4D, 'space': 0x39, 'ctrl': 0x1D, 'alt': 0x38, 'shift': 0x2A,
    'insert': 0x52, 'del': 0x53, 'home': 0x47, 'end': 0x4F, 'pgup': 0x49, 'pgdn': 0x51,
    'a': 0x1E, 'b': 0x30, 'c': 0x2E, 'd': 0x20, 'e': 0x12, 'f': 0x21, 'g': 0x22,
    'h': 0x23, 'i': 0x17, 'j': 0x24, 'k': 0x25, 'l': 0x26, 'm': 0x32, 'n': 0x31,
    'o': 0x18, 'p': 0x19, 'q': 0x10, 'r': 0x13, 's': 0x1F, 't': 0x14, 'u': 0x16,
    'v': 0x2F, 'w': 0x11, 'x': 0x2D, 'y': 0x15, 'z': 0x2C, 'up': 0x48, 'down': 0x50
}

class LogitechInput:
    def __init__(self):
        self.dll = None
        paths = [
            "lghub_device.dll",
            os.path.join(BASE_DIR, "lghub_device.dll"),
            r"C:\Program Files\LGHUB\lghub_device.dll",
            r"C:\Program Files\Logitech Gaming Software\SDK\Keyboard\LogitechLed.dll"
        ]
        for p in paths:
            if os.path.exists(p) or p == "lghub_device.dll":
                try:
                    self.dll = ctypes.CDLL(p)
                    self.dll.device_open()
                    break
                except:
                    pass

    def move(self, dx, dy):
        if self.dll:
            try:
                self.dll.moveR(int(dx), int(dy))
            except:
                pass

    def mouse_down(self, btn=1):
        if self.dll:
            try:
                self.dll.mouse_down(btn)
            except:
                pass

    def mouse_up(self, btn=1):
        if self.dll:
            try:
                self.dll.mouse_up(btn)
            except:
                pass

    def key_down(self, key_name):
        if self.dll and key_name in KEY_SCAN_CODES:
            try:
                self.dll.key_down(KEY_SCAN_CODES[key_name])
            except:
                pass

    def key_up(self, key_name):
        if self.dll and key_name in KEY_SCAN_CODES:
            try:
                self.dll.key_up(KEY_SCAN_CODES[key_name])
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
        self.version = "v1.2.8"
        self.setWindowTitle(f"AUTOmaple {self.version} (2026.06.04)")
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
        
        # 미니맵 캐릭터 좌표 및 복귀 설정 변수
        self.char_x = -1
        self.char_y = -1
        
        self.use_bottom_hunt = False
        self.bottom_y_threshold = 80
        self.bottom_hunt_time_sec = 10
        self.is_bottom_hunting = False
        self.bottom_hunt_start_time = 0
        
        self.use_fall_recovery = False
        self.fall_y_threshold = 110
        self.is_falling_recovering = False
        
        self.use_escape_lost = False
        self.lost_timeout_sec = 5
        self.last_char_seen_time = time.time()
        
        self.use_watch_mode = False
        self.use_anti_town = False
        self.last_anti_afk_time = time.time()
        
        # 낚시 사냥 변수
        self.use_fishing_mode = False
        self.fish_x = -1
        self.fish_y = -1
        
        # 입력 시뮬레이션 관련 변수
        self.input_mode = 0  # 0: PyAutoGUI, 1: Windows SendInput, 2: Logitech G HUB
        self.logitech_input = LogitechInput()
        self.key_states = {}
        
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

        self.setup_ui()
        self.apply_qss()
        
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
            keyboard.add_hotkey('f5', self.hotkey_start_handler)
            keyboard.add_hotkey('f4', self.hotkey_stop_handler)
            keyboard.add_hotkey('f8', self.hotkey_fix_fish_handler)
            keyboard.add_hotkey('f2', self.hotkey_shape_start_handler)
            keyboard.add_hotkey('f3', self.hotkey_shape_stop_handler)
            keyboard.add_hotkey('f11', lambda: self.signals.sell_signal.emit())
        except: pass

    def create_data_row(self, layout, label, value):
        row = QHBoxLayout()
        lbl = QLabel(label); lbl.setObjectName("dataLabel")
        val = QLabel(value); val.setObjectName("dataValue")
        val.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        row.addWidget(lbl); row.addStretch(); row.addWidget(val)
        layout.addLayout(row)
        return val

    def create_slider_row(self, layout, label, min_v, max_v, current_v, callback, is_float=False):
        row = QHBoxLayout()
        lbl = QLabel(label); lbl.setFixedWidth(140); lbl.setObjectName("dataLabel")
        slider = QSlider(Qt.Horizontal); slider.setRange(min_v, max_v); slider.setValue(int(current_v)); slider.setFixedHeight(30)
        val_lbl = QLabel(str(current_v/10.0 if is_float else current_v))
        val_lbl.setFixedWidth(45); val_lbl.setStyleSheet("color: #00d2ff; font-weight: bold;")
        slider.valueChanged.connect(lambda v: (val_lbl.setText(str(v/10.0 if is_float else v)), callback(v)))
        row.addWidget(lbl); row.addWidget(slider); row.addWidget(val_lbl)
        layout.addLayout(row)
        return slider

    def create_key_combo(self, grid, title, r, c, default_v):
        box = QVBoxLayout()
        lbl = QLabel(title); lbl.setObjectName("subLabel")
        cb = QComboBox(); cb.setFixedHeight(35)
        cb.addItems(["space", "ctrl", "alt", "shift", "insert", "del", "home", "end", "pgup", "pgdn"] + list("abcdefghijklmnopqrstuvwxyz"))
        cb.setCurrentText(default_v)
        box.addWidget(lbl); box.addWidget(cb)
        grid.addLayout(box, r, c)
        return cb

    def run_manual_sell(self):
        if self.is_selling: return
        self.log("💰 인벤토리 수동 판매 시퀀스 시작")
        self.is_selling = True; winsound.Beep(1000, 200)
        QTimer.singleShot(2000, self.finish_selling)

    def finish_selling(self):
        self.is_selling = False; self.log("✅ 판매 완료 - 사냥 모드 복귀")

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
        
        self.sel_btn = QPushButton("영역 설정"); self.sel_btn.setFixedSize(80, 25); self.sel_btn.setStyleSheet("font-size: 10px; padding: 2px; border-radius: 5px; background-color: #238636; color: white;"); self.sel_btn.clicked.connect(self.open_selector); mini_header.addWidget(self.sel_btn)
        
        self.auto_det_btn = QPushButton("자동 인식"); self.auto_det_btn.setFixedSize(80, 25); self.auto_det_btn.setStyleSheet("font-size: 10px; padding: 2px; border-radius: 5px; background-color: #0288d1; color: white;"); self.auto_det_btn.clicked.connect(self.auto_detect_minimap); mini_header.addWidget(self.auto_det_btn)
        
        left_vbox.addLayout(mini_header)
        self.minimap_preview = QLabel("WAITING..."); self.minimap_preview.setObjectName("previewLabel"); self.minimap_preview.setFixedSize(470, 200); self.minimap_preview.setAlignment(Qt.AlignCenter); left_vbox.addWidget(self.minimap_preview); left_vbox.addSpacing(15); left_vbox.addWidget(QLabel("MACRO DETECTION ENGINE [LIVE]", objectName="panelTitle"))
        self.shape_preview = QLabel("SEARCHING..."); self.shape_preview.setObjectName("previewLabel"); self.shape_preview.setFixedSize(470, 260); self.shape_preview.setAlignment(Qt.AlignCenter); left_vbox.addWidget(self.shape_preview); self.shape_console = QTextEdit(); self.shape_console.setReadOnly(True); self.shape_console.setFixedHeight(100); self.shape_console.setObjectName("logTerminal"); self.shape_console.setStyleSheet("color: #58a6ff; font-size: 10px;"); left_vbox.addWidget(self.shape_console); content_layout.addWidget(left_frame)
        center_frame = QFrame(objectName="panelFrame"); center_vbox = QVBoxLayout(center_frame); center_vbox.setContentsMargins(15, 30, 15, 15); center_vbox.addWidget(QLabel("CORE ALGORITHM", objectName="panelTitle")); self.main_tabs = QTabWidget(); center_vbox.addWidget(self.main_tabs)
        self.mode_tabs = QTabWidget(); self.mode_tabs.currentChanged.connect(self.on_hunt_mode_tab_changed); tab_lr_widget = QWidget(); tab_lr_vbox = QVBoxLayout(tab_lr_widget); self.x_min_slider = self.create_slider_row(tab_lr_vbox, "좌측 경계:", 0, 400, self.x_min, self.update_x_min); self.x_max_slider = self.create_slider_row(tab_lr_vbox, "우측 경계:", 0, 400, self.x_max, self.update_x_max); tab_lr_vbox.addStretch(); self.mode_tabs.addTab(tab_lr_widget, "좌우 이동"); tab_st_widget = QWidget(); tab_st_vbox = QVBoxLayout(tab_st_widget); self.stat_range_slider = self.create_slider_row(tab_st_vbox, "제자리 범위:", 1, 100, self.stationary_range, self.update_stat_range); tab_st_vbox.addStretch(); self.mode_tabs.addTab(tab_st_widget, "제자리 사냥"); self.main_tabs.addTab(self.mode_tabs, "작동 모드")
        
        tab_skill_widget = QWidget(); tab_skill_vbox = QVBoxLayout(tab_skill_widget); self.precision_slider = self.create_slider_row(tab_skill_vbox, "인식 정밀도:", 1, 30, int(self.precision_val*10), self.update_precision, is_float=True); self.att_slider = self.create_slider_row(tab_skill_vbox, "공격 주기:", 100, 3000, self.attack_delay_ms, self.update_att_delay); self.dash_slider = self.create_slider_row(tab_skill_vbox, "이동 주기:", 100, 10000, self.dash_delay_ms, self.update_dash_delay); self.pet_slider = self.create_slider_row(tab_skill_vbox, "소모품(분):", 1, 60, self.periodic_interval_min, self.update_pet_interval)
        
        key_grid = QGridLayout(); key_grid.setSpacing(12)
        self.key_att_cb = self.create_key_combo(key_grid, "공격", 0, 0, "end")
        self.key_dash_cb = self.create_key_combo(key_grid, "이동", 0, 1, "space")
        self.key_jump_cb = self.create_key_combo(key_grid, "점프", 1, 0, "alt")
        self.key_teleport_cb = self.create_key_combo(key_grid, "텔레포트", 1, 1, "shift")
        self.key_pet_cb = self.create_key_combo(key_grid, "소모품", 2, 0, "del")
        
        tab_skill_vbox.addLayout(key_grid); tab_skill_vbox.addStretch(); self.main_tabs.addTab(tab_skill_widget, "단축키/정밀도")
        tab_adv_widget = QWidget(); tab_adv_vbox = QVBoxLayout(tab_adv_widget); self.chk_alert = QCheckBox("거탐 알람 울리기"); self.chk_alert.setChecked(True); self.chk_alert.toggled.connect(self.update_use_alert); tab_adv_vbox.addWidget(self.chk_alert); self.chk_shape_anti = QCheckBox("투명 도형 추적 엔진 활성화 [F2 시작 / F3 중지]"); self.chk_shape_anti.setChecked(False); self.chk_shape_anti.toggled.connect(self.update_use_shape_anti); tab_adv_vbox.addWidget(self.chk_shape_anti); self.chk_sell = QCheckBox("자동 판매 (준비 중)"); self.chk_sell.setEnabled(False); tab_adv_vbox.addWidget(self.chk_sell); self.sell_slider = self.create_slider_row(tab_adv_vbox, "판매 주기:", 10, 60, self.sell_interval_min, self.update_sell_interval); self.chk_top = QCheckBox("창 항상 맨 위로 고정"); self.chk_top.setChecked(True); self.chk_top.toggled.connect(self.update_window_flags); tab_adv_vbox.addWidget(self.chk_top); self.opacity_slider = self.create_slider_row(tab_adv_vbox, "투명도:", 30, 100, 100, self.update_opacity); input_row = QHBoxLayout(); input_lbl = QLabel("입력 시뮬레이션:"); input_lbl.setObjectName("dataLabel"); input_lbl.setFixedWidth(140); self.input_mode_combo = QComboBox(); self.input_mode_combo.setFixedHeight(35); self.input_mode_combo.addItems(["PyAutoGUI (기본)", "Windows SendInput (커스텀 API)", "Logitech G HUB (드라이버 레벨)"]); self.input_mode_combo.setCurrentIndex(self.input_mode); self.input_mode_combo.currentIndexChanged.connect(self.update_input_mode); input_row.addWidget(input_lbl); input_row.addWidget(self.input_mode_combo); tab_adv_vbox.addLayout(input_row); tab_adv_vbox.addStretch(); self.main_tabs.addTab(tab_adv_widget, "시스템 환경")
        
        # 좌표/안전 설정 탭
        tab_coord_widget = QWidget()
        tab_coord_vbox = QVBoxLayout(tab_coord_widget)
        
        self.chk_bottom_hunt = QCheckBox("하단 사냥 활성화 (지정 시간 후 자동 복귀)")
        self.chk_bottom_hunt.setChecked(False)
        self.chk_bottom_hunt.toggled.connect(self.update_use_bottom_hunt)
        tab_coord_vbox.addWidget(self.chk_bottom_hunt)
        self.bottom_y_slider = self.create_slider_row(tab_coord_vbox, "하단 Y 기준값:", 0, 150, self.bottom_y_threshold, self.update_bottom_y)
        self.bottom_time_slider = self.create_slider_row(tab_coord_vbox, "하단 유지 시간(초):", 5, 30, self.bottom_hunt_time_sec, self.update_bottom_time)
        
        tab_coord_vbox.addSpacing(10)
        
        self.chk_fall_recovery = QCheckBox("추락 감지 시 복귀 (텔레포트 시퀀스)")
        self.chk_fall_recovery.setChecked(False)
        self.chk_fall_recovery.toggled.connect(self.update_use_fall_recovery)
        tab_coord_vbox.addWidget(self.chk_fall_recovery)
        self.fall_y_slider = self.create_slider_row(tab_coord_vbox, "추락 Y 기준값:", 0, 150, self.fall_y_threshold, self.update_fall_y)
        
        tab_coord_vbox.addSpacing(10)
        
        self.chk_escape_lost = QCheckBox("캐릭터 인식 불가 시 사냥 일시 중단")
        self.chk_escape_lost.setChecked(False)
        self.chk_escape_lost.toggled.connect(self.update_use_escape_lost)
        tab_coord_vbox.addWidget(self.chk_escape_lost)
        self.lost_time_slider = self.create_slider_row(tab_coord_vbox, "탈출 대기 시간(초):", 2, 15, self.lost_timeout_sec, self.update_lost_timeout)
        
        tab_coord_vbox.addSpacing(10)
        
        self.chk_watch_mode = QCheckBox("감시(잠수) 모드 활성화 (사냥 중지 및 안티매크로 감시)")
        self.chk_watch_mode.setChecked(False)
        self.chk_watch_mode.toggled.connect(self.update_use_watch_mode)
        tab_coord_vbox.addWidget(self.chk_watch_mode)
        
        self.chk_anti_town = QCheckBox("마을 이동 방지 활성화 (주기적 미세 좌우 이동)")
        self.chk_anti_town.setChecked(False)
        self.chk_anti_town.toggled.connect(self.update_use_anti_town)
        tab_coord_vbox.addWidget(self.chk_anti_town)
        
        tab_coord_vbox.addSpacing(10)
        
        self.chk_fishing_mode = QCheckBox("낚시사냥 활성화 (F8키로 지정한 자리에 고정)")
        self.chk_fishing_mode.setChecked(False)
        self.chk_fishing_mode.toggled.connect(self.update_use_fishing_mode)
        tab_coord_vbox.addWidget(self.chk_fishing_mode)
        
        self.lbl_fish_pos = QLabel("지정된 낚시 좌표: X: 미지정, Y: 미지정")
        self.lbl_fish_pos.setStyleSheet("color: #00d2ff; font-weight: bold; font-size: 13px; margin-left: 20px;")
        tab_coord_vbox.addWidget(self.lbl_fish_pos)
        
        tab_coord_vbox.addStretch()
        self.main_tabs.addTab(tab_coord_widget, "좌표/안전 설정")
        
        content_layout.addWidget(center_frame)
        
        right_frame = QFrame(objectName="panelFrame"); right_frame.setFixedWidth(330); right_vbox = QVBoxLayout(right_frame)
        right_vbox.setContentsMargins(20, 30, 20, 20); right_vbox.addWidget(QLabel("SYSTEM METRICS", objectName="panelTitle"))
        self.cpu_label = QLabel("CPU 사용률(0%)", objectName="subLabel"); right_vbox.addWidget(self.cpu_label)
        self.cpu_bar = QProgressBar(objectName="metricBar"); self.cpu_bar.setFixedHeight(12); self.cpu_bar.setTextVisible(False); right_vbox.addWidget(self.cpu_bar)
        right_vbox.addSpacing(10); self.ram_label = QLabel("RAM 점유율(0%)", objectName="subLabel"); right_vbox.addWidget(self.ram_label)
        self.ram_bar = QProgressBar(objectName="metricBar"); self.ram_bar.setFixedHeight(12); self.ram_bar.setTextVisible(False); right_vbox.addWidget(self.ram_bar)
        right_vbox.addSpacing(25)
        
        self.data_runtime = self.create_data_row(right_vbox, "가동 시간", "00:00:00")
        self.data_total_time = self.create_data_row(right_vbox, "누적 사냥", "00:00:00")
        self.data_actions = self.create_data_row(right_vbox, "명령 횟수", "0")
        self.data_errors = self.create_data_row(right_vbox, "탐지 기록", "0회")
        self.data_char_pos = self.create_data_row(right_vbox, "캐릭터 좌표", "인식 불가")
        
        right_vbox.addSpacing(25); right_vbox.addWidget(QLabel("SYSTEM LOGS", objectName="panelTitle"))
        self.log_text = QTextEdit(); self.log_text.setObjectName("logTerminal"); self.log_text.setReadOnly(True); right_vbox.addWidget(self.log_text)
        content_layout.addWidget(right_frame); main_layout.addLayout(content_layout)
        
        footer = QHBoxLayout(); footer.setSpacing(15); self.start_btn = QPushButton("사냥 시작 [F5]", objectName="startBtn"); self.start_btn.setFixedHeight(85); self.start_btn.clicked.connect(self.start_hunting); footer.addWidget(self.start_btn, 2); self.stop_btn = QPushButton("사냥 중지 [F4]", objectName="stopBtn"); self.stop_btn.setFixedHeight(85); self.stop_btn.clicked.connect(self.stop_hunting); self.stop_btn.setEnabled(False); footer.addWidget(self.stop_btn, 2); self.manual_sell_btn = QPushButton("인벤 판매 [F11]", objectName="sellBtn"); self.manual_sell_btn.setFixedHeight(85); self.manual_sell_btn.clicked.connect(self.run_manual_sell); footer.addWidget(self.manual_sell_btn, 1); self.stop_all_btn = QPushButton("종료"); self.stop_all_btn.setObjectName("stopBtn"); self.stop_all_btn.setFixedHeight(85); self.stop_all_btn.clicked.connect(self.close); footer.addWidget(self.stop_all_btn, 1); main_layout.addLayout(footer)

    def apply_qss(self):
        style = """QMainWindow { background-color: #0b0e14; } #mainTitle { color: #ffffff; font-size: 42px; font-weight: 900; } #panelTitle { color: #00d2ff; font-size: 16px; font-weight: 800; } #subLabel { color: #8a99af; font-size: 13px; } #dataLabel { color: #64748b; font-size: 15px; } #dataValue { color: #ffffff; font-size: 18px; font-weight: 700; } #panelFrame { background-color: #161b22; border: 1px solid #30363d; border-radius: 25px; } QTabWidget::pane { border: 1px solid #30363d; background: #161b22; border-radius: 15px; } QTabBar::tab { background: #0d1117; color: #8b949e; padding: 12px 10px; min-width: 110px; } QTabBar::tab:selected { background: #161b22; color: #00d2ff; border-bottom: 3px solid #00d2ff; } QPushButton { background-color: #21262d; color: #c9d1d9; border-radius: 15px; font-weight: 700; } #startBtn { background-color: #238636; color: #ffffff; font-size: 28px; } #stopBtn { border: 2px solid #f85149; color: #f85149; font-size: 24px; } #logTerminal { background-color: #0d1117; color: #8b949e; border-radius: 15px; padding: 10px; } QLabel#previewLabel { background-color: #000000; border-radius: 20px; border: 2px solid #30363d; }"""
        self.setStyleSheet(style)

    def set_key_state(self, key, state):
        current_state = self.key_states.get(key, False)
        if current_state == state:
            return
        self.key_states[key] = state
        
        mode = self.input_mode
        if mode == 2 and not self.logitech_input.dll:
            mode = 1  # Fallback to SendInput
            
        if mode == 0:
            if state:
                pyautogui.keyDown(key)
            else:
                pyautogui.keyUp(key)
        elif mode == 1:
            scan_code = KEY_SCAN_CODES.get(key)
            if scan_code is not None:
                extra = ctypes.c_ulong(0)
                ii_ = INPUT_UNION()
                flags = KEYEVENTF_SCANCODE | (KEYEVENTF_KEYUP if not state else 0)
                ii_.ki = KEYBDINPUT(0, scan_code, flags, 0, ctypes.pointer(extra))
                x = INPUT(1, ii_)
                ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))
        elif mode == 2:
            if state:
                self.logitech_input.key_down(key)
            else:
                self.logitech_input.key_up(key)

    def drag_mouse_down(self):
        mode = self.input_mode
        if mode == 2 and not self.logitech_input.dll:
            mode = 1
            
        if mode == 0:
            pyautogui.mouseDown()
        elif mode == 1:
            extra = ctypes.c_ulong(0)
            ii_ = INPUT_UNION()
            ii_.mi = MOUSEINPUT(0, 0, 0, MOUSEEVENTF_LEFTDOWN, 0, ctypes.pointer(extra))
            x = INPUT(0, ii_)
            ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))
        elif mode == 2:
            self.logitech_input.mouse_down(1)

    def drag_mouse_up(self):
        mode = self.input_mode
        if mode == 2 and not self.logitech_input.dll:
            mode = 1
            
        if mode == 0:
            pyautogui.mouseUp()
        elif mode == 1:
            extra = ctypes.c_ulong(0)
            ii_ = INPUT_UNION()
            ii_.mi = MOUSEINPUT(0, 0, 0, MOUSEEVENTF_LEFTUP, 0, ctypes.pointer(extra))
            x = INPUT(0, ii_)
            ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))
        elif mode == 2:
            self.logitech_input.mouse_up(1)

    def update_input_mode(self, idx):
        self.input_mode = idx
        mode_names = ["PyAutoGUI", "Windows SendInput", "Logitech G HUB"]
        self.log(f"🎮 입력 시뮬레이션 방식 변경: {mode_names[idx]}")
        if idx == 2 and not self.logitech_input.dll:
            self.log("⚠️ 경고: Logitech G HUB 드라이버 DLL(lghub_device.dll)을 로드하지 못했습니다. 실제 동작 시 Windows SendInput으로 자동 대체됩니다.")

    def human_mouse_move(self, tx, ty):
        try:
            pyautogui.PAUSE = 0; cx, cy = pyautogui.position(); dist = np.hypot(tx-cx, ty-cy)
            if dist < 2: return
            lerp = random.uniform(0.15, 0.45) if dist > 50 else random.uniform(0.5, 0.8)
            ox, oy = (random.uniform(-3, 3), random.uniform(-3, 3)) if dist < 20 else (0, 0)
            target_x = cx + (tx-cx)*lerp + ox
            target_y = cy + (ty-cy)*lerp + oy
            
            mode = self.input_mode
            if mode == 2 and not self.logitech_input.dll:
                mode = 1
                
            if mode == 0:
                pyautogui.moveTo(target_x, target_y)
            elif mode == 1:
                ctypes.windll.user32.SetCursorPos(int(target_x), int(target_y))
            elif mode == 2:
                dx = int(target_x) - cx
                dy = int(target_y) - cy
                self.logitech_input.move(dx, dy)
        except: pass

    def get_anti_target_color(self):
        path = os.path.join(BASE_DIR, "anti1.png")
        if not os.path.exists(path): return np.array([140, 50, 50]), np.array([175, 255, 255])
        try:
            img = cv2.imread(path); hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
            mask = cv2.inRange(hsv, (140, 50, 50), (175, 255, 255))
            avg_hsv = np.mean(hsv[mask > 0], axis=0) if np.any(mask) else np.mean(hsv[img.shape[0]//4:3*img.shape[0]//4, img.shape[1]//4:3*img.shape[1]//4], axis=(0,1))
            self.log(f"💡 타겟 색상 분석 완료: HSV {int(avg_hsv[0])}")
            return np.array([max(0, avg_hsv[0]-20), 40, 40]), np.array([min(180, avg_hsv[0]+20), 255, 255])
        except: return None, None

    def shape_tracking_loop(self):
        target_lower, target_upper = None, None
        lk_params = dict(winSize=(21, 21), maxLevel=3, criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 30, 0.01))
        feature_params = dict(maxCorners=20, qualityLevel=0.1, minDistance=5, blockSize=5)
        old_gray, p0, popup_roi = None, None, None
        is_tracking, last_x, last_y, vx, vy, inertia_cnt = False, None, None, 0.0, 0.0, 0
        MAX_INERTIA_FRAMES = 20
        lost_cnt = 0
        lockon_start_time = None
        bg_cache = {}
        dynamic_bg = None

        while not self.stop_threads:
            if self.use_shape_anti:
                try:
                    with mss.mss() as sct:
                        monitor = sct.monitors[1]
                        scr = np.array(sct.grab(monitor))
                        scr_bgr = cv2.cvtColor(scr, cv2.COLOR_BGRA2BGR)
                        frame_gray = cv2.cvtColor(scr_bgr, cv2.COLOR_BGR2GRAY)
                        if popup_roi is None:
                            for bg_name in ["anti0.png", "anti0.1.png"]:
                                bg_path = os.path.join(BASE_DIR, bg_name)
                                if os.path.exists(bg_path):
                                    bg_img = cv2.imread(bg_path, 0)
                                    if bg_img is not None:
                                        res = cv2.matchTemplate(frame_gray, bg_img, cv2.TM_CCOEFF_NORMED)
                                        _, max_val, _, max_loc = cv2.minMaxLoc(res)
                                        if max_val > 0.5: popup_roi = (max_loc[0], max_loc[1], bg_img.shape[1], bg_img.shape[0]); break
                            if popup_roi is None:
                                scr_h, scr_w = frame_gray.shape
                                popup_roi = (max(0, (scr_w - 1024) // 2), max(0, (scr_h - 679) // 2 - 20), 1024, 679)
                        
                        rx, ry, rw, rh = popup_roi
                        cropped_gray, cropped_bgr = frame_gray[ry:ry+rh, rx:rx+rw], scr_bgr[ry:ry+rh, rx:rx+rw]
                        log_msg, found_valid, target_pos, is_initial_lockon = "", False, None, False

                        if not is_tracking:
                            if lockon_start_time is None:
                                lockon_start_time = time.time()
                                dynamic_bg = None
                                self.log("⏳ 초기 정가운데 락온 탐색 시작 (무제한 탐색)")
                            
                            cx_center, cy_center = rw // 2, rh // 2
                            cw_half = 80
                            cx_min, cx_max = cx_center - cw_half, cx_center + cw_half
                            cy_min, cy_max = cy_center - cw_half, cy_center + cw_half
                            
                            if dynamic_bg is None:
                                dynamic_bg = cropped_gray.copy()
                                time.sleep(0.04)
                                continue
                            
                            diff = cv2.absdiff(cropped_gray, dynamic_bg)
                            _, diff_mask = cv2.threshold(diff, 15, 255, cv2.THRESH_BINARY)
                            _, white_mask = cv2.threshold(cropped_gray, 180, 255, cv2.THRESH_BINARY)
                            initial_mask = cv2.bitwise_or(diff_mask, white_mask)
                            contours, _ = cv2.findContours(initial_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                            valid_targets = []
                            for c in contours:
                                area = cv2.contourArea(c)
                                if 300 < area < 30000:
                                    x_b, y_b, w_b, h_b = cv2.boundingRect(c)
                                    if 0.5 < float(w_b)/h_b < 2.0:
                                        hull = cv2.convexHull(c); hull_area = cv2.contourArea(hull)
                                        if (float(area)/hull_area if hull_area > 0 else 0) > 0.4:
                                            M = cv2.moments(c)
                                            if M["m00"] > 0:
                                                cx_mom, cy_mom = int(M["m10"]/M["m00"]), int(M["m01"]/M["m00"])
                                                if cx_min <= cx_mom <= cx_max and cy_min <= cy_mom <= cy_max:
                                                     valid_targets.append((c, area, (cx_mom, cy_mom)))
                            if valid_targets:
                                best_contour, _, (cx_mom, cy_mom) = max(valid_targets, key=lambda x: x[1])
                                target_pos = (cx_mom, cy_mom); found_valid, is_tracking, is_initial_lockon = True, True, True
                                last_x, last_y, vx, vy, inertia_cnt = cx_mom, cy_mom, 0.0, 0.0, 0
                                lockon_start_time = None
                                lost_cnt = 0
                                
                                # 도형 내부 고밀도 격자점 (5px 간격) 특징점 강제 생성
                                x_b, y_b, w_b, h_b = cv2.boundingRect(best_contour)
                                grid_points = []
                                for gy in range(y_b, y_b + h_b, 5):
                                    for gx in range(x_b, x_b + w_b, 5):
                                        if cv2.pointPolygonTest(best_contour, (float(gx), float(gy)), False) >= 0:
                                            grid_points.append([[float(gx), float(gy)]])
                                if len(grid_points) >= 5:
                                    p0 = np.array(grid_points, dtype=np.float32)
                                else:
                                    roi_mask = np.zeros_like(cropped_gray)
                                    cv2.drawContours(roi_mask, [best_contour], -1, 255, -1)
                                    p0 = cv2.goodFeaturesToTrack(cropped_gray, mask=roi_mask, **feature_params)
                                
                                self.log(f"🔒 [{self.frame_num:05d}] 실시간 동적 배경차분 정가운데 락온 성공! ({cx_mom},{cy_mom})")
                        else:
                            if p0 is not None and old_gray is not None and len(p0) > 0:
                                p1, st, err = cv2.calcOpticalFlowPyrLK(old_gray, cropped_gray, p0, None, **lk_params)
                                if p1 is not None and st is not None:
                                    good_new = p1[st == 1]
                                    if len(good_new) >= 3:
                                        mean_x, mean_y = int(np.mean(good_new[:, 0])), int(np.mean(good_new[:, 1]))
                                        dx, dy = mean_x - last_x, mean_y - last_y
                                        dist = np.hypot(dx, dy)
                                        
                                        is_valid_trajectory = True
                                        if dist > 40:
                                            is_valid_trajectory = False
                                        
                                        prev_speed = np.hypot(vx, vy)
                                        if is_valid_trajectory and prev_speed > 2.0 and dist > 5.0:
                                            cos_sim = (vx * dx + vy * dy) / (prev_speed * dist)
                                            if cos_sim < 0.17:
                                                is_valid_trajectory = False
                                                log_msg = f"⚠️ 방향 급변 검출 (cos: {cos_sim:.2f}) - 관성 궤적 대체"
                                        
                                        if is_valid_trajectory:
                                            found_valid = True; target_pos = (mean_x, mean_y); p0 = good_new.reshape(-1, 1, 2)
                                            vx, vy = 0.8*vx + 0.2*dx, 0.8*vy + 0.2*dy
                                            last_x, last_y, inertia_cnt = mean_x, mean_y, 0
                                        else:
                                            p0 = None
                                    else: p0 = None
                            if not found_valid and last_x is not None and last_y is not None:
                                lw = 80
                                lx_min, ly_min = max(0, last_x - lw), max(0, last_y - lw)
                                lx_max, ly_max = min(rw, last_x + lw), min(rh, last_y + lw)
                                local_gray = cropped_gray[ly_min:ly_max, lx_min:lx_max]
                                
                                bg_name = "anti0.png" if rw == 1024 else "anti0.1.png"
                                if bg_name not in bg_cache:
                                    bg_path = os.path.join(BASE_DIR, bg_name)
                                    if os.path.exists(bg_path):
                                        bg_cache[bg_name] = cv2.imread(bg_path, cv2.IMREAD_GRAYSCALE)
                                    else:
                                        bg_cache[bg_name] = None
                                
                                bg_ref = bg_cache.get(bg_name)
                                if bg_ref is not None:
                                    diff = cv2.absdiff(local_gray, bg_ref[ly_min:ly_max, lx_min:lx_max])
                                    _, thresh = cv2.threshold(cv2.GaussianBlur(diff, (5, 5), 0), 5, 255, cv2.THRESH_BINARY)
                                else: _, thresh = cv2.threshold(local_gray, 150, 255, cv2.THRESH_BINARY)
                                contours, _ = cv2.findContours(cv2.dilate(thresh, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3)), iterations=1), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                                valid_local = []
                                for c in contours:
                                    area = cv2.contourArea(c)
                                    if 300 < area < 25000:
                                        x, y, w, h = cv2.boundingRect(c)
                                        if 0.5 < float(w)/h < 2.0:
                                            hull = cv2.convexHull(c); hull_area = cv2.contourArea(hull)
                                            if (float(area)/hull_area if hull_area > 0 else 0) > 0.3: valid_local.append((c, area))
                                if valid_local:
                                    best_contour, _ = max(valid_local, key=lambda x: x[1])
                                    M = cv2.moments(best_contour)
                                    if M["m00"] > 0:
                                        local_cx, local_cy = int(M["m10"]/M["m00"]) + lx_min, int(M["m01"]/M["m00"]) + ly_min
                                        if np.hypot(local_cx - last_x, local_cy - last_y) <= 40:
                                            found_valid = True; target_pos = (local_cx, local_cy)
                                            
                                            # 국소 영역도 동일하게 5px 고밀도 격자 특징점 재조정 (Re-grid)
                                            global_contour = best_contour + np.array([lx_min, ly_min])
                                            x_b, y_b, w_b, h_b = cv2.boundingRect(global_contour)
                                            grid_points = []
                                            for gy in range(y_b, y_b + h_b, 5):
                                                for gx in range(x_b, x_b + w_b, 5):
                                                    if cv2.pointPolygonTest(global_contour, (float(gx), float(gy)), False) >= 0:
                                                        grid_points.append([[float(gx), float(gy)]])
                                            if len(grid_points) >= 5:
                                                p0 = np.array(grid_points, dtype=np.float32)
                                            else:
                                                roi_mask = np.zeros_like(cropped_gray)
                                                cv2.drawContours(roi_mask, [global_contour], -1, 255, -1)
                                                p0 = cv2.goodFeaturesToTrack(cropped_gray, mask=roi_mask, **feature_params)
                                                
                                            vx, vy = 0.8*vx + 0.2*(local_cx-last_x), 0.8*vy + 0.2*(local_cy-last_y)
                                            last_x, last_y, inertia_cnt = local_cx, local_cy, 0
                            if not found_valid and last_x is not None and last_y is not None and (abs(vx) > 0.1 or abs(vy) > 0.1):
                                inertia_cnt += 1
                                if inertia_cnt <= MAX_INERTIA_FRAMES:
                                    speed = np.hypot(vx, vy)
                                    use_vx, use_vy = (vx/speed)*15.0 if speed > 15 else vx, (vy/speed)*15.0 if speed > 15 else vy
                                    target_pos = (max(10, min(rw-10, int(last_x + use_vx))), max(10, min(rh-10, int(last_y + use_vy))))
                                    found_valid, last_x, last_y = True, target_pos[0], target_pos[1]
                        
                        debug_feed = cv2.addWeighted(cropped_bgr, 0.5, np.zeros(cropped_bgr.shape, cropped_bgr.dtype), 0, 0)
                        
                        if p0 is not None:
                            for pt in p0:
                                cv2.circle(debug_feed, (int(pt[0][0]), int(pt[0][1])), 2, (0, 255, 0), -1)
                        
                        if is_tracking and last_x is not None and last_y is not None:
                            cv2.rectangle(debug_feed, (max(0, last_x-80), max(0, last_y-80)), (min(rw, last_x+80), min(rh, last_y+80)), (255, 100, 0), 1)
                        else:
                            cx_center, cy_center = rw // 2, rh // 2
                            cv2.rectangle(debug_feed, (cx_center-80, cy_center-80), (cx_center+80, cy_center+80), (128, 128, 128), 1)
                        self.frame_num += 1
                        if found_valid and target_pos is not None:
                            lost_cnt = 0
                            lx, ly = target_pos
                            cv2.circle(debug_feed, (lx, ly), 10, (0, 255, 255) if inertia_cnt > 0 else (0, 0, 255), 2)
                            tx, ty = rx + lx + monitor["left"], ry + ly + monitor["top"]
                            if not self.is_dragging_anti: 
                                if is_initial_lockon:
                                    if self.input_mode == 1:
                                        ctypes.windll.user32.SetCursorPos(int(tx), int(ty))
                                    elif self.input_mode == 2 and self.logitech_input.dll:
                                        cx, cy = pyautogui.position()
                                        self.logitech_input.move(tx - cx, ty - cy)
                                    else:
                                        pyautogui.moveTo(tx, ty)
                                self.drag_mouse_down(); self.is_dragging_anti = True
                            self.human_mouse_move(tx, ty)
                        else:
                            lost_cnt += 1
                            if lost_cnt > 8 and self.is_dragging_anti:
                                self.drag_mouse_up(); self.is_dragging_anti = False
                            if lost_cnt > 20:
                                is_tracking, p0, last_x, last_y, vx, vy, inertia_cnt, popup_roi = False, None, None, None, 0.0, 0.0, 0, None
                                lockon_start_time = None
                                dynamic_bg = None
                                self.signals.shape_stop_signal.emit()
                        old_gray = cropped_gray.copy()
                        self.signals.shape_monitor_signal.emit((debug_feed, log_msg))
                except Exception as e:
                    pass
                time.sleep(0.02)
            else:
                if self.is_dragging_anti: 
                    self.drag_mouse_up()
                    self.is_dragging_anti = False
                target_lower, target_upper = None, None
                p0, old_gray = None, None
                is_tracking = False
                last_x, last_y = None, None
                vx, vy = 0.0, 0.0
                inertia_cnt = 0
                popup_roi = None
                lost_cnt = 0
                lockon_start_time = None
                dynamic_bg = None
                time.sleep(0.5)

    def update_log(self, m): self.log_text.append(f"<span style='color:#484f58'>[{time.strftime('%H:%M:%S')}]</span> {m}"); self.log_text.verticalScrollBar().setValue(self.log_text.verticalScrollBar().maximum())
    
    def update_status_ui(self, d): 
        self.data_runtime.setText(d.get("uptime", "00:00:00")); self.data_total_time.setText(d.get("total_uptime", "00:00:00"))
        self.cpu_bar.setValue(d.get('cpu', 0)); self.ram_bar.setValue(d.get('ram', 0))
        self.data_actions.setText(str(d.get("actions", 0))); self.data_errors.setText(f"{d.get('err_cnt', 0)}회")
        
        cx = d.get("char_x", -1)
        cy = d.get("char_y", -1)
        if cx != -1 and cy != -1:
            self.data_char_pos.setText(f"X: {cx}, Y: {cy}")
        else:
            self.data_char_pos.setText("인식 불가")
            
    def update_minimap_preview(self, i): h, w, c = i.shape; self.minimap_preview.setPixmap(QPixmap.fromImage(QImage(i.data, w, h, c*w, QImage.Format_RGB888).rgbSwapped()).scaled(self.minimap_preview.size(), Qt.IgnoreAspectRatio, Qt.SmoothTransformation))
    def update_shape_analytics(self, d): h, w, c = d[0].shape; self.shape_preview.setPixmap(QPixmap.fromImage(QImage(d[0].data, w, h, c*w, QImage.Format_RGB888).rgbSwapped()).scaled(self.shape_preview.size(), Qt.IgnoreAspectRatio, Qt.SmoothTransformation)); (self.shape_console.append(d[1]), self.shape_console.verticalScrollBar().setValue(self.shape_console.verticalScrollBar().maximum())) if d[1] else None
    
    def hunter_core(self):
        cur_dir, l_att, l_dash, l_del = 'right', 0, 0, time.time()
        self.last_char_seen_time = time.time()
        self.last_anti_afk_time = time.time()
        self.is_falling_recovering = False
        self.is_bottom_hunting = False
        
        try:
            while self.is_running:
                if self.is_selling or self.is_dragging_anti: 
                    if self.is_dragging_anti or self.is_selling: 
                        self.set_key_state('left', False)
                        self.set_key_state('right', False)
                    time.sleep(0.1); continue
                
                with mss.mss() as sct:
                     reg = {"top": self.reg_t, "left": self.reg_l, "width": self.reg_w, "height": self.reg_h}
                     try:
                        shot = np.array(sct.grab(reg)); img = cv2.cvtColor(shot, cv2.COLOR_BGRA2BGR); m = self.color_margin
                        low = np.array([max(0, self.base_lower[2]-m), max(0, self.base_lower[1]-m), max(0, self.base_lower[0]-m)])
                        high = np.array([min(255, self.base_upper[2]+m), min(255, self.base_upper[1]+m), min(255, self.base_upper[0]+m)])
                        mask = cv2.inRange(img, low, high)
                        
                        cx, cy = -1, -1
                        if np.any(mask):
                            M = cv2.moments(mask)
                            if M["m00"] > 0:
                                cx, cy = int(M["m10"]/M["m00"]), int(M["m01"]/M["m00"])
                        
                        self.char_x, self.char_y = cx, cy
                        
                        # 1. 캐릭터 인식 상태 갱신 및 안전 탈출 처리
                        if cx != -1 and cy != -1:
                            self.last_char_seen_time = time.time()
                        else:
                            if self.use_escape_lost and (time.time() - self.last_char_seen_time > self.lost_timeout_sec):
                                self.log(f"⚠️ [비상] {self.lost_timeout_sec}초 이상 캐릭터 좌표 인식 불가로 긴급 사냥을 중단합니다.")
                                self.signals.alert_signal.emit()
                                self.is_running = False
                                break
                        
                        # 2. 감시(잠수) 모드 처리
                        if self.use_watch_mode:
                            self.set_key_state('left', False)
                            self.set_key_state('right', False)
                            
                            # 마을 이동 방지 (Anti-AFK)
                            if self.use_anti_town and (time.time() - self.last_anti_afk_time > 20):
                                self.log("💤 [감시 모드] 잠수 방지 및 마을 이동 방지 미세 동작 수행")
                                self.set_key_state('left', True)
                                time.sleep(0.1)
                                self.set_key_state('left', False)
                                time.sleep(0.05)
                                self.set_key_state('right', True)
                                time.sleep(0.1)
                                self.set_key_state('right', False)
                                self.last_anti_afk_time = time.time()
                                
                            time.sleep(0.1)
                            continue
                            
                        # 3. 낚시사냥 모드 처리
                        if self.use_fishing_mode and self.fish_x != -1 and self.fish_y != -1:
                            if cx != -1 and cy != -1:
                                dx = cx - self.fish_x
                                dy = cy - self.fish_y
                                
                                # 이탈 한도 (±5px) 체크
                                if abs(dx) > 5 or abs(dy) > 5:
                                    self.log(f"🎣 낚시 자리 이탈 감지 -> 텔레포트 복귀 기동 (현재 X:{cx}, Y:{cy} / 목표 X:{self.fish_x}, Y:{self.fish_y})")
                                    teleport_key = self.key_teleport_cb.currentText()
                                    
                                    # Y축 텔레포트 복귀 (목표보다 아래에 있으면 Up + Teleport)
                                    if dy > 5:
                                        self.set_key_state('left', False)
                                        self.set_key_state('right', False)
                                        self.set_key_state('up', True)
                                        time.sleep(0.08)
                                        self.press_key(teleport_key)
                                        time.sleep(0.2)
                                        self.set_key_state('up', False)
                                        time.sleep(0.1)
                                        continue
                                        
                                    # X축 텔레포트 복귀
                                    if dx > 5:
                                        # 오른쪽 -> 왼쪽 이동
                                        self.set_key_state('right', False)
                                        self.set_key_state('left', True)
                                        time.sleep(0.05)
                                        self.press_key(teleport_key)
                                        time.sleep(0.15)
                                        self.set_key_state('left', False)
                                    elif dx < -5:
                                        # 왼쪽 -> 오른쪽 이동
                                        self.set_key_state('left', False)
                                        self.set_key_state('right', True)
                                        time.sleep(0.05)
                                        self.press_key(teleport_key)
                                        time.sleep(0.15)
                                        self.set_key_state('right', False)
                                        
                                    time.sleep(0.1)
                                    continue
                                else:
                                    # 제자리 낚시 안착 -> 핑퐁 이동 정지 후 스킬 난사
                                    self.set_key_state('left', False)
                                    self.set_key_state('right', False)
                                    
                                    now = time.time()*1000
                                    if now - l_att >= self.attack_delay_ms: 
                                        self.press_key(self.key_att_cb.currentText())
                                        l_att = now
                                    if time.time() - l_del >= self.periodic_interval_min*60: 
                                        self.press_key(self.key_pet_cb.currentText())
                                        l_del = time.time()
                                    time.sleep(0.1)
                                    continue
                        
                        # 4. 자동 복층/핑퐁 사냥 연산
                        if cx != -1 and cy != -1:
                            # A. 추락 복귀 핸들링
                            if self.use_fall_recovery and cy >= self.fall_y_threshold:
                                if not self.is_falling_recovering:
                                    self.log(f"🚨 캐릭터 추락 감지 (Y: {cy} >= 임계값: {self.fall_y_threshold}). 텔레포트 복귀 동작 개시!")
                                    self.is_falling_recovering = True
                                
                                self.set_key_state('left', False)
                                self.set_key_state('right', False)
                                
                                # 텔레포트 수직 도약 복귀
                                teleport_key = self.key_teleport_cb.currentText()
                                self.set_key_state('up', True)
                                time.sleep(0.08)
                                self.press_key(teleport_key)
                                time.sleep(0.2)
                                self.set_key_state('up', False)
                                time.sleep(0.15)
                                continue
                            else:
                                if self.is_falling_recovering:
                                    self.log("✅ 추락 복귀 완료. 일반 사냥으로 복귀합니다.")
                                    self.is_falling_recovering = False
                                    
                            # B. 하단 사냥 후 자동 복귀 핸들링
                            if self.use_bottom_hunt:
                                if cy >= self.bottom_y_threshold:
                                    if not self.is_bottom_hunting:
                                        self.log(f"⬇️ 하단 사냥 지역 진입 (Y: {cy}). {self.bottom_hunt_time_sec}초간 하단 사냥 후 복귀합니다.")
                                        self.is_bottom_hunting = True
                                        self.bottom_hunt_start_time = time.time()
                                    
                                    # 하단 사냥 유효시간 초과 시, 상단으로 강제 텔레포트 복귀
                                    if time.time() - self.bottom_hunt_start_time > self.bottom_hunt_time_sec:
                                        self.log("⏰ 하단 사냥 제한 시간 도래. 텔레포트 복귀 동작 수행")
                                        self.set_key_state('left', False)
                                        self.set_key_state('right', False)
                                        
                                        teleport_key = self.key_teleport_cb.currentText()
                                        self.set_key_state('up', True)
                                        time.sleep(0.08)
                                        self.press_key(teleport_key)
                                        time.sleep(0.2)
                                        self.set_key_state('up', False)
                                        time.sleep(0.15)
                                        continue
                                else:
                                    if self.is_bottom_hunting:
                                        self.log("⬆️ 상단 라인 도달 확인. 일반 사냥으로 롤백합니다.")
                                        self.is_bottom_hunting = False
                                        
                            # C. 일반 핑퐁 사냥 연산
                            if self.hunt_mode == 0:
                                if cx >= self.x_max and cur_dir == 'right':
                                    self.set_key_state('right', False)
                                    cur_dir = 'left'
                                elif cx <= self.x_min and cur_dir == 'left':
                                    self.set_key_state('left', False)
                                    cur_dir = 'right'
                            self.set_key_state(cur_dir, True)
                            
                            now = time.time()*1000
                            if now - l_att >= self.attack_delay_ms: self.press_key(self.key_att_cb.currentText()); l_att = now
                            if now - l_dash >= self.dash_delay_ms: self.press_key(self.key_dash_cb.currentText()); l_dash = now
                            if time.time() - l_del >= self.periodic_interval_min*60: self.press_key(self.key_pet_cb.currentText()); l_del = time.time()
                     except Exception as e: pass
                time.sleep(0.04)
        finally: 
            self.set_key_state('left', False)
            self.set_key_state('right', False)
            self.set_key_state('up', False)
            self.is_running = False

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
                        
                        # 타겟 바운더리 라인 렌더링
                        cv2.line(p_img, (self.x_min, 0), (self.x_min, self.reg_h), (59, 130, 246), 2)
                        cv2.line(p_img, (self.x_max, 0), (self.x_max, self.reg_h), (239, 68, 68), 2)
                        
                        cx, cy = -1, -1
                        if np.any(mask):
                            M = cv2.moments(mask)
                            if M["m00"] > 0: 
                                cx, cy = int(M["m10"]/M["m00"]), int(M["m01"]/M["m00"])
                                cv2.circle(p_img, (cx, cy), 5, (34, 197, 94), -1)
                        
                        # 모니터링 시 스레드 동기화 갱신
                        self.char_x, self.char_y = cx, cy
                        
                        self.signals.preview_signal.emit(p_img)
                    except: pass
                time.sleep(0.1)

    def anti_macro_loop(self):
        while not self.stop_threads:
            if self.use_anti_macro and self.is_running:
                try:
                    with mss.mss() as sct:
                        img = np.array(sct.grab(sct.monitors[0])); gray = cv2.cvtColor(img, cv2.COLOR_BGRA2GRAY)
                        for i in range(1, 4):
                            p = os.path.join(BASE_DIR, f"anti{i}.png")
                            if os.path.exists(p):
                                tm = cv2.imread(p, 0)
                                if tm is not None and np.max(cv2.matchTemplate(gray, tm, cv2.TM_CCOEFF_NORMED)) > 0.8:
                                    self.err_cnt += 1
                                    self.signals.alert_signal.emit()
                                    self.signals.shape_start_signal.emit() # 감지 시 도형 추적 엔진 자동 활성화
                                    break
                except: pass
                time.sleep(2)
            else:
                time.sleep(1) # 사냥 미가동 혹은 감지 비활성화 시 대기 주기 연장

    def status_update_loop(self):
        while not self.stop_threads:
            try:
                up = int(time.time() - self.current_hunt_start) if self.is_running else 0; total = self.total_hunting_time + up
                self.signals.status_signal.emit({
                    "uptime": f"{up//3600:02d}:{(up%3600)//60:02d}:{up%60:02d}", 
                    "total_uptime": f"{total//3600:02d}:{(total%3600)//60:02d}:{total%60:02d}", 
                    "cpu": int(psutil.cpu_percent()), 
                    "ram": int(psutil.virtual_memory().percent), 
                    "actions": self.actions_cnt, 
                    "err_cnt": self.err_cnt,
                    "char_x": self.char_x,
                    "char_y": self.char_y
                })
            except: pass
            time.sleep(1.0)

    def press_key(self, k): self.set_key_state(k, True); time.sleep(random.uniform(0.05, 0.1)); self.set_key_state(k, False); self.actions_cnt += 1
    
    def auto_detect_minimap(self):
        self.log("🔍 미니맵 자동 인식 스캔 시작 (1280x720 창모드 최적화)...")
        try:
            with mss.mss() as sct:
                monitor = {"top": 0, "left": 0, "width": 700, "height": 600}
                shot = np.array(sct.grab(monitor))
                img = cv2.cvtColor(shot, cv2.COLOR_BGRA2BGR)
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                
                m = self.color_margin
                low = np.array([max(0, self.base_lower[2]-m), max(0, self.base_lower[1]-m), max(0, self.base_lower[0]-m)])
                high = np.array([min(255, self.base_upper[2]+m), min(255, self.base_upper[1]+m), min(255, self.base_upper[0]+m)])
                mask = cv2.inRange(img, low, high)
                
                cx, cy = -1, -1
                if np.any(mask):
                    M = cv2.moments(mask)
                    if M["m00"] > 0:
                        cx, cy = int(M["m10"]/M["m00"]), int(M["m01"]/M["m00"])
                        
                if cx == -1 or cy == -1:
                    self.log("⚠️ 자동 인식 실패: 화면 내에서 노란색 캐릭터 점을 찾을 수 없습니다. (창모드 활성화 확인 요망)")
                    return False
                    
                # Canny Edge 및 팽창 연산으로 끊어진 엣지를 강제 연결
                edges = cv2.Canny(gray, 20, 100)
                kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
                dilated = cv2.dilate(edges, kernel, iterations=1)
                
                # RETR_LIST를 통해 내부를 포함한 모든 닫힌 컨투어 탐색
                contours, _ = cv2.findContours(dilated, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
                
                best_rect = None
                candidate_rects = []
                for c in contours:
                    x, y, w, h = cv2.boundingRect(c)
                    # 1280x720 해상도에서 실제 지형 캔버스의 타겟 규격 튜닝 (150px~260px, 80px~160px)
                    if 150 < w < 260 and 80 < h < 160:
                        if x <= cx <= x+w and y <= cy <= y+h:
                            candidate_rects.append((x, y, w, h))
                            
                if candidate_rects:
                    # 면적이 가장 최소인 후보를 최적의 미니맵 직사각형으로 확정
                    best_rect = min(candidate_rects, key=lambda r: r[2] * r[3])
                            
                # 만약 에지 팽창으로 실패하면, 이진화 임계값 완화(thresh 75)를 취해 검출 시도
                if best_rect is None:
                    _, thresh = cv2.threshold(gray, 75, 255, cv2.THRESH_BINARY_INV)
                    contours, _ = cv2.findContours(thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
                    candidate_rects = []
                    for c in contours:
                        x, y, w, h = cv2.boundingRect(c)
                        if 150 < w < 260 and 80 < h < 160:
                            if x <= cx <= x+w and y <= cy <= y+h:
                                candidate_rects.append((x, y, w, h))
                    if candidate_rects:
                        best_rect = min(candidate_rects, key=lambda r: r[2] * r[3])
                                
                if best_rect:
                    x, y, w, h = best_rect
                    # 여백 보정
                    self.reg_l = x + 3
                    self.reg_t = y + 3
                    self.reg_w = w - 6
                    self.reg_h = h - 6
                    
                    margin_px = int(self.reg_w * 0.15)
                    self.x_min = margin_px
                    self.x_max = self.reg_w - margin_px
                    
                    self.x_min_slider.setValue(self.x_min)
                    self.x_max_slider.setValue(self.x_max)
                    
                    self.log(f"✅ 미니맵 자동 검출 성공! 위치: ({self.reg_l}, {self.reg_t}), 크기: {self.reg_w}x{self.reg_h}")
                    self.log(f"📍 사냥 구역 자동 지정: 좌 {self.x_min}px ~ 우 {self.x_max}px")
                    winsound.Beep(1200, 200)
                    return True
                else:
                    self.reg_l = max(0, cx - 100)
                    self.reg_t = max(0, cy - 75)
                    self.reg_w = 200
                    self.reg_h = 150
                    self.x_min = 20
                    self.x_max = 180
                    self.x_min_slider.setValue(self.x_min)
                    self.x_max_slider.setValue(self.x_max)
                    self.log("⚠️ 외곽 경계 검출 실패로 캐릭터 위치 기준 200x150 기본 영역 강제 폴백 설정.")
                    winsound.Beep(1000, 300)
                    return True
        except Exception as e:
            self.log(f"❌ 자동 인식 스캔 예외 발생: {str(e)}")
            return False

    def start_hunting(self): 
        if self.reg_w <= 10 or self.minimap_preview.text() == "WAITING...":
            self.auto_detect_minimap()
        self.is_running = True; self.start_btn.setEnabled(False); self.stop_btn.setEnabled(True); self.current_hunt_start = time.time(); threading.Thread(target=self.hunter_core, daemon=True).start()
    def stop_hunting(self): self.is_running = False; self.start_btn.setEnabled(True); self.stop_btn.setEnabled(False); self.total_hunting_time += int(time.time()-self.current_hunt_start); self.set_key_state('left', False); self.set_key_state('right', False); self.set_key_state('up', False)
    def hotkey_start_handler(self): self.signals.start_signal.emit()
    def hotkey_stop_handler(self): self.signals.stop_signal.emit()
    def hotkey_shape_start_handler(self): self.signals.shape_start_signal.emit()
    def hotkey_shape_stop_handler(self): self.signals.shape_stop_signal.emit()
    
    def hotkey_fix_fish_handler(self):
        if self.char_x != -1 and self.char_y != -1:
            self.fish_x = self.char_x
            self.fish_y = self.char_y
            self.lbl_fish_pos.setText(f"지정된 낚시 좌표: X: {self.fish_x}, Y: {self.fish_y}")
            self.log(f"🎣 [낚시 좌표 고정 완료] -> X: {self.fish_x}, Y: {self.fish_y}")
            winsound.Beep(1500, 300)
        else:
            self.log("⚠️ [낚시 좌표 픽스 실패] 현재 캐릭터 위치 인식이 불가능합니다.")
            winsound.Beep(800, 300)
            
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
    
    def update_use_bottom_hunt(self, b): self.use_bottom_hunt = b
    def update_bottom_y(self, v): self.bottom_y_threshold = v
    def update_bottom_time(self, v): self.bottom_hunt_time_sec = v
    def update_use_fall_recovery(self, b): self.use_fall_recovery = b
    def update_fall_y(self, v): self.fall_y_threshold = v
    def update_use_escape_lost(self, b): self.use_escape_lost = b
    def update_lost_timeout(self, v): self.lost_timeout_sec = v
    def update_use_watch_mode(self, b): self.use_watch_mode = b
    def update_use_anti_town(self, b): self.use_anti_town = b
    def update_use_fishing_mode(self, b): self.use_fishing_mode = b
    
    def on_profile_change(self, n): self.apply_profile_data(n) if n in self.profiles_data else None
    def update_profile_list(self): self.profile_combo.blockSignals(True); self.profile_combo.clear(); self.profile_combo.addItems(list(self.profiles_data.keys())); self.profile_combo.blockSignals(False)
    def load_all_profiles(self): 
        if os.path.exists(CONFIG_FILE) and os.path.getsize(CONFIG_FILE) > 0:
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f: self.profiles_data = json.load(f)
                self.update_profile_list()
                if self.profiles_data: n = list(self.profiles_data.keys())[0]; self.profile_combo.setCurrentText(n); self.apply_profile_data(n)
            except: pass
    def save_current_profile(self): 
        n = self.profile_combo.currentText()
        if not n: return
        self.profiles_data[n] = {
            "reg": {"t": self.reg_t, "l": self.reg_l, "w": self.reg_w, "h": self.reg_h}, 
            "range": {"min": self.x_min, "max": self.x_max, "stat": self.stationary_range}, 
            "keys": {
                "att": self.key_att_cb.currentText(), 
                "dash": self.key_dash_cb.currentText(), 
                "jump": self.key_jump_cb.currentText(), 
                "teleport": self.key_teleport_cb.currentText(),
                "pet": self.key_pet_cb.currentText()
            }, 
            "params": {"margin": self.color_margin, "precision": self.precision_val, "ad": self.attack_delay_ms, "dd": self.dash_delay_ms, "mode": self.hunt_mode, "per_int": self.periodic_interval_min, "sell_int": self.sell_interval_min, "sound": self.use_sound_alert, "shape_anti": self.use_shape_anti, "input_mode": self.input_mode},
            "coord": {
                "use_bottom": self.use_bottom_hunt, "bottom_y": self.bottom_y_threshold, "bottom_time": self.bottom_hunt_time_sec,
                "use_fall": self.use_fall_recovery, "fall_y": self.fall_y_threshold,
                "use_escape": self.use_escape_lost, "lost_time": self.lost_timeout_sec,
                "use_watch": self.use_watch_mode, "use_anti_town": self.use_anti_town,
                "use_fishing": self.use_fishing_mode, "fish_x": self.fish_x, "fish_y": self.fish_y
            }
        }
        with open(CONFIG_FILE, "w", encoding="utf-8") as f: json.dump(self.profiles_data, f, ensure_ascii=False, indent=4)
        self.update_profile_list(); QMessageBox.information(self, "저장", "프로필 저장됨")
    def apply_profile_data(self, n): 
        if n not in self.profiles_data: return
        d = self.profiles_data[n]; p = d["params"]; ke = d.get("keys", {})
        self.reg_t, self.reg_l, self.reg_w, self.reg_h = d["reg"]["t"], d["reg"]["l"], d["reg"]["w"], d["reg"]["h"]
        self.x_min_slider.setValue(d["range"]["min"]); self.x_max_slider.setValue(d["range"]["max"]); self.stat_range_slider.setValue(d["range"]["stat"])
        self.precision_slider.setValue(int(p["precision"]*10)); self.att_slider.setValue(p["ad"]); self.dash_slider.setValue(p["dd"])
        self.pet_slider.setValue(p["per_int"]); self.sell_slider.setValue(p["sell_int"])
        self.chk_alert.setChecked(p["sound"]); self.chk_shape_anti.setChecked(p["shape_anti"]); self.mode_tabs.setCurrentIndex(p["mode"])
        self.input_mode = p.get("input_mode", 0)
        self.input_mode_combo.setCurrentIndex(self.input_mode)
        
        # 단축키 설정 로드
        self.key_att_cb.setCurrentText(ke.get("att", "end"))
        self.key_dash_cb.setCurrentText(ke.get("dash", "space"))
        self.key_jump_cb.setCurrentText(ke.get("jump", "alt"))
        self.key_teleport_cb.setCurrentText(ke.get("teleport", "shift"))
        self.key_pet_cb.setCurrentText(ke.get("pet", "del"))
        
        # 신규 설정 변수 로드
        co = d.get("coord", {})
        self.chk_bottom_hunt.setChecked(co.get("use_bottom", False))
        self.bottom_y_slider.setValue(co.get("bottom_y", 80))
        self.bottom_time_slider.setValue(co.get("bottom_time", 10))
        self.chk_fall_recovery.setChecked(co.get("use_fall", False))
        self.fall_y_slider.setValue(co.get("fall_y", 110))
        self.chk_escape_lost.setChecked(co.get("use_escape", False))
        self.lost_time_slider.setValue(co.get("lost_time", 5))
        self.chk_watch_mode.setChecked(co.get("use_watch", False))
        self.chk_anti_town.setChecked(co.get("use_anti_town", False))
        
        # 낚시 설정 로드
        self.chk_fishing_mode.setChecked(co.get("use_fishing", False))
        self.fish_x = co.get("fish_x", -1)
        self.fish_y = co.get("fish_y", -1)
        if self.fish_x != -1 and self.fish_y != -1:
            self.lbl_fish_pos.setText(f"지정된 낚시 좌표: X: {self.fish_x}, Y: {self.fish_y}")
        else:
            self.lbl_fish_pos.setText("지정된 낚시 좌표: X: 미지정, Y: 미지정")
        
    def open_selector(self): 
        self.selector = QWidget(); self.selector.setWindowOpacity(0.3); self.selector.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint); self.selector.showFullScreen(); self.selector.setCursor(Qt.CrossCursor)
        self.selector.mousePressEvent = lambda e: setattr(self, 'sel_start', e.pos()); self.selector.mouseReleaseEvent = self.sel_finish; self.selector.show()
    def sel_finish(self, e): 
        if hasattr(self, 'sel_start') and self.sel_start:
            end = e.pos(); self.reg_l, self.reg_t, self.reg_w, self.reg_h = min(self.sel_start.x(), end.x()), min(self.sel_start.y(), end.y()), abs(self.sel_start.x()-end.x()), abs(self.sel_start.y()-end.y())
        self.selector.close(); self.selector.deleteLater()
    def play_custom_sound(self): 
        def _p():
            s = time.time()
            while time.time()-s < 10 and self.use_sound_alert: winsound.Beep(3000, 100); winsound.Beep(4000, 100)
        threading.Thread(target=_p, daemon=True).start()
    def log(self, m): self.signals.log_signal.emit(m)
    def closeEvent(self, e): 
        self.stop_threads = True; self.is_running = False
        try:
            self.set_key_state('left', False)
            self.set_key_state('right', False)
            self.set_key_state('up', False)
            self.drag_mouse_up()
        except: pass
        e.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv); window = AUTOmapleV9_7(); window.show(); sys.exit(app.exec())
