import sys
import os
import time
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
from PIL import Image, ImageDraw, ImageFont

from PySide6.QtCore import Qt, QTimer, Signal, QObject, QSize, QPoint
from PySide6.QtGui import QColor, QFont, QImage, QPixmap, QIcon, QAction
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QGridLayout, QFrame, QLabel, QPushButton, QComboBox, QSlider, 
    QLineEdit, QTabWidget, QCheckBox, QRadioButton, QButtonGroup,
    QProgressBar, QTextEdit, QSizePolicy, QSpacerItem, QMessageBox,
    QGroupBox, QScrollArea
)

# 경로 설정
if getattr(sys, 'frozen', False):
    BASE_DIR = sys._MEIPASS
    CONFIG_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    CONFIG_DIR = BASE_DIR
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")

# --- DPI 보정 ---
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except:
    pass

# 모듈 패키지 임포트 보장
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from modules.logger import AppLogger
from modules.settings import SettingsManager
from modules.minimap import MinimapDetector
from modules.movement import MovementController
from modules.combat import CombatController
from modules.waypoint import WaypointManager
from modules.ui import UiSetup

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
    f2_signal = Signal()
    f1_signal = Signal()
    update_available_signal = Signal(str)

class AUTOmapleV9_7(QMainWindow):
    def __init__(self):
        super().__init__()
        self.version = "v2.0.0"
        self.setWindowTitle(f"AUTOmaple {self.version} (2026.06.08 - V4 상용 배포판)")
        self.setMinimumSize(380, 960)
        self.resize(380, 960)
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        
        # 테마 및 관리자 모드 상태 변수
        self.theme_mode = "dark"
        self.is_admin_mode = False
        self.is_admin_user = False
        
        # 전역 경로 공유
        self.base_dir = BASE_DIR
        self.config_dir = CONFIG_DIR
        self.config_file = CONFIG_FILE
        
        # 상태 변수
        self.is_running = False
        self.is_selling = False
        self.is_attacking = False
        self.is_moving = False
        self.is_teleporting = False
        self.total_hunting_time = 0
        self.current_hunt_start = 0
        self.program_start_time = time.time()
        self.actions_cnt = 0
        self.err_cnt = 0
        self.frame_num = 0
        self.is_dragging_anti = False
        self.is_pingpong_fixed_attacking = False  # 제자리 고정 공격 상태 플래그
        self.is_pingpong_fixed_prevent_attack = False  # 제자리 고정 공격 금지 플래그
        
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

        # 복층 사냥 변수
        self.use_multifloor_hunt = False
        self.multifloor_up_count = 1

        # 순환사냥 V2 변수 (V3 확장)
        self.waypoint_count = 30
        self.waypoints = [{"x_min": -1, "x_max": -1, "y": -1, "move_type": "TELE_LEFT", "stay_time": 2.0} for _ in range(self.waypoint_count)]
        self.visited_waypoints = [False] * self.waypoint_count
        self.teleport_threshold = 20
        self.landing_start_time = None
        self.fall_count = 0
        self.last_char_y = -1
        self.current_waypoint_idx = 0
        self.waypoint_record_idx = 0
        self.is_first_v2_loop = True
        self.transit_moved = False
        self.last_completed_waypoint_idx = -1
        
        # 사냥 경로 녹화 관련 변수
        self.is_recording = False
        self.recording_data = []
        self.recording_start_time = 0
        
        # 입력 시뮬레이션 관련 변수
        self.input_mode = 0  # 0: PyAutoGUI, 1: Windows SendInput, 2: Logitech G HUB
        self.key_states = {}
        
        # 기본 설정
        self.reg_t, self.reg_l, self.reg_w, self.reg_h = 100, 100, 200, 150
        self.x_min, self.x_max, self.stationary_range = 20, 180, 15
        self.precision_val, self.color_margin = 0.0, 0
        self.attack_delay_ms, self.dash_delay_ms = 200, 500
        self.periodic_interval_min, self.sell_interval_min = 5, 15
        self.use_auto_sell, self.use_anti_macro, self.use_shape_anti, self.use_sound_alert = False, True, False, True
        self.hunt_mode = 0 
        self.hunt_layer_idx = -1
        self.recovery_layer_idx = -1
        self.use_debug_mode = False
        self.base_lower = np.array([245, 230, 0]); self.base_upper = np.array([254, 255, 129])
        self.profiles_data = {}
        
        # Teleport and Action status vars
        self.teleport_x = -1
        self.teleport_y = -1
        self.current_action_status = None

        self.signals = Communicate()
        self.signals.log_signal.connect(self.update_log)
        self.signals.preview_signal.connect(self.update_minimap_preview)
        self.signals.shape_monitor_signal.connect(self.update_shape_analytics)
        self.signals.status_signal.connect(self.update_status_ui)
        self.signals.alert_signal.connect(self.play_custom_sound)
        self.signals.f2_signal.connect(self.handle_f2_main_thread)
        self.signals.f1_signal.connect(self.register_sell_position)
        self.signals.update_available_signal.connect(self.show_update_dialog)

        # 모듈 인스턴스화
        self.logger = AppLogger(self)
        self.settings_manager = SettingsManager(self)
        self.minimap_detector = MinimapDetector(self)
        self.movement_controller = MovementController(self)
        self.combat_controller = CombatController(self)
        self.waypoint_manager = WaypointManager(self)

        # UI 셋업
        UiSetup.setup_ui(self)
        
        # 상단 버튼 시그널 바인딩
        self.btn_theme_toggle.clicked.connect(self.toggle_theme)
        self.btn_admin_mode.clicked.connect(self.toggle_admin_mode)
        
        # UAC 관리자 권한 탐지
        self.is_admin_user = ctypes.windll.shell32.IsUserAnAdmin() != 0
        if not self.is_admin_user:
            self.admin_status_lbl.setText("⚠️ UAC 일반 권한")
            self.setWindowTitle(f"AUTOmaple {self.version} [⚠️일반권한]")
        else:
            self.admin_status_lbl.setText("🛡️ 관리자 권한")
            
        UiSetup.apply_qss(self, self.theme_mode)
        UiSetup.set_admin_mode_visibility(self, self.is_admin_mode)
        
        self.signals.start_signal.connect(self.start_btn.click)
        self.signals.stop_signal.connect(self.stop_btn.click)
        self.signals.sell_signal.connect(self.manual_sell_btn.click)
        self.signals.shape_start_signal.connect(lambda: self.chk_shape_anti.setChecked(True))
        self.signals.shape_stop_signal.connect(lambda: self.chk_shape_anti.setChecked(False))

        self.settings_manager.load_all_profiles()
        
        # 관리자 권한 미부여 경고 로그 출력
        if not self.is_admin_user:
            self.logger.log("<span style='color:#f85149; font-weight:bold;'>[경고] 관리자 권한으로 실행되지 않았습니다! 다른 PC나 게임 창이 활성화되어 있을 때 단축키(F5/F6) 및 마우스 조작이 씹힐 수 있으니 반드시 프로그램을 우클릭하여 '관리자 권한으로 실행'해 주세요.</span>", "SYSTEM")
        self.stop_threads = False
        
        # 스레드 루프 시작
        threading.Thread(target=self.monitor_loop, daemon=True).start()
        threading.Thread(target=self.minimap_detector.anti_macro_loop, daemon=True).start()
        threading.Thread(target=self.minimap_detector.shape_tracking_loop, daemon=True).start()
        threading.Thread(target=self.status_update_loop, daemon=True).start()
        
        try:
            keyboard.unhook_all()
            keyboard.add_hotkey('f4', self.waypoint_manager.toggle_route_recording)
            keyboard.add_hotkey('f5', self.hotkey_start_handler)
            keyboard.add_hotkey('f6', self.hotkey_stop_handler)
            keyboard.add_hotkey('f9', self.hotkey_fix_fish_handler)
            keyboard.add_hotkey('f2', self.hotkey_f2_handler)
            keyboard.add_hotkey('f1', self.hotkey_f1_handler)
        except: 
            pass
        
        if self.hunt_mode == 1:
            self.hunt_mode = 0  # 제자리 사냥 모드는 핑퐁 고정 모드로 통합
        if self.hunt_mode == 0:
            self.radio_lr.setChecked(True)
        elif self.hunt_mode == 2:
            self.radio_v2.setChecked(True)
        self.update_mode_ui_states()
        
        # 기동 2초 후 자동 업데이트 검사 실행
        QTimer.singleShot(2000, self.check_startup_update)

    def set_key_state(self, key, state):
        self.movement_controller.set_key_state(key, state)
        
    def press_key(self, k):
        self.movement_controller.press_key(k)
        
    def drag_mouse_down(self):
        self.movement_controller.drag_mouse_down()
        
    def drag_mouse_up(self):
        self.movement_controller.drag_mouse_up()
        
    def human_mouse_move(self, tx, ty):
        self.movement_controller.human_mouse_move(tx, ty)

    def register_sell_position(self):
        widget = QApplication.focusWidget()
        if widget and isinstance(widget, QLineEdit) and widget.objectName().startswith("sell_pos"):
            cx, cy = pyautogui.position()
            widget.setText(f"{cx}, {cy}")
            widget.editingFinished.emit()
            self.settings_manager.save_settings_silently()
            self.logger.log(f"[{widget.toolTip() or widget.objectName()}] 좌표 등록 완료 -> {cx}, {cy}", "SYSTEM")
        else:
            self.run_manual_sell()

    def trigger_update(self):
        url = getattr(self, 'update_url', "https://raw.githubusercontent.com/CASHCOW95/world-project/master/update.json")
        if not url:
            self.logger.log("[업데이트] 업데이트 JSON URL이 지정되지 않았습니다.", "SYSTEM")
            winsound.Beep(500, 500)
            return
        
        self.btn_oneclick_update.setEnabled(False)
        self.btn_oneclick_update.setText("업데이트 중...")
        
        def update_worker():
            import urllib.request
            import urllib.error
            import json
            import zipfile
            
            try:
                self.logger.log(f"[업데이트] 최신 버전 확인 중: {url}", "SYSTEM")
                req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req, timeout=5) as response:
                    data = json.loads(response.read().decode('utf-8'))
                
                latest_ver = data.get("version", "")
                download_url = data.get("download_url", "")
                
                if not latest_ver or not download_url:
                    self.logger.log("[업데이트] 잘못된 업데이트 정보 형식입니다.", "SYSTEM")
                    return
                
                self.logger.log(f"[업데이트] 최신 패키지 다운로드 시작 -> {download_url}", "SYSTEM")
                zip_path = "update_temp.zip"
                
                req_dl = urllib.request.Request(download_url, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req_dl) as dl_resp, open(zip_path, 'wb') as out_file:
                    meta = dl_resp.info()
                    file_size = int(meta.get("Content-Length", 0))
                    
                    downloaded = 0
                    block_size = 8192
                    while True:
                        buffer = dl_resp.read(block_size)
                        if not buffer:
                            break
                        downloaded += len(buffer)
                        out_file.write(buffer)
                        if file_size > 0 and downloaded % (block_size * 400) == 0:
                            percent = downloaded * 100.0 / file_size
                            self.logger.log(f"[업데이트] 다운로드 중... {percent:.1f}%", "SYSTEM")
                
                self.logger.log("[업데이트] 다운로드 완료! 롤백 백업 배치 파일 생성 중...", "SYSTEM")
                
                bat_path = "update_worker.bat"
                
                is_frozen = getattr(sys, 'frozen', False)
                if is_frozen:
                    exe_name = os.path.basename(sys.executable)
                    run_cmd = f"start {exe_name}"
                    py_clean_cmd = ""
                    rollback_run_cmd = f"start {exe_name}"
                else:
                    curr_py_name = os.path.basename(sys.argv[0])
                    new_py_name = f"AUTOmaple_{latest_ver}_LK.py"
                    if curr_py_name != new_py_name:
                        py_clean_cmd = f'if exist "{curr_py_name}" del "{curr_py_name}"'
                    else:
                        py_clean_cmd = ""
                    run_cmd = f"start .venv\\Scripts\\python.exe {new_py_name}"
                    rollback_run_cmd = f"start .venv\\Scripts\\python.exe {curr_py_name}"
                
                bat_content = f"""@echo off
title AUTOmaple Auto Updater
echo ==============================================
echo  AUTOmaple Auto Updater (Version {latest_ver})
echo ==============================================
echo.
echo [1/5] Waiting for program to exit...
timeout /t 2 /nobreak > nul

echo [2/5] Creating backup...
if exist "update_backup" rd /s /q "update_backup"
mkdir "update_backup"

:: 설정/라이선스/로그 등의 파일은 임시 백업으로 이동하지 않고 격리하여 보존
if exist "config.json" copy "config.json" "update_backup\\" > nul
if exist "license.dat" copy "license.dat" "update_backup\\" > nul
if exist "route.json" copy "route.json" "update_backup\\" > nul
if exist "waypoints.json" copy "waypoints.json" "update_backup\\" > nul
if exist "user_settings.json" copy "user_settings.json" "update_backup\\" > nul
if exist "logs" xcopy /e /i /y "logs" "update_backup\\logs" > nul

:: 현재 폴더의 프로그램 구성 요소 백업
mkdir "update_backup\\program"
if exist "core" xcopy /e /i /y "core" "update_backup\\program\\core" > nul
if exist "*.exe" copy /y "*.exe" "update_backup\\program\\" > nul
if exist "*.dll" copy /y "*.dll" "update_backup\\program\\" > nul
if exist "*.py" copy /y "*.py" "update_backup\\program\\" > nul

echo [3/5] Extracting update package...
if exist "update_extracted" rd /s /q "update_extracted"
powershell -Command "Expand-Archive -Path '{zip_path}' -DestinationPath 'update_extracted' -Force"
if %ERRORLEVEL% neq 0 goto ROLLBACK

echo [4/5] Excluding user settings from release...
if exist "update_extracted\\config.json" del "update_extracted\\config.json"
if exist "update_extracted\\license.dat" del "update_extracted\\license.dat"
if exist "update_extracted\\route.json" del "update_extracted\\route.json"
if exist "update_extracted\\waypoints.json" del "update_extracted\\waypoints.json"
if exist "update_extracted\\user_settings.json" del "update_extracted\\user_settings.json"
if exist "update_extracted\\logs" rd /s /q "update_extracted\\logs"

echo Applying update...
xcopy /e /y "update_extracted\\*" "." > nul
if %ERRORLEVEL% neq 0 goto ROLLBACK

{py_clean_cmd}

rd /s /q "update_extracted"
if exist "{zip_path}" del "{zip_path}"
echo.
echo [5/5] Update successfully applied! Restarting...
{run_cmd}
del "%~f0"
exit

:ROLLBACK
echo.
echo ==============================================
echo [ERROR] Update failed! Rolling back...
echo ==============================================
echo.
if exist "update_extracted" rd /s /q "update_extracted"
if exist "update_backup\\program" xcopy /e /y "update_backup\\program\\*" "." > nul
if exist "update_backup\\config.json" copy /y "update_backup\\config.json" "." > nul
if exist "update_backup\\license.dat" copy /y "update_backup\\license.dat" "." > nul
if exist "update_backup\\route.json" copy /y "update_backup\\route.json" "." > nul
if exist "update_backup\\waypoints.json" copy /y "update_backup\\waypoints.json" "." > nul
if exist "update_backup\\user_settings.json" copy /y "update_backup\\user_settings.json" "." > nul
if exist "update_backup\\logs" xcopy /e /i /y "update_backup\\logs" "logs" > nul

echo Rollback complete. Restarting old version...
{rollback_run_cmd}
del "%~f0"
exit"""
                with open(bat_path, "w", encoding="euc-kr") as bat_f:
                    bat_f.write(bat_content)
                
                self.logger.log("[업데이트] 업데이트 패키지 적용을 위해 프로그램을 종료하고 업데이트 런처를 실행합니다.", "SYSTEM")
                time.sleep(1.0)
                os.startfile(bat_path)
                QApplication.quit()
                
            except Exception as e:
                self.logger.log(f"[업데이트 실패] 오류 발생: {str(e)}", "SYSTEM")
                winsound.Beep(500, 500)
            finally:
                self.btn_oneclick_update.setEnabled(True)
                self.btn_oneclick_update.setText("🚀 업데이트 실행")
                
        threading.Thread(target=update_worker, daemon=True).start()

    def check_startup_update(self):
        url = getattr(self, 'update_url', "https://raw.githubusercontent.com/CASHCOW95/world-project/master/update.json")
        if not url:
            return
            
        def check_worker():
            import urllib.request
            import json
            try:
                self.logger.log(f"[업데이트] 최신 버전 확인 중: {url}", "SYSTEM")
                req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req, timeout=3) as response:
                    data = json.loads(response.read().decode('utf-8'))
                
                latest_ver = data.get("version", "")
                download_url = data.get("download_url", "")
                msg = data.get("message", "")
                
                clean_ver = latest_ver.lower().replace("v", "")
                clean_curr = self.version.lower().replace("v", "")
                
                if clean_ver and clean_ver != clean_curr:
                    self.logger.log(f"[시스템] 새로운 버전({latest_ver})이 감지되었습니다. 사유: {msg}", "SYSTEM")
                    self.btn_oneclick_update.setEnabled(True)
                    self.signals.update_available_signal.emit(latest_ver)
                else:
                    self.logger.log("[업데이트] 현재 최신 버전을 사용 중입니다.", "SYSTEM")
            except Exception as e:
                self.logger.log(f"[업데이트 검사 에러] {str(e)}", "SYSTEM")
        threading.Thread(target=check_worker, daemon=True).start()

    def show_update_dialog(self, latest_ver):
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("업데이트 안내")
        msg_box.setText(f"새로운 업데이트 버전({latest_ver})이 존재합니다.\n\n지금 자동 업데이트를 실행하시겠습니까?")
        msg_box.setStyleSheet("QLabel { color: #ffffff; } QPushButton { background-color: #21262d; color: #c9d1d9; padding: 5px 15px; border-radius: 5px; }")
        
        run_btn = msg_box.addButton("업데이트 실행", QMessageBox.AcceptRole)
        cancel_btn = msg_box.addButton("취소", QMessageBox.RejectRole)
        
        msg_box.setDefaultButton(run_btn)
        msg_box.exec()
        
        if msg_box.clickedButton() == run_btn:
            self.trigger_update()

    def run_manual_sell(self):
        if self.is_selling: 
            return
        
        try:
            def parse_pos(txt):
                parts = txt.split(",")
                return int(parts[0].strip()), int(parts[1].strip())
            
            p1 = parse_pos(self.txt_sell_pos1.text())
            p2 = parse_pos(self.txt_sell_pos2.text())
            p3 = parse_pos(self.txt_sell_pos3.text())
            p4 = parse_pos(self.txt_sell_pos4.text())
            p5 = parse_pos(self.txt_sell_pos5.text())
            
            sell_rows = int(self.txt_sell_rows.text().strip() or "8")
            sell_start_row = int(self.txt_sell_start_row.text().strip() or "2")
            sell_delay = float(self.txt_sell_delay.text().strip() or "0.05")
        except Exception as e:
            self.logger.log(f"[판매 에러] 좌표 파싱 실패 (X, Y 형태로 입력되었는지 확인해주세요): {str(e)}", "SYSTEM")
            winsound.Beep(500, 500)
            return
            
        if any(pos == (0, 0) for pos in [p1, p2, p3, p4, p5]):
            self.logger.log("[판매 실패] 모든 좌표(1~5)가 올바르게 설정되어야 합니다.", "SYSTEM")
            winsound.Beep(500, 500)
            return

        self.logger.log("인벤토리 수동 판매 시퀀스 시작 (A방식 고도화)", "SYSTEM")
        self.is_selling = True
        try:
            self.set_key_state(self.key_att_cb.currentText(), False)
        except:
            pass
        self.is_pingpong_fixed_attacking = False
        winsound.Beep(1000, 200)
        
        def sell_thread_worker():
            try:
                pyautogui.PAUSE = 0
                
                # 1. 인벤토리 더블클릭(좌표1) -> 상점열기
                self.logger.log("1. 상점 열기 시도 (좌표1 더블클릭)", "SYSTEM")
                self.human_mouse_move(p1[0], p1[1])
                time.sleep(0.1)
                self.drag_mouse_down()
                time.sleep(0.05)
                self.drag_mouse_up()
                time.sleep(0.1)
                self.drag_mouse_down()
                time.sleep(0.05)
                self.drag_mouse_up()
                time.sleep(float(self.txt_sell_delay1.text().strip() or "1.5")) # 상점 로딩 대기
                
                if not self.is_selling: return
                
                # 2. 좌표2 클릭 후 엔터 -> 상점 확인/진입
                self.logger.log("2. 거래/판매 모드 진입 (좌표2 클릭 및 엔터)", "SYSTEM")
                self.human_mouse_move(p2[0], p2[1])
                time.sleep(0.1)
                self.drag_mouse_down()
                time.sleep(0.05)
                self.drag_mouse_up()
                time.sleep(0.2)
                self.press_key('enter')
                time.sleep(float(self.txt_sell_delay2.text().strip() or "1.0")) # 상점UI 활성화 대기
                
                if not self.is_selling: return
                
                # 3. 기타창이동(좌표3)
                self.logger.log("3. 기타창 탭 클릭 (좌표3 클릭)", "SYSTEM")
                self.human_mouse_move(p3[0], p3[1])
                time.sleep(0.1)
                self.drag_mouse_down()
                time.sleep(0.05)
                self.drag_mouse_up()
                time.sleep(float(self.txt_sell_delay3.text().strip() or "0.5"))
                
                if not self.is_selling: return
                
                # 4. 좌표4 더블클릭, 엔터 반복
                total_cnt = (sell_rows - sell_start_row + 1) * 4
                if total_cnt <= 0:
                    total_cnt = 32
                
                self.logger.log(f"4. 아이템 판매 루틴 작동 (좌표4 반복 더블클릭 + 엔터, 총 {total_cnt}회)", "SYSTEM")
                for i in range(total_cnt):
                    if not self.is_selling:
                        break
                    self.human_mouse_move(p4[0], p4[1])
                    time.sleep(0.01)
                    self.drag_mouse_down()
                    time.sleep(0.05)
                    self.drag_mouse_up()
                    time.sleep(0.10)
                    self.drag_mouse_down()
                    time.sleep(0.05)
                    self.drag_mouse_up()
                    time.sleep(float(self.txt_sell_delay4.text().strip() or "0.12")) # 더블클릭 후 판매 확인창 딜레이
                    self.press_key('enter')
                    time.sleep(max(0.05, sell_delay))
                    
                if not self.is_selling: return
                
                # 5. 좌표5 상점나가기
                self.logger.log("5. 상점 닫기 (좌표5 클릭)", "SYSTEM")
                self.human_mouse_move(p5[0], p5[1])
                time.sleep(0.1)
                self.drag_mouse_down()
                time.sleep(0.05)
                self.drag_mouse_up()
                time.sleep(float(self.txt_sell_delay5.text().strip() or "0.5"))
                
            except Exception as e:
                self.logger.log(f"[판매 오류] 루틴 실행 중 에러: {str(e)}", "SYSTEM")
            finally:
                self.is_selling = False
                self.logger.log("상점 판매 시퀀스 완료 - 사냥 모드 복귀", "SYSTEM")
                winsound.Beep(1200, 200)
                
        threading.Thread(target=sell_thread_worker, daemon=True).start()

    def update_log(self, m): 
        self.log_text.append(f"<span style='color:#484f58'>[{time.strftime('%H:%M:%S')}]</span> {m}")
        self.log_text.verticalScrollBar().setValue(self.log_text.verticalScrollBar().maximum())
        
    def update_status_ui(self, d): 
        self.data_runtime.setText(d.get("uptime", "00:00:00"))
        self.data_total_time.setText(d.get("total_uptime", "00:00:00"))
        self.cpu_bar.setValue(d.get('cpu', 0))
        self.ram_bar.setValue(d.get('ram', 0))
        self.data_recovery_left.setText(d.get("recovery_left", "비활성"))
        self.data_pet_left.setText(d.get("pet_left", "비활성"))
        self.data_errors.setText(f"{d.get('err_cnt', 0)}회")
        
        cx = d.get("char_x", -1)
        cy = d.get("char_y", -1)
        if cx != -1 and cy != -1:
            self.data_char_pos.setText(f"X: {cx}, Y: {cy}")
        else:
            self.data_char_pos.setText("인식 불가")
            
    def on_pingpong_x_min_edited(self):
        try:
            val = int(self.txt_pingpong_x_min.text().strip())
            self.x_min_slider.setValue(val)
            self.x_min = val
            self.settings_manager.save_settings_silently()
        except:
            pass
            
    def on_pingpong_x_max_edited(self):
        try:
            val = int(self.txt_pingpong_x_max.text().strip())
            self.x_max_slider.setValue(val)
            self.x_max = val
            self.settings_manager.save_settings_silently()
        except:
            pass
            
    def hotkey_f1_handler(self):
        self.signals.f1_signal.emit()

    def hotkey_f2_handler(self):
        self.signals.f2_signal.emit()
        
    def handle_f2_main_thread(self):
        if self.char_x == -1 or self.char_y == -1:
            self.logger.log("[F2 입력 실패] 현재 캐릭터 위치 인식이 불가능합니다.", "WAYPOINT")
            winsound.Beep(800, 300)
            return
            
        widget = QApplication.focusWidget()
        if widget and isinstance(widget, QLineEdit):
            obj_name = widget.objectName()
            cx, cy = self.char_x, self.char_y
            val = None
            
            if obj_name in ["x_min", "return_x_min"] or obj_name.endswith("_x_min"):
                val = max(0, cx - 1)
            elif obj_name in ["x_max", "return_x_max"] or obj_name.endswith("_x_max"):
                val = cx + 1
            elif obj_name in ["y_min"] or obj_name.endswith("_y_min"):
                val = max(0, cy - 1)
            elif obj_name in ["y_max"] or obj_name.endswith("_y_max"):
                val = cy + 1
            elif obj_name in ["teleport_x"] or obj_name.endswith("_x"):
                val = cx
            elif obj_name in ["hunt_y", "recovery_y", "teleport_y"] or obj_name.endswith("_y"):
                val = cy
                
            if val is not None:
                widget.setText(str(val))
                widget.editingFinished.emit()
                self.logger.log(f"[F2 자동 입력] 필드: {obj_name} -> 값: {val} 입력 완료", "WAYPOINT")
                winsound.Beep(1400, 200)
                self.settings_manager.save_settings_silently()
                return
                
        # Fallback
        self.waypoint_manager.hotkey_record_waypoint()
        
    def get_current_status_text(self):
        if not self.is_running:
            return "[대기 중]"
        if self.is_selling:
            return "[상점 판매 중]"
        if getattr(self, 'current_action_status', None):
            return f"[{self.current_action_status}]"
        if self.is_falling_recovering:
            return "[추락 복귀 중]"
        if self.is_bottom_hunting:
            return "[하단 사냥 중]"
        
        if self.hunt_mode == 0:
            if not self.is_recovering:
                return "[핑퐁사냥 중]"
            else:
                state_map = {
                    "moving_to_recovery_y": "회수층 이동 중",
                    "collecting": "아이템 회수 중",
                    "moving_to_return_start": "복귀지점 이동 중",
                    "executing_return_seq": "복귀동작 실행 중",
                    "verifying_return": "사냥층 복귀 확인 중"
                }
                return f"[{state_map.get(self.recovery_state, '회수모드 가동 중')}]"
        elif self.hunt_mode == 1:
            return "[제자리 사냥 중]"
        elif self.hunt_mode == 2:
            return f"[순환사냥 슬롯 {self.current_waypoint_idx + 1}]"
        return "[사냥 중]"
            
    def update_minimap_preview(self, i): 
        h, w, c = i.shape
        self.minimap_preview.setPixmap(QPixmap.fromImage(QImage(i.data, w, h, c*w, QImage.Format_RGB888).rgbSwapped()).scaled(self.minimap_preview.size(), Qt.IgnoreAspectRatio, Qt.SmoothTransformation))
        
    def update_shape_analytics(self, d): 
        h, w, c = d[0].shape
        self.shape_preview.setPixmap(QPixmap.fromImage(QImage(d[0].data, w, h, c*w, QImage.Format_RGB888).rgbSwapped()).scaled(self.shape_preview.size(), Qt.IgnoreAspectRatio, Qt.SmoothTransformation))
        if d[1]:
            self.shape_console.append(d[1])
            self.shape_console.verticalScrollBar().setValue(self.shape_console.verticalScrollBar().maximum())

    def update_waypoint_ui(self, idx):
        self.waypoint_manager.update_waypoint_ui(idx)

    def hunter_core(self):
        try:
            cur_dir, l_att, l_dash, l_del = 'right', 0, 0, time.time()
            self.last_char_seen_time = time.time()
            self.last_anti_afk_time = time.time()
            self.is_falling_recovering = False
            self.is_bottom_hunting = False
            
            # 핑퐁 회수 모드 변수 초기화
            try:
                self.use_recovery = self.chk_pingpong_recovery.isChecked()
            except Exception as e:
                self.use_recovery = False
                self.logger.log(f"[경고] use_recovery 초기화 실패: {str(e)}", "SYSTEM")

            try:
                self.recovery_interval = int(self.txt_pingpong_recovery_interval.text().strip() or "60")
            except Exception as e:
                self.recovery_interval = 60
                self.logger.log(f"[경고] recovery_interval 파싱 실패: {str(e)}", "SYSTEM")

            try:
                self.recovery_duration = int(self.txt_pingpong_recovery_duration.text().strip() or "10")
            except Exception as e:
                self.recovery_duration = 10
                self.logger.log(f"[경고] recovery_duration 파싱 실패: {str(e)}", "SYSTEM")
            
            # UI 설정값 파싱 (발판 스캔에 무관하게 항상 최우선 사용)
            try:
                self.hunt_y = int(self.txt_pingpong_hunt_y.text().split("Y:")[-1].replace(")", "").strip())
            except:
                try:
                    self.hunt_y = int(self.txt_pingpong_hunt_y.text().strip())
                except Exception as e:
                    self.hunt_y = 67
                    self.logger.log(f"[경고] hunt_y 파싱 실패: {str(e)}", "SYSTEM")

            try:
                self.recovery_y = int(self.txt_pingpong_recovery_y.text().split("Y:")[-1].replace(")", "").strip())
            except:
                try:
                    self.recovery_y = int(self.txt_pingpong_recovery_y.text().strip())
                except Exception as e:
                    self.recovery_y = 81
                    self.logger.log(f"[경고] recovery_y 파싱 실패: {str(e)}", "SYSTEM")
                    
            # 실시간 발판 스캔 (단순 로깅용, 설정값을 절대 덮어쓰지 않음)
            try:
                layers = self.minimap_detector.detect_floor_layers()
                if layers:
                    self.logger.log(f"[핑퐁회수 기동 스캔] 감지된 발판 레이어 Y 목록: {layers}", "WAYPOINT")
                else:
                    self.logger.log("[핑퐁회수 기동 스캔 실패] 발판 레이어 스캔 실패. 기존 등록 값으로 기동합니다.", "WAYPOINT")
            except Exception as e:
                self.logger.log(f"[경고] 발판 레이어 스캔 에러: {str(e)}", "WAYPOINT")

            # 핑퐁 기동 로그 출력
            if self.hunt_mode == 0:
                try:
                    self.logger.log(f"[핑퐁]\n사냥 시작\n설정된 사냥층 Y = {self.hunt_y}", "WAYPOINT")
                    self.logger.log(f"[핑퐁]\n설정 사냥층 Y = {self.txt_pingpong_hunt_y.text().strip()}", "WAYPOINT")
                    self.logger.log(f"[핑퐁]\n설정 회수층 Y = {self.txt_pingpong_recovery_y.text().strip()}", "WAYPOINT")
                    self.logger.log(f"[핑퐁]\n실행 사냥층 Y = {self.hunt_y}", "WAYPOINT")
                    self.logger.log(f"[핑퐁]\n오버레이 사냥층 Y = {self.hunt_y}", "WAYPOINT")
                except Exception as e:
                    self.logger.log(f"[경고] 핑퐁 기동 로그 출력 에러: {str(e)}", "WAYPOINT")

            try:
                self.return_x_min = int(self.txt_pingpong_return_x_min.text().strip() or "45")
            except Exception as e:
                self.return_x_min = 45
                self.logger.log(f"[경고] return_x_min 파싱 실패: {str(e)}", "SYSTEM")

            try:
                self.return_x_max = int(self.txt_pingpong_return_x_max.text().strip() or "50")
            except Exception as e:
                self.return_x_max = 50
                self.logger.log(f"[경고] return_x_max 파싱 실패: {str(e)}", "SYSTEM")

            try:
                self.rope_climb_time = float(self.txt_pingpong_rope_climb_time.text().strip() or "1.5")
            except Exception as e:
                self.rope_climb_time = 1.5
                self.logger.log(f"[경고] rope_climb_time 파싱 실패: {str(e)}", "SYSTEM")

            try:
                self.return_sequence = self.txt_pingpong_return_seq.text().strip()
            except Exception as e:
                self.return_sequence = "TELE_UP, ATTACK"
                self.logger.log(f"[경고] return_sequence 파싱 실패: {str(e)}", "SYSTEM")

            try:
                self.recovery_sequence = self.txt_pingpong_recovery_seq.text().strip()
            except Exception as e:
                self.recovery_sequence = ""
                self.logger.log(f"[경고] recovery_sequence 파싱 실패: {str(e)}", "SYSTEM")

            self.is_recovering = False
            self.recovery_state = "idle"
            self.last_buff1_time = 0.0
            self.last_buff2_time = 0.0
            self.last_recovery_teleport_time = 0.0
            
            # 핑퐁 사냥층 이탈 감지 및 자동 복귀 시스템용 변수 초기화
            self.is_falling_recovering = False
            self.falling_recovery_state = "idle"
            self.last_hunt_layer_ok_time = time.time()
            self.last_recovery_time = time.time()
            self.last_pet_buff_time = time.time()
            self.att_key_hold_start = time.time()
            self.has_printed_fall_tele_log = False
            self.has_printed_loop_entry_log = False
            
            self.is_first_v2_loop = True
            self.transit_moved = False
            if self.hunt_mode == 2:
                try:
                    valid_pts = [(idx, pt) for idx, pt in enumerate(self.waypoints) if pt["x_min"] != -1 and pt["y"] != -1]
                    wp_cur = self.waypoints[self.current_waypoint_idx] if len(self.waypoints) > self.current_waypoint_idx else {"x_min": -1, "x_max": -1, "y": -1}
                    tx_min, tx_max = wp_cur["x_min"], wp_cur["x_max"]
                    ty = wp_cur["y"]
                    self.logger.log(f"[V2 진입 검증] 모드: {self.hunt_mode}, 유효 waypoint 개수: {len(valid_pts)}, 현재 인덱스: {self.current_waypoint_idx}, 목표 범위: X({tx_min}~{tx_max}), Y({ty}), 현재 캐릭터: ({self.char_x}, {self.char_y})", "WAYPOINT")
                except Exception as e:
                    self.logger.log(f"[경고] V2 진입 검증 에러: {str(e)}", "WAYPOINT")
                    
        except Exception as e:
            self.logger.log(f"[시스템] 사냥 코어 변수 기동 중 심각한 오류 발생: {str(e)}", "SYSTEM")
            self.is_running = False
            self.start_btn.setEnabled(True)
            self.stop_btn.setEnabled(False)
            return
            
        try:
            while self.is_running:
                if self.is_selling or self.is_dragging_anti: 
                    self.set_key_state('left', False)
                    self.set_key_state('right', False)
                    try:
                        self.set_key_state(self.key_att_cb.currentText(), False)
                    except:
                        pass
                    self.is_pingpong_fixed_attacking = False
                    time.sleep(0.1)
                    continue
                
                # 공격키 59초 홀드 리셋 (매크로 차단 우회 및 입력 해제 방지)
                try:
                    att_key = self.key_att_cb.currentText()
                    if self.key_states.get(att_key, False):
                        hold_duration = time.time() - getattr(self, 'att_key_hold_start', 0.0)
                        if hold_duration >= 59.0:
                            try:
                                release_delay = float(self.txt_att_reset_delay.text().strip() or "0.15")
                            except:
                                release_delay = 0.15
                            self.logger.log(f"[공격키 리셋] 59초 경과 -> 물리적으로 키 뗐다({release_delay}초) 다시 누름 (우회)", "SYSTEM")
                            self.set_key_state(att_key, False)
                            time.sleep(release_delay)
                            self.set_key_state(att_key, True)
                            self.att_key_hold_start = time.time()
                except Exception as e:
                    self.logger.log(f"[공격키 리셋 에러] {str(e)}", "SYSTEM")
                
                with mss.mss() as sct:
                    cx, cy, img, mask = self.minimap_detector.get_player_coords(sct)
                    self.char_x, self.char_y = cx, cy
                    
                    if cx != -1 and cy != -1:
                        self.last_char_seen_time = time.time()
                        
                        # 핑퐁 사냥층 이탈 감지 및 자동 복귀 필터
                        if self.hunt_mode == 0 and not self.is_recovering and self.use_recovery:
                            if cx != -1 and cy != -1:
                                if abs(cy - self.hunt_y) <= 3:
                                    self.last_hunt_layer_ok_time = time.time()
                                else:
                                    if not self.is_falling_recovering:
                                        if time.time() - self.last_hunt_layer_ok_time > 1.5:
                                            self.logger.log("사냥층 이탈 감지", "PINGPONG")
                                            self.is_falling_recovering = True
                                            self.falling_recovery_state = "moving_to_return_start"
                                            self.has_printed_fall_tele_log = False
                                            self.logger.log("자동 복귀 시작", "PINGPONG")
                                            self.set_key_state('left', False)
                                            self.set_key_state('right', False)
                                            if getattr(self, 'is_pingpong_fixed_attacking', False):
                                                self.set_key_state(self.key_att_cb.currentText(), False)
                                                self.is_pingpong_fixed_attacking = False
                            else:
                                self.last_hunt_layer_ok_time = time.time()
                    else:
                        if self.hunt_mode == 0 and not self.is_recovering:
                            self.last_hunt_layer_ok_time = time.time()
                        if self.use_escape_lost and (time.time() - self.last_char_seen_time > self.lost_timeout_sec):
                            self.logger.log(f"[비상] {self.lost_timeout_sec}초 이상 캐릭터 좌표 인식 불가로 긴급 사냥을 중단합니다.", "SYSTEM")
                            self.signals.alert_signal.emit()
                            self.is_running = False
                            break
                    
                    # 감시(잠수) 모드 처리
                    if self.use_watch_mode:
                        self.set_key_state('left', False)
                        self.set_key_state('right', False)
                        if self.use_anti_town and (time.time() - self.last_anti_afk_time > 20):
                            self.logger.log("[감시 모드] 잠수 방지 및 마을 이동 방지 미세 동작 수행", "MOVEMENT")
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
                        
                    # 낚시사냥 모드 처리
                    if self.use_fishing_mode and self.fish_x != -1 and self.fish_y != -1:
                        if cx != -1 and cy != -1:
                            dx = cx - self.fish_x
                            dy = cy - self.fish_y
                            
                            if abs(dx) > 5 or abs(dy) > 5:
                                teleport_key = self.key_teleport_cb.currentText()
                                
                                if abs(dx) > 5:
                                    if abs(dx) >= 20:
                                        if dx > 0:
                                            self.logger.log(f"🎣 낚시 자리 이탈 (X 오차: {dx}px) -> 왼쪽 텔레포트 고속 이동", "MOVEMENT")
                                            self.set_key_state('right', False)
                                            self.set_key_state('left', True)
                                            time.sleep(0.05)
                                            self.press_key(teleport_key)
                                            time.sleep(0.15)
                                            self.set_key_state('left', False)
                                        else:
                                            self.logger.log(f"🎣 낚시 자리 이탈 (X 오차: {dx}px) -> 오른쪽 텔레포트 고속 이동", "MOVEMENT")
                                            self.set_key_state('left', False)
                                            self.set_key_state('right', True)
                                            time.sleep(0.05)
                                            self.press_key(teleport_key)
                                            time.sleep(0.15)
                                            self.set_key_state('right', False)
                                    else:
                                        self.logger.log(f"🎣 낚시 자리 이탈 (X 오차: {dx}px) -> X축 우선 걷기 정렬", "MOVEMENT")
                                        if dx > 0:
                                            self.set_key_state('right', False)
                                            self.set_key_state('left', True)
                                        else:
                                            self.set_key_state('left', False)
                                            self.set_key_state('right', True)
                                        time.sleep(0.05)
                                    continue
                                else:
                                    self.set_key_state('left', False)
                                    self.set_key_state('right', False)
                                    
                                    if dy > 5:
                                        self.logger.log(f"🎣 낚시 자리 Y축 이탈 (Y 오차: {dy}px) -> 텔레포트 상승", "MOVEMENT")
                                        self.set_key_state('up', True)
                                        time.sleep(0.08)
                                        self.press_key(teleport_key)
                                        time.sleep(0.2)
                                        self.set_key_state('up', False)
                                        time.sleep(0.1)
                                        continue
                                    elif dy < -5:
                                        self.logger.log(f"🎣 낚시 자리 Y축 이탈 (Y 오차: {-dy}px) -> 하단 낙하 기동", "MOVEMENT")
                                        self.set_key_state('down', True)
                                        time.sleep(0.08)
                                        self.press_key(self.key_jump_cb.currentText())
                                        time.sleep(0.02)
                                        self.set_key_state('down', False)
                                        time.sleep(0.2)
                                        continue

                    # 하단 사냥 후 자동 복귀 핸들링
                    if self.use_bottom_hunt:
                        if cy >= (self.bottom_y_threshold - 1):
                            if not self.is_bottom_hunting:
                                self.logger.log(f"하단 사냥 지역 진입 (Y: {cy}). {self.bottom_hunt_time_sec}초간 하단 사냥 후 복귀합니다.", "WAYPOINT")
                                self.is_bottom_hunting = True
                                self.bottom_hunt_start_time = time.time()
                            
                            if time.time() - self.bottom_hunt_start_time > self.bottom_hunt_time_sec:
                                self.logger.log("하단 사냥 제한 시간 도래. 텔레포트 복귀 동작 수행", "MOVEMENT")
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
                                self.logger.log("상단 라인 도달 확인. 일반 사냥으로 복귀합니다.", "WAYPOINT")
                                self.is_bottom_hunting = False

                    if self.hunt_mode == 0:
                        if not self.has_printed_loop_entry_log:
                            self.logger.log("메인 루프 진입", "PINGPONG")
                            self.logger.log(f"is_running={self.is_running}", "PINGPONG")
                            self.logger.log(f"attack_enabled={not self.is_recovering and not self.is_falling_recovering}", "PINGPONG")
                            self.logger.log(f"hunt_enabled={not self.is_falling_recovering}", "PINGPONG")
                            self.logger.log(f"is_collecting={self.is_recovering}", "PINGPONG")
                            
                            target_boundary = self.x_max if cur_dir == 'right' else self.x_min
                            target_name = "우측 경계" if cur_dir == 'right' else "좌측 경계"
                            self.logger.log(f"현재 목표 = {target_name}({target_boundary})", "PINGPONG")
                            
                            self.has_printed_loop_entry_log = True
                        # 사냥층 이탈 자동 복귀 상태 머신
                        if self.is_falling_recovering:
                            if cx == -1 or cy == -1:
                                time.sleep(0.04)
                                continue
                            
                            if self.falling_recovery_state == "moving_to_return_start":
                                # 실시간 텔포포인트 및 복귀 설정값 파싱
                                try:
                                    self.teleport_x = int(self.txt_pingpong_teleport_x.text().strip() or "-1")
                                except:
                                    self.teleport_x = -1
                                try:
                                    self.teleport_y = int(self.txt_pingpong_teleport_y.text().strip() or "-1")
                                except:
                                    self.teleport_y = -1
                                
                                target_y = self.teleport_y if (self.teleport_x != -1 and self.teleport_y != -1) else self.recovery_y
                                
                                # Y축 이탈시 정렬
                                if abs(cy - target_y) > 4:
                                    self.set_key_state('left', False)
                                    self.set_key_state('right', False)
                                    dy = cy - target_y
                                    self.movement_controller.perform_vertical_move(dy, "TELEPORT")
                                    time.sleep(0.25)
                                    continue
                                
                                if self.teleport_x != -1 and self.teleport_y != -1:
                                    # 1순위: 텔포포인트(T) 이동
                                    if not self.has_printed_fall_tele_log:
                                        self.logger.log("[핑퐁] 텔포포인트 이동", "MOVEMENT")
                                        self.has_printed_fall_tele_log = True
                                    self.logger.log(f"[핑퐁] 현재 위치 : X={cx} Y={cy}", "MOVEMENT")
                                    
                                    if abs(cx - self.teleport_x) <= 1:
                                        self.set_key_state('left', False)
                                        self.set_key_state('right', False)
                                        self.falling_recovery_state = "executing_return_seq"
                                    else:
                                        if cx < self.teleport_x:
                                            self.set_key_state('left', False)
                                            self.set_key_state('right', True)
                                            if self.teleport_x - cx > 25:
                                                self.press_key(self.key_teleport_cb.currentText())
                                                time.sleep(0.15)
                                            else:
                                                time.sleep(0.05)
                                        else:
                                            self.set_key_state('right', False)
                                            self.set_key_state('left', True)
                                            if cx - self.teleport_x > 25:
                                                self.press_key(self.key_teleport_cb.currentText())
                                                time.sleep(0.15)
                                            else:
                                                time.sleep(0.05)
                                else:
                                    # 2순위: 복귀 X범위 이동
                                    if not self.has_printed_fall_tele_log:
                                        self.logger.log("[핑퐁] 텔포포인트 이동", "MOVEMENT")
                                        self.has_printed_fall_tele_log = True
                                    self.logger.log(f"[핑퐁] 현재 위치 : X={cx} Y={cy}", "MOVEMENT")
                                    
                                    if self.return_x_min <= cx <= self.return_x_max:
                                        self.set_key_state('left', False)
                                        self.set_key_state('right', False)
                                        self.falling_recovery_state = "executing_return_seq"
                                    else:
                                        if cx < self.return_x_min:
                                            self.set_key_state('left', False)
                                            self.set_key_state('right', True)
                                            if self.return_x_min - cx > 25:
                                                self.press_key(self.key_teleport_cb.currentText())
                                                time.sleep(0.15)
                                            else:
                                                time.sleep(0.05)
                                        else:
                                            self.set_key_state('right', False)
                                            self.set_key_state('left', True)
                                            if cx - self.return_x_max > 25:
                                                self.press_key(self.key_teleport_cb.currentText())
                                                time.sleep(0.15)
                                            else:
                                                time.sleep(0.05)
                                continue
                                
                            elif self.falling_recovery_state == "executing_return_seq":
                                self.logger.log("[핑퐁] 복귀 시퀀스 실행", "MOVEMENT")
                                seq_str = self.return_sequence.strip()
                                if seq_str:
                                    actions = [a.strip() for a in seq_str.split(",") if a.strip()]
                                    total_acts = len(actions)
                                    for idx, act in enumerate(actions):
                                        if not self.is_running or self.is_selling or self.is_dragging_anti:
                                            break
                                        self.logger.log(f"[핑퐁] 복귀 시퀀스 실행: {act} ({idx+1}/{total_acts})", "MOVEMENT")
                                        
                                        # 도우미 함수 호출로 연계 처리
                                        self.execute_sequence_action(act)
                                        
                                        # 다음 동작이 공격 스킬이거나 연계 공격인 경우 딜레이를 최소화(0.05초)하여 즉시 시전 연계
                                        next_is_attack = False
                                        if idx + 1 < total_acts:
                                            next_act = actions[idx+1].strip()
                                            if next_act == "ATTACK" or next_act.lower() == "end" or next_act.lower() == self.key_att_cb.currentText().lower() or "+" in next_act:
                                                next_is_attack = True
                                                
                                        if next_is_attack:
                                            time.sleep(0.05)
                                        else:
                                            time.sleep(1.0)
                                self.falling_recovery_state = "verifying_return"
                                continue
                                
                            elif self.falling_recovery_state == "verifying_return":
                                self.logger.log("[핑퐁] 사냥층 복귀 확인", "MOVEMENT")
                                if abs(cy - self.hunt_y) <= 3:
                                    self.logger.log("[핑퐁] 핑퐁사냥 재개", "WAYPOINT")
                                    self.is_falling_recovering = False
                                    self.last_hunt_layer_ok_time = time.time()
                                    self.falling_recovery_state = "idle"
                                else:
                                    self.falling_recovery_state = "moving_to_return_start"
                                    self.has_printed_fall_tele_log = False
                                    time.sleep(0.5)
                                continue

                        # 회수 모드 활성화 시 주기 체크 및 상태 머신 실행
                        if self.use_recovery:
                            # 넉백 불시착 감지: 회수 주기가 아닌데 강제로 회수층에 낙하한 경우, 회수 단계를 스킵하고 즉시 복귀 시퀀스 작동
                            if not self.is_recovering and not self.is_falling_recovering:
                                if cy != -1 and abs(cy - self.recovery_y) <= 3:
                                    self.logger.log("[넉백 감지] 회수 주기 도달 전 회수층 추락 감지 -> 즉시 사냥층 복귀 시퀀스 작동", "SYSTEM")
                                    self.is_recovering = True
                                    self.recovery_state = "moving_to_return_start"
                                    self.set_key_state('left', False)
                                    self.set_key_state('right', False)
                                    try:
                                        self.set_key_state(self.key_att_cb.currentText(), False)
                                    except:
                                        pass
                                    self.is_pingpong_fixed_attacking = False
                                    continue

                            if not self.is_recovering and (time.time() - self.last_recovery_time > self.recovery_interval):
                                self.is_recovering = True
                                self.recovery_state = "moving_to_recovery_y"
                                self.logger.log(f"[핑퐁회수] 회수 주기 도달 -> 회수층(Y: {self.recovery_y}) 이동 시작", "MOVEMENT")
                                self.set_key_state('left', False)
                                self.set_key_state('right', False)
                                att_key = self.key_att_cb.currentText()
                                self.set_key_state(att_key, False)
                                self.is_pingpong_fixed_attacking = False
                                
                            if self.is_recovering:
                                if cx == -1 or cy == -1:
                                    time.sleep(0.04)
                                    continue
                                    
                                if self.recovery_state == "moving_to_recovery_y":
                                    seq_str = self.recovery_sequence.strip()
                                    if seq_str:
                                        actions = [a.strip() for a in seq_str.split(",") if a.strip()]
                                        self.logger.log(f"[핑퐁회수] 회수층 이동 시퀀스 실행: {actions}", "MOVEMENT")
                                        total_acts = len(actions)
                                        for idx, act in enumerate(actions):
                                            if not self.is_running or self.is_selling or self.is_dragging_anti:
                                                break
                                            self.logger.log(f"[핑퐁회수]\n회수 시퀀스 실행\n{act} ({idx+1}/{total_acts})", "MOVEMENT")
                                            self.execute_sequence_action(act)
                                            
                                            next_is_attack = False
                                            if idx + 1 < total_acts:
                                                next_act = actions[idx+1].strip()
                                                if next_act == "ATTACK" or next_act.lower() == "end" or next_act.lower() == self.key_att_cb.currentText().lower() or "+" in next_act:
                                                    next_is_attack = True
                                                    
                                            if next_is_attack:
                                                time.sleep(0.05)
                                            else:
                                                time.sleep(1.0)
                                                
                                        self.recovery_state = "collecting"
                                        self.recovery_start_time = time.time()
                                        self.logger.log(f"[핑퐁회수] 회수층 도착 (시퀀스 완료) -> {self.recovery_duration}초간 아이템 회수 시작", "MOVEMENT")
                                        self.set_key_state('left', False)
                                        self.set_key_state('right', False)
                                    else:
                                        if abs(cy - self.recovery_y) <= 3:
                                            self.recovery_state = "collecting"
                                            self.recovery_start_time = time.time()
                                            self.logger.log(f"[핑퐁회수] 회수층 도착 -> {self.recovery_duration}초간 아이템 회수 시작", "MOVEMENT")
                                            self.set_key_state('left', False)
                                            self.set_key_state('right', False)
                                        else:
                                            dy = cy - self.recovery_y
                                            self.movement_controller.perform_vertical_move(dy, "TELEPORT")
                                            time.sleep(0.2)
                                    continue
                                    
                                elif self.recovery_state == "collecting":
                                    if time.time() - self.recovery_start_time > self.recovery_duration:
                                        self.recovery_state = "moving_to_return_start"
                                        self.set_key_state('left', False)
                                        self.set_key_state('right', False)
                                        
                                        # 텔포포인트 실시간 파싱
                                        try:
                                            self.teleport_x = int(self.txt_pingpong_teleport_x.text().strip() or "-1")
                                        except:
                                            self.teleport_x = -1
                                        try:
                                            self.teleport_y = int(self.txt_pingpong_teleport_y.text().strip() or "-1")
                                        except:
                                            self.teleport_y = -1
                                            
                                        if self.teleport_x != -1 and self.teleport_y != -1:
                                            self.logger.log(f"[핑퐁회수]\n텔포포인트 설정 확인\nX={self.teleport_x} Y={self.teleport_y}", "MOVEMENT")
                                            self.logger.log("[핑퐁회수]\n텔포포인트 이동 시작", "MOVEMENT")
                                        else:
                                            self.logger.log(f"[핑퐁회수] 회수 시간 만료 -> 복귀 시작 범위(X: {self.return_x_min}~{self.return_x_max}, Y: {self.recovery_y}) 이동 시작", "MOVEMENT")
                                    else:
                                        reached_boundary = False
                                        if cx >= (self.x_max - 1) and cur_dir == 'right':
                                            self.set_key_state('right', False)
                                            cur_dir = 'left'
                                            reached_boundary = True
                                        elif cx <= (self.x_min + 1) and cur_dir == 'left':
                                            self.set_key_state('left', False)
                                            cur_dir = 'right'
                                            reached_boundary = True
                                        self.set_key_state(cur_dir, True)
                                        
                                        # 핑퐁 회수 시 텔레포트 적용
                                        now_ms = time.time() * 1000
                                        if now_ms - getattr(self, 'last_recovery_teleport_time', 0.0) > self.dash_delay_ms:
                                            self.press_key(self.key_teleport_cb.currentText())
                                            self.last_recovery_teleport_time = now_ms
                                            
                                        # 회수모드 진입 시 공격 OFF (아이템 회수에만 집중)
                                        att_key = self.key_att_cb.currentText()
                                        self.set_key_state(att_key, False)
                                        self.is_pingpong_fixed_attacking = False
                                        time.sleep(0.04)
                                    continue
                                    
                                elif self.recovery_state == "moving_to_return_start":
                                    # 실시간 좌표 파싱 보증
                                    try:
                                        self.teleport_x = int(self.txt_pingpong_teleport_x.text().strip() or "-1")
                                    except:
                                        self.teleport_x = -1
                                    try:
                                        self.teleport_y = int(self.txt_pingpong_teleport_y.text().strip() or "-1")
                                    except:
                                        self.teleport_y = -1

                                    target_y = self.teleport_y if (self.teleport_x != -1 and self.teleport_y != -1) else self.recovery_y
                                    
                                    if abs(cy - target_y) > 4:
                                        self.logger.log(f"[핑퐁회수] Y층 이탈 감지 (현재 Y: {cy}, 목표 Y: {target_y}) -> 재정렬 시도", "MOVEMENT")
                                        self.set_key_state('left', False)
                                        self.set_key_state('right', False)
                                        dy = cy - target_y
                                        self.movement_controller.perform_vertical_move(dy, "TELEPORT")
                                        time.sleep(0.25)
                                        continue
                                        
                                    if self.teleport_x != -1 and self.teleport_y != -1:
                                        # 1순위: 텔포포인트(T) 이동
                                        self.logger.log(f"[핑퐁회수]\n현재 위치 : X={cx} Y={cy}", "MOVEMENT")
                                        if abs(cx - self.teleport_x) <= 1:
                                            self.set_key_state('left', False)
                                            self.set_key_state('right', False)
                                            self.recovery_state = "executing_return_seq"
                                            self.logger.log("[핑퐁회수]\n텔포포인트 도착 완료", "MOVEMENT")
                                        else:
                                            if cx < self.teleport_x:
                                                self.set_key_state('left', False)
                                                self.set_key_state('right', True)
                                                if self.teleport_x - cx > 25:
                                                    self.press_key(self.key_teleport_cb.currentText())
                                                    time.sleep(0.15)
                                                else:
                                                    time.sleep(0.05)
                                            else:
                                                self.set_key_state('right', False)
                                                self.set_key_state('left', True)
                                                if cx - self.teleport_x > 25:
                                                    self.press_key(self.key_teleport_cb.currentText())
                                                    time.sleep(0.15)
                                                else:
                                                    time.sleep(0.05)
                                    else:
                                        # 2순위: 복귀 X범위 이동
                                        if self.return_x_min <= cx <= self.return_x_max:
                                            self.set_key_state('left', False)
                                            self.set_key_state('right', False)
                                            self.recovery_state = "executing_return_seq"
                                            self.logger.log(f"[핑퐁회수] 복귀 시작 범위 진입 완료(X: {cx}, Y: {cy}) -> 복귀 동작 시퀀스 실행", "MOVEMENT")
                                        else:
                                            if cx < self.return_x_min:
                                                self.set_key_state('left', False)
                                                self.set_key_state('right', True)
                                                if self.return_x_min - cx > 25:
                                                    self.press_key(self.key_teleport_cb.currentText())
                                                    time.sleep(0.15)
                                                else:
                                                    time.sleep(0.05)
                                            else:
                                                self.set_key_state('right', False)
                                                self.set_key_state('left', True)
                                                if cx - self.return_x_max > 25:
                                                    self.press_key(self.key_teleport_cb.currentText())
                                                    time.sleep(0.15)
                                                else:
                                                    time.sleep(0.05)
                                    continue
                                    
                                elif self.recovery_state == "executing_return_seq":
                                    seq_str = self.return_sequence.strip()
                                    if seq_str:
                                        actions = [a.strip() for a in seq_str.split(",") if a.strip()]
                                        self.logger.log(f"[핑퐁회수] 동작 재생 시퀀스 실행: {actions}", "MOVEMENT")
                                        total_acts = len(actions)
                                        for idx, act in enumerate(actions):
                                            if not self.is_running or self.is_selling or self.is_dragging_anti:
                                                break
                                            self.logger.log(f"[핑퐁회수]\n복귀 시퀀스 실행\n{act} ({idx+1}/{total_acts})", "MOVEMENT")
                                            
                                            # 도우미 함수 호출로 연계 처리
                                            self.execute_sequence_action(act)
                                            
                                            # 다음 동작이 공격 스킬이거나 연계 공격인 경우 딜레이를 최소화(0.05초)하여 즉시 시전 연계
                                            next_is_attack = False
                                            if idx + 1 < total_acts:
                                                next_act = actions[idx+1].strip()
                                                if next_act == "ATTACK" or next_act.lower() == "end" or next_act.lower() == self.key_att_cb.currentText().lower() or "+" in next_act:
                                                    next_is_attack = True
                                                    
                                            if next_is_attack:
                                                time.sleep(0.05)
                                            else:
                                                time.sleep(1.0)
                                    self.recovery_state = "verifying_return"
                                    continue
                                    
                                elif self.recovery_state == "verifying_return":
                                    if abs(cy - self.hunt_y) <= 3:
                                        self.logger.log(f"[핑퐁회수] 사냥층 복귀 확인 완료 (현재 Y: {cy}, 사냥층 Y: {self.hunt_y}) -> 핑퐁사냥 재개", "WAYPOINT")
                                        self.is_recovering = False
                                        self.last_recovery_time = time.time()
                                        self.recovery_state = "idle"
                                    else:
                                        self.logger.log(f"[핑퐁회수 경고] 사냥층 복귀 실패 (현재 Y: {cy}, 사냥층 Y: {self.hunt_y}) -> 회수층으로 재이동 후 시퀀스 재시도", "WAYPOINT")
                                        self.recovery_state = "moving_to_recovery_y"
                                        time.sleep(0.5)
                                    continue
                        
                        # 일반 핑퐁사냥 동작
                        if getattr(self, 'chk_pingpong_fixed', None) and self.chk_pingpong_fixed.isChecked():
                            att_key = self.key_att_cb.currentText()
                            
                            # Y 좌표 인지 기반 공격 방지 로직: 현재 회수층 부근이거나 사냥층을 벗어난 상태인 경우 스킬 사용 불가능하게 해제 (회수 모드 사용 시에만 유효)
                            is_at_hunt_layer = (cy == -1 or abs(cy - self.hunt_y) <= 3) if self.use_recovery else True
                            is_at_recovery_layer = (cy != -1 and abs(cy - self.recovery_y) <= 3) if self.use_recovery else False
                            
                            if not is_at_hunt_layer or is_at_recovery_layer:
                                self.set_key_state(att_key, False)
                                self.is_pingpong_fixed_attacking = False
                                now_sec = time.time()
                                if now_sec - getattr(self, 'last_pingpong_diag_log_time', 0.0) >= 1.0:
                                    self.last_pingpong_diag_log_time = now_sec
                                    self.logger.log(f"제자리 고정 사냥 예외 - 사냥층 이탈 또는 회수층 진입 감지(현재 Y: {cy}, 사냥층 Y: {self.hunt_y}, 회수층 Y: {self.recovery_y}) 공격 일시 중지", "PINGPONG")
                            else:
                                self.set_key_state('left', False)
                                self.set_key_state('right', False)
                                self.set_key_state(att_key, True)
                                self.is_pingpong_fixed_attacking = True
                                
                                now_sec = time.time()
                                if now_sec - getattr(self, 'last_pingpong_diag_log_time', 0.0) >= 1.0:
                                    self.last_pingpong_diag_log_time = now_sec
                                    self.logger.log("제자리 고정 사냥 중 - 공격 키 누름 유지 (아이템 회수 시에만 이동)", "PINGPONG")
                        else:
                            reached_boundary = False
                            if cx >= (self.x_max - 1) and cur_dir == 'right':
                                self.set_key_state('right', False)
                                cur_dir = 'left'
                                reached_boundary = True
                                self.logger.log(f"현재 목표 = 좌측 경계({self.x_min})", "PINGPONG")
                            elif cx <= (self.x_min + 1) and cur_dir == 'left':
                                self.set_key_state('left', False)
                                cur_dir = 'right'
                                reached_boundary = True
                                self.logger.log(f"현재 목표 = 우측 경계({self.x_max})", "PINGPONG")
                                
                            # 핑퐁 이동 및 판단 진단 로그 (1초 주기 스로틀링)
                            now_sec = time.time()
                            if now_sec - getattr(self, 'last_pingpong_diag_log_time', 0.0) >= 1.0:
                                self.last_pingpong_diag_log_time = now_sec
                                target_x = self.x_max if cur_dir == 'right' else self.x_min
                                target_name = "우측 경계" if cur_dir == 'right' else "좌측 경계"
                                dist = abs(cx - target_x) if cx != -1 else 999
                                need_move = (cx != -1)
                                
                                self.logger.log(f"{target_name} 이동 시작\n현재 X={cx}\n목표 X={target_x}", "PINGPONG")
                                self.logger.log(f"현재 X={cx}\n\n목표 X={target_x}\n\n거리={dist}\n\n이동 필요={need_move}", "PINGPONG")

                            # 복층 순환사냥 기동
                            if reached_boundary and self.use_multifloor_hunt and self.multifloor_up_count > 0:
                                self.logger.log(f"복층 이동 기동: 방향전환 시 텔레포트 상승 {self.multifloor_up_count}회 수행", "MOVEMENT")
                                teleport_key = self.key_teleport_cb.currentText()
                                self.set_key_state('up', True)
                                time.sleep(0.08)
                                for i in range(self.multifloor_up_count):
                                    if not self.is_running or self.is_selling or self.is_dragging_anti:
                                        break
                                    self.current_action_status = f"텔포상 {i+1}/{self.multifloor_up_count}"
                                    self.press_key(teleport_key)
                                    time.sleep(0.25)
                                self.current_action_status = None
                                self.set_key_state('up', False)
                                time.sleep(0.15)
                                
                            # 가고자 하는 방향의 반대 방향 키 강제 해제 (충돌 차단)
                            self.set_key_state('left' if cur_dir == 'right' else 'right', False)
                            self.set_key_state(cur_dir, True)

                    elif self.hunt_mode == 2:
                        valid_pts = [(idx, pt) for idx, pt in enumerate(self.waypoints) if pt["x_min"] != -1 and pt["y"] != -1]

                        
                        if not valid_pts:
                            self.logger.log("순환사냥 V2 경고: 기록된 유효한 좌표가 없습니다. 핑퐁사냥으로 사냥합니다.", "WAYPOINT")
                            self.hunt_mode = 0
                            time.sleep(0.2)
                            continue
  
                        valid_indices = [v[0] for v in valid_pts]
  
                        if self.is_first_v2_loop:
                            if cx != -1 and cy != -1:
                                min_dist = float('inf')
                                closest_idx = valid_indices[0]
                                for idx, pt in valid_pts:
                                    c_wp_x = (pt["x_min"] + pt["x_max"]) / 2
                                    c_wp_y = pt["y"]
                                    dist = ((cx - c_wp_x)**2 + (cy - c_wp_y)**2)**0.5
                                    if dist < min_dist:
                                        min_dist = dist
                                        closest_idx = idx
                                self.current_waypoint_idx = closest_idx
                                self.logger.log(f"[V2 최초 시작점] 캐릭터 위치({cx}, {cy})에서 가장 가까운 슬롯 {closest_idx+1} 지정 (거리: {min_dist:.2f})", "WAYPOINT")
                            else:
                                self.current_waypoint_idx = valid_indices[0]
                                self.logger.log(f"[V2 최초 시작점] 캐릭터 위치 인식 불가능 -> 첫 번째 슬롯 {self.current_waypoint_idx+1} 시작", "WAYPOINT")
                            self.is_first_v2_loop = False
                            self.transit_moved = False
  
                        target_idx = self.current_waypoint_idx
                        if target_idx not in valid_indices:
                            target_idx = valid_indices[0]
                            self.current_waypoint_idx = target_idx
                            self.logger.log(f"[V2 고정순환] 오름차순 목적지 재설정 -> 슬롯 {target_idx+1} (X범위: {self.waypoints[target_idx]['x_min']}~{self.waypoints[target_idx]['x_max']}, Y: {self.waypoints[target_idx]['y']})", "WAYPOINT")
  
                        wp = self.waypoints[target_idx]
                        x_min, x_max = wp["x_min"], wp["x_max"]
                        target_y = wp["y"]
                        
                        # X축/Y축 오차 계산 (즉시 안착 여부 우선 검증을 위해 최상단 이동)
                        if cx < x_min:
                            dx = cx - x_min
                        elif cx > x_max:
                            dx = cx - x_max
                        else:
                            dx = 0
                            
                        # Y축 오차 계산 (V3: 허용 오차를 +-8로 대폭 완화)
                        if abs(cy - target_y) <= 8:
                            dy = 0
                        else:
                            dy = cy - target_y
                            
                        # 도착 판정: X범위 진입 최우선 + 완화된 Y오차 (즉시 안착 여부 우선 확인)
                        is_reached = (dx == 0 and dy == 0)
                        
                        if is_reached:
                            # 즉시 안착 처리 및 이동 입력 해제
                            self.set_key_state('left', False)
                            self.set_key_state('right', False)
                            self.set_key_state('up', False)
                            self.set_key_state('down', False)
                            self.is_moving = False
                            self.is_teleporting = False
                            time.sleep(0.05)
                            
                            stay_sec = wp.get("stay_time", 2.0)
                            self.logger.log(f"순환 좌표 슬롯 {target_idx+1} 안착 완료 (즉시 안착) -> 체류 사냥 시작 ({stay_sec}초)", "WAYPOINT")
                            
                            l_att = self.combat_controller.execute_stay_combat(stay_sec, l_att)
                            
                            self.landing_start_time = None
                            self.fall_count = 0
                            self.last_completed_waypoint_idx = target_idx
                            self.transit_moved = False
                            # 안착 완료 및 체류 종료 후, 다음 슬롯 시작 시 미끄러짐/떨림을 막기 위한 0.8초 잠금 타이머 기록
                            self.landing_lock_time = time.time()
                            
                            try:
                                curr_pos = valid_indices.index(target_idx)
                                next_pos = (curr_pos + 1) % len(valid_indices)
                                self.current_waypoint_idx = valid_indices[next_pos]
                            except ValueError:
                                self.current_waypoint_idx = valid_indices[0]
                                
                            self.logger.log(f"다음 슬롯으로 전환 -> 슬롯 {self.current_waypoint_idx+1}", "WAYPOINT")
                            time.sleep(0.1)
                            continue

                        # 아직 도착하지 않았고, 체류 종료 후 이동을 시작하는 시점인 경우:
                        # 0.8초 동안 모든 입력 잠금 처리 (DX/DY=0 상태로 사냥이 끝난 후 미끄러짐 방지)
                        elapsed_lock = time.time() - getattr(self, 'landing_lock_time', 0.0)
                        if elapsed_lock < 0.8:
                            self.set_key_state('left', False)
                            self.set_key_state('right', False)
                            self.set_key_state('up', False)
                            self.set_key_state('down', False)
                            time.sleep(0.05)
                            continue

                        # 1. 전환 이동방식 실행 (체류 종료 후 최초 1회, 잠금 해제 이후 실행)
                        if not getattr(self, 'transit_moved', False):
                            if hasattr(self, 'last_completed_waypoint_idx') and self.last_completed_waypoint_idx != -1:
                                move_mode = self.waypoints[self.last_completed_waypoint_idx].get("move_type", "TELE_LEFT")
                            else:
                                move_mode = wp.get("move_type", "TELE_LEFT")
                                
                            slot_from = getattr(self, 'last_completed_waypoint_idx', -1) + 1
                            slot_to = target_idx + 1
                            self.logger.log(f"[슬롯 이동] slot_from={slot_from}, slot_to={slot_to}, move_type={move_mode}", "WAYPOINT")
                            self.movement_controller.execute_move_action(move_mode)
                            self.transit_moved = True
                            self.transit_time = time.time()
                            time.sleep(0.15)
                            continue

                        self.logger.log(f"[V3 목표 추적] 슬롯 {target_idx+1} -> 범위: X({x_min}~{x_max}), Y({target_y}), 캐릭터: ({cx}, {cy}), 오차: DX={dx}, DY={dy}", "WAYPOINT")

                        # 아직 도착하지 않은 경우:
                        # 2. 이동 로직 잠금 상태 검토 (0.8초간 보조 이동 보정 개입 차단)
                        elapsed_transit = time.time() - getattr(self, 'transit_time', 0.0)
                        if elapsed_transit < 0.8:
                            time.sleep(0.05)
                            continue

                        # 3. 실패 시 보조 이동 (보정)
                        if hasattr(self, 'last_completed_waypoint_idx') and self.last_completed_waypoint_idx != -1:
                            move_mode = self.waypoints[self.last_completed_waypoint_idx].get("move_type", "TELE_LEFT")
                        else:
                            move_mode = wp.get("move_type", "TELE_LEFT")
                        
                        def get_base_move_mode(m):
                            if m in ["TELE_LEFT", "TELE_RIGHT", "TELE_UP"]:
                                return "TELEPORT"
                            elif m in ["JUMP_LEFT", "JUMP_RIGHT", "JUMP_UP"]:
                                return "JUMP"
                            elif m in ["WALK_LEFT", "WALK_RIGHT"]:
                                return "WALK"
                            elif m in ["DROP"]:
                                return "DROP"
                            return m
                        
                        base_move_mode = get_base_move_mode(move_mode)

                        # Y축 보정 우선
                        if dy != 0:
                            self.set_key_state('left', False)
                            self.set_key_state('right', False)
                            self.is_moving = False
                            self.last_char_y = cy
                            self.movement_controller.perform_vertical_move(dy, base_move_mode)
                            time.sleep(0.15)
                            _, check_cy, _, _ = self.minimap_detector.get_player_coords(sct)
                            if check_cy != -1 and abs(check_cy - self.last_char_y) <= 2:
                                self.fall_count += 1
                            else:
                                self.fall_count = 0
                        else:
                            # X축 보정
                            self.movement_controller.perform_horizontal_move(dx, base_move_mode)
                            continue
  
                        if self.fall_count >= 4:
                            self.logger.log(f"[수직 복귀 실패 감지] 연속 {self.fall_count}회 수직 이동 실패. 비상 탈출 실행.", "MOVEMENT")
                            self.fall_count = 0
                            
                            escape_dir = 'left' if random.choice([True, False]) else 'right'
                            self.set_key_state(escape_dir, True)
                            time.sleep(0.3)
                            self.set_key_state(escape_dir, False)
                            
                            try:
                                curr_pos = valid_indices.index(target_idx)
                                next_pos = (curr_pos + 1) % len(valid_indices)
                                self.current_waypoint_idx = valid_indices[next_pos]
                            except ValueError:
                                self.current_waypoint_idx = valid_indices[0]
                                
                            self.landing_start_time = None
                            self.transit_moved = False
                            self.logger.log(f"[V2 고정순환] 수직 이동 실패로 인한 다음 목적지 강제 갱신 -> 슬롯 {self.current_waypoint_idx+1}", "WAYPOINT")
                            continue
              # 하위 호환 및 기본 추론 이동 (구버전 데이터용)
                        if dx != 0:
                            self.movement_controller.perform_horizontal_move(dx, move_mode)
                            continue
                        else:
                            self.set_key_state('left', False)
                            self.set_key_state('right', False)
                            self.is_moving = False
                            self.last_char_y = cy
                            self.movement_controller.perform_vertical_move(dy, move_mode)
                            time.sleep(0.15)
                            _, check_cy, _, _ = self.minimap_detector.get_player_coords(sct)
                            if check_cy != -1 and abs(check_cy - self.last_char_y) <= 2:
                                self.fall_count += 1
                            else:
                                self.fall_count = 0
  
                        if self.fall_count >= 4:
                            self.logger.log(f"[수직 복귀 실패 감지] 연속 {self.fall_count}회 수직 이동 실패. 비상 탈출 실행.", "MOVEMENT")
                            self.fall_count = 0
                            
                            escape_dir = 'left' if random.choice([True, False]) else 'right'
                            self.set_key_state(escape_dir, True)
                            time.sleep(0.3)
                            self.set_key_state(escape_dir, False)
                            
                            try:
                                curr_pos = valid_indices.index(target_idx)
                                next_pos = (curr_pos + 1) % len(valid_indices)
                                self.current_waypoint_idx = valid_indices[next_pos]
                            except ValueError:
                                self.current_waypoint_idx = valid_indices[0]
                                
                            self.landing_start_time = None
                            self.logger.log(f"[V2 고정순환] 수직 이동 실패로 인한 다음 목적지 강제 갱신 -> 슬롯 {self.current_waypoint_idx+1}", "WAYPOINT")
                            continue
  
                    # 핑퐁/제자리 사냥 공격/딜레이 처리
                    if not self.is_recovering and not self.is_falling_recovering:
                        now = time.time()*1000
                        l_att, l_dash = self.combat_controller.execute_normal_combat(now, l_att, l_dash)
                    
                    # 펫 버프 처리
                    self.last_pet_buff_time = self.combat_controller.execute_pet_buff(self.last_pet_buff_time)
                    
                    # 독립 버프 자동 시전 제어
                    if not self.is_recovering and not self.is_falling_recovering:
                        # 버프 1
                        if self.chk_buff1_use.isChecked():
                            try:
                                b1_int = int(self.txt_buff1_int.text().strip() or "180")
                                b1_hold = float(self.txt_buff1_hold.text().strip() or "0.5")
                                b1_key = self.cb_buff1_key.currentText()
                                if time.time() - getattr(self, 'last_buff1_time', 0.0) > b1_int:
                                    self.logger.log(f"[버프1] 버프 시전 (키: {b1_key}, {b1_hold}초 홀드)", "SYSTEM")
                                    self.set_key_state('left', False)
                                    self.set_key_state('right', False)
                                    time.sleep(0.05)
                                    self.set_key_state(b1_key, True)
                                    time.sleep(b1_hold)
                                    self.set_key_state(b1_key, False)
                                    self.last_buff1_time = time.time()
                                    time.sleep(0.1)
                            except Exception as e:
                                self.logger.log(f"[버프1 에러] {str(e)}", "SYSTEM")
                                
                        # 버프 2
                        if self.chk_buff2_use.isChecked():
                            try:
                                b2_int = int(self.txt_buff2_int.text().strip() or "200")
                                b2_hold = float(self.txt_buff2_hold.text().strip() or "0.5")
                                b2_key = self.cb_buff2_key.currentText()
                                if time.time() - getattr(self, 'last_buff2_time', 0.0) > b2_int:
                                    self.logger.log(f"[버프2] 버프 시전 (키: {b2_key}, {b2_hold}초 홀드)", "SYSTEM")
                                    self.set_key_state('left', False)
                                    self.set_key_state('right', False)
                                    time.sleep(0.05)
                                    self.set_key_state(b2_key, True)
                                    time.sleep(b2_hold)
                                    self.set_key_state(b2_key, False)
                                    self.last_buff2_time = time.time()
                                    time.sleep(0.1)
                            except Exception as e:
                                self.logger.log(f"[버프2 에러] {str(e)}", "SYSTEM")
                    
                time.sleep(0.04)
        except Exception as e:
            self.logger.log(f"[시스템] 사냥 루프 실행 중 심각한 오류 발생: {str(e)}", "SYSTEM")
            import traceback
            traceback.print_exc()
        finally: 
            self.set_key_state('left', False)
            self.set_key_state('right', False)
            self.set_key_state('up', False)
            try:
                self.set_key_state(self.key_att_cb.currentText(), False)
            except:
                pass
            self.is_pingpong_fixed_attacking = False
            self.is_running = False

    def monitor_loop(self):
        with mss.mss() as sct:
            while not self.stop_threads:
                if self.reg_w > 5:
                    try:
                        cx, cy, img, mask = self.minimap_detector.get_player_coords(sct)
                        if img is None or img.size == 0:
                            time.sleep(0.5)
                            continue
                            
                        p_img = img.copy()
                        
                        # 1) 사냥구간 반투명 녹색 채우기
                        overlay = p_img.copy()
                        cv2.rectangle(overlay, (self.x_min, 0), (self.x_max, self.reg_h), (94, 197, 34), -1)
                        if self.x_max > self.x_min and self.x_min >= 0 and self.x_max <= self.reg_w:
                            p_img[0:self.reg_h, self.x_min:self.x_max] = cv2.addWeighted(
                                overlay[0:self.reg_h, self.x_min:self.x_max], 0.15, 
                                p_img[0:self.reg_h, self.x_min:self.x_max], 0.85, 0
                            )
                            
                        # 2) 회수구간 반투명 노란색 채우기
                        if self.chk_pingpong_recovery.isChecked() and hasattr(self, 'recovery_y') and self.recovery_y != -1:
                            y_min_rec = max(0, self.recovery_y - 3)
                            y_max_rec = min(self.reg_h, self.recovery_y + 3)
                            if y_max_rec > y_min_rec:
                                overlay_y = p_img.copy()
                                cv2.rectangle(overlay_y, (0, y_min_rec), (self.reg_w, y_max_rec), (0, 234, 255), -1)
                                p_img[y_min_rec:y_max_rec, 0:self.reg_w] = cv2.addWeighted(
                                    overlay_y[y_min_rec:y_max_rec, 0:self.reg_w], 0.25, 
                                    p_img[y_min_rec:y_max_rec, 0:self.reg_w], 0.75, 0
                                )
                                
                        # 3) 디버그 눈금 격자 (Grid Ruler) 그리기 - 디버그 모드 시 적용
                        if getattr(self, 'use_debug_mode', False):
                            # 세로 격자선 및 라벨 (X축 눈금자)
                            for x in range(20, self.reg_w, 20):
                                cv2.line(p_img, (x, 0), (x, self.reg_h), (60, 60, 60), 1)
                                cv2.putText(p_img, str(x), (x + 2, 10), cv2.FONT_HERSHEY_SIMPLEX, 0.25, (130, 130, 130), 1, cv2.LINE_AA)
                            # 가로 격자선 및 라벨 (Y축 눈금자)
                            for y in range(20, self.reg_h, 20):
                                cv2.line(p_img, (0, y), (self.reg_w, y), (60, 60, 60), 1)
                                cv2.putText(p_img, str(y), (2, y - 2), cv2.FONT_HERSHEY_SIMPLEX, 0.25, (130, 130, 130), 1, cv2.LINE_AA)
                                
                        # 4) 좌우 경계선 그리기 (기존 코드 유지)
                        cv2.line(p_img, (self.x_min, 0), (self.x_min, self.reg_h), (59, 130, 246), 2)
                        cv2.line(p_img, (self.x_max, 0), (self.x_max, self.reg_h), (239, 68, 68), 2)
                        
                        # 5) 낚시 좌표 그리기 (기존 코드 유지)
                        if self.use_fishing_mode and self.fish_x != -1 and self.fish_y != -1:
                            cv2.circle(p_img, (self.fish_x, self.fish_y), 6, (34, 197, 94), 2)
                            
                        # 6) 텔레포트 포인트 (T) 그리기
                        if hasattr(self, 'teleport_x') and hasattr(self, 'teleport_y'):
                            tx, ty = self.teleport_x, self.teleport_y
                            if tx != -1 and ty != -1 and 0 <= tx <= self.reg_w and 0 <= ty <= self.reg_h:
                                cv2.circle(p_img, (tx, ty), 4, (75, 0, 130), -1)
                                cv2.putText(p_img, "T", (tx - 3, ty - 6), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (255, 255, 255), 1, cv2.LINE_AA)
                                
                        # 7) 순환사냥 웨이포인트들 그리기 (기존 코드 유지)
                        for idx, pt in enumerate(self.waypoints):
                            x_min_wp, x_max_wp = pt.get("x_min", -1), pt.get("x_max", -1)
                            y_wp = pt.get("y", -1)
                            if x_min_wp != -1 and y_wp != -1:
                                cv2.line(p_img, (x_min_wp, y_wp), (x_max_wp, y_wp), (168, 85, 247), 2)
                                cv2.putText(p_img, str(idx+1), (x_min_wp, y_wp - 3), cv2.FONT_HERSHEY_SIMPLEX, 0.3, (168, 85, 247), 1)
                                
                        # 8) 캐릭터 위치 그리기 (기존 코드 유지)
                        if cx != -1 and cy != -1:
                            cv2.circle(p_img, (cx, cy), 5, (34, 197, 94), -1)
                            
                        # 9) HUD 상태 박스 및 실시간 텍스트 오버레이 렌더링
                        if getattr(self, 'use_debug_mode', False):
                            status_text = self.get_current_status_text()
                            lines = [
                                f"캐릭터 : ({cx},{cy})",
                                f"설정 사냥층 : {getattr(self, 'hunt_y', -1)}",
                                f"설정 회수층 : {getattr(self, 'recovery_y', -1)}",
                                f"현재 감지층 : {cy}"
                            ]
                            
                            def estimate_pixel_width(text):
                                w = 0
                                for char in text:
                                    if ord(char) > 127:
                                        w += 11
                                    else:
                                        w += 6.5
                                return int(w)
                                
                            hud_w = estimate_pixel_width(status_text) + 12
                            hud_h = 18
                            hud_x1, hud_y1 = 5, 5
                            hud_x2, hud_y2 = hud_x1 + hud_w, hud_y1 + hud_h
                            
                            max_line_w = max(estimate_pixel_width(line) for line in lines)
                            info_w = max_line_w + 12
                            info_h = 16 * len(lines) + 6
                            info_x1, info_y1 = 5, hud_y2 + 3
                            info_x2, info_y2 = info_x1 + info_w, info_y1 + info_h
                            
                            # OpenCV로 배경 반투명 박스 일괄 렌더링
                            hud_overlay = p_img.copy()
                            cv2.rectangle(hud_overlay, (hud_x1, hud_y1), (hud_x2, hud_y2), (15, 15, 15), -1)
                            cv2.rectangle(hud_overlay, (info_x1, info_y1), (info_x2, info_y2), (15, 15, 15), -1)
                            p_img = cv2.addWeighted(hud_overlay, 0.6, p_img, 0.4, 0)
                            
                            # PIL(Pillow)로 한글 및 정보 텍스트 오버레이
                            img_pil = Image.fromarray(cv2.cvtColor(p_img, cv2.COLOR_BGR2RGB))
                            draw = ImageDraw.Draw(img_pil)
                            
                            try:
                                font = ImageFont.truetype("malgun.ttf", 11)
                            except:
                                try:
                                    font = ImageFont.truetype("C:/Windows/Fonts/malgun.ttf", 11)
                                except:
                                    font = ImageFont.load_default()
                                    
                            draw.text((hud_x1 + 6, hud_y1 + 2), status_text, font=font, fill=(0, 210, 255))
                            for idx, line in enumerate(lines):
                                draw.text((info_x1 + 6, info_y1 + 3 + idx * 16), line, font=font, fill=(255, 255, 255))
                            p_img = cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)
                        
                        self.char_x, self.char_y = cx, cy
                        self.signals.preview_signal.emit(p_img)
                    except Exception as e:
                        pass
                time.sleep(0.1)


    def execute_sequence_action(self, act):
        # '+' 기호 연계 입력 지원 (예: TELE_UP+ATTACK)
        if "+" in act:
            sub_acts = [sa.strip() for sa in act.split("+") if sa.strip()]
            self.logger.log(f"[시퀀스 연계] 연달아 동시 입력 실행: {sub_acts}", "MOVEMENT")
            for sa in sub_acts:
                self.execute_single_sequence_action(sa)
        else:
            self.execute_single_sequence_action(act)

    def execute_single_sequence_action(self, act):
        korean_map = {
            "위텔포": "TELE_UP", "위+텔포": "TELE_UP", "위텔레포트": "TELE_UP",
            "아래텔포": "DROP", "아래+텔포": "DROP", "아래텔레포트": "DROP",
            "좌텔포": "TELE_LEFT", "좌+텔포": "TELE_LEFT", "왼쪽텔포": "TELE_LEFT", "왼쪽+텔포": "TELE_LEFT",
            "우텔포": "TELE_RIGHT", "우+텔포": "TELE_RIGHT", "오른쪽텔포": "TELE_RIGHT", "오른쪽+텔포": "TELE_RIGHT",
            "위점프": "JUMP_UP", "위+점프": "JUMP_UP",
            "좌점프": "JUMP_LEFT", "좌+점프": "JUMP_LEFT", "왼쪽점프": "JUMP_LEFT", "왼쪽+점프": "JUMP_LEFT",
            "우점프": "JUMP_RIGHT", "우+점프": "JUMP_RIGHT", "오른쪽점프": "JUMP_RIGHT", "오른쪽+점프": "JUMP_RIGHT",
            "좌": "WALK_LEFT", "왼쪽": "WALK_LEFT",
            "우": "WALK_RIGHT", "오른쪽": "WALK_RIGHT",
            "아래": "DROP",
            "공격": "ATTACK"
        }
        act_clean = act.strip().replace(" ", "")
        if act_clean in korean_map:
            act = korean_map[act_clean]
            
        att_key = self.key_att_cb.currentText()
        is_act_attack = (act == "ATTACK" or act.lower() == "end" or act.lower() == att_key.lower())
        
        # 이동 명령 수행 전에 공격 릴리즈 (혹시 모를 홀드 방지용)
        is_move_act = act in ["TELE_UP", "TELE_LEFT", "TELE_RIGHT", "JUMP_UP", "JUMP_LEFT", "JUMP_RIGHT", "WALK_LEFT", "WALK_RIGHT", "DROP", "ROPE_UP"]
        if is_move_act:
            self.set_key_state(att_key, False)
            self.is_pingpong_fixed_attacking = False
            
        if act == "TELE_UP":
            self.movement_controller.execute_move_action("TELE_UP")
        elif act == "TELE_LEFT":
            self.movement_controller.execute_move_action("TELE_LEFT")
        elif act == "TELE_RIGHT":
            self.movement_controller.execute_move_action("TELE_RIGHT")
        elif act == "JUMP_UP":
            self.movement_controller.execute_move_action("JUMP_UP")
        elif act == "JUMP_LEFT":
            self.movement_controller.execute_move_action("JUMP_LEFT")
        elif act == "JUMP_RIGHT":
            self.movement_controller.execute_move_action("JUMP_RIGHT")
        elif act == "WALK_LEFT":
            self.movement_controller.execute_move_action("WALK_LEFT")
        elif act == "WALK_RIGHT":
            self.movement_controller.execute_move_action("WALK_RIGHT")
        elif act == "DROP":
            self.movement_controller.execute_move_action("DROP")
        elif act == "ROPE_UP":
            self.set_key_state('up', True)
            time.sleep(self.rope_climb_time)
            self.set_key_state('up', False)
        elif is_act_attack:
            self.press_key(att_key)
            self.logger.log(f"[시퀀스] 공격 키 입력 실행 ({att_key})", "MOVEMENT")
        else:
            try:
                self.press_key(act.lower())
            except Exception as e:
                self.logger.log(f"[시퀀스 경고] 알 수 없는 동작 명령어: {act} ({str(e)})", "MOVEMENT")

    def status_update_loop(self):
        while not self.stop_threads:
            try:
                up = int(time.time() - self.current_hunt_start) if self.is_running else 0
                total = self.total_hunting_time + up
                
                # 1. 회수 남은시간 계산
                recovery_left_str = "비활성"
                if self.is_running and getattr(self, 'use_recovery', False):
                    if not getattr(self, 'is_recovering', False):
                        last_rec = getattr(self, 'last_recovery_time', 0)
                        rec_interval = getattr(self, 'recovery_interval', 60)
                        time_left = max(0, int(rec_interval - (time.time() - last_rec)))
                        recovery_left_str = f"{time_left}초"
                    else:
                        rec_state = getattr(self, 'recovery_state', 'idle')
                        if rec_state == "collecting":
                            rec_start = getattr(self, 'recovery_start_time', 0)
                            rec_duration = getattr(self, 'recovery_duration', 10)
                            time_left = max(0, int(rec_duration - (time.time() - rec_start)))
                            recovery_left_str = f"회수중 ({time_left}초)"
                        elif rec_state in ["moving_to_recovery_y", "moving_to_return_start", "executing_return_seq", "verifying_return"]:
                            recovery_left_str = "이동중"
                        else:
                            recovery_left_str = "회수중"
                
                # 2. 펫먹이 남은시간 계산
                pet_left_str = "비활성"
                # 3. 자동판매 남은시간 및 트리거 처리
                if self.is_running and getattr(self, 'chk_auto_sell', None) and self.chk_auto_sell.isChecked():
                    try:
                        interval_min = int(self.txt_auto_sell_interval.text().strip() or "5")
                        last_sell = getattr(self, 'last_auto_sell_time', 0.0)
                        if last_sell == 0.0:
                            self.last_auto_sell_time = time.time()
                            last_sell = self.last_auto_sell_time
                        
                        time_elapsed = time.time() - last_sell
                        interval_sec = interval_min * 60
                        
                        if time_elapsed >= interval_sec:
                            if not self.is_selling:
                                self.logger.log(f"[자동판매] {interval_min}분 주기 도달 -> 자동 판매 시퀀스 트리거", "SYSTEM")
                                self.signals.sell_signal.emit()
                                self.last_auto_sell_time = time.time()
                    except Exception as e:
                        pass

                self.signals.status_signal.emit({
                    "uptime": f"{up//3600:02d}:{(up%3600)//60:02d}:{up%60:02d}", 
                    "total_uptime": f"{total//3600:02d}:{(total%3600)//60:02d}:{total%60:02d}", 
                    "cpu": int(psutil.cpu_percent()), 
                    "ram": int(psutil.virtual_memory().percent), 
                    "err_cnt": self.err_cnt,
                    "char_x": self.char_x,
                    "char_y": self.char_y,
                    "recovery_left": recovery_left_str,
                    "pet_left": pet_left_str
                })
            except: 
                pass
            time.sleep(1.0)

    def start_hunting(self): 
        self.logger.log("사냥 시작 버튼 클릭", "SYSTEM")
        
        self.is_running = True
        self.is_moving = False
        self.is_teleporting = False
        self.is_attacking = False
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.current_hunt_start = time.time()
        
        self.logger.log("사냥 시작 검증 통과", "SYSTEM")
        
        self.hunter_thread = threading.Thread(target=self.hunter_core, daemon=True)
        self.logger.log("사냥 루프 생성", "SYSTEM")
        
        self.hunter_thread.start()
        self.logger.log("사냥 시스템을 가동합니다.", "SYSTEM")

    def stop_hunting(self): 
        self.is_running = False
        self.is_selling = False
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        if self.current_hunt_start > 0:
            self.total_hunting_time += int(time.time() - self.current_hunt_start)
        
        keys_to_release = ['left', 'right', 'up', 'down', 'space', 'ctrl', 'alt', 'shift', 'insert', 'del', 'home', 'end', 'pgup', 'pgdn'] + list("abcdefghijklmnopqrstuvwxyz")
        for key in keys_to_release:
            try:
                self.set_key_state(key, False)
            except:
                pass
                
        self.is_moving = False
        self.is_teleporting = False
        self.is_attacking = False
        self.logger.log("[전역 긴급 정지] 사냥 시스템을 즉시 중지하고 모든 입력을 해제했습니다.", "SYSTEM")

    def hotkey_start_handler(self): 
        self.signals.start_signal.emit()
        
    def hotkey_stop_handler(self): 
        self.signals.stop_signal.emit()
    
    def hotkey_fix_fish_handler(self):
        if self.char_x != -1 and self.char_y != -1:
            self.fish_x = self.char_x
            self.fish_y = self.char_y
            self.lbl_fish_pos.setText(f"지정된 낚시 좌표: X: {self.fish_x}, Y: {self.fish_y}")
            self.logger.log(f"[낚시 좌표 고정 완료] -> X: {self.fish_x}, Y: {self.fish_y}", "WAYPOINT")
            winsound.Beep(1500, 300)
        else:
            self.logger.log("[낚시 좌표 픽스 실패] 현재 캐릭터 위치 인식이 불가능합니다.", "WAYPOINT")
            winsound.Beep(800, 300)

    def on_hunt_mode_radio_changed(self, btn):
        idx = self.btn_group_mode.id(btn)
        self.hunt_mode = idx
        mode_names = ["핑퐁사냥", "제자리 사냥", "순환사냥 V2"]
        self.logger.log(f"작동 모드 변경: {mode_names[idx] if idx < len(mode_names) else idx}", "SYSTEM")
        self.update_mode_ui_states()

    def update_mode_ui_states(self):
        self.grp_lr_settings.setEnabled(self.hunt_mode == 0)
        self.grp_stat_settings.setEnabled(self.hunt_mode == 1)
        self.grp_v2_settings.setEnabled(self.hunt_mode == 2)
        
        # 핑퐁사냥 모드(0) 선택 시 창 높이를 최소 980px로 자동 확장
        if self.hunt_mode == 0:
            if self.height() < 980:
                self.resize(self.width(), 980)

    def update_use_alert(self, state):
        self.use_sound_alert = state
        self.logger.log(f"거탐 사운드 알람: {'활성화' if state else '비활성화'}", "SYSTEM")

    def update_use_anti_town(self, state):
        self.use_anti_town = state
        self.logger.log(f"잠수 AFK 방지: {'활성화' if state else '비활성화'}", "SYSTEM")

    def update_use_bottom_hunt(self, state):
        self.use_bottom_hunt = state
        self.logger.log(f"하단 사냥 및 자동 복귀: {'활성화' if state else '비활성화'}", "SYSTEM")

    def update_use_escape_lost(self, state):
        self.use_escape_lost = state
        self.logger.log(f"캐릭터 인식 유실 시 사냥 중단: {'활성화' if state else '비활성화'}", "SYSTEM")

    def update_use_fall_recovery(self, state):
        self.use_fall_recovery = state
        self.logger.log(f"추락 감지 복귀: {'활성화' if state else '비활성화'}", "SYSTEM")

    def update_use_fishing_mode(self, state):
        self.use_fishing_mode = state
        self.logger.log(f"낚시사냥 모드: {'활성화' if state else '비활성화'}", "SYSTEM")

    def update_use_multifloor(self, state):
        self.use_multifloor_hunt = state
        self.logger.log(f"복층 순환사냥 모드: {'활성화' if state else '비활성화'}", "SYSTEM")

    def update_use_shape_anti(self, state):
        self.use_shape_anti = state
        self.logger.log(f"👁️ 투명 도형 추적 엔진: {'활성화' if state else '비활성화'}", "SYSTEM")

    def update_use_watch_mode(self, state):
        self.use_watch_mode = state
        self.logger.log(f"감시(잠수) 전용 모드: {'활성화' if state else '비활성화'}", "SYSTEM")

    def update_window_flags(self, state):
        if state:
            self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        else:
            self.setWindowFlags(self.windowFlags() & ~Qt.WindowStaysOnTopHint)
        self.show()
        self.logger.log(f"창 항상 맨 위 고정: {'활성화' if state else '비활성화'}", "SYSTEM")

    def update_x_min(self, v):
        self.x_min = v
        if hasattr(self, 'txt_pingpong_x_min'):
            self.txt_pingpong_x_min.setText(str(v))
        self.logger.log(f"좌측 경계 임계값 변경 -> {v}", "SYSTEM")

    def update_x_max(self, v):
        self.x_max = v
        if hasattr(self, 'txt_pingpong_x_max'):
            self.txt_pingpong_x_max.setText(str(v))
        self.logger.log(f"우측 경계 임계값 변경 -> {v}", "SYSTEM")

    def update_stat_range(self, v):
        self.stationary_range = v
        self.logger.log(f"제자리 범위 임계값 변경 -> {v}", "SYSTEM")

    def update_precision(self, v):
        self.precision_val = 0.0
        self.color_margin = 0

    def update_att_delay(self, v):
        self.attack_delay_ms = v
        self.logger.log(f"공격 주기 변경 -> {v}ms", "SYSTEM")

    def update_dash_delay(self, v):
        self.dash_delay_ms = v
        self.logger.log(f"텔레포트 주기 변경 -> {v}ms", "SYSTEM")

    def update_pet_interval(self, v):
        self.periodic_interval_min = v
        self.logger.log(f"소모품 주기 변경 -> {v}분", "SYSTEM")

    def update_sell_interval(self, v):
        self.sell_interval_min = v
        self.logger.log(f"판매 주기 변경 -> {v}분", "SYSTEM")

    def update_opacity(self, v):
        self.setWindowOpacity(v / 100.0)

    def update_bottom_y(self, v):
        self.bottom_y_threshold = v
        self.logger.log(f"하단 Y 기준값 변경 -> {v}", "SYSTEM")

    def update_bottom_time(self, v):
        self.bottom_hunt_time_sec = v
        self.logger.log(f"하단 유지 시간 변경 -> {v}초", "SYSTEM")

    def update_fall_y(self, v):
        self.fall_y_threshold = v
        self.logger.log(f"추락 Y 기준값 변경 -> {v}", "SYSTEM")

    def update_lost_timeout(self, v):
        self.lost_timeout_sec = v
        self.logger.log(f"탈출 대기 시간 변경 -> {v}초", "SYSTEM")

    def update_multifloor_up_count(self, v):
        self.multifloor_up_count = v
        self.logger.log(f"텔레포트 상승 횟수 변경 -> {v}회", "SYSTEM")

    def open_selector(self):
        self.selector = QWidget()
        self.selector.setWindowOpacity(0.3)
        self.selector.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.selector.showFullScreen()
        self.selector.setCursor(Qt.CrossCursor)
        self.selector.mousePressEvent = lambda e: setattr(self, 'sel_start', e.position().toPoint())
        self.selector.mouseReleaseEvent = self.sel_finish
        self.selector.show()
        
    def sel_finish(self, e): 
        if hasattr(self, 'sel_start') and self.sel_start:
            end = e.position().toPoint()
            l = min(self.sel_start.x(), end.x())
            t = min(self.sel_start.y(), end.y())
            w = abs(self.sel_start.x() - end.x())
            h = abs(self.sel_start.y() - end.y())
            
            dpi = QApplication.primaryScreen().devicePixelRatio()
            new_l = int(l * dpi)
            new_t = int(t * dpi)
            new_w = int(w * dpi)
            new_h = int(h * dpi)
            
            if (new_l != self.reg_l or new_t != self.reg_t or new_w != self.reg_w or new_h != self.reg_h):
                self.logger.log(f"[디버그] ROI 변경 감지 (수동 드래그) -> 기존 L:{self.reg_l}, T:{self.reg_t}, W:{self.reg_w}, H:{self.reg_h} | 신규 L:{new_l}, T:{new_t}, W:{new_w}, H:{new_h}", "MINIMAP")
                
            self.reg_l = new_l
            self.reg_t = new_t
            self.reg_w = new_w
            self.reg_h = new_h
            
            margin_px = int(self.reg_w * 0.15)
            self.x_min = margin_px
            self.x_max = self.reg_w - margin_px
            self.x_min_slider.setValue(self.x_min)
            self.x_max_slider.setValue(self.x_max)
            
            self.logger.log(f"미니맵 수동 드래그 지정 완료 -> 물리 좌표: L:{self.reg_l}, T:{self.reg_t}, W:{self.reg_w}, H:{self.reg_h} (DPI Scale: {dpi:.2f})", "MINIMAP")
            self.settings_manager.save_settings_silently()
            
        self.selector.close()
        self.selector.deleteLater()

    def update_input_mode(self, idx):
        self.input_mode = idx
        mode_names = ["PyAutoGUI", "Windows SendInput", "Logitech G HUB"]
        self.logger.log(f"입력 시뮬레이션 방식 변경: {mode_names[idx]}", "SYSTEM")
        if idx == 2 and not self.movement_controller.logitech_input.dll:
            self.logger.log("경고: Logitech G HUB 드라이버 DLL(lghub_device.dll)을 로드하지 못했습니다. 실제 동작 시 Windows SendInput으로 자동 대체됩니다.", "SYSTEM")

    def register_current_layer(self, mode):
        if self.char_x == -1 or self.char_y == -1:
            self.logger.log("[층 등록 실패] 현재 캐릭터 위치 인식이 불가능합니다.", "WAYPOINT")
            winsound.Beep(800, 300)
            return
            
        display_y = self.char_y
        layers = self.minimap_detector.detect_floor_layers()
        closest_layer_val = min(layers, key=lambda y: abs(y - display_y)) if layers else -1
        final_save_y = display_y
        
        # 층 등록 진단 로그 추가 (표시좌표, 실측좌표, 최종 저장값)
        self.logger.log(
            f"[층 등록 진단] 표시좌표(캐릭터 Y): {display_y} | 실측좌표(가장 가까운 발판 Y): {closest_layer_val} (감지 목록: {layers}) | 최종 저장값: {final_save_y}", 
            "WAYPOINT"
        )
        
        if mode == 'hunt':
            self.hunt_y = final_save_y
            self.hunt_layer_idx = layers.index(closest_layer_val) if closest_layer_val != -1 else -1
            self.txt_pingpong_hunt_y.setText(str(final_save_y))
            self.logger.log(f"[핑퐁]\n사냥층 등록\n\n저장값 : {final_save_y}", "WAYPOINT")
            self.logger.log(f"[사냥층 등록 완료] 캐릭터 Y좌표: {final_save_y} 저장 완료", "WAYPOINT")
        else:
            self.recovery_y = final_save_y
            self.recovery_layer_idx = closest_layer_val != -1 and layers.index(closest_layer_val) or -1
            self.txt_pingpong_recovery_y.setText(str(final_save_y))
            self.logger.log(f"[핑퐁]\n회수층 등록\n\n저장값 : {final_save_y}", "WAYPOINT")
            self.logger.log(f"[회수층 등록 완료] 캐릭터 Y좌표: {final_save_y} 저장 완료", "WAYPOINT")
            
        winsound.Beep(1400, 200)
        self.settings_manager.save_settings_silently()

    def play_custom_sound(self): 
        def _p():
            s = time.time()
            while time.time()-s < 10 and self.use_sound_alert: 
                winsound.Beep(3000, 100)
                winsound.Beep(4000, 100)
        threading.Thread(target=_p, daemon=True).start()

    def toggle_theme(self):
        self.theme_mode = "light" if self.theme_mode == "dark" else "dark"
        UiSetup.apply_qss(self, self.theme_mode)
        self.settings_manager.save_settings_silently()
        self.logger.log(f"테마 전환 적용 완료 -> {self.theme_mode.upper()} 모드", "SYSTEM")

    def toggle_admin_mode(self):
        if self.is_admin_mode:
            self.is_admin_mode = False
            UiSetup.set_admin_mode_visibility(self, False)
            self.settings_manager.save_settings_silently()
            self.logger.log("관리자 설정 모드가 비활성화되었습니다. (고급 설정 숨김)", "SYSTEM")
        else:
            from PySide6.QtWidgets import QInputDialog, QLineEdit
            pw, ok = QInputDialog.getText(self, "관리자 인증", "관리자 비밀번호를 입력하세요:", QLineEdit.Password)
            if ok and pw == "admin123":
                self.is_admin_mode = True
                UiSetup.set_admin_mode_visibility(self, True)
                self.settings_manager.save_settings_silently()
                self.logger.log("관리자 설정 모드가 활성화되었습니다. (고급 설정 편집 가능)", "SYSTEM")
            elif ok:
                QMessageBox.warning(self, "인증 실패", "비밀번호가 올바르지 않습니다.")
                self.logger.log("관리자 인증 실패: 비밀번호 오류", "SYSTEM")

    def closeEvent(self, e): 
        self.stop_threads = True
        self.is_running = False
        try:
            self.set_key_state('left', False)
            self.set_key_state('right', False)
            self.set_key_state('up', False)
            self.drag_mouse_up()
        except: 
            pass
        e.accept()
 
def kill_duplicate_processes():
    current_pid = os.getpid()
    for proc in psutil.process_iter(['pid', 'name', 'exe']):
        try:
            pinfo = proc.info
            pid = pinfo['pid']
            if pid == current_pid:
                continue
            name = pinfo.get('name') or ''
            exe = pinfo.get('exe') or ''
            if 'AUTOmaple' in name or 'AUTOmaple' in exe:
                p = psutil.Process(pid)
                p.terminate()
                try:
                    p.wait(timeout=0.5)
                except psutil.TimeoutExpired:
                    p.kill()
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
 
if __name__ == "__main__":
    kill_duplicate_processes()
    app = QApplication(sys.argv)
    window = AUTOmapleV9_7()
    window.show()
    sys.exit(app.exec())
