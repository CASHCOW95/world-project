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

from PySide6.QtCore import Qt, QTimer, Signal, QObject, QPoint
from PySide6.QtGui import QColor, QFont, QImage, QPixmap
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLineEdit, QMessageBox
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
from modules.settings_v2 import SettingsManagerV2
from modules.minimap_v2 import MinimapDetectorV2
from modules.movement import MovementController
from modules.combat import CombatController
from modules.ui_v2 import UiSetupV2

class CommunicateV2(QObject):
    log_signal = Signal(str)
    preview_signal = Signal(np.ndarray)
    status_signal = Signal(dict)
    alert_signal = Signal()
    start_signal = Signal()
    stop_signal = Signal()
    sell_signal = Signal()
    f2_signal = Signal()
    f1_signal = Signal()

class AUTOmapleV2(QMainWindow):
    def __init__(self):
        super().__init__()
        self.version = "v2.0.0"
        self.setWindowTitle(f"AUTOmaple {self.version}")
        self.setMinimumSize(430, 620)
        self.setMaximumWidth(430)
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        
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
        self.is_pingpong_fixed_attacking = False
        self.att_key_hold_start = 0.0
        
        # 미니맵 캐릭터 좌표 및 복귀 설정 변수
        self.char_x = -1
        self.char_y = -1
        
        self.use_escape_lost = False
        self.lost_timeout_sec = 5
        self.last_char_seen_time = time.time()
        
        # 낚시 사냥 변수
        self.use_fishing_mode = False
        self.fish_x = -1
        self.fish_y = -1
        
        # 입력 시뮬레이션 관련 변수
        self.input_mode = 0  # 0: PyAutoGUI, 1: Windows SendInput, 2: Logitech G HUB
        self.key_states = {}
        
        # 기본 설정
        self.reg_t, self.reg_l, self.reg_w, self.reg_h = 100, 100, 200, 150
        self.x_min, self.x_max, self.stationary_range = 20, 180, 15
        self.attack_delay_ms, self.dash_delay_ms = 200, 500
        self.periodic_interval_min, self.sell_interval_min = 5, 15
        self.use_auto_sell, self.use_sound_alert = False, True
        self.hunt_mode = 0 
        self.hunt_layer_idx = -1
        self.recovery_layer_idx = -1
        self.base_lower = np.array([245, 230, 0]); self.base_upper = np.array([254, 255, 129])
        self.profiles_data = {}
        
        # Teleport and Action status vars
        self.teleport_x = -1
        self.teleport_y = -1
        self.recovery_start_x = -1
        self.recovery_start_y = -1
        self.reached_recovery_start = False
        self.is_loading_profile = False
        
        # 미니맵 색상 감지 파라미터 (settings에서 덮어씌움)
        self.color_margin = 0
        self.precision_val = 0.0
        
        # 추락/복귀/하단사냥 관련 (settings에서 덮어씌움)
        self.use_fall_recovery = False
        self.fall_y_threshold = 110
        self.use_bottom_hunt = False
        self.bottom_y_threshold = 80
        self.bottom_hunt_time_sec = 10
        self.fall_count = 0
        
        # 사냥/회수층 Y (hunter_core 시작 시 재설정)
        self.hunt_y = 67
        self.recovery_y = 81
        self.update_url = ""
        
        self.signals = CommunicateV2()
        self.signals.log_signal.connect(self.update_log)
        self.signals.preview_signal.connect(self.update_minimap_preview)
        self.signals.status_signal.connect(self.update_status_ui)
        self.signals.alert_signal.connect(self.play_custom_sound)
        self.signals.f2_signal.connect(self.handle_f2_main_thread)
        self.signals.f1_signal.connect(self.register_sell_position)
        
        # 모듈 인스턴스화
        self.logger = AppLogger(self)
        self.settings_manager = SettingsManagerV2(self)
        self.minimap_detector = MinimapDetectorV2(self)
        self.movement_controller = MovementController(self)
        self.combat_controller = CombatController(self)
        
        # UI 셋업
        UiSetupV2.setup_ui(self)
        UiSetupV2.apply_qss(self)
        
        # 핫키 시그널 → 메서드 직접 연결 (btn.click() 경유 시 disabled 상태에서 무시될 수 있음)
        self.signals.start_signal.connect(self.start_hunting)
        self.signals.stop_signal.connect(self.stop_hunting)
        self.signals.sell_signal.connect(self.run_manual_sell)
        
        self.settings_manager.load_all_profiles()
        self.stop_threads = False
        
        # 스레드 루프 시작
        threading.Thread(target=self.monitor_loop, daemon=True).start()
        threading.Thread(target=self.status_update_loop, daemon=True).start()
        
        # 핫키 등록 (개별 try-except로 실패 시에도 나머지 등록 보장)
        try:
            keyboard.unhook_all()
        except:
            pass
        
        hotkey_map = {
            'f5': ('사냥 시작', self.hotkey_start_handler),
            'f6': ('사냥 중지', self.hotkey_stop_handler),
            'f3': ('인벤 수동판매', self.hotkey_sell_handler),
            'f9': ('낚시 좌표 고정', self.hotkey_fix_fish_handler),
            'f2': ('좌표 자동입력', self.hotkey_f2_handler),
            'f1': ('판매 좌표 등록', self.hotkey_f1_handler),
        }
        for key, (desc, handler) in hotkey_map.items():
            try:
                keyboard.add_hotkey(key, handler)
            except Exception as e:
                print(f"[핫키 등록 실패] {key.upper()} ({desc}): {e}")

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
            self.logger.log(f"[{widget.objectName()}] 좌표 등록 완료 -> {cx}, {cy}", "SYSTEM")
        else:
            self.run_manual_sell()

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
            self.logger.log(f"[판매 에러] 좌표 파싱 실패: {str(e)}", "SYSTEM")
            winsound.Beep(500, 500)
            return
            
        if any(pos == (0, 0) for pos in [p1, p2, p3, p4, p5]):
            self.logger.log("[판매 실패] 모든 좌표(1~5)가 설정되어야 합니다.", "SYSTEM")
            winsound.Beep(500, 500)
            return

        self.logger.log("인벤토리 수동 판매 시퀀스 시작", "SYSTEM")
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
                
                # 1. 상점열기
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
                time.sleep(float(self.txt_sell_delay1.text().strip() or "1.5"))
                
                if not self.is_selling: return
                
                # 2. 거래/판매 진입
                self.logger.log("2. 판매 모드 진입 (좌표2 클릭 및 엔터)", "SYSTEM")
                self.human_mouse_move(p2[0], p2[1])
                time.sleep(0.1)
                self.drag_mouse_down()
                time.sleep(0.05)
                self.drag_mouse_up()
                time.sleep(0.2)
                self.press_key('enter')
                time.sleep(float(self.txt_sell_delay2.text().strip() or "1.0"))
                
                if not self.is_selling: return
                
                # 3. 기타창이동
                self.logger.log("3. 기타창 탭 클릭 (좌표3 클릭)", "SYSTEM")
                self.human_mouse_move(p3[0], p3[1])
                time.sleep(0.1)
                self.drag_mouse_down()
                time.sleep(0.05)
                self.drag_mouse_up()
                time.sleep(float(self.txt_sell_delay3.text().strip() or "0.5"))
                
                if not self.is_selling: return
                
                # 4. 반복 더블클릭 및 엔터
                total_cnt = (sell_rows - sell_start_row + 1) * 4
                if total_cnt <= 0:
                    total_cnt = 32
                
                self.logger.log(f"4. 아이템 판매 루틴 작동 ({total_cnt}회)", "SYSTEM")
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
                    time.sleep(float(self.txt_sell_delay4.text().strip() or "0.12"))
                    self.press_key('enter')
                    time.sleep(max(0.05, sell_delay))
                    
                if not self.is_selling: return
                
                # 5. 상점 닫기
                self.logger.log("5. 상점 닫기 (좌표5 클릭)", "SYSTEM")
                self.human_mouse_move(p5[0], p5[1])
                time.sleep(0.1)
                self.drag_mouse_down()
                time.sleep(0.05)
                self.drag_mouse_up()
                time.sleep(float(self.txt_sell_delay5.text().strip() or "0.5"))
                
            except Exception as e:
                self.logger.log(f"[판매 오류] {str(e)}", "SYSTEM")
            finally:
                self.is_selling = False
                self.logger.log("판매 시퀀스 완료", "SYSTEM")
                winsound.Beep(1200, 200)
                
        threading.Thread(target=sell_thread_worker, daemon=True).start()

    def update_log(self, m): 
        self.log_text.append(f"<span style='color:#484f58'>[{time.strftime('%H:%M:%S')}]</span> {m}")
        self.log_text.verticalScrollBar().setValue(self.log_text.verticalScrollBar().maximum())
        
    def update_status_ui(self, d): 
        self.data_runtime.setText(d.get("uptime", "00:00:00"))
        self.data_total_time.setText(d.get("total_uptime", "00:00:00"))
        self.data_errors.setText(f"{d.get('err_cnt', 0)}회")
        
        cx = d.get("char_x", -1)
        cy = d.get("char_y", -1)
        if cx != -1 and cy != -1:
            self.data_char_pos.setText(f"캐릭터: X: {cx}, Y: {cy}")
        else:
            self.data_char_pos.setText("캐릭터: 인식 불가")
            
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
            self.logger.log("캐릭터 위치 인식 실패로 자동입력이 불가합니다.", "SYSTEM")
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
            elif obj_name in ["teleport_x"] or obj_name.endswith("_x"):
                val = cx
            elif obj_name in ["hunt_y", "recovery_y", "teleport_y", "recovery_start_y"] or obj_name.endswith("_y"):
                val = cy
            elif obj_name in ["recovery_start_x"]:
                val = cx
                
            if val is not None:
                widget.setText(str(val))
                widget.editingFinished.emit()
                self.logger.log(f"[F2 자동입력] {obj_name} -> {val}", "SYSTEM")
                winsound.Beep(1400, 200)
                self.settings_manager.save_settings_silently()

    def hotkey_fix_fish_handler(self):
        if self.char_x != -1 and self.char_y != -1:
            self.fish_x = self.char_x
            self.fish_y = self.char_y
            self.lbl_fish_pos.setText(f"낚시 좌표: X: {self.fish_x}, Y: {self.fish_y}")
            self.logger.log(f"🎣 [낚시 좌표 고정 완료] -> X: {self.fish_x}, Y: {self.fish_y}", "SYSTEM")
            winsound.Beep(1500, 300)
            self.settings_manager.save_settings_silently()
        else:
            self.logger.log("⚠️ [낚시 좌표 픽스 실패] 캐릭터 위치 인식 불가", "SYSTEM")
            winsound.Beep(800, 300)

    def update_minimap_preview(self, i): 
        h, w, c = i.shape
        self.minimap_preview.setPixmap(QPixmap.fromImage(QImage(i.data, w, h, c*w, QImage.Format_RGB888).rgbSwapped()).scaled(self.minimap_preview.size(), Qt.IgnoreAspectRatio, Qt.SmoothTransformation))

    def hunter_core(self):
        try:
            cur_dir, l_att, l_dash, l_del = 'right', 0, 0, time.time()
            self.last_char_seen_time = time.time()
            self.last_recovery_time = time.time()
            self.is_falling_recovering = False
            self.is_recovering = False
            self.reached_recovery_start = False
            
            # 버프 타이머
            self.last_buff1_time = 0.0
            self.last_buff2_time = 0.0
            self.last_recovery_teleport_time = 0.0
            self.last_completed_waypoint_idx = -1
            
            # 자동 판매 타이머
            self.last_auto_sell_time = time.time()
            
            # 파라미터 로컬 바인딩
            self.use_recovery = self.chk_pingpong_recovery.isChecked()
            self.recovery_interval = int(self.txt_pingpong_recovery_interval.text().strip() or "60")
            self.recovery_duration = int(self.txt_pingpong_recovery_duration.text().strip() or "10")
            
            try:
                self.hunt_y = int(self.txt_pingpong_hunt_y.text().strip())
            except:
                self.hunt_y = 67
            try:
                self.recovery_y = int(self.txt_pingpong_recovery_y.text().strip())
            except:
                self.recovery_y = 81
                
            self.return_x_min = int(self.txt_pingpong_return_x_min.text().strip() or "45")
            self.return_x_max = int(self.txt_pingpong_return_x_max.text().strip() or "50")
            self.rope_climb_time = float(self.txt_pingpong_rope_climb_time.text().strip() or "1.5")
            self.return_sequence = self.txt_pingpong_return_seq.text().strip()
            self.recovery_sequence = self.txt_pingpong_recovery_seq.text().strip()
            self.seq_delay = float(self.txt_pingpong_seq_delay.text().strip() or "1.0")

            self.recovery_state = "idle"
            if self.use_recovery:
                self.logger.log(f"[핑퐁사냥 기동] 회수 모드 ON | 사냥층 Y={self.hunt_y}, 회수층 Y={self.recovery_y}", "WAYPOINT")
            else:
                self.logger.log("[핑퐁사냥 기동] 사냥 시작", "WAYPOINT")
            
            while self.is_running:
                if self.is_selling: 
                    self.set_key_state('left', False)
                    self.set_key_state('right', False)
                    try:
                        self.set_key_state(self.key_att_cb.currentText(), False)
                    except:
                        pass
                    self.is_pingpong_fixed_attacking = False
                    time.sleep(0.1)
                    continue
                
                with mss.mss() as sct:
                    cx, cy, img, mask = self.minimap_detector.get_player_coords(sct)
                    self.char_x, self.char_y = cx, cy
                    
                    if cx != -1 and cy != -1:
                        self.last_char_seen_time = time.time()
                        
                        # 낚시 사냥 처리
                        if self.use_fishing_mode and self.fish_x != -1 and self.fish_y != -1:
                            dx = cx - self.fish_x
                            dy = cy - self.fish_y
                            if abs(dx) > 5 or abs(dy) > 5:
                                teleport_key = self.key_teleport_cb.currentText()
                                if abs(dx) > 5:
                                    if abs(dx) >= 20:
                                        self.set_key_state('right' if dx > 0 else 'left', False)
                                        self.set_key_state('left' if dx > 0 else 'right', True)
                                        time.sleep(0.05)
                                        self.press_key(teleport_key)
                                        time.sleep(0.15)
                                        self.set_key_state('left' if dx > 0 else 'right', False)
                                    else:
                                        self.set_key_state('right' if dx > 0 else 'left', False)
                                        self.set_key_state('left' if dx > 0 else 'right', True)
                                        time.sleep(0.05)
                                    continue
                                else:
                                    self.set_key_state('left', False)
                                    self.set_key_state('right', False)
                                    if dy > 5:
                                        self.set_key_state('up', True)
                                        time.sleep(0.08)
                                        self.press_key(teleport_key)
                                        time.sleep(0.2)
                                        self.set_key_state('up', False)
                                    elif dy < -5:
                                        self.set_key_state('down', True)
                                        time.sleep(0.08)
                                        self.press_key(self.key_jump_cb.currentText())
                                        time.sleep(0.02)
                                        self.set_key_state('down', False)
                                        time.sleep(0.2)
                                    continue
                        
                        # 핑퐁 사냥층 이탈 낙하 감지 복귀
                        if not self.is_recovering and self.use_fall_recovery:
                            if cy >= self.fall_y_threshold:
                                self.logger.log("[추락 감지] 회수층으로 이탈하여 복귀 시퀀스를 즉시 작동합니다.", "SYSTEM")
                                self.is_recovering = True
                                self.recovery_state = "executing_return_seq"
                                self.set_key_state('left', False)
                                self.set_key_state('right', False)
                                try:
                                    self.set_key_state(self.key_att_cb.currentText(), False)
                                except:
                                    pass
                                self.is_pingpong_fixed_attacking = False
                                continue
                        
                        # 넉백 감지 (회수층 추락)
                        if self.use_recovery and not self.is_recovering:
                            if abs(cy - self.recovery_y) <= 3:
                                self.logger.log("[넉백 감지] 회수층 강제 추락 확인 -> 즉시 복귀 시작", "SYSTEM")
                                self.is_recovering = True
                                self.recovery_state = "executing_return_seq"
                                self.set_key_state('left', False)
                                self.set_key_state('right', False)
                                try:
                                    self.set_key_state(self.key_att_cb.currentText(), False)
                                except:
                                    pass
                                self.is_pingpong_fixed_attacking = False
                                continue

                        # 주기적인 아이템 회수 돌입
                        if self.use_recovery and not self.is_recovering and (time.time() - self.last_recovery_time > self.recovery_interval):
                            self.is_recovering = True
                            self.recovery_state = "executing_recovery_seq"
                            self.logger.log("[핑퐁회수] 회수 주기 도달 -> 회수층 이동 시퀀스 실행", "MOVEMENT")
                            self.set_key_state('left', False)
                            self.set_key_state('right', False)
                            try:
                                self.set_key_state(self.key_att_cb.currentText(), False)
                            except:
                                pass
                            self.is_pingpong_fixed_attacking = False

                        # 회수 모드 상태 머신
                        if self.is_recovering:
                            if self.recovery_state == "executing_recovery_seq":
                                seq_str = self.recovery_sequence.strip()
                                if seq_str:
                                    actions = [a.strip() for a in seq_str.split(",") if a.strip()]
                                    self.logger.log(f"[핑퐁회수] 회수층 이동 시퀀스 실행: {actions}", "MOVEMENT")
                                    for act in actions:
                                        if not self.is_running or self.is_selling: break
                                        self.execute_sequence_action(act)
                                        time.sleep(self.seq_delay)
                                else:
                                    self.logger.log("[핑퐁회수] 회수층 이동 시퀀스 미설정 → 즉시 회수 수집 시작", "MOVEMENT")
                                self.recovery_state = "collecting"
                                self.recovery_start_time = time.time()
                                self.logger.log(f"[핑퐁회수] 회수층 도착 → {self.recovery_duration}초간 회수 수집", "MOVEMENT")
                                self.set_key_state('left', False)
                                self.set_key_state('right', False)
                                continue
                                
                            elif self.recovery_state == "collecting":
                                if time.time() - self.recovery_start_time > self.recovery_duration:
                                    self.set_key_state('left', False)
                                    self.set_key_state('right', False)
                                    self.recovery_state = "executing_return_seq"
                                    self.logger.log("[핑퐁회수] 회수 완료 → 복귀 시퀀스 실행", "MOVEMENT")
                                else:
                                    # 회수 수집 이동 (좌우 핑퐁)
                                    if cx >= (self.x_max - 1) and cur_dir == 'right':
                                        self.set_key_state('right', False)
                                        cur_dir = 'left'
                                    elif cx <= (self.x_min + 1) and cur_dir == 'left':
                                        self.set_key_state('left', False)
                                        cur_dir = 'right'
                                    self.set_key_state(cur_dir, True)
                                    
                                    if self.chk_pingpong_recovery_teleport.isChecked():
                                        now_ms = time.time() * 1000
                                        if now_ms - getattr(self, 'last_recovery_teleport_time', 0.0) > self.dash_delay_ms:
                                            self.press_key(self.key_teleport_cb.currentText())
                                            self.last_recovery_teleport_time = now_ms
                                            
                                    self.set_key_state(self.key_att_cb.currentText(), False)
                                    self.is_pingpong_fixed_attacking = False
                                    time.sleep(0.04)
                                continue
                                
                            elif self.recovery_state == "executing_return_seq":
                                seq_str = self.return_sequence.strip()
                                if seq_str:
                                    actions = [a.strip() for a in seq_str.split(",") if a.strip()]
                                    self.logger.log(f"[핑퐁회수] 복귀 시퀀스 실행: {actions}", "MOVEMENT")
                                    for act in actions:
                                        if not self.is_running or self.is_selling: break
                                        self.execute_sequence_action(act)
                                        time.sleep(self.seq_delay)
                                else:
                                    self.logger.log("[핑퐁회수] 복귀 시퀀스 미설정 → 즉시 사냥 재개", "MOVEMENT")
                                    
                                # 사냥층 Y 검증
                                time.sleep(0.5)
                                with mss.mss() as sct2:
                                    cx2, cy2, _, _ = self.minimap_detector.get_player_coords(sct2)
                                    if cx2 != -1 and cy2 != -1 and abs(cy2 - self.hunt_y) <= 3:
                                        self.logger.log("[핑퐁회수] 사냥층 무사 복귀 → 사냥 재개", "WAYPOINT")
                                        self.is_recovering = False
                                        self.last_recovery_time = time.time()
                                        self.recovery_state = "idle"
                                    else:
                                        self.logger.log(f"[핑퐁회수] 사냥층 미도달 (현재 Y={cy2}) → 복귀 시퀀스 재시도", "MOVEMENT")
                                        self.recovery_state = "executing_return_seq"
                                continue
                        
                        # 자동 판매 주기 도래 처리
                        if self.chk_auto_sell.isChecked() and not self.is_recovering:
                            auto_sell_int = int(self.txt_auto_sell_interval.text().strip() or "5")
                            if time.time() - self.last_auto_sell_time > auto_sell_int * 60:
                                self.logger.log("[자동판매] 판매 주기가 되어 상점 판매 시퀀스를 시작합니다.", "SYSTEM")
                                self.run_manual_sell()
                                self.last_auto_sell_time = time.time()
                                continue

                        # --- 일반 핑퐁 사냥 메인 제어 루틴 ---
                        now = time.time() * 1000
                        
                        # 제자리 고정 사냥 모드 처리
                        if self.chk_pingpong_fixed.isChecked():
                            self.set_key_state('left', False)
                            self.set_key_state('right', False)
                            
                            # 고정점 Y축 이탈 시 미세 수직 정렬
                            if abs(cy - self.hunt_y) > 3:
                                dy = cy - self.hunt_y
                                self.movement_controller.perform_vertical_move(dy, "JUMP")
                                time.sleep(0.2)
                                continue
                                
                            if not self.is_pingpong_fixed_attacking:
                                self.set_key_state(self.key_att_cb.currentText(), True)
                                self.is_pingpong_fixed_attacking = True
                                self.att_key_hold_start = time.time()
                            
                            # 공격키 리셋 (매크로 차단 우회)
                            att_reset_sec = int(self.txt_att_reset_sec.text().strip() or "59")
                            if self.att_key_hold_start > 0 and (time.time() - self.att_key_hold_start) >= att_reset_sec:
                                att_key = self.key_att_cb.currentText()
                                self.set_key_state(att_key, False)
                                time.sleep(0.1)
                                self.set_key_state(att_key, True)
                                self.att_key_hold_start = time.time()
                                self.logger.log(f"[공격키 리셋] {att_reset_sec}초 경과 → 키 재입력 완료", "SYSTEM")
                            
                            time.sleep(0.04)
                        
                        else:
                            # 좌우 핑퐁 사냥 모드 처리
                            
                            # Y축 미세 정렬
                            if abs(cy - self.hunt_y) > 3:
                                self.set_key_state('left', False)
                                self.set_key_state('right', False)
                                self.set_key_state(self.key_att_cb.currentText(), False)
                                self.is_pingpong_fixed_attacking = False
                                dy = cy - self.hunt_y
                                self.movement_controller.perform_vertical_move(dy, "JUMP")
                                time.sleep(0.2)
                                continue
                                
                            if cx >= (self.x_max - 1) and cur_dir == 'right':
                                self.set_key_state('right', False)
                                cur_dir = 'left'
                            elif cx <= (self.x_min + 1) and cur_dir == 'left':
                                self.set_key_state('left', False)
                                cur_dir = 'right'
                                
                            self.set_key_state(cur_dir, True)
                            
                            # 공격키 꾹 누르기
                            if not self.is_pingpong_fixed_attacking:
                                self.set_key_state(self.key_att_cb.currentText(), True)
                                self.is_pingpong_fixed_attacking = True
                                self.att_key_hold_start = time.time()
                            
                            # 공격키 리셋 (매크로 차단 우회)
                            att_reset_sec = int(self.txt_att_reset_sec.text().strip() or "59")
                            if self.att_key_hold_start > 0 and (time.time() - self.att_key_hold_start) >= att_reset_sec:
                                att_key = self.key_att_cb.currentText()
                                self.set_key_state(att_key, False)
                                time.sleep(0.1)
                                self.set_key_state(att_key, True)
                                self.att_key_hold_start = time.time()
                                self.logger.log(f"[공격키 리셋] {att_reset_sec}초 경과 → 키 재입력 완료", "SYSTEM")
                            
                            # 대시 주기 시전
                            if now - l_dash >= self.dash_delay_ms:
                                self.press_key(self.key_teleport_cb.currentText())
                                l_dash = now
                                
                            time.sleep(0.04)
                            
                        # 버프 1 자동 시전
                        if self.chk_buff1_use.isChecked():
                            b1_int = int(self.txt_buff1_int.text().strip() or "180")
                            if time.time() - self.last_buff1_time > b1_int:
                                self.logger.log("[버프 1] 자동 시전 시작", "SYSTEM")
                                b1_key = self.cb_buff1_key.currentText()
                                b1_hold = float(self.txt_buff1_hold.text().strip() or "0.5")
                                self.set_key_state(b1_key, True)
                                time.sleep(b1_hold)
                                self.set_key_state(b1_key, False)
                                self.last_buff1_time = time.time()
                                time.sleep(0.5)
                                
                        # 버프 2 자동 시전
                        if self.chk_buff2_use.isChecked():
                            b2_int = int(self.txt_buff2_int.text().strip() or "200")
                            if time.time() - self.last_buff2_time > b2_int:
                                self.logger.log("[버프 2] 자동 시전 시작", "SYSTEM")
                                b2_key = self.cb_buff2_key.currentText()
                                b2_hold = float(self.txt_buff2_hold.text().strip() or "0.5")
                                self.set_key_state(b2_key, True)
                                time.sleep(b2_hold)
                                self.set_key_state(b2_key, False)
                                self.last_buff2_time = time.time()
                                time.sleep(0.5)
                                
                        # 소모품(펫물약) 자동 사용 주기 시전
                        if time.time() - l_del >= self.periodic_interval_min * 60:
                            self.press_key(self.key_pet_cb.currentText())
                            l_del = time.time()
                            
                    else:
                        # 캐릭터 위치 유실 핸들링
                        if self.use_escape_lost and (time.time() - self.last_char_seen_time > self.lost_timeout_sec):
                            self.logger.log(f"[비상] {self.lost_timeout_sec}초 이상 캐릭터 미탐색 긴급 사냥 중단", "SYSTEM")
                            self.signals.alert_signal.emit()
                            self.is_running = False
                            
                time.sleep(0.04)
        finally:
            self.set_key_state('left', False)
            self.set_key_state('right', False)
            self.set_key_state('up', False)
            self.set_key_state('down', False)
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
                    reg = {"top": self.reg_t, "left": self.reg_l, "width": self.reg_w, "height": self.reg_h}
                    try:
                        shot = np.array(sct.grab(reg))
                        img = cv2.cvtColor(shot, cv2.COLOR_BGRA2BGR)
                        m = self.color_margin
                        low = np.array([max(0, self.base_lower[2]-m), max(0, self.base_lower[1]-m), max(0, self.base_lower[0]-m)])
                        high = np.array([min(255, self.base_upper[2]+m), min(255, self.base_upper[1]+m), min(255, self.base_upper[0]+m)])
                        mask = cv2.inRange(img, low, high)
                        p_img = img.copy()
                        
                        # 핑퐁 좌우 사냥 경계선 렌더링
                        cv2.line(p_img, (self.x_min, 0), (self.x_min, self.reg_h), (59, 130, 246), 2)
                        cv2.line(p_img, (self.x_max, 0), (self.x_max, self.reg_h), (239, 68, 68), 2)
                        
                        # 낚시 설정 좌표 시각화
                        if self.use_fishing_mode and self.fish_x != -1 and self.fish_y != -1:
                            cv2.circle(p_img, (self.fish_x, self.fish_y), 6, (34, 197, 94), 2)
                            
                        cx, cy = -1, -1
                        if np.any(mask):
                            M = cv2.moments(mask)
                            if M["m00"] > 0:
                                cx, cy = int(M["m10"]/M["m00"]), int(M["m01"]/M["m00"])
                                cv2.circle(p_img, (cx, cy), 5, (34, 197, 94), -1)
                                
                        self.char_x, self.char_y = cx, cy
                        self.signals.preview_signal.emit(p_img)
                    except:
                        pass
                time.sleep(0.1)

    def status_update_loop(self):
        while not self.stop_threads:
            try:
                up = int(time.time() - self.current_hunt_start) if self.is_running else 0
                total = self.total_hunting_time + up
                self.signals.status_signal.emit({
                    "uptime": f"{up//3600:02d}:{(up%3600)//60:02d}:{up%60:02d}", 
                    "total_uptime": f"{total//3600:02d}:{(total%3600)//60:02d}:{total%60:02d}",
                    "err_cnt": self.err_cnt,
                    "char_x": self.char_x,
                    "char_y": self.char_y
                })
            except:
                pass
            time.sleep(1.0)

    def execute_sequence_action(self, act):
        # 딜레이 표기가 들어간 부분 분리 (예: "TELE_UP:0.8")
        clean_act = act.split(":")[0].strip().upper()
        
        if clean_act == "TELE_UP":
            self.set_key_state('up', True)
            time.sleep(0.05)
            self.press_key(self.key_teleport_cb.currentText())
            time.sleep(0.05)
            self.set_key_state('up', False)
        elif clean_act == "TELE_DOWN":
            self.set_key_state('down', True)
            time.sleep(0.05)
            self.press_key(self.key_teleport_cb.currentText())
            time.sleep(0.05)
            self.set_key_state('down', False)
        elif clean_act == "TELE_LEFT":
            self.set_key_state('left', True)
            time.sleep(0.05)
            self.press_key(self.key_teleport_cb.currentText())
            time.sleep(0.05)
            self.set_key_state('left', False)
        elif clean_act == "TELE_RIGHT":
            self.set_key_state('right', True)
            time.sleep(0.05)
            self.press_key(self.key_teleport_cb.currentText())
            time.sleep(0.05)
            self.set_key_state('right', False)
        elif clean_act == "JUMP_DOWN":
            self.set_key_state('down', True)
            time.sleep(0.05)
            self.press_key(self.key_jump_cb.currentText())
            time.sleep(0.05)
            self.set_key_state('down', False)
        elif clean_act == "ATTACK":
            self.press_key(self.key_att_cb.currentText())
        elif clean_act == "JUMP":
            self.press_key(self.key_jump_cb.currentText())
        elif clean_act.startswith("WAIT"):
            try:
                w_time = float(clean_act.split("_")[-1])
                time.sleep(w_time)
            except:
                time.sleep(1.0)

    def start_hunting(self): 
        if self.reg_w <= 10:
            self.minimap_detector.auto_detect_minimap()
        self.is_running = True
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.current_hunt_start = time.time()
        
        self.hunter_thread = threading.Thread(target=self.hunter_core, daemon=True)
        self.hunter_thread.start()
        self.logger.log("🚀 AUTOmaple v2.0.0 사냥 기동 시작", "SYSTEM")

    def stop_hunting(self): 
        self.is_running = False
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        if self.current_hunt_start > 0:
            self.total_hunting_time += int(time.time() - self.current_hunt_start)
            
        for key in ['left', 'right', 'up', 'down']:
            self.set_key_state(key, False)
        try:
            self.set_key_state(self.key_att_cb.currentText(), False)
        except:
            pass
        self.is_pingpong_fixed_attacking = False
        self.logger.log("🛑 사냥 시스템 중지", "SYSTEM")

    def hotkey_start_handler(self):
        if not self.is_running:
            self.signals.start_signal.emit()
        
    def hotkey_stop_handler(self):
        if self.is_running:
            self.signals.stop_signal.emit()
    
    def hotkey_sell_handler(self):
        self.signals.sell_signal.emit()

    def play_custom_sound(self): 
        def _p():
            s = time.time()
            while time.time()-s < 5 and self.use_sound_alert: 
                winsound.Beep(2500, 150)
                winsound.Beep(3500, 150)
        threading.Thread(target=_p, daemon=True).start()

    def update_x_min(self, v):
        self.x_min = v
        if hasattr(self, 'txt_pingpong_x_min'):
            self.txt_pingpong_x_min.setText(str(v))

    def update_x_max(self, v):
        self.x_max = v
        if hasattr(self, 'txt_pingpong_x_max'):
            self.txt_pingpong_x_max.setText(str(v))

    def update_stat_range(self, v):
        self.stationary_range = v

    def update_att_delay(self, v):
        self.attack_delay_ms = v

    def update_dash_delay(self, v):
        self.dash_delay_ms = v

    def update_pet_interval(self, v):
        self.periodic_interval_min = v

    def update_sell_interval(self, v):
        self.sell_interval_min = v

    def closeEvent(self, e): 
        self.stop_threads = True
        self.is_running = False
        try:
            self.set_key_state('left', False)
            self.set_key_state('right', False)
            self.set_key_state('up', False)
            self.set_key_state('down', False)
            self.drag_mouse_up()
        except: 
            pass
        e.accept()

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
            if 'AUTOmaple_v2.0.0_LK' in name or 'AUTOmaple_v2.0.0_LK' in exe:
                p = psutil.Process(pid)
                p.terminate()
                try:
                    p.wait(timeout=0.5)
                except psutil.TimeoutExpired:
                    p.kill()
        except:
            pass

if __name__ == "__main__":
    kill_duplicate_processes()
    app = QApplication(sys.argv)
    window = AUTOmapleV2()
    window.show()
    sys.exit(app.exec())
